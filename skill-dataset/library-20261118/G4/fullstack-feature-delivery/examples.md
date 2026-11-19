# 案例实录：资产管理批量编辑 + 覆盖导入（dws 前后端）

> 背景：用户是前端开发者、初次参与 Java 后端开发。需求输入形态：**形态 A（口头两句话，无 PRD/交互稿）**。需求原文：
> "1. 资产信息支持批量选中进行编辑 2. 资产信息支持重新导入覆盖更新"
>
> 形态 A 信息量最小，故阶段 0 的重心是隐含决策点确认（见下表）；若本需求以形态 B/C 输入（带 PRD/交互稿），则阶段 0 重心先变为功能点清单提炼与回读确认，决策点确认环节相同。
> 后端工程 dws-server（Java / DDD 四层 / JAX-RS+Dubbo / MyBatis-tk / EasyExcel），前端工程 dws-ops（React18 / antd5 / react-query / mobx）。

## 七阶段实录对照

| 阶段       | 实际动作                                                  | 产出                                                                             |
| ---------- | --------------------------------------------------------- | -------------------------------------------------------------------------------- |
| 0 需求甄别 | 复述两条需求，确认隐含决策                                | 定案：patch 语义 / 7 字段白名单 / 上限 500 / 覆盖由前端显式勾选                  |
| 1 现状调研 | 读 asset 模块全链路 + 前端页面                            | 现状：仅单条 CRUD、导入遇重复报错；缺口：无批量接口、无覆盖模式、前端无多选      |
| 2 方案计划 | CreatePlan 输出后端计划 → 用户批准                        | 10 文件后端计划；随后前端 6 文件计划（用户先要求落 docs 再执行）                 |
| 3 后端实现 | 分层落地 + 13 个单测                                      | 代码 + 静态核查（沙箱无 JDK，编译命令交用户）                                    |
| 4 接口文档 | 产出前端对接文档                                          | 含网关前缀/错误文案表/Excel 规范/覆盖警告；顺手补齐 @Size 校验使文档与代码同源   |
| 5 前端实现 | 类型→model→组件→页面                                      | 6 文件，后端已部署 172.20.237.241 可直接联调                                     |
| 6 验收闭环 | eslint 0 error（--fix 修 2 排序警告）+ tsc 改动文件零错误 | 输出 4 组验收用例（正向/覆盖/重复/回归）                                         |
| 7 知识沉淀 | 记忆入库                                                  | dws-server 无 JDK/Maven；dws-ops 有 Node 可本地验证；ImportExcelModal 引用方约束 |

## 关键决策实录

| 决策点         | 选择                                             | 放弃的方案                           | 理由                                                                      |
| -------------- | ------------------------------------------------ | ------------------------------------ | ------------------------------------------------------------------------- |
| 批量编辑语义   | patch（null 不改）                               | PUT 全量覆盖                         | 批量场景用户只改个别字段，全量覆盖易误清数据                              |
| 接口形态       | 新增 `POST /assets/batch-update`                 | 改造单条 `PUT /assets/{id}`          | 不破坏既有契约                                                            |
| upsert 实现    | 应用层分流（先 getByNumbers 再分 insert/update） | `INSERT ... ON DUPLICATE KEY UPDATE` | asset_number 无唯一索引，DB 层 upsert 不可行                              |
| 导入写库       | 两阶段（全量校验→事务统一写）                    | 流式边读边写                         | 顺带修复存量"部分写入"缺陷：校验失败零写入                                |
| overwrite 传参 | 可选表单字段，缺省 false                         | 必填参数 / 新接口                    | 旧前端调用行为完全不变                                                    |
| 覆盖触发       | 前端 Checkbox 显式勾选                           | 导入即覆盖                           | 覆盖是破坏性操作，必须显式选择 + 警示文案                                 |
| 上限 500       | 后端 @Size + 应用层校验 + 前端前置拦截           | 仅后端校验                           | 前端拦截体验好，后端兜底保安全                                            |
| 数据库         | 不改表                                           | 加唯一索引                           | 17+6 列已支撑；唯一索引会改变"应用层分流"设计且影响历史数据，触发条件未到 |

## 后端落地（10 文件）

```
AssetBatchUpdateVo.java      新建  ids(@NotEmpty @Size(max=500)) + 7 个可空 patch 字段
AssetRestApi.java            编辑   + POST /assets/batch-update 声明（复用既有权限绑定）
Constants.java               编辑   + OVERWRITE 常量
AssetReadListener.java       重构   纯收集不落库；overwrite 下已存在编号不再报错；空编号 NPE 防护
AssetAppServiceImpl.java     重构   importExcel 两阶段 + persistImported 分流(分批500) + batchUpdate 校验链
AssetDomainService(.Impl).java 编辑 + getByIds / getByNumbers / updateByIds / updateBatch
AssetMapper.java             编辑   + MapStruct fromBatchUpdate
AssetRestApiImpl.java        编辑   实现 batchUpdateAsset；解析可选 overwrite（解析失败仅 warn 不拒绝）
AssetAppServiceImplTest.java 新建  13 用例（批量编辑分支 + 导入分流 + listener 双模式）
```

要点：导入临时文件 try-finally 删除；批量编辑去重后校验存在性；全部事务 `rollbackFor = Exception.class`（工程惯例）。

## 前端落地（6 文件）

```
interfaces/assetManagement.ts  +IBatchUpdateAssetParams（ids + Partial<Pick<AssetProperties, 7字段>>）
models/assetManagement.ts      +batchUpdateAsset → POST /dws/asset/assets/batch-update
batchEditModal/index.tsx       新建  7 字段全非必填 + "留空保持不变"提示 + 空值剔除 + 全空拦截
assetManagement/index.tsx      编辑   Table rowSelection + 批量编辑(N)按钮(s_asset_update) + >500 拦截 + 成功清勾选
                                 handleRequest 追加 overwrite='true'
import-excel-modal/index.tsx   编辑   可选 showOverwriteOption + Checkbox + onRequest 可选第二参（其余 3 个引用方零改动）
import-excel-modal/index.less  编辑   overwrite-option 样式
```

要点：通用组件 ImportExcelModal 被 4 个页面引用，扩展全部走可选 props，opt-in 生效；patch 提交前剔除空值；覆盖 Checkbox 附警示"留空的选填列会被清空"。

## 插曲与教训

1. **mvn 不在 PATH** → 多轮确认沙箱无 JDK/Maven → 降级静态核查（每个新 API 与工程现存用法逐一比对），编译命令交用户 → 沉淀为记忆，后续任务不再重复探索
2. **写接口文档发现代码缺 @Size** → 先补代码（管理部门/管理人 1-20）再落文档，保持契约同源
3. **顺手发现存量缺陷**：导入部分写入、空编号 NPE、editModal maxLength=50 与后端 20 不一致 → 前两个随重构顺带修复，第三个作为存量问题单独告知不动
4. **前端计划先落 docs 再执行**：用户控制节奏，计划文档化后批准执行——跨端改动"计划批准后再动手"不是官僚流程，是对齐成本最低的点
5. **验收方式随环境分层**：后端静态核查 + 用户侧编译；前端本地 eslint/tsc 全量跑（过滤既有 enow 报错）

## 成效

- 后端：两功能 + 13 单测一次交付，向后兼容（旧调用零感知）
- 前端：6 文件一次通过 lint/tsc，通用组件扩展零回归风险
- 文档：接口契约 + Excel 规范 + 错误文案表，前端可独立对接
- 方法论：沉淀为本 skill（fullstack-feature-delivery）

## 续篇：环境补齐后的单测回补（逮到真 bug）

初次交付时沙箱无 JDK/Maven，13 个单测只经过静态核查、从未真正执行。后续应用户要求就地搭好 JDK8 + Maven 3.9.9（安装实录沉淀为 environment.md），回补执行单测：

1. **首跑假绿**：`Tests run: 0` + BUILD SUCCESS。排查发现三层根因：BOM 管控 junit 4.13.2 与 starter-test 自带 vintage-engine 5.5.2 不兼容（发现阶段崩溃）；排除 vintage 后 mockito-junit-jupiter 残留 junit-platform-commons 使 surefire 仍选 JUnitPlatformProvider 并自动注入 vintage。修复：模块 pom 三排除 + 显式 junit4 → surefire 退回 JUnit4Provider。
2. **真跑遗红**：13 用例 12 绿 1 红——`listener_nullAssetNumber_noNpe_markedRequiredMissing` 逮到监听器收集门槛漏洞：必填缺失（requireNum）与字段超长（lengthNum）的行未纳入“不收集”判断，会被塞进待写入列表（应用层有兜底不会落库，但契约不一致）。补齐门槛后 13/13 全绿。

教训：静态核查交付的用例，机器验证的回补不可省略——12 个用例的推理是对的，但第 13 个暴露了静态核查覆盖不到的语义缝隙；“Tests run: 0 + BUILD SUCCESS”是单测最大的陷阱。

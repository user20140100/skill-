# requirement-analysis-pro 验证案例

> 维护者测试资料，不属于运行时方法论，正常需求任务不得加载。案例聚焦电子制造业 ERP、SCM、MES 及其周边系统，用于验证触发、分类、渐进式路由、专业输出和非触发边界。

## 目录

- [测试方法](#测试方法)
- [正常与复杂场景](#正常与复杂场景)
- [边缘与风险场景](#边缘与风险场景)
- [交付路由场景](#交付路由场景)
- [不应触发场景](#不应触发场景)
- [通过标准](#通过标准)

## 测试方法

每个案例记录：

- `trigger`：是否应触发本 Skill；
- `type`：项目型、专项、变更型或不适用；
- `load`：预期读取的参考文件；
- `must`：输出必须满足的断言；
- `must_not`：禁止行为。

执行时重点观察真实输出，不只检查是否出现关键词。

## 正常与复杂场景

### VAL-001 ERP、SCM、MES 订单履约协同平台

**测试提问**：

> 我们是电子制造企业，销售订单在 ERP，供应计划在 SCM，工单和报工在 MES。现在订单交期、物料齐套和生产进度无法统一，请整理一个订单履约协同平台的完整需求，分阶段建设。

- `trigger`: yes
- `type`: project
- `load`: `doc-structure-common.md`, `doc-structure-project.md`; 关系复杂时再加载 `chart-selection.md`
- `must`:
  - 判定项目型；
  - 使用 L1～L4 描述端到端价值流、主干流程和主要场景；
  - 明确 ERP、SCM、MES 的责任边界、业务事件和数据责任源；
  - 覆盖订单、计划、物料、工单、生产进度和异常闭环；
  - 包含数据迁移、接口上线顺序、监控、运营和分阶段切片。
- `must_not`:
  - 不虚构现有系统接口和指标值；
  - 不把项目蓝图直接写成单个开发功能。

### VAL-002 SCM 物料齐套预警自动化

**测试提问**：

> 请设计一个物料齐套预警专项。SCM 根据 ERP 的订单和采购数据、MES 的工单需求，提前识别缺料并推动采购、计划和仓库处理。

- `trigger`: yes
- `type`: special
- `load`: `doc-structure-common.md`, `doc-structure-special.md`; 需要流程时加载 `chart-selection.md`
- `must`:
  - 聚焦齐套预警和处置闭环；
  - 定义齐套口径、BOM/ECO 版本、替代料、库存状态、在途和需求时间；
  - 区分规则计算、固定工作流和需要语义判断的能力；
  - 说明预警分级、责任角色、异常接管、重算、监控和效果指标。
- `must_not`:
  - 不默认使用 Agent；
  - 不补造阈值、提前期或库存可用口径。

### VAL-003 MES 工单报工页面变更

**测试提问**：

> MES 工单报工页面增加“设备停机分钟数”和“停机原因”，提交时校验原因必填，并同步给 ERP 成本归集。请写变更需求。

- `trigger`: yes
- `type`: ad_hoc
- `load`: `doc-structure-common.md`, `doc-structure-ad-hoc.md`
- `must`:
  - 输出变更前后、字段、校验、页面反馈和接口影响；
  - 核对单位、枚举、必填条件、历史记录和 ERP 同步失败处理；
  - 页面变化写入对应功能或受影响 `PAGE`，不重做整套 MES 页面；
  - 覆盖验收、兼容、监控和回滚。
- `must_not`:
  - 不输出项目级蓝图；
  - 不虚构 ERP 接口 URL 或成本规则。

### VAL-004 PLM—ERP—MES 工程变更生效

**测试提问**：

> 电子产品 ECO 发布后，PLM、ERP、MES 经常使用不同 BOM 版本。请设计工程变更生效与在制工单处理专项，包含旧版本切换、例外审批和追溯。

- `trigger`: yes
- `type`: special
- `load`: `doc-structure-common.md`, `doc-structure-special.md`; 需要状态和集成图时加载 `chart-selection.md`
- `must`:
  - 明确 PLM、ERP、MES 的版本责任和生效事件；
  - 区分未下达、已下达、在制、完工工单的处理；
  - 说明替代料、库存、工艺、追溯和回滚影响；
  - 建立状态、规则、接口、审计和验收追踪。
- `must_not`:
  - 不使用“取最新 BOM”代替业务规则；
  - 不忽略已投料和在制品影响。

### VAL-005 批次和序列号全链路追溯

**测试提问**：

> 设计从供应商来料批次、SMT 上料、生产序列号、检验、入库到客户出货的追溯需求，涉及 SRM、WMS、MES、QMS 和 ERP。

- `trigger`: yes
- `type`: project
- `load`: `doc-structure-common.md`, `doc-structure-project.md`; 对象和流程复杂时加载 `chart-selection.md`
- `must`:
  - 明确批次、序列号、物料、工单、检验和出货对象关系；
  - 定义采集点、责任系统、正向/反向追溯和数据保留；
  - 覆盖拆批、合批、返工、替换、报废和数据补录；
  - 说明接口失败、离线采集、对账、权限和审计。
- `must_not`:
  - 不将所有字段塞入一张图；
  - 不遗漏批次与序列号基数和历史追溯。

### VAL-006 供应商交付异常 Agent

**测试提问**：

> 我们希望做一个供应商交付异常 Agent，读取 SCM 采购计划、供应商回复和历史交付记录，给出风险解释、催交建议，并生成给采购员确认的沟通草稿。

- `trigger`: yes
- `type`: special
- `load`: `doc-structure-common.md`, `doc-structure-special.md`, `sdd-specification.md`; 有复杂交互时加载 `prototype-spec.md`
- `must`:
  - 证明非结构化供应商回复和上下文判断需要模型能力；
  - 定义输入时效、知识来源、工具权限、结构化输出、证据和置信度；
  - 催交通知只生成草稿或由采购确认发送；
  - 包含失败降级、人工接管、评测集、监控、成本和版本。
- `must_not`:
  - 不允许 Agent 自行修改采购订单或交期；
  - 不使用模型记忆补齐企业事实。

### VAL-007 智能排产辅助

**测试提问**：

> MES 想增加智能排产助手，综合订单优先级、物料齐套、产能、设备维护、换线和工艺约束，生成计划员可比较和确认的排产方案。

- `trigger`: yes
- `type`: special
- `load`: `doc-structure-common.md`, `doc-structure-special.md`, `sdd-specification.md`
- `must`:
  - 区分 LLM 与优化器/规则引擎职责；
  - 定义数据快照、硬约束、软约束、目标函数、权重和不可行反馈；
  - 输出基线、备选方案、影响解释和不可变审批快照；
  - 审批后执行前重新校验订单、库存、BOM、产能和设备状态；
  - 包含仿真、人工确认、下达、回写、对账和撤销。
- `must_not`:
  - 不让 LLM 直接计算确定性排产结果；
  - 不在输入变化后沿用旧审批。

### VAL-008 固定规则优先而非 Agent

**测试提问**：

> ERP 采购申请提交时，若金额超过配置阈值且物料属于固定资产，就必须走指定审批流。请判断要不要做 Agent，并写需求。

- `trigger`: yes
- `type`: ad_hoc
- `load`: `doc-structure-common.md`, `doc-structure-ad-hoc.md`
- `must`:
  - 选择参数配置、确定性校验和固定审批流；
  - 定义金额单位、阈值版本、生效范围、物料分类来源和例外；
  - 覆盖配置权限、审计、测试和回滚。
- `must_not`:
  - 不引入 Agent 或大模型；
  - 不自行给出金额阈值。

## 边缘与风险场景

### VAL-009 ERP 库存扣减小改动风险升级

**测试提问**：

> ERP 出库确认时增加一个规则：MES 工单未报工完成也允许先扣库存。看起来只是一个校验调整，请写需求。

- `trigger`: yes
- `type`: special_by_risk
- `load`: `doc-structure-common.md`, `doc-structure-special.md`
- `must`:
  - 因库存和生产状态一致性升级为专项深度；
  - 分析 ERP 库存、MES 工单/WIP、过账、成本和追溯影响；
  - 覆盖并发、重复扣减、补偿、对账、权限和审计。
- `must_not`:
  - 不按普通页面校验变更直接交付；
  - 不忽略逆向冲销和失败恢复。

### VAL-010 信息不足

**测试提问**：

> 帮我做一个 MES 异常管理需求，越详细越好。

- `trigger`: yes
- `type`: pending_classification
- `load`: `doc-structure-common.md`; 分类所需信息确认后再读取一种类型文件
- `must`:
  - 先定义当前已知问题和最小待确认项；
  - 只追问会影响范围、规则、数据、自动化和验收的信息；
  - 可先给分析骨架和待确认清单。
- `must_not`:
  - 不虚构异常类型、流程、角色、阈值、接口和页面；
  - 不预读全部参考文件。

### VAL-011 多功能异常驾驶舱页面

**测试提问**：

> 为工厂计划员设计一个异常驾驶舱，集中处理订单欠料、工单延期、设备停机和质量冻结，需要列表、下钻、批量分派和 AI 建议。请输出需求和原型输入。

- `trigger`: yes
- `type`: special
- `load`: `doc-structure-common.md`, `doc-structure-special.md`, `prototype-spec.md`; AI 开发规格明确时再加载 `sdd-specification.md`
- `must`:
  - 建立多个 `FR` 和共享 `PAGE`，双向映射；
  - 定义组织/工厂范围、指标口径、异常状态、批量上限和权限；
  - 页面展示证据、影响预览、建议、人工确认和失败降级；
  - 独立原型包引用而不复制业务规则。
- `must_not`:
  - 不为每个功能重复定义同一驾驶舱页面；
  - 不把无页面的后台计算强行页面化。

## 交付路由场景

### VAL-012 ERP—MES 工单状态 SDD

**测试提问**：

> 把 ERP 下达生产订单、MES 接收并执行、完工回传的状态同步需求整理成可直接交给开发和测试的 SDD 规格包。

- `trigger`: yes
- `type`: special_sdd
- `load`: `doc-structure-common.md`, `doc-structure-special.md`, `sdd-specification.md`
- `must`:
  - 输出需求基线、`spec.md`、测试和追踪矩阵；
  - 定义状态、事件、幂等、乱序、重放、部分成功、补偿和对账；
  - 覆盖 ERP/MES 责任、业务日历、工厂和工单版本；
  - 未通过 DoR 时保持 Draft。
- `must_not`:
  - 不虚构框架、数据库、类名和代码任务；
  - 不以流程图代替状态和接口条款。

### VAL-013 转飞书云文档

**测试提问**：

> 需求内容确认后，请把这份 MES 工单异常需求转成正式飞书云文档。

- `trigger`: yes
- `type`: same_as_source
- `load`: 已完成需求所需文件；本 Skill 不加载飞书读写参考
- `must`:
  - 先保证 Markdown 内容完整并通过质量检查；
  - 再交由 `lark-doc-studio` 转换与发布。
- `must_not`:
  - 不在本 Skill 中直接读写飞书文档或画板；
  - 不复制远端写入和视觉实现规则。

### VAL-016 沿用已有需求文档格式

**测试提问**：

> 请按《报价需求 V2.1》的现有章节和表格格式，把本次会议纪要中的修改内容整合进去；同时参考《客户主数据需求》和《价格规则需求》，检查数量、字段、状态和规则是否前后一致。不要改成新的需求模板。

- `trigger`: yes
- `type`: same_as_source
- `load`: 目标需求文档、会议纪要及用户指定的相关需求文档；不加载结构模板
- `must`:
  - 保留目标文档的章节顺序、编号、表格结构、术语和表达粒度；
  - 将会议纪要内容去重后归入原有章节，不强制新增标准章节或编码；
  - 检查数量、单位、字段、状态、规则、版本和引用关系的前后一致性；
  - 对照两份相关需求文档验证系统边界、功能归属、字段定义和业务规则；
  - 标明冲突来源、影响和【待确认】事项，不自行选择一种说法覆盖其他来源。
- `must_not`:
  - 不套用项目型、专项或变更型标准目录；
  - 不强制新增 `FR-xxx`、`PAGE-xxx` 或 `Q-xxx`；
  - 不把其他需求文档中的内容无依据地并入目标文档。

## 不应触发场景

### VAL-014 纯 SQL 优化

**测试提问**：

> 帮我优化一段查询 MES 工单良率的 StarRocks SQL，降低扫描量。

- `trigger`: no
- `type`: not_applicable
- `load`: none
- `must`: 路由到 SQL 或数据开发能力
- `must_not`: 不生成需求分析文档

### VAL-015 纯接口编码

**测试提问**：

> 请用 Java 写一个接收 ERP 工单消息的 Kafka 消费者，并补单元测试。

- `trigger`: no
- `type`: not_applicable
- `load`: none
- `must`: 路由到编码能力
- `must_not`: 不自动扩展为 ERP—MES 需求分析

## 通过标准

- 16 个案例的触发和类型判定全部正确。
- 每个触发案例只加载必要参考文件，没有普通任务全量加载 references。
- 项目型、专项、变更型和风险升级路由正确。
- 流程只使用统一 L1～L6；系统功能使用模块、功能组和 `FR`。
- `FR` 与 `PAGE` 职责清楚，无页面功能不创建页面。
- ERP、SCM、MES 的数据责任、状态、事件、接口和运行边界得到核对。
- 确定性规则优先于 Agent；AI 场景包含人审、安全、降级、评测和运营。
- 未知流程、规则、阈值、字段和接口均标「待确认」，没有编造。
- SDD 场景保持 What/Verify 与 How/When 分离。
- 非触发案例不生成需求文档。

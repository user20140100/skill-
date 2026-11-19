# 实习课题任务清单（TODO）

> 课题：AI Agent 技能（Agent Skills）全链路安全审计与效果评估系统
>
> 答辩时间：2026-11-19 16:00-17:00（周四下午）｜ 答辩地点：1103 ｜ 代码提交：https://dojo.gz.cvte.cn/

## 阶段一：技术调研与环境搭建

- [x] **1. 调研并锁定开源评估框架**
  - 寻找一个或多个支持「三层评估」的开源框架：① 静态质量与安全扫描 ② 语义去重（冗余冲突分析）③ 实时沙盒评估（效果评估）
  - 锁定一套与其配套的专用 Agent Skill 静态/模型驱动安全扫描器（注意：框架与扫描器可能是两个独立项目）
  - 产出选型结论（选定项目作为后续开发的基线）

- [x] **2. 本地 Mac 环境搭建并跑通**
  - 安装所选框架及底层安全扫描器组件的全套依赖
  - 安装并配置 **Docker 沙盒环境**（效果评估环节的前提）
  - 配置 **LLM API Key**
  - 跑通官方基准示例（benchmark）

## 阶段二：攻防测试与三层评估实战

- [ ] **3. 创建 3 个测试靶场 Skill**（数据集已构建 51 个：正向 14 / 冗余 30 / 安全 7）
  - [x] ① 正向业务 Skill（`skill-dataset/positive/`，14 个）
  - [x] ② 冗余冲突 Skill（`skill-dataset/redundant/`，30 个 8 组，测语义重叠拦截）
  - [x] ③ 安全靶场 Skill（`skill-dataset/security/custom-rules-range/`：刻意植入规则 A 白名单放行（非白名单外发保留告警）+ 规则 B 明文凭证正样本，及占位符负样本，用于验证任务 A 规则与演示查杀）

- [x] **4. 运行完整评估流水线并验证三环节**（基线 tier1/2/3 已成功复现跑通）
  - [x] 流水线跑通：Tier1 `reports/skillevaluator-tier1.*`、Tier2 `reports/redundant-catalog.json`、Tier3 `positive/changelog/evals/results/*`（with/without 对照）
  - [x] 收尾量化结论：对 dataset 三组出最终报告 —— security→flag 审计报告、redundant→dup、positive→pass_rate_gain / Lift（产出 `docs/收尾量化结论.md`）

- [x] **5. 开发冗余冲突 Skill 的推荐功能**（已端到端验证）
  - [x] 评估后向用户推荐更优 Skill：`judge`（确定性规则 + 报告渲染 + 可选 LLM 叙述）
  - [x] 联网搜索相关 Skill 供用户查看选择：`detect`（正向 skill 对公司库 catalog 语义比对）+ `search`（`cskills` 关键词）
  - [x] 参数式选定冗余 skill（`pipeline --candidate`）+ 共享用例自动复制（`--eval-source`）
  - [x] 单元测试 77 例全绿；与官方三层评估解耦（`skill-evaluation-pipelines/`、`skill-security-scanners/` 零改动）
  - [x] 真实 Docker 端到端跑通 `detect → pipeline → judge`：正向 `calc-pro` vs 冗余 `calculator`（相似度 0.913），产出双结论推荐报告 `reports/recommendation.md`
  - [x] 编写 skill 中立共享用例集（`skill-dataset/shared/arithmetic`，9 例）+ 确定演示对（calc-pro / calculator）
  - [x] 增益轨评判指标优化：不评估流程准确性/工具调用准确性，改为「结果一致 + skill 激活 + token 输入/输出 + 耗时 + 轮数」作效率依据；结论文档 `docs/正向skill与冗余skill的适用边界结论.md`

## 阶段三：安全规则扩展与工程化交付

- [x] **6. 开发自定义安全审计策略扩展（任务 A）**（完整需求见 `docs/自定义安全检测扩展需求.md`；.yar 规则 + suppression 扩展已落地并验证）
  - 深入研究安全扫描器与评估框架的规则机制
    - ✅ 已确认：自定义规则应加到 **SkillSpector 扫描器**（规则引擎），而非框架流水线；官方扩展点为 `--yara-rules-dir`，非侵入式挂载 YARA 规则
  - 新增 **2 项**企业自定义安全审计扩展（规则 A 抑制层放行 + 规则 B 检测规则）：
    - [x] **规则 A：域名白名单放行（抑制层扩展，不新增告警）**
      - 定位：与规则 B（新增告警规则）正交的「放行/降误报」扩展——数据发往用户信任的域名时不再作为风险 finding，避免误报；本身**不新增任何 finding**
      - 现状：SkillSpector 已有 `Baseline`/`partition_findings` 抑制机制（`suppression.py`），在评分与去重前拦截；但 `SuppressionRule` 仅支持 `id`/`path`/`message` 三个 glob 维度，无「域名」维度
      - 落点：SkillSpector `suppression.py`，扩展 `SuppressionRule` 增加 `allow_domain`（可选 `methods` 二维白名单）；经 `--baseline baseline.yaml` 挂载
      - 实现要点：
        - 从 `finding.file` + `start_line` 经 `file_cache` 取原文行，正则提取目标 host（去协议/端口、小写归一化）
        - 精确 host 匹配 + `*.` 子域名通配（不支持任意正则）；复用 `reason` 必填 + `suppressed` 审计留痕
        - 方式维度复用 rule_id/sink 分类（E1=http、E5=cloud-storage、socket=TT sink），零新增文本提取
      - 边界：仅覆盖「字面量 URL」；变量/动态 URL 需常量传播（列为范围外）；ftp 外发当前无检测规则，需先补 YARA 检测才有对象可放行
      - 验证：靶场 Skill 植入发往白名单域名的外发，确认进 `suppressed` 不计分；发往非白名单域名仍正常告警
    - [x] **规则 B：禁止明文凭证内嵌命令行 / 连接串**
      - 现状：PE3「Credential File Access」已覆盖读取敏感文件（`~/.ssh/*`、`.env`、`.netrc`、`.docker/config.json`、浏览器 Cookie 库、keychain、`/etc/shadow` 等，见 `static_patterns_privilege_escalation.py:125-149`），「读敏感文件」维度已饱和；但「凭证出现在进程参数 / 命令行 / 连接串」这一泄露面无规则覆盖（全仓 grep `chpasswd`/`-u user:pass`/URL userinfo 零命中）
      - 落点：SkillSpector，新增 YARA 规则（匹配 `echo '<user>:<pw>' | chpasswd`、`curl -u user:pass`、`mysql -p<pass>` / `psql "postgres://user:pass@host"` 连接串、URL userinfo `://user:pass@`）
      - 验证：在靶场 Skill 植入 `echo 'root:P@ss' | chpasswd` / `curl -u admin:secret https://...` / `mysql -uroot -pSecret123` / `psql "postgres://admin:pass@db.internal/db"` 指令，确认命中
  - 在靶场 Skill 上验证规则 B 检测与规则 A 放行的拦截/放行效果
  - [x] 规则开关（灰度控制）：运行完整 tier1 前可自由勾选启用/停用规则 A/B（独立开关），对比启用前后审查结果差异（`custom-rules/select.yaml` + `toggle.py`，4 组合已实测正交）

- [x] **7. 编写自动化流水线 CLI 脚本（任务 B，Python）**
  - [x] 一键批量扫描目录下所有 Skill：`scan --dir` 自动发现含 `SKILL.md` 的 skill；`--run` 真执行（默认 dry-run 打印命令）
  - [x] 过滤高危风险项：`security.verdict == "unsafe"`（SkillSpector HIGH/CRITICAL 或 Tier1 critical/high>0）进「高危风险项」表
  - [x] 输出包含「安全评级 + 沙盒对比数据」的 **Markdown / HTML** 综合审计报告（`render_markdown`/`render_html`，含 HTML 转义防注入）
  - [x] 支持 LLM 语义分析：`--llm` 去掉 `--no-llm`（默认静态）；qwen3.8-flash 实测跑通（es-log-query 风险分 36→87、Tier1 high 6→12）
  - [x] 单元测试 80 例全绿；端到端验证高危过滤 + 报告输出（`reports/audit*.md/.html`）

- [x] **8. 编写可复现的 `README.md`**（`deliverables/02-完整代码与测试靶场/README.md` 已就绪；根 README.md 提交前替换为正式版）

## 阶段四：进阶扩展（加分项）

- [ ] **9. 实现检测到 Skill 问题后的自动修复功能**

## 交付物

- [x] **10. 架构与安全机制解析报告**（`deliverables/01-架构与安全机制解析报告/` 已完成；待补任务 A 细节与 Tier3 量化数据）
  - 拆解评估框架与底层安全扫描器的协同工作原理
  - 覆盖「静态扫描 vs LLM 深度安全审计 vs 沙盒隔离实测」三者的分工

- [x] **11. 现场演示与复盘准备**（`deliverables/03-现场演示与复盘/`：脚本 + 排障笔记 + 复盘报告已就绪）
  - 现场演示对「恶意靶场 Skill」的查杀过程
  - 展示评估报告
  - 分享 Mac 环境下的排障经验

- [ ] **12. 完整代码与测试靶场仓库**（最终交付；3 个 Skill + README + 任务 A 规则 + 任务 B 脚本已就绪）
  - 3 个自建测试 Skill
  - 自定义安全规则配置 / 代码
  - 一键批处理脚本
  - 可复现的 `README.md`

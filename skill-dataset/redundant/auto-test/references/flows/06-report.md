# 06-report. 测试报告与覆盖率看板子流程

## 目标

聚合历史运行数据（`runs/*/summary.json`）和 nl 用例清单，生成零依赖的静态 HTML 看板，展示通过率趋势、模块覆盖率、失败 Top-N 和 Flaky 检测。

## 前置条件

- `.auto-test/` 已初始化（`01-init` 完成）
- 至少有 1 个 `runs/run-*/summary.json` 存在

## 产物

```text
.auto-test/reports/
  history.json        ← 聚合数据（进 git，供团队共享和 CI 读取）
  dashboard.html      ← 静态看板（不进 git，本地查看）
```

## 触发来源

- **自动**：`04-spec-run` Step 8 报告生成完毕后自动调用
- **手动**：用户说"生成报告"/"看覆盖率"/"dashboard"/"测试看板" 时路由到此

## 步骤

### Step 1: 生成 history.json

```bash
node ~/.claude/skills/auto-test/scripts/report_gen.mjs --root <项目根>
```

读取 stdout JSON：

| 结果 | 处理 |
|---|---|
| `{ "error": "NO_RUNS", ... }` | 告知用户"暂无运行记录，请先执行一次 04-spec-run" |
| `{ "ok": true, ... }` | 继续 Step 2 |

### Step 2: 拷贝 dashboard.html 并注入数据

将 skill 模板拷贝到项目报告目录：

```bash
cp ~/.claude/skills/auto-test/templates/dashboard.html .auto-test/reports/dashboard.html
```

若已存在则覆盖（模板可能有版本更新）。

然后将 `history.json` 内联注入到 dashboard.html 中（使 `file://` 协议下也能正常加载）：
在 HTML 的第一个 `<script>` 标签开头插入一行 `window.__DASHBOARD_DATA__ = <history.json内容>;`。

### Step 3: 告知用户

```text
测试看板已生成：
  - 数据文件：.auto-test/reports/history.json
  - 看板页面：.auto-test/reports/dashboard.html

用浏览器打开 dashboard.html 即可查看（零依赖、离线可用）。

包含：
  - 最近一次运行总览（通过率/通过/失败/fixme/升级）
  - 通过率历史趋势图
  - 按模块的覆盖率分布
  - 失败 Top-10 排行
  - Flaky 用例检测
```

## 看板维度说明

| 维度 | 数据来源 | 说明 |
|---|---|---|
| 总览卡片 | 最近一次 runHistory | passed/failed/fixmed/escalated 计数 + 通过率 |
| 趋势图 | 全量 runHistory | 纯 SVG 折线图，x 轴时间、y 轴通过率 |
| 模块覆盖率 | moduleCoverage | 按 route-key 分组；nlCount（分母）、lastPassCount（分子）；色块三档 ≥80%/≥50%/<50% |
| 失败 Top-N | failTopN | 最近 10 次运行中失败次数最多的前 10 个 caseId |
| Flaky 检测 | flaky | 最近 10 次运行中状态交替 ≥2 次的用例 |

## 与 04-spec-run 的联动

`04-spec-run` Step 8（report.md 写完后）追加：

```text
Step 8.1: 调用 06-report 更新看板
  - 运行 report_gen.mjs
  - 拷贝 dashboard.html
  - 提示用户可查看看板
```

## 事故级硬约束

- 报告生成失败不阻塞 04-spec-run 的完成判定（report 是增值产物，不是完成门）
- history.json 只聚合数据，不修改任何 runs/ 或 nl/ 文件
- dashboard.html 通过 fetch('./history.json') 加载数据，不内嵌数据到 HTML

# Playwright CLI Protocol

auto-test 使用 `@playwright/cli` 作为唯一的浏览器探查层，使用 Playwright Test (`npx playwright test`) 作为测试执行层。禁止在 skill 流程中依赖其它浏览器自动化通道。

## 前置要求

执行任意页面探查前必须确认：

```bash
command -v playwright-cli >/dev/null 2>&1
playwright-cli --help >/dev/null
```

缺失时安装：

```bash
npm install -g @playwright/cli@latest
playwright-cli install --skills agents
```

执行页面探查的 agent 必须先读取项目根的 `.agents/skills/playwright-cli/SKILL.md`，再读取本文件。前者提供官方最新 CLI 用法，后者提供 auto-test 的安全约束。若 `.agents/skills/playwright-cli/SKILL.md` 不存在，先执行 `playwright-cli install --skills agents`。

协议按当前官方 `playwright-cli --help` 约定维护。由于安装使用 `@playwright/cli@latest`，执行前必须通过 `playwright-cli --help`；如发现命令名变化，先更新本协议再继续执行页面探查。

## Session 规则

- 每个任务必须使用独立短 session：`playwright-cli -s=at-<hash8> ...`。
- `<hash8>` 由 `routeKey / caseId / runId` 等稳定输入计算，建议取 sha1 的前 8 位；不要直接拼接完整 routeKey + caseId，避免超过 CLI 底层 socket 路径长度限制。
- 打开业务页面前如需要登录态，必须先 `open about:blank` 创建 session，再执行 `state-load <storageStatePath>`，最后 `goto <url>`。
- 任务结束后执行 `playwright-cli -s=<session> close`；异常中断时可用 `playwright-cli kill-all` 清理。
- 同一路由内仍然串行回写 `_selectors.ts` / `_mocks.ts`，session 隔离不能替代文件写入互斥。

## 命令映射

| 场景 | 命令 |
| --- | --- |
| 打开页面 | `playwright-cli -s=<session> open <url>` |
| 导航 | `playwright-cli -s=<session> goto <url>` |
| 页面结构 | `playwright-cli -s=<session> snapshot` |
| 点击 | `playwright-cli -s=<session> click <ref>` |
| 输入文本 | `playwright-cli -s=<session> type <text>` |
| 填充字段 | `playwright-cli -s=<session> fill <ref> <text>` |
| 下拉选择 | `playwright-cli -s=<session> select <ref> <value>` |
| 复选/单选 | `playwright-cli -s=<session> check <ref>` / `playwright-cli -s=<session> uncheck <ref>` |
| 悬停 | `playwright-cli -s=<session> hover <ref>` |
| 拖拽 | `playwright-cli -s=<session> drag <startRef> <endRef>` |
| 文件上传 | `playwright-cli -s=<session> upload <file>` |
| 截图 | `playwright-cli -s=<session> screenshot` |
| 键盘 | `playwright-cli -s=<session> press <key>` / `keydown <key>` / `keyup <key>` |
| 历史导航 | `playwright-cli -s=<session> go-back` / `go-forward` / `reload` |
| 标签页 | `playwright-cli -s=<session> tab-list` / `tab-new [url]` / `tab-select <index>` / `tab-close [index]` |
| 弹窗 | `playwright-cli -s=<session> dialog-accept [prompt]` / `dialog-dismiss` |
| Console | `playwright-cli -s=<session> console` |
| 网络请求列表 | `playwright-cli -s=<session> requests` |
| 单条请求详情 | `playwright-cli -s=<session> request <num>` |
| 网络 mock | `playwright-cli -s=<session> route <pattern>` / `route-list` / `unroute [pattern]` |
| 执行 JS | `playwright-cli -s=<session> eval <func>` |
| 执行 Playwright 代码 | `playwright-cli -s=<session> run-code <code>` |
| 保存登录态 | `playwright-cli -s=<session> state-save <path>` |
| 加载登录态 | `playwright-cli -s=<session> state-load <path>` |
| 关闭页面 | `playwright-cli -s=<session> close` |

> 表格中 `/` 表示多个可选子命令，不是一条可直接执行的命令字符串；实际执行时必须选择其中一个完整命令。

## Snapshot 规则

- selector、文案、URL、状态必须来自 `playwright-cli -s=<session> snapshot`、`requests`、`console`、`eval` 或 `run-code` 的真实输出。
- 每次点击、输入、导航、加载登录态、mock 网络或触发页面变化后，必须重新执行 `snapshot` 再继续定位元素。
- snapshot 中的 ref 只用于当前 CLI 操作，不得直接写入 spec；写入 `_selectors.ts` 时必须映射为七选一 locator：`getByRole > getByLabel > getByPlaceholder > getByText > getByAltText > getByTitle > getByTestId`。
- 禁止凭 CSS/XPath/querySelector 补 selector，除非用于临时 `eval` 或 `run-code` 诊断且不落入测试资产。

## 等待规则

`@playwright/cli` 没有单独的 `wait_for` 等价命令。等待必须使用有界条件：

```bash
playwright-cli -s=<session> run-code "await page.getByText(/提交成功/).waitFor({ timeout: 10000 })"
playwright-cli -s=<session> run-code "await page.getByRole('button', { name: /提交/ }).waitFor({ state: 'visible', timeout: 10000 })"
```

若使用 snapshot 轮询，最多重试 5 次，每次间隔不超过 2 秒；仍未满足时停止并报告，不得用无界等待或固定长 sleep 掩盖问题。

## 登录态规则

SSO 或企业登录采集使用有头持久 session：

```bash
mkdir -p .auto-test/.auth
playwright-cli -s=auto-test-login open <baseUrl> --headed --persistent
# 用户完成登录后
playwright-cli -s=auto-test-login state-save .auto-test/.auth/storageState.json
playwright-cli -s=auto-test-login close
```

保存后必须校验 `storageState.json` 存在且 cookies 或 origins 非空。禁止用 `document.cookie` 自行拼 storageState。

后续加载登录态的推荐顺序：

```bash
playwright-cli -s=<session> open about:blank
playwright-cli -s=<session> state-load .auto-test/.auth/storageState.json
playwright-cli -s=<session> goto <business-url>
```

## 证据规则

涉及动态页面探查的 agent 必须在结构化输出中记录：

- session 名称
- 打开的 URL
- 使用过的关键命令
- snapshot 文件路径或输出摘要
- 从真实页面读到的关键事实

主流程发现动态决策缺少这些证据时，必须拒收并要求重做。

## 浏览器安装规则

浏览器安装使用 CLI 自带命令，不混用 `npx playwright install`：

```bash
playwright-cli install-browser chromium
```

Linux/CI 需要系统依赖时使用：

```bash
playwright-cli install-browser chromium --with-deps
```

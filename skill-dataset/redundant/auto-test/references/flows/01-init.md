# 01. 初始化子流程

## 目标

初始化只做项目接入和运行基础设施准备，不生成 doc、plan、nl 或 spec。

初始化完成后，后续流程必须能知道：

- 项目根目录。
- 源码根目录。
- 测试环境地址。
- 需求文档来源。
- 登录方式。
- auto-test 产物目录。

## 步骤 1：LLM 先探索项目

不要一开始就把所有问题抛给用户。先只读探索项目：

- 识别项目类型：React、Vue、Next、Vite、Umi、Angular 或其他。
- 识别路由结构：如 `src/pages`、`src/views`、`src/routes`、`app`、`pages`。
- 识别测试配置：是否已有 `playwright.config.ts`。
- 识别需求文档候选位置：如 `docs/`、`README.md`、`prd/`、`requirements/`。

如果是标准有路由前端项目，并且只有一个可信的源码根目录，直接采用该目录作为 `componentRoot`，不要再问用户。

**若探索时发现项目已有 e2e/Playwright/cypress 等测试目录（`tests/`、`e2e/`、`playwright/`、`test/e2e/` 等）但 `.auto-test/` 不存在对应 doc/plan/nl**：必须先停下，跳到 `references/flows/00-bootstrap-from-existing-specs.md`，与用户对齐处理方式（重新走 / 反向回填 / 仅接管新模块），确认后再回到本流程的步骤 2。

只有出现以下情况才询问用户：

- 存在多个同等可信的源码根目录。
- 无法判断路由入口。
- 自动判断会影响后续测试范围。
- `baseUrl`：即使从项目配置推断出来，也必须向用户确认后才能采用。
- `loginType`：必须向用户确认，不能由 LLM 自行决定。

## 步骤 2：形成配置

生成 `.auto-test/config.json` 所需字段：

```json
{
  "version": "0.1",
  "initialized": true,
  "baseUrl": "<测试环境地址>",
  "componentRoot": "<源码根目录>",
  "docs": {
    "mode": "external|internal|none",
    "externalPath": "<已有需求文档路径，可空>"
  },
  "loginType": "form|sso|none",
  "syncIgnore": ["**/*.pdf", "README*"]
}
```

字段规则：

- `baseUrl` 即使能从项目配置推断，也必须经用户确认后才能写入，不能编造。
- `componentRoot` 优先由 LLM 探索得出。
- `docs.mode=external` 表示项目已有需求文档。
- `docs.mode=internal` 表示后续由代码反推需求并写入 `.auto-test/docs/`。
- `docs.mode=none` 只在用户明确暂不接入需求文档时使用。
- `syncIgnore` 是项目特有的"sync 忽略路径"，会**追加**到 `sync_collect.mjs` / `sync_check.mjs` 的内置默认黑名单后。默认黑名单已覆盖 `.auto-test/**`、`*.lock`、`.eslintrc*`、`dist/**`、`tests/**`、`*.spec.ts`、`*.test.ts` 等通用项；项目可在此追加自己的特殊路径，如 `src/legacy/**`、`scripts/codegen/**`。**不能覆盖默认黑名单**，只能追加。初始化时填空数组即可，后续按需补。

## 步骤 3：创建目录

必须创建：

```text
.auto-test/
  config.json
  docs/
  case/
    plans/
    nl/
    specs/
  runs/
  .auth/
  .tmp/
```

目录规则：

- `.auto-test/docs/` 永远创建。
- `docs.mode=external` 时，`.auto-test/docs/` 保存 auto-test 的需求映射文档，链接到已有需求文档，不直接覆盖原文档。
- `.auto-test/docs/`、`.auto-test/case/plans/`、`.auto-test/case/nl/`、`.auto-test/case/specs/` 是团队共享资产，可进 git。
- `.auto-test/runs/`、`.auto-test/.auth/`、`.auto-test/.tmp/` 是本地运行或敏感数据，不进 git。

## 步骤 3.5：安装 Playwright CLI 与浏览器

> `SKILL.md §2.1.0` 已前置确保 `playwright-cli` 可用。本步骤负责把目标项目运行 Playwright 所需的浏览器安装好，并确保 `.agents/skills/playwright-cli` 已写入项目根。

### 安装 Playwright CLI skills（幂等）

```bash
playwright-cli install --skills agents
```

后续主流程与 subagent 都必须先读取 `.agents/skills/playwright-cli/SKILL.md` 获取官方 CLI 用法，再读取 auto-test 的 `references/playwright-cli-protocol.md` 获取本 skill 的 session、登录态和取证约束。

判定：

- 成功（exit code 0）→ 继续安装 Chromium。
- 失败 → 停止并报告错误信息（常见原因：`@playwright/cli` 安装不完整、权限不足、磁盘不可写）。

### 安装 Chromium（自动）

```bash
playwright-cli install-browser chromium
```

> 幂等操作：已安装时立即返回，未安装时自动下载 ~150MB。

判定：

- 安装成功（exit code 0）→ 继续后续步骤
- 安装失败 → 停止并报告错误信息（常见原因：网络不通、磁盘空间不足、权限问题）

Linux/CI 环境额外处理（macOS/Windows 跳过）：

```bash
if [[ "$OSTYPE" == "linux"* ]]; then
  playwright-cli install-browser chromium --with-deps 2>/dev/null || echo "⚠️ 系统依赖安装需要 sudo 权限，请手动执行: sudo playwright-cli install-browser chromium --with-deps"
fi
```

---

## 步骤 4：登录与 Playwright

### 步骤 4.0：dev server 端口探活（强制前置）

调用 `playwright-cli open <url>` 或 `playwright-cli goto <url>` 之前必须先确认 `baseUrl` 可达。否则 CLI 会撞 `net::ERR_CONNECTION_REFUSED`，浪费一轮交互且产生误导性错误。

探活方式（任选，且必须在 LLM 自己的 Bash 中执行，不是丢给用户）：

```bash
curl -sf -o /dev/null -m 3 <baseUrl> && echo OK || echo DOWN
# 或
lsof -iTCP:<port> -sTCP:LISTEN -n -P >/dev/null && echo OK || echo DOWN
```

判定：

- 探活返回 `OK`：继续登录采集。
- 探活返回 `DOWN` 或超时：**停止**当前步骤，明确告知用户 dev server 未启动、需要启动哪个命令（从 `package.json` scripts 中选最贴近的，例如 `npm run dev`/`hot:fat` 等），等用户确认服务起来后再继续。
- 不允许跳过探活直接调 `playwright-cli`。

> 注：`loginType=none` 也要探活，否则连 `baseUrl` 都打不开还谈什么测试。

### 步骤 4.1：登录方式

LLM 可先探索项目推断 `loginType`，但**必须向用户确认后才能采用**。向用户展示推断结果和依据，由用户选择 `form` / `sso` / `none`。

记录 `loginType`：

- `form`：需要登录页、账号输入框提示、密码输入框提示、登录按钮文案、登录后 URL。
- `sso`：必须由 LLM 主动用 `playwright-cli` 以有头持久 session 打开 `baseUrl`，让用户在浏览器里完成登录，然后通过 `playwright-cli state-save` 直接导出到 `.auto-test/.auth/storageState.json`。**禁止只丢一段 `npx playwright codegen` 命令让用户自己跑**，也不要用 `document.cookie` 自己拼 storageState。
- `none`：公开页面无需登录。

SSO 采集流程（LLM 必须主动执行，不能让用户自行操作）：

1. 确保 auth 目录存在：
   ```bash
   mkdir -p .auto-test/.auth
   ```
2. 打开有头持久 session：
   ```bash
   playwright-cli -s=auto-test-login open <baseUrl> --headed --persistent
   ```
3. 提示用户在弹出的浏览器中完成登录，登录后无需关闭窗口。
4. LLM 用 `snapshot` 或有界 `run-code` 确认出现登录后的业务页面特征：
   ```bash
   playwright-cli -s=auto-test-login snapshot
   # 或
   playwright-cli -s=auto-test-login run-code "await page.getByText(/<登录后页面文案>/).waitFor({ timeout: 10000 })"
   ```
5. 保存完整登录态：
   ```bash
   playwright-cli -s=auto-test-login state-save .auto-test/.auth/storageState.json
   ```
6. 校验文件存在且非空（`cookies.length > 0` 或 `origins.length > 0`），再继续后续步骤。
7. 校验通过后，**必须主动关闭 session**：
   ```bash
   playwright-cli -s=auto-test-login close
   ```

`playwright-cli` 登录态采集约束：

- 保存登录态只能用 `state-save` 或 Playwright 原生 `storageState({ path })`，禁止读 `document.cookie` 自己拼。
- 手动登录必须使用 `--headed --persistent`，否则用户无法完成 SSO 或浏览器关闭后状态丢失。
- 后续页面探查进入业务页前必须按顺序执行：`playwright-cli -s=at-<hash8> open about:blank` → `playwright-cli -s=at-<hash8> state-load .auto-test/.auth/storageState.json` → `playwright-cli -s=at-<hash8> goto <业务URL>`。`<hash8>` 取 routeKey/caseId/runId 等稳定输入的短 hash，禁止直接拼接长 routeKey + caseId。

检查 Playwright 配置：

- 无 `playwright.config.ts` 时，复制 `~/.claude/skills/auto-test/templates/playwright.config.template.ts` 到项目根目录的 `playwright.config.ts`，并替换其中标 `<<< ... >>>` 的占位字段（至少 `baseURL`，与 `.auto-test/config.json` 的 `baseUrl` 保持一致）。模板内置 `testDir=.auto-test/case/specs`、`storageState=.auto-test/.auth/storageState.json`、html/json reporter 输出到 `.auto-test/runs/last/`，与本 skill 的目录约定对齐。
- 已有 `playwright.config.ts` 时，**禁止覆盖**。读取后逐项比对模板，明确告知用户需要合并的字段：`testDir`、`use.baseURL`、`use.storageState`、`reporter`、`outputDir`、`timeout`、`expect.timeout`、`use.trace/video/screenshot`，由用户决定是否合并。
- 模板路径：`~/.claude/skills/auto-test/templates/playwright.config.template.ts`（实际调用时把 `~` 展开为绝对路径）。

## 步骤 5：gitignore

确保以下路径不进 git：

```text
.auto-test/.auth/
.auto-test/runs/
.auto-test/.tmp/
.playwright-cli/
```

> `.playwright-cli/` 是 `@playwright/cli` 保存 snapshot、截图、session 辅助文件的本地目录，各人本地各自生成，绝不进 git。

## 步骤 6：装增量同步基础设施

为支持后续 `05-sync.md` 增量同步流程，init 末尾必须把 hook 与 sync-state 装好。**所有动作由 LLM 用 Bash / Write / Edit 工具直接执行，不再封装额外脚本。**

### 6.1：探测 git-ai

```bash
command -v git-ai >/dev/null 2>&1 && echo OK || echo MISSING
```

- `OK` → 打印 `✅ git-ai 已装，增量同步方案 A（语义路径）可用`
- `MISSING` → 打印 `⚠️ git-ai 未装，增量同步将退化到方案 B（重扫源码兜底）。如要走方案 A，请先安装 git-ai 后重跑 init`

不强制安装 git-ai，只告知影响。

### 6.2：拷贝 sync 脚本到项目本地

把 skill 自带的 mjs 拷到目标项目 `.auto-test/scripts/`，让 hook 可以稳定调用：

```bash
mkdir -p .auto-test/scripts
cp ~/.claude/skills/auto-test/scripts/sync_common.mjs    .auto-test/scripts/
cp ~/.claude/skills/auto-test/scripts/sync_collect.mjs   .auto-test/scripts/
cp ~/.claude/skills/auto-test/scripts/sync_check.mjs     .auto-test/scripts/
cp ~/.claude/skills/auto-test/scripts/dirty_check.mjs    .auto-test/scripts/
chmod +x .auto-test/scripts/sync_collect.mjs .auto-test/scripts/sync_check.mjs .auto-test/scripts/dirty_check.mjs
```

`~` 必须展开为绝对路径。`.auto-test/scripts/` **进 git**，作为团队共享资产。每个脚本文件顶部有 `SCRIPT_VERSION` 常量（如 `const SCRIPT_VERSION = "0.2.1"`），入口自检（SKILL.md §2.1.1）会自动对比 skill 源目录和项目本地的版本号，过时则自动覆盖更新。团队版本由 commit 节点控制，避免 A 用 v1 / B 用 v2 的格式割裂。

### 6.3：装 post-commit hook

检查 `.git/hooks/post-commit` 是否存在：

- **不存在**：用 Write 创建：
  ```sh
  #!/bin/sh
  # auto-test sync collect (managed by auto-test skill)
  node .auto-test/scripts/sync_collect.mjs --root . || true
  ```
  然后 `chmod +x .git/hooks/post-commit`

- **已存在**：用 Read 检查文件内容是否含字符串 `sync_collect.mjs`：
  - 已含 → 跳过（幂等）
  - 未含 → 用 Edit 在文件末尾追加：
    ```sh

    # auto-test sync collect (managed by auto-test skill)
    node .auto-test/scripts/sync_collect.mjs --root . || true
    ```

> **`|| true` 不可省**：hook 失败不能阻塞 commit。

### 6.4：写 sync-state.json 初值

拿当前 HEAD 与 git user：

```bash
git rev-parse HEAD
git config user.name
```

用 Write 创建 `.auto-test/sync-state.json`：

```json
{
  "lastSyncedCommit": "<当前 HEAD>",
  "lastSyncAt": "<ISO 时间戳>",
  "lastSyncBy": "<git user.name>"
}
```

> 初值用当前 HEAD，意味着"init 之前的 commit 一律不补同步"，避免历史包袱。

### 6.5：自检

```bash
test -x .git/hooks/post-commit && echo HOOK_OK || echo HOOK_FAIL
test -x .auto-test/scripts/sync_collect.mjs && echo COLLECT_OK || echo COLLECT_FAIL
test -x .auto-test/scripts/sync_check.mjs   && echo CHECK_OK   || echo CHECK_FAIL
test -f .auto-test/sync-state.json && echo STATE_OK || echo STATE_FAIL
```

任一 FAIL → 停止并报告。

## 步骤 7：初始化校验

init 完成前必须校验：

- `.auto-test/config.json` 存在且字段合法。
- `componentRoot` 存在。
- `.auto-test/` 基础目录齐全。
- `docs.mode=external` 时，可以追溯到原需求文档。
- 登录配置完整，敏感信息不进 git。
- Playwright 配置已生成，或已提示用户手动合并。
- 步骤 6 的 hook、scripts、sync-state.json 全部就位（HOOK_OK / COLLECT_OK / CHECK_OK / STATE_OK）。

任一项不满足，停止并报告缺失项，不进入 doc/plan/nl 链路。

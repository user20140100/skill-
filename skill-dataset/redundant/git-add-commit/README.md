# git-add-commit — AI 驱动的 Git 提交助手

> 告别手写 commit message，让 AI 读懂你的代码改动，一键生成规范提交 + 安全推送。

---

## 它能做什么？

只需说一句「**帮我提交**」，AI 会自动完成：

1. **读取你的团队提交模板** — 自动识别 `git config commit.template`，适配任何团队规范，无需手动配置
2. **分析代码改动** — 扫描 `git diff`，理解本次修改的目的、范围、影响
3. **生成完整 commit message** — 按模板字段填写 why / how / influence / check / jira，标题不超限
4. **安全推送到临时分支** — 格式 `temp{日期}_类型_修改点`，不污染主干，随时可撤销

---

## 为什么用这个 Skill？

### 痛点一：手写 commit 又慢又不规范

```
# 以前
git commit -m "fix bug"   ← 被 review 打回

# 现在
说一句"帮我提交"，AI 输出：
[bugfix] 修复KTC信号强度指令返回HEX格式错误
[why] 返回值为ASCII字符30 31，而非HEX格式01
[how] 修改parseSignalStrength()格式化逻辑
[influence] KTC厂商信号强度查询功能
[check] ADB验证返回HEX格式01
[jira] SXRD-21528
```

### 痛点二：直接 push 到主干，风险高

本 Skill 强制推送到临时分支，格式如：

```
temp20260430_bugfix_ktcSignalFormat
temp20260430_feature_addBrightnessCtrl
```

主干永远干净，Code Review 通过后再合并，误操作风险为零。

### 痛点三：每个项目模板不同，难以统一

**模板完全自定义** — Skill 在运行时读取当前 repo 的 `commit.template`，支持：

- 任意字段名（`[why]` / `[reason]` / `[desc]` 都行）
- 任意文件路径（`~/.stCommitMsg` / `.gitmessage` / 项目内模板）
- 没有模板？自动降级为通用格式，同样规范

```bash
# 配置你的团队模板（一次配置，永久生效）
git config --global commit.template ~/.stCommitMsg

# Skill 自动识别，无需额外设置
```

---

## 快速上手

### 安装

```bash
cskills install git-add-commit
```

### 使用

在 Claude Code 中，直接说：

```
帮我提交
提交代码
commit 一下
```

AI 会询问 Jira 号（默认 N/A），然后全自动完成剩余步骤。

---

## 自定义你的提交模板

模板文件示例（`~/.stCommitMsg`）：

```
[修改类型]

[why]
[how]
[influence]
[check]
[jira]
```

修改类型约定：
| 类型 | 场景 |
|------|------|
| `bugfix` | 缺陷修复 |
| `feature` | 新功能开发 |
| `config` | 配置/编译变更 |

Skill 会读取你的模板，按字段结构生成对应内容，**不会遗漏任何字段**。

---

## 临时分支管理

推送后如需清理：

```bash
# 撤销本地 commit
git reset HEAD~1

# 删除远程临时分支
git push origin :temp20260430_bugfix_ktcSignalFormat
```

---

## 作者

shishaoxian@cvte.com


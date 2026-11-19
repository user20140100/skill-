# 代码审查清单（详细版）

> 本文件是 `code-review-and-teach` Skill 的参考文档，在执行流程 A 时按需加载。

---

## 一、机密泄露扫描

### 1.1 扫描正则模式库

执行扫描时，对每个文件依次使用以下正则：

#### Token / 认证信息

| # | 模式 | 正则 | 替换为 |
|---|------|------|--------|
| 1 | JWT Token（三段式） | `eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}` | `your_jwt_token_here` |
| 2 | Bearer Token | `Bearer\s+[A-Za-z0-9+/=_-]{20,}` | `Bearer your_token_here` |
| 3 | 通用 Token 赋值 | `(TOKEN|token|api_token)\s*[:=]\s*['"][A-Za-z0-9_\-!@#$%^&*.]{16,}['"]` | `TOKEN = "your_token_here"` |
| 4 | x-auth-token 头 | `x-auth-token.*:\s*['"][A-Za-z0-9_\-!@#$%^&*.]{16,}['"]` | `x-auth-token: "your_token_here"` |

#### Webhook

| # | 模式 | 正则 | 替换为 |
|---|------|------|--------|
| 5 | 企业微信 Webhook | `https?://qyapi\.weixin\.qq\.com/cgi-bin/webhook/send\?key=[A-Za-z0-9-]+` | `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_webhook_key` |
| 6 | 飞书 Bot Webhook | `https?://open\.feishu\.cn/open-apis/bot/v2/hook/[A-Za-z0-9-]+` | `https://open.feishu.cn/open-apis/bot/v2/hook/your_hook_id` |
| 7 | 钉钉 Webhook | `https?://oapi\.dingtalk\.com/robot/send\?access_token=[A-Za-z0-9]+` | `https://oapi.dingtalk.com/robot/send?access_token=your_token` |

#### 密钥 / 密码

| # | 模式 | 正则 | 替换为 |
|---|------|------|--------|
| 8 | App Secret | `(app_secret|AppSecret|appSecret)\s*[:=]\s*['"][A-Za-z0-9_-]{8,}['"]` | `app_secret = "your_secret_here"` |
| 9 | API Key | `(api_key|ApiKey|apiKey)\s*[:=]\s*['"][A-Za-z0-9_-]{8,}['"]` | `api_key = "your_api_key_here"` |
| 10 | Password 明文 | `(password|passwd|PASSWORD)\s*[:=]\s*['"][^\s'"]{4,}['"]` | `password = "your_password_here"` |
| 11 | 加密密钥 | `(AES_KEY|SECRET_KEY|ENCRYPTION_KEY|PRIVATE_KEY)\s*[:=]\s*['"][A-Za-z0-9_/+-]{16,}['"]` | `SECRET_KEY = "your_secret_here"` |

#### 数据库

| # | 模式 | 正则 | 替换为 |
|---|------|------|--------|
| 12 | 数据库连接串 | `(mysql|postgres|mongodb|redis|sqlite)://[^:]+:[^@]+@[^/\s"']+` | `数据库连接串，需替换` |

#### 网络信息

| # | 模式 | 正则 | 替换为 |
|---|------|------|--------|
| 13 | 内网 IPv4 | `\b(10\.\d{1,3}|172\.(1[6-9]\|2\d\|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b` | 记录位置（仅警告） |
| 14 | 硬编码用户路径 | `/Users/[^/\s"']{2,}/[^\s"']*` | 提示改为动态路径 |

### 1.2 白名单规则

以下情况**不视为机密泄露**：

| 模式 | 原因 |
|------|------|
| `your_token_here` / `your_xxx_here` | 已是占位符 |
| `placeholder` / `changeme` / `replace_me` | 已是占位符 |
| `xxxx` / `****` / `...`  | 明显的脱敏写法 |
| `example\.com` / `test\.com` / `localhost` | 示例域名 |
| `127.0.0.1` / `0.0.0.0` | 本地回环地址 |
| `your_` 开头的值 | 明显的占位符前缀 |

### 1.3 扫描执行流程

```
1. find 目标目录下所有文本文件
   → find {dir} -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.vue" -o -name "*.md" -o -name "*.sh" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.txt" -o -name "*.env" -o -name "*.cfg" -o -name "*.ini" -o -name "*.toml" \)

2. 排除不需要扫描的目录
   → -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -not -path "*/dist/*" -not -path "*/.skill/*"

3. 对每个文件执行 grep，使用上述正则

4. 对每个命中，检查是否在白名单中

5. 分类展示：阻断项（1-12）vs 警告项（13-14）
```

---

## 二、新人友好度评分细则

### 2.1 评分项详细标准

#### ✅ 有一键部署脚本（+2 分）

检查是否存在以下文件之一：
- `setup.sh`（可执行）
- `Makefile`（含 install 目标）
- `docker-compose.yml` / `Dockerfile`
- `install.sh` / `bootstrap.sh`

评分标准：
- 存在且可执行 → +2
- 存在但不可执行（缺少 chmod +x）→ +1
- 不存在 → 0

#### ✅ 配置项集中在 ≤2 个文件中（+2 分）

检查配置文件数量：
- 搜索 `config*.py`, `config*.js`, `config*.json`, `config*.yaml`, `.env`, `settings.*`
- 数量 ≤ 2 → +2
- 数量 3-4 → +1
- 数量 > 4 → 0

#### ✅ 配置步骤 ≤ 3 步（+2 分）

检查配置流程复杂度：
- 阅读 SKILL.md / README.md 中的配置说明
- 统计用户需要手动执行的操作步骤数（不包括运行 setup.sh 这一步）
- ≤ 3 步 → +2
- 4-5 步 → +1
- > 5 步 → 0

#### ✅ 有 README 或 SKILL.md（+1 分）

- 存在 README.md 或 SKILL.md → +1
- 不存在 → 0

#### ✅ 依赖声明（+1 分）

检查是否存在以下文件之一：
- `requirements.txt`（Python）
- `package.json`（Node.js）
- `pyproject.toml`（Python）
- `go.mod`（Go）

- 存在且包含实际依赖 → +1
- 不存在 → 0

#### ✅ 无硬编码绝对路径（+1 分）

- 搜索结果中无 `/Users/` 开头或 `C:\Users\` 开头的路径 → +1
- 存在 1-3 处 → 0
- 存在 > 3 处 → -2（进入扣分项）

#### ✅ 关键配置项有注释说明（+1 分）

检查 config 文件中：
- 每个必填配置项旁边是否有 `#` 注释说明其含义
- 覆盖率 ≥ 80% → +1
- 覆盖率 50-79% → 0
- 覆盖率 < 50% → 0

#### ❌ 需要手动创建 > 3 个配置文件（-1 分）

检查是否需要用户手动创建文件：
- 搜索 `cp *.example` / `mv *.template` / "重命名为" / "复制一份"
- 需要创建 > 3 个 → -1

#### ❌ 需要手动修改 > 5 个文件才能运行（-2 分）

- 计数需要用户手动编辑的文件数（不包括自动生成的文件）
- > 5 个 → -2

### 2.2 最终评分与建议

| 分数 | 等级 | 建议 |
|------|------|------|
| 8-10 | 🟢 优秀 | 新人可独立完成配置，无需额外帮助 |
| 5-7 | 🟡 一般 | 新人可能需要 1-2 次询问，建议补齐缺失项 |
| 0-4 | 🔴 差 | 新人大概率配置失败，建议全面优化后再发布 |

---

## 三、代码注释检查标准

### 3.1 Python 文件

#### 文件级 docstring（必须）

```python
"""
模块功能简述

功能：这个模块是做什么的，解决什么问题
输入：依赖哪些外部文件 / API
输出：产出什么结果
用法：如何调用（命令行示例或 import 示例）
"""
```

检查方式：
- 读取文件前 20 行
- 检查是否有 `"""..."""` 或 `'''...'''` 多行字符串
- 检查是否包含"功能"或"用途"相关关键词

#### 函数 docstring（公开函数必须）

检查方式：
- 提取所有 `def xxx(` 定义的函数
- 排除 `_` 开头的私有函数
- 检查函数定义下一行是否有 docstring
- 检查 docstring 是否包含参数说明

#### 复杂逻辑注释（建议）

检查方式：
- 统计连续无空行代码块的行数
- > 10 行连续代码 → 标记为"复杂逻辑"，建议添加行内注释

#### 魔法数字注释（建议）

检查方式：
- 搜索代码中的数字字面量（非 0/1/-1/2/100/1000 等常见值）
- 检查该行是否有注释说明数字含义

### 3.2 前端文件（.vue / .jsx / .tsx）

#### 组件说明（必须）

每个 `.vue` 文件的 `<script>` 顶部应有组件用途注释：
```javascript
/**
 * 交货计划导入页面
 * 功能：选择 Excel 文件 → 预览数据 → 提交导入
 * 依赖：importApi.ts, useUserStore
 */
```

#### 关键函数注释（建议）

复杂函数（> 20 行）应有 JSDoc 注释。

### 3.3 Shell 脚本

#### 脚本头部注释（必须）

```bash
#!/bin/bash
# ============================================================
# 脚本名称：setup.sh
# 功能：一键部署 auto-import skill 到项目目录
# 用法：bash setup.sh
# ============================================================
```

---

## 四、发布前清理清单

### 4.1 自动清理（无需确认）

| 类型 | 匹配模式 | 操作 |
|------|---------|------|
| Python 缓存 | `__pycache__/`, `*.pyc`, `*.pyo` | 删除 |
| macOS 系统文件 | `.DS_Store` | 删除 |
| Vim 临时文件 | `*.swp`, `*.swo`, `*~` | 删除 |
| 空文件 | 0 字节文件 | 列出后询问 |

### 4.2 需确认后清理

| 类型 | 匹配模式 | 操作 |
|------|---------|------|
| 临时测试脚本 | `test_*.py`, `temp_*.py`, `debug_*.py` | 询问后删除 |
| 旧版本文件 | `*.skill`（旧版本） | 询问后删除 |
| 日志文件 | `*.log` | 询问后删除 |
| IDE 配置 | `.vscode/`, `.idea/` | 询问是否保留 |
| node_modules | `node_modules/` | 询问是否删除（发布 Skill 时应删） |

---

## 五、审查结果输出

每次审查完成后，将结果保存到 `cache/code-review-report.md`，格式见 SKILL.md 模板。
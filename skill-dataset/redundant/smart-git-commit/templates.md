# Commit 模板库

切换方式：对话中说「用 XXX 模板」，或直接编辑本文件新增/修改模板。

---

## jira-bug（默认）

```
[JIRA BUG Num.]<BIOS版本标识> JIRA BUG描述
[Label]       :
[File]        :
```

字段规则：

- `[JIRA BUG Num.]`：JIRA / issue 编号。优先从分支名提取；提取不到则留空并**询问用户**，禁止编造。
  - **避坑**：`CCB-H340-MA01` 这类板型号会被 issue 号正则误抓；已判定为板型/客户/版本的段一律排除。
- `<BIOS版本标识>`：**从当前分支名派生**，格式 `{客户}{板型}主板Bios定制{版本}`。解析规则见下节。
  - 与 `JIRA BUG描述` 之间用**单个空格**分隔。
  - 跳过时该位置直接省略，**不留前导空格**。
- `JIRA BUG描述`：一句话说明改动**目的**（Why 优先，其次 What），中文，句末不加句号。
- `[Label]`：改动性质标签，逗号分隔。可选值：fix / feature / refactor / build / docs / test / migrate / chore。
- `[File]`：变更文件清单，逗号分隔。路径**相对到顶层 Pkg** —— 从文件向上层文件夹遍历，取第一个以 `Pkg` 结尾的文件夹作为起点：
  - 例：`.../PanYuhangPkg/DxeModule/Xxx/Xxx.c` → `PanYuhangPkg/DxeModule/Xxx/Xxx.c`
  - 文件不在任何 `Pkg` 目录下 → 退回 git 仓库相对路径
  - **≤8 个文件**逐个列出；**>8 个文件**改为概括目录 + 关键文件名

### BIOS 版本标识解析规则

判据表（客户白名单 / 关键词 / 正则）在 `customers.md`，解析前先读它。

**规范化**：去 `origin/` → 去 `Branch_` → 按 `/` 切段。

**抽要素**：

| 要素 | 规则 | 示例 |
|---|---|---|
| 版本 ver | 从末段往前找第一个匹配版本正则的段（`^[VT]\d+(\.\d+)*[a-zA-Z]*(-[A-Za-z0-9_.]+)?$`，忽略大小写），原样保留；**该段之后的段全部裁掉** | `V0.04` `T0.00-XMC` `V0.09a` |
| 板型 board | 主干**第一段原样保留，整段不剥离前缀**；不含数字则判定失败 | `CCB-H340-MA01` |
| 客户 customer | 在「基线段之后、版本段之前」的余段里：a) `Customer`/`Oem`/`定制` 段 → 取紧随其后一段（高）；b) 命中白名单（高）；c) 未入白名单的全大写短码（**低→问**）；d) 只剩阶段/类型/占位符/人名 → 无客户线（**→问**） | `诚迈` `Haier` `Lecoo` |
| 定制词 | 客户段存在 → 固定串 `主板Bios定制`；无客户线不许写"定制" | `主板Bios定制` |

**拼装式**：`{customer}{board}主板Bios定制{ver}`

实测对照：

| 分支 | 标识串 | 信度 |
|---|---|---|
| `CCB-H340-MA01/CRB_R02.03-Pre/Customer/诚迈/V0.04` | `诚迈CCB-H340-MA01主板Bios定制V0.04` | 高 |
| `CCB-H340-MA01/CRB_R02.02/Haier/Release/V0.03` | `HaierCCB-H340-MA01主板Bios定制V0.03` | 高 |
| `MB.IWCL.ID02/CRB_05.72.17.0009/Release/Lecoo/V0.09` | `LecooMB.IWCL.ID02主板Bios定制V0.09` | 高 |
| `CCB-H340-MA01/CRB_R01.00/GX/ES/Debug/T0.01` | `GXCCB-H340-MA01主板Bios定制T0.01` | 高 |
| `CCB-H340-MA01/CRB_R02.03-Pre/Release/V0.21` | —— | 低 → 问 |
| `MB.IWCL.ID02/.../Release/MAINBOARD/V0.09a` | —— | 低 → 问 |
| `MB.IWCL.ID02/CRB_05.72.17.0009/migrate/v0.08/PYH/migrate-test` | —— | 低 → 问 |
| `MB.IWCL.ID01/CRB_05.72.21.0010` | —— | 低（版本缺失）→ 问 |
| `CRB：05.71.44.0003` / `main` | —— | 低（板型缺失）→ 问 |

**低信度时的提问规范**：用提问工具，附段分解，选项给 ① 采用建议值 ② 用户手写完整标识串 ③ 本次不带标识串。

### 渲染示例

```
[PROJ-1234]诚迈CCB-H340-MA01主板Bios定制V0.04 修复 Setup 中 SMBIOS Type 140 显示异常
[Label]       : fix, setup
[File]        : PanYuhangPkg/DxeModule/PyhSmbiosType140Setup/PyhSmbiosType140Setup.c, PanYuhangPkg/DxeModule/PyhSmbiosType140Setup/PyhSmbiosType140Setup.inf
```

标识串被跳过时的降级形态：

```
[PROJ-1234]修复 Setup 中 SMBIOS Type 140 显示异常
[Label]       : fix, setup
[File]        : PanYuhangPkg/DxeModule/PyhSmbiosType140Setup/PyhSmbiosType140Setup.c
```

---

## conventional

```
<type>(<scope>): <subject>

<body>

<footer>
```

- `type`：feat / fix / docs / style / refactor / perf / test / build / ci / chore
- `subject`：祈使句，≤72 字符，句末不加句号
- `body`：说明 Why；`footer`：放 BREAKING CHANGE / issue 引用
- **不加 BIOS 版本标识前缀**（该前缀仅 jira-bug 模板使用）

---

## simple

```
<一句话概括改动>
```

适用于临时提交、练手分支。**不加 BIOS 版本标识前缀**。

---

## 自定义模板

在本文件追加一节，写明三件事即可：

1. 模板骨架（代码块）
2. 字段规则（每个字段从哪取值、取不到怎么办）
3. 渲染示例

之后在对话中用「用 <模板名> 模板」切换。

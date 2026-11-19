# 版本定位

> Step 2 的参考。dump / 快照对应历史版本二进制，必须先定位代码版本并 checkout，让符号 / 源码对齐。
> 对崩溃 dump 和挂起快照同样适用——活进程附加时也要符号对齐才能看懂栈。

## 为什么必须版本定位

崩溃栈帧行号（如 `my_module.cpp:128`）是对**特定版本**二进制编译出来的。如果用当前代码看历史 dump 的行号：

- 代码已改动，行号对不上 → 看错代码
- PDB 不是同一版本 → 符号解析错位或失败

**跳过版本定位 = 看错代码**。这是 Hard Rule 2。

## 流程

### 1. 从 dump / 快照拿崩溃模块版本

用 `!lmi` 查崩溃模块的版本信息：

```
!lmi <module>.exe
```

或列所有模块找版本：

```
lm m <module>*
!lmi <module>.exe
```

`!lmi` 输出关键字段：
- `FileVersion` — 文件版本（如 `1.2.10.0`）
- `ProductVersion` — 产品版本
- `Pdb` / `GUID` / `Age` — PDB 标识（用于符号匹配）

CLI 一次性拿：

```bash
cdb -z C:/dumps/app.dmp -c "!lmi <your-app>.exe; q" -y "srv*..."
```

挂起快照同理（活进程附加或 dump 都有模块信息）。

### 2. 用版本号查 git tag / commit

先确认目标项目的"版本号约定"——版本号常见来源：

- 版本定义文件：CMakeLists `project(... VERSION X.Y.Z)`、`VERSION` 文件、`package.json` 等
- commit message 规律：如 `chore: release X.Y.Z`、`chore: update <module> to X.Y.Z`
- git tag：`git tag` 看是否按版本号打 tag（如 `v1.2.10`、`1.2.10`）

查 tag：

```bash
git -C <repo> tag --list '*<version>*'
```

查 commit：

```bash
git -C <repo> log --oneline --grep='<version>'
```

### 3. checkout 到该版本（用 worktree，不污染当前分支）

用 `git worktree` 建独立工作区 checkout 历史版本（不污染主分支）：

```bash
git -C <repo> worktree add ../<repo>-<version> <tag>
# 或用 commit:
git -C <repo> worktree add ../<repo>-<sha> <sha>
```

在 worktree 里分析该版本源码。**不要在主工作区 checkout 历史版本**，会干扰当前开发。

### 4. 匹配不到 → 让用户确认

如果版本号匹配不到任何 tag / commit：

- 可能版本号是内部构建号，未打 tag
- 可能 dump 来自未提交的本地构建
- 可能子模块版本文件与 tag 规律不同

**不要擅自假设**。把 `!lmi` 输出的 FileVersion / ProductVersion / PDB GUID 展示给用户，问：
- 这个 dump / 快照对应哪个 commit / tag？
- 或者构建来源是什么（CI / 本地 / 某次发布）？

用户确认后再 checkout。

## 符号对齐

版本定位的目的是让 PDB 和源码对齐。三种情况：

### 情况 A：有该版本归档 PDB

把 PDB 目录加入 `_NT_SYMBOL_PATH`：

```
srv*C:\Symbols*https://msdl.microsoft.com/download/symbols;<archive_pdb_dir>
```

### 情况 B：无归档 PDB，能 checkout 该版本

checkout 后重新构建生成 PDB：

```bash
cd ../<repo>-<version>
<build-command>    # 用项目自身构建命令生成该版本 PDB（如 cmake --build、npm run build、conan build）
```

把构建产物目录加入 `_NT_SYMBOL_PATH`。

### 情况 C：第三方依赖包（Conan / vcpkg 等）

依赖库的 PDB 通常不在主项目仓库，来源：
- 包管理器缓存：如 Conan `~/.conan2/data/<pkg>/...`、vcpkg `buildtrees/<pkg>/`
- 本地 editable：`conan editable add .` 的目录

版本对齐：checkout 主项目该版本后，看其依赖清单（如 `conanfile.txt` / `vcpkg.json`）要求的依赖版本，找对应 PDB。

## 验证版本已对齐

跑 `k` 看栈帧：
- 帧带 `源文件:行号`（如 `my_module.cpp:128`）→ 符号已对齐 ✅
- 只有地址 / `??` → 符号缺失，检查 PDB 路径和版本

```text
0:000> k
 # Child-SP          RetAddr           Call Site
00 00000000`12345678 00007ff6`abc12345 MyApp::WorkerThread::<lambda>::operator() (my_module.cpp:128)
```

行号能对上 worktree 里 checkout 的源码 = 版本定位成功。

## 反模式

- **用当前代码看历史 dump** — 行号对不上，看错代码
- **在主工作区 checkout 历史版本** — 污染当前开发，应该用 worktree
- **版本匹配不到就猜** — 必须让用户确认
- **跳过符号对齐直接看栈** — 只有地址的栈没有定位价值
- **挂起分析就不做版本定位** — 活进程快照同样需要符号对齐

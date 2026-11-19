# 开发环境检查、安装与本地验证（Windows / macOS）

> 配套 fullstack-feature-delivery 阶段 6（验收闭环）的前置能力：**验证不降级优先**——环境缺失先就地搭环境（涉及系统级安装须先获用户授权），确实无法搭建才回退静态核查。
> 本文件来自 dws-server（JDK8 + Maven 3.9.9 多模块工程）实测沉淀，含本次踩坑的完整根因链。

## 1. 环境探测（先判有无，再判版本匹配）

声称"环境缺失"前必须探测过，避免误判后白白降级静态核查：

```powershell
# Windows（PowerShell / CMD 通用探测）
where.exe java ; where.exe mvn
java -version ; mvn -v
# 常见安装位置兜底检查
Test-Path 'C:\Program Files\Java','C:\Program Files\Eclipse Adoptium',"$env:USERPROFILE\.jdks","$env:USERPROFILE\tools"
```

```bash
# macOS
which java mvn ; java -version ; mvn -v
/usr/libexec/java_home -V          # 列出已装全部 JDK
ls /Library/Java/JavaVirtualMachines ~/Library/Java/JavaVirtualMachines 2>/dev/null
```

**版本匹配以工程为准**：读根 pom 的 `maven.compiler.source/target`（如 `1.8` → 装 JDK 8），不要装最新版导致字节码级别不匹配。

## 2. Windows 安装（JDK8 + Maven 实测路径）

### JDK：winget 机器级安装

```powershell
winget install EclipseAdoptium.Temurin.8.JDK --scope machine `
  --accept-source-agreements --accept-package-agreements --disable-interactivity
```

坑（实测）：

- `--scope user` 会报"找不到适用的安装程序"——Temurin 的 MSI 只支持机器级，必须 `--scope machine`
- winget 默认源是 msstore 时可能卡协议交互，统一带 `--disable-interactivity` 等免交互参数
- 备选：从 https://adoptium.net 手动下载 MSI

### Maven：winget 无包，手动安装（免安装 zip）

```powershell
$dir = "$env:USERPROFILE\tools"
Invoke-WebRequest "https://archive.apache.org/dist/maven/maven-3/3.9.9/binaries/apache-maven-3.9.9-bin.zip" -OutFile "$dir\maven.zip"
Invoke-WebRequest "https://archive.apache.org/dist/maven/maven-3/3.9.9/binaries/apache-maven-3.9.9-bin.zip.sha512" -OutFile "$dir\maven.zip.sha512"
# SHA512 校验（防下载损坏，大文件哈希比对用布尔判断更可靠）
$expected = (Get-Content "$dir\maven.zip.sha512").Split(' ')[0].Trim().ToLower()
$actual = (Get-FileHash "$dir\maven.zip" -Algorithm SHA512).Hash.ToLower()
if ($expected -ne $actual) { throw "校验失败，重新下载" }
Expand-Archive "$dir\maven.zip" -DestinationPath $dir
Remove-Item "$dir\maven.zip","$dir\maven.zip.sha512"
```

### 环境变量（用户级即可）

```powershell
[Environment]::SetEnvironmentVariable('JAVA_HOME','C:\Program Files\Eclipse Adoptium\jdk-8.0.504.1-hotspot','User')
[Environment]::SetEnvironmentVariable('MAVEN_HOME',"$env:USERPROFILE\tools\apache-maven-3.9.9",'User')
$p = [Environment]::GetEnvironmentVariable('Path','User')
[Environment]::SetEnvironmentVariable('Path',"$p;$env:JAVA_HOME\bin;$env:MAVEN_HOME\bin",'User')
```

**坑：旧终端不继承新环境变量**。安装前打开的 CMD/PowerShell 报 `'java' 不是内部或外部命令` 属正常现象——环境变量只在进程启动时读取。解法：重开终端；或临时 `set "PATH=%PATH%;<jdk>\bin;<maven>\bin"`。从 IDE/常驻程序派生的终端要重启父进程。

## 3. macOS 安装（JDK8 + Maven）

```bash
# 方式一：Homebrew（推荐，Apple Silicon 需 JDK8 8u345+，brew 会装最新补丁版）
brew install --cask temurin@8
brew install maven

# JAVA_HOME 写入 ~/.zshrc
echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 1.8)' >> ~/.zshrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.zshrc
source ~/.zshrc

# 方式二：SDKMAN（多 JDK 并存、切版本方便）
curl -s "https://get.sdkman.io" | bash
sdk install java 8.0.412-tem     # 自动管理 JAVA_HOME
sdk install maven
```

注意：`brew install openjdk@8` 是 keg-only，需要手动 link 或配 PATH，优先用 cask 版省事。

两平台装完统一验证：`java -version` 输出目标大版本、`mvn -v` 显示正确 Java home、`echo $JAVA_HOME` / `echo %JAVA_HOME%` 非空。

## 4. 本地编译验证（Maven 多模块）

```powershell
# Windows / macOS 通用（PowerShell 中带点号的 -D 参数必须整体加引号）
mvn -pl application/dws-asset-parent/dws-asset -am clean compile -DskipTests
```

规则：

- **`-am` 必带**：本地仓库未 install 兄弟模块 SNAPSHOT 时，不带会依赖解析失败
- 每次终端会话先设 `JAVA_HOME`/`MAVEN_HOME`/`Path`（agent 的每次命令调用都是新进程）——复杂命令写成 `.ps1` 脚本文件执行，避免引号嵌套被外层 shell 吃掉
- 首次构建需能访问工程私服（公司 artifactory/nexus）；受限沙箱中 Maven 写 `~/.m2` 在工作区外，需用户授权

## 5. 单测执行与"假绿"识别（重点）

```powershell
mvn -pl application/dws-asset-parent/dws-asset -am test `
  "-Dtest=AssetAppServiceImplTest" "-Dsurefire.failIfNoSpecifiedTests=false"
```

全量 `test` 易被工程既有无关用例（如历史 NPE）挡住，用 `-Dtest` 过滤目标类。

**判读三要素**（缺一不可，只看 BUILD SUCCESS 会上当）：

1. `Using auto detected provider ...` 行——确认测试引擎（JUnit4Provider / JUnitPlatformProvider）
2. `Tests run: N` 的 **N 必须 > 0 且等于预期用例数**
3. `Failures: 0, Errors: 0`

### 假绿典型案例（实测根因链）

现象：`Tests run: 0, Failures: 0` + BUILD SUCCESS，单测等于没跑。

根因链（三层，逐层剥开）：

1. 工程父 BOM 把 `junit:junit` 管控为 4.13.2，而 `spring-boot-starter-test`（Boot 2.2.6）自带 `junit-vintage-engine:5.5.2`，其 `JUnit4VersionCheck` 无法解析 junit 4.13+ 版本号 → vintage 引擎在**测试发现阶段**崩溃，JUnit4 用例全部静默丢失
2. 排除 vintage 后，`mockito-junit-jupiter` 残留的 `junit-platform-commons` 仍让 surefire 选择 JUnitPlatformProvider，并**自动下载注入**一份 vintage，同样崩溃
3. 信号词：日志出现 `TestEngine with ID 'junit-vintage' failed to discover tests`

修复模板（模块 pom 内，不动全局 BOM）：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
    <exclusions>
        <exclusion><groupId>org.junit.jupiter</groupId><artifactId>junit-jupiter</artifactId></exclusion>
        <exclusion><groupId>org.junit.vintage</groupId><artifactId>junit-vintage-engine</artifactId></exclusion>
        <exclusion><groupId>org.mockito</groupId><artifactId>mockito-junit-jupiter</artifactId></exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>junit</groupId><artifactId>junit</artifactId><scope>test</scope>
</dependency>
```

排查工具：`mvn dependency:tree "-Dincludes=junit:junit,org.junit.platform:*,org.junit.jupiter:*,org.junit.vintage:*"` 看 JUnit 体系实际来源。

**曾经静态交付的用例，环境就绪后必须回补执行**——本案例回补时 13 用例跑出 12 通过 1 失败，逮到监听器收集门槛的真 bug（必填缺失行漏拦截）。静态核查再细致也覆盖不了全部语义缝隙。

## 6. 快速排查清单

| 现象                                             | 根因                              | 动作                     |
| ------------------------------------------------ | --------------------------------- | ------------------------ |
| `'java' 不是内部或外部命令`                      | 终端早于安装打开，环境变量不继承  | 重开终端 / 临时 set PATH |
| 新终端仍找不到                                   | 用户 Path 未含 JDK/Maven bin      | 查注册表级环境变量补写   |
| 模块依赖解析失败                                 | 编译命令漏 `-am`                  | 补 `-am`                 |
| `-Dxxx` 被当未知 lifecycle phase                 | PowerShell 参数解析               | 带点号参数整体加引号     |
| `Tests run: 0` 且 BUILD SUCCESS                  | vintage 引擎发现阶段崩溃（见 §5） | 三排除 + 显式 junit4     |
| 日志有 `TestEngine ... failed to discover tests` | 同上                              | 同上                     |
| 全量 test 被无关用例挡住                         | 工程既有失败用例                  | `-Dtest=XxxTest` 过滤    |

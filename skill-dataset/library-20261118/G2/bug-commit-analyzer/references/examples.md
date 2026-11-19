# 使用示例

## 场景1：定位问题引入点

### 示例 1.1 — 根据错误日志定位回归

**用户输入**：
```
/bug-commit-analyzer RK3576 平台，录音有杂音，log 显示
[ERR] audio_dsp: buffer underrun detected, channel 2
之前 v2.0 的 tag 是正常的，现在 dev 分支有问题
```

**Skill 执行过程**：

1. **信息收集**：
   - 关键字：`audio_dsp`、`buffer underrun`、`channel`、`录音`、`杂音`
   - 文件名：搜索 `audio_dsp` 相关源文件
   - `git fetch --all --prune` 同步远程
   - 获取根提交并保存为 `$ROOTS`

2. **历史搜索**（并行）：
   - `git log --all --oneline --grep="buffer underrun" | grep -vE "$ROOTS"`
   - `git log --all --oneline --grep="audio_dsp" | grep -vE "$ROOTS"`
   - `git log --all --oneline -S "buffer underrun" | grep -vE "$ROOTS"`
   - `git log --all --oneline --grep="录音" | grep -vE "$ROOTS"`

3. **分析结果**：发现 commit `a1b2c3d` "audio_dsp: refactor dma buffer management" 修改了 buffer 大小

4. **git blame 确认**：`git blame -L <line>,<line> <file>` 确认该行由 `a1b2c3d` 修改

5. **git bisect 精确定位**（区间较大时）：
   ```
   git bisect start
   git bisect bad HEAD
   git bisect good v2.0
   → 二分定位到 a1b2c3d 是第一笔 bad commit
   ```

6. **查看 diff**：`git show a1b2c3d` 确认 buffer size 从 4096 改为 2048

**输出结论**：
```
根因定位：
- 提交 a1b2c3d (作者: zhangsan, 日期: 2026-05-20)
  "audio_dsp: refactor dma buffer management"
  将 DMA buffer 从 4096 改为 2048，导致双通道录音时 buffer underrun

修复建议：
- 文件: drivers/audio/rk3576/dsp_buffer.c:128
- 将 BUFFER_SIZE 从 2048 改回 4096，或改为 8192 留足余量

风险评估：
- 影响所有 RK3576 平台的录音功能
- 单通道录音可能不受影响（buffer 足够）

关联文件：
- drivers/audio/rk3576/dsp_buffer.h（宏定义位置）
```

---

### 示例 1.2 — 配置宏异常导致的功能失效

**用户输入**：
```
/bug-commit-analyzer customer_haier 的机器 HDMI 无声音输出，
但 customer_midea 是正常的。帮定位哪笔提交改了 HDMI 配置
```

**Skill 执行过程**：

1. 关键字提取：`HDMI`、`customer_haier`、`customer_midea`
2. 搜索含 `HDMI` 和 `haier` 的提交
3. 并行搜索 `customer_midea` 分支的 HDMI 配置作为参考
4. `git log --all -S "HDMI_OUTPUT_ENABLE" | grep -vE "$ROOTS"` 追踪宏变更
5. 跨客户对比：发现 haier 的配置宏值为 0，midea 为 1

**输出结论**：
```
根因定位：
- 提交 b2c3d4e (作者: lisi, 日期: 2026-06-01)
  "[config][customer_haier] disable HDMI output by default"
  将 HDMI_OUTPUT_ENABLE 从 1 改为 0

修复建议：
- 文件: config/customer/haier/board_rk3576.h:56
- 将 #define HDMI_OUTPUT_ENABLE 0 改回 1

参考：customer_midea 同文件第 56 行为 #define HDMI_OUTPUT_ENABLE 1
```

---

## 场景2：搜索参考实现

### 示例 2.1 — 搜索功能实现参考

**用户输入**：
```
/bug-commit-analyzer AD82120B 功放芯片需要加 DRC 配置，
搜索有没有其他项目已经做过类似的，参考一下
```

**Skill 执行过程**：

1. 关键字提取：`AD82120B`、`DRC`
2. 并行搜索（本地）：
   - `git log --all --oneline --grep="AD82120B" | grep -vE "$ROOTS"`
   - `git log --all --oneline --grep="DRC" | grep -vE "$ROOTS"`
   - `git log --all --oneline -S "drc_config" | grep -vE "$ROOTS"`
3. 本地没找到 AD82120B 相关结果 → 触发 GitLab API 搜索
4. 远程搜索同 group 下其他项目，查找含 DRC 配置的分支
5. 在 `audio-amplifier` 项目中找到 `customer_tcl` 分支有 AD82120B + DRC 的提交

**输出结论**：
```
历史参考：
- 提交 c3d4e5f (项目: audio-amplifier, 分支: customer_tcl, 作者: wangwu, 日期: 2026-04-15)
  "[feature] AD82120B: add DRC configuration for TCL project"

  变更摘要（diff）：
  + #define AD82120B_DRC_ENABLE      1
  + #define AD82120B_DRC_THRESHOLD  -20  // dB
  + #define AD82120B_DRC_RATIO      4   // :1
  + static const struct drc_config ad82120b_drc = {
  +     .threshold = -20,
  +     .ratio = 4,
  +     .attack_time = 10,
  +     .release_time = 100,
  + };

实现建议：
- 参考文件结构：config/chip/ad82120b.h（宏定义）+ drivers/audio/ad82120b.c（drc_config 结构体）
- 关注 attack_time 和 release_time 参数需要根据实际听感调整
```

---

### 示例 2.2 — 跨客户配置参考

**用户输入**：
```
/bug-commit-analyzer 搜一下所有客户对 AUDIO_SAMPLE_RATE 这个宏的设置，
我们 customer_xiaomi 现在配的 48000 好像有问题
```

**Skill 执行过程**：

1. 关键字：`AUDIO_SAMPLE_RATE`
2. 并行搜索：
   - `git log --all -S "AUDIO_SAMPLE_RATE" --oneline | grep -vE "$ROOTS"` — 找所有修改过该宏的提交
   - `git log --all --oneline --grep="AUDIO_SAMPLE_RATE" | grep -vE "$ROOTS"` — 找 commit message 中提到该宏的提交
3. 对搜索结果中的每个客户分支，用 `git show` 查看当前宏值
4. 构建覆盖链：全局默认 → 产品线 → 客户 → 机型

**输出结论**：
```
配置覆盖链及跨客户对比：

全局默认（config/default.h）:         AUDIO_SAMPLE_RATE 48000
├── customer_xiaomi（当前问题分支）:   AUDIO_SAMPLE_RATE 48000 ← 与默认相同
├── customer_huawei:                  AUDIO_SAMPLE_RATE 44100
├── customer_midea:                   AUDIO_SAMPLE_RATE 48000
├── customer_haier:                   AUDIO_SAMPLE_RATE 96000
└── customer_tcl (机型 TK-200):       AUDIO_SAMPLE_RATE 48000

分析：
- xiaomi 当前值 48000 与大多数客户一致，不是异常偏离
- 如确认 48000 有问题，可能是驱动层采样率转换逻辑有 bug，而非宏配置问题
- 可参考 customer_haier 的 96000 配置作为验证对照

关联文件：
- config/default.h:32
- config/customer/xiaomi/audio_config.h:18
- drivers/audio/sample_rate_conv.c（采样率转换实现）
```
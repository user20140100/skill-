<!--
Split from: ./source-of-truth/C&Cpp编程规范-初稿v0.3.md
This file is intended for on-demand loading during style reviews.
Do not use the archived source-of-truth as runtime input.
-->

> Note: Chapter "三. 安全规约" sections "3-3 进程与线程" + "3-3 其他".

### 3-3 进程与线程
### 3-3-1 变量的线程（进程）安全

3-3-3-1、\[SC] 多进程/线程可以访问的资源（变量、缓存区、共享内存等），除非是常量，否则必须做互斥保护，请不要出现临界资源不作保护的随意读写行为。
说明：临界资源，同一时刻只能由一个线程进行读写操作，如果临界资源不做互斥性保护，当多个进程/线程同时操作时，就会产生数据不一致、结果不可预测、错误难排除等未定义的行为，严重可导致程序崩溃。

## 3-3 其他

### 3-3-1 随机数的使用/异步安全函数

【设计类问题】

3-3-1-1、\[SC] 在设计加密验证相关的随机数产生上，必须使用跨平台通用的专用密码学库，如OpenSSL、libsodium。​普通的随机数产生，C语言、C++推荐使用的API见用例，请不要使用随机数种子方式去产生随机数，因为这样产生的随机数序列是固定或可预测的。

正例：
```
// C语言
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

#define FAILED  (-1)
#define SUCCESS 0

int32_t GetRangeRandomNumber(uint32_t left, uint32_t right, uint32_t* r) {
    int randomData = open("/dev/urandom", O_RDONLY);
    if (randomData < 0) {
        /* /dev/urandom是 Linux 系统中的密码学安全随机数生成器 (CSPRNG)，
         适合生成密钥、令牌等 */
        perror("Failed to open /dev/urandom");
        return FAILED;
    }
    int32_t randomNumber;
    int32_t ret = read(randomData, &randomNumber, sizeof(randomNumber));
    close(randomData);
    if (ret != sizeof(randomNumber)) {
        fprintf(stderr, "Failed to read from /dev/urandom\n");
        return FAILED;
    }
    // 生成 [left, right] 范围的随机数（无偏差）
    *r = (randomNumber % (right - left)) + left;
    LOG_DEBUG("Secure random number: %d\n", *r);
    return SUCCESS;
}

```
```
// C++ 11
#include <iostream>
#include <random>

void GetRandomNumberExample() {
    // 1. 随机数引擎：负责生成原始随机序列
    // std::random_device 用于获取非确定性随机数（如硬件熵）作为种子，是真随机数，无法预测
    std::random_device rd;
    // 使用梅森旋转算法引擎，用 random_device 的输出初始化
    std::mt19937 gen(rd());
    
    // 2. 分布器：控制随机数的范围和分布规律
    // 生成 [1, 100] 均匀分布的整数
    std::uniform_int_distribution<int> intDis(1, 100);
    
    // 生成 [0.0, 1.0) 均匀分布的浮点数
    std::uniform_real_distribution<double> doubleDis(0.0, 1.0);
    
    // 3. 生成随机数：将引擎实例传递给分布器
    std::cout << "Random Integer: " << intDis(gen) << std::endl;
    std::cout << "Random Double: " << doubleDis(gen) << std::endl;
    
    // 其他分布
    // 正态分布 (均值为 5.0，标准差为 2.0)
    std::normal_distribution<> normalDis(5.0, 2.0);
    std::cout << "Normal distribution: " << normalDis(gen) << std::endl;
    // 伯努利分布 (返回 true 的概率为 0.3)
    std::bernoulli_distribution bernoulliDis(0.3);
    std::cout << "Bernoulli distribution (true with p=0.3): " <<
        std::boolalpha << bernoulliDis(gen) << std::endl;
}

```
反例：
```
void GetRandomNumberExample() {
    // 用时间戳设置种子
    srand((unsigned int)time(NULL));
    // 生成一个 [0, RAND_MAX] 的随机整数
    int r1 = rand();
    LOG_DEBUG("Random number: %d\n", r1);
    
    // 生成一个 [1, 100] 范围内的随机整数，这种方法存在分布偏差
    int r2 = rand() % 100 + 1;
    LOG_DEBUG("Random number between 1 and 100: %d\n", r2);
    
    // 生成一个 [0.0, 1.0) 范围内的随机浮点数
    double r3 = (double)rand() / (RAND_MAX + 1.0);
    LOG_DEBUG("Random float between 0.0 and 1.0: %f\n", r3);
    return 0;
}
/* 使用反例中相关的接口去生成的随机数，是有可能被预测且存在弊端：
    （1）用srand产生随机数种子，只要入参确定，种子就确定，种子确定后产生随机数的序列就确定了。而time函数是一个秒级时间戳函数，一秒内多次调用返回的时间值相同，那么黑客就可能通过调用接口的时间、日志时间等推测出随机数算法，进而获取到伪随机数序列；
    （2）rand函数生成的范围随机数，并不是均匀分布，存在较大的分布偏差。
    所以这种生成随机数的方式，不推荐去使用，在安全相关的场景禁止使用。
 */
```
3-3-1-2、\[SC] 信号处理函数中，请不要使用非异步安全函数(non-async-safe functions)。
说明：信号处理函数中使用非异步安全函数，会导致未定义行为，包括：死锁、数据错乱、内存泄漏、I/O异常。下面列举常见的异步安全、非异步安全函数：

```
// 常见异步安全函数
// C++标准库：基本没有异步安全函数
write()          // 低层次I/O
read()           // 低层次I/O
signal()         // 但要注意递归问题
sigaction()      // 设置信号处理
_exit()          // 立即退出
_Exit()          // 立即退出
abort()          // 终止程序
kill()           // 发送信号
getpid()         // 获取进程ID
getuid()         // 获取用户ID
```

```
// 常见非异步安全函数
printf()         // 使用缓冲I/O
fprintf()        // 使用缓冲I/O
cout <<          // C++流操作
malloc()         // 内存分配
free()           // 内存释放
new              // C++内存分配
delete           // C++内存释放
strtok()         // 非可重入
rand()           // 使用静态状态
pthread_mutex_lock()  // 可能造成死锁
std::vector::push_back()  // 可能破坏内部状态
```

反例：
```
#include <csignal>
#include <iostream>
#include <mutex>
#include <thread>

std::mutex g_mutex;
int g_counter = 0;

void signal_handler(int signal) {
    std::lock_guard<std::mutex> lock(g_mutex);  // 可能造成死锁
    std::cout << "Signal " << signal << " received" << std::endl;
    g_counter++;
}
```

### 3-3-2 工程构建与信息披露

3-3-2-1、\[SC] 不会被执行的代码不允许被构建到release版本的软件中。
说明：不会被执行的代码俗称'死代码'，可能是调试时的代码、#if 0、其他项目的代码等，死代码的存在给程序增加了安全风险、可维护性也降低、如果存在白盒测试，代码测试覆盖率也会降低等问题。本地调试类代码，不应该合入到release所在分支中（或文件中）；不同项目的代码，要做好项目的构建管理，使不同项目代码在构建时能被正确处理。

——————————————————————————————

设计类问题

3-3-2-2、\[SC] 不允许使用未向客户披露的端口，以及不允许声明要使用的端口实际未使用。
说明：如果交付给客户的软件中使用了未向客户披露的端口，客户在测试过程抓取报文时发现，轻则做繁琐的澄清解释，重则丢失客户信任，甚至客户要求赔偿，对公司造成损失。反之亦然。

3-3-2-3、\[SC] release版本软件中，不允许留有任何客户未知的“后门”代码，如本地连接进入调试模式、远程连接root登录、未披露的开关类操作等。
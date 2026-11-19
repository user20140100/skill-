<!--
Split from: ./source-of-truth/C&Cpp编程规范-初稿v0.3.md
This file is intended for on-demand loading during style reviews.
Do not use the archived source-of-truth as runtime input.
-->

> Note: Chapter "二. 实践规约" section "2-1 文件".

# 二. 实践规约

## 2-1 文件

### 2-1-1 通用规则

2-1-1-1、\[ES] 单个源文件代码行数不允许超过2000行（包含空行、注释在内），超过2000行的源文件很大可能是因为违反设计原则中的“职能单一原则”，要思考如何拆分文件。
说明：单个文件代码行数过多，可读性会降低，后期如果要维护、拓展都会很困难。

800line

2-1-1-2、 \[ES] 头文件必须自给自足。
说明：头文件如果有使用到非自身定义的宏、类型、变量等，都必须引用对应的头文件。检验方式为头文件可以单独编译通过，或被其他文件作为第1个头文件引用。

除了项目中公共、基础的头文件，其他必现满足

2-1-1-3、\[ES]\[P] 头文件必须使用宏来防止重复include。且应该使用#ifndef加头文件宏的方式解决，请不要使用#pragma once。
说明:预编译指令#pragma含义比较复杂，且不同平台、编译器支持度不同，为保证平台兼容性，#ifndef加头文件宏方式是所有编译器都兼容的做法。头文件宏，一般统一命名为文件名(全大写字母)加_H。

正例：头文件data_process.h
```
#ifndef DATA_PROCESS_H
#define DATA_PROCESS_H

// code...

#endif
```

2-1-1-4、\[ES] 请不要乱引入头文件，即不使用的头文件不引入。

2-1-1-5、\[ES]\[P]\[SC] 头文件顺序引入顺序，需严格按照如下顺序：
a.对应的头文件（.c/.cpp文件）
b.C标准库头文件
c.C++标准库头文件
d.系统/平台相关头文件（第二方库文件）
e.第三方库头文件
f.项目内其他头文件(第一方库文件)
说明：与.c/.cpp对应的头文件放在最开始位置，可以最早发现对应头文件自包含问题；然后是越稳定的头文件靠前，先引入可避免项目内头文件的宏意外污染它们；项目内头文件后引入，可明确依赖关系。

试行

2-1-1-6、\[ES] 源文件中同类元素要写在文件同一区域，各类元素定义顺序（分布位置）需按以下顺序：
a.文件首部注释（版权声明、简洁等）
b.预处理指令，头文件引入#include
c.宏常量定义
d.宏函数定义
e.结构体、别名定义
f.枚举定义
g.变量声明
h.函数声明
i.函数实现
j.C++命名空间，类，结构体定义
说明：自定义数据类型放在最前，方便下文使用。同类元素放在一起，且不同类元素顺序固定，可以让文件结构更加清晰，寻找某个具体元素非常方便；相反没有顺序，随意写在文件各个位置，会增加文件杂乱感，可读性降低、维护困难。

2-1-1-7、\[ES] .c文件、.cpp文件中同一类元素中各个元素相对位置要与.h文件保存一致。
说明：如在.h中声明函数的顺序为：
```
void Init(void);
void Process(void);
void Destroy(void);
```
那么在.c/.cpp文件中，函数实现也应该保持这个顺序。

2-1-1-8、\[ES] 源文件中同类元素(用途相似、处理某个业务流程等)，应该聚集到一起，不同类型的元素可以用一个空行分隔。
说明：好的头文件，相当于一个大纲目录，顺序、分类都非常有条理；.c/.cpp文件也同理。

正例：
```
// init
void InitOfStandard(void);
void InitOfSimple(void);

// process
void ProcessOfStandard(void);
void ProcessOfSimple(void);

// destroy
void DestroyOfStandard(void);
void DestroyOfSimple(void);
```

2-1-1-9、文件编码统一使用UTF-8。

### 2-1-2 C++规则

2-1-2-1、\[SC] C++文件使用C标准库时，请不要使用旧式的.h后缀的头文件。

正例：
```
// 使用不带.h后缀的C标准库头文件
#include <cstdint>
```
反例：
```
#include <stdint.h>
```

2-1-2-2、 \[ES] C++文件的命名空间内(包括匿名命名空间)各类元素、结构体中的各类元素定义顺序（分布位置），需遵循规则【2-1-1-6】。类中的元素定义与排布还需遵循：
访问权限声明顺序：
a.public
b.protected
c.private
每个访问权限区块只声明1次，同一区块内，各元素声明次序为：
a.内部类型（枚举/结构体/类）；
b.函数
c.变量
其中职能、归属一样变量（函数）应该聚集放在一个区域，职能不同的变量（函数）应该分隔，并适当加上注释；
其中函数的声明排版为：
a.构造函数/析构函数/初始化之类的函数
b.实现的接口函数
c.操作内部数据的函数(get、set)
d.业务函数

正例：
```
class NetDiagnosisHelper : public SystemEventListener, public EtherNetListener {
public:
    // inner typedef
    enum NetDiagnosisStatus {
        NET_DIAGNOSIS_STATUS_IDLE,
        NET_DIAGNOSIS_STATUS_CHECKING,
        NET_DIAGNOSIS_STATUS_WAIT_CMD,
        NET_DIAGNOSIS_STATUS_HEALING,
        NET_DIAGNOSIS_STATUS_RESPOND,
    }; 

    enum EtherNetCode {
        ETHER_NET_CODE_NORMAL,
        ETHER_NET_CODE_CARD_DOWN,
        ETHER_NET_CODE_VALN_NOT_EXIST,
        ETHER_NET_CODE_ROUTE_FAULT,
        ETHER_NET_CODE_GATEWAY_FAULT,
        ETHER_NET_CODE_FIREWALL_FAULT,
        ETHER_NET_CODE_UNKNOW_FAULT,
    };

    // constructor、destructor、init
    NetDiagnosisHelper() : cmd("") {}
    ~NetDiagnosisHelper() = default;
    void init(void);
    
    // implement interface
    // SystemEventListner API
    void OnSystemReadyHandler(void) override;
    void OnSystemExiteHandler(void) override;
    
    // EtherNetListener API
    void OnNetCardUpHandler(void) override;

    // get、set function
    NetDiagnosisStatus GetCurrentDiaStatus(void);
    void SetCmd(std::string cmd);

// protected: // 可以没有

private:
    // const value
    static const uint32_t NET_CHECK_INTERVAL_TIEM = 600000
    // inner status value
    NetDiagnosisStatus currentDiagStatus { NET_DIAGNOSIS_STATUS_IDLE };
    EtherNetCode checkingCode { ETHER_NET_CODE_NORMAL };
    // business value
    std::string cmd;
    
    // business function
    void StartEnterNetCheck(void);
    void TryEnterNetHeal(void);
};
```

2-1-2-3、\[SC] 头文件中请不要使用 using namespace xxx。
说明：如果头文件中使用了using namespace引用命名空间，那么一个头文件include的头文件也可能使用了using namespace，当出现同名符号时，就会出现错误。


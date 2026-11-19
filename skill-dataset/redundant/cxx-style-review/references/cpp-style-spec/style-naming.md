<!--
Split from: ./source-of-truth/C&Cpp编程规范-初稿v0.3.md
This file is intended for on-demand loading during style reviews.
Do not use the archived source-of-truth as runtime input.
-->

> Note: Chapter "一. 风格规约" section "1-1 命名".

# 一. 风格规约

## 1-1 命名
说明：命名的总体原则是尽可能用简洁的词汇，表达当前对象的含义，做到见名知意的效果。

### 1-1-1 文件

1-1-1-1、\[ES] 文件命名统一使用大驼峰风格命名，在防止同名与表面含义前提下尽量简短。词语使用因为单词，避免出现非国际词语的拼音。
说明：C++类命名为大驼峰风格命名，文件名与类名同名方便查找文件。

正例：
```
DataAccess.h
DataAccess.c
DataAccess.cpp
```

反例：



```
dataAccess.h // 使用小驼峰
data_Access.c // 使用下划线
Data_Access.cpp // 使用了下划线
data$process.c // 使用了其他符号
shu_ju_fang_wen.cpp // 使用拼音
```



1-1-1-2、\[ES]\[P] 文件后缀要求，头文件后缀统一为.h，C语言源文件统一后缀为.c，C++语言源文件统一后缀为.cpp。

正例：
```
DataAccess.h
DataAccess.c
DataAccess.cpp
```

反例：
```
DataAccess.H // 使用大写字母H作为头文件后缀不符合规范
DataAccess.C // 使用大写字母C作为C文件后缀不符合规范
DataAccess.hxx // 使用hxx作为C++文件的后缀不符合规范
```

### 1-1-2 宏

1-1-2-1、\[ES] 定义宏常量以字母开头，所有字母都用大写，单词之间用下划线分隔。
说明：避免使用下划线开头定义宏，很多三方库的宏定义以单下划线开头，双下划线开头是Cpp标准库中定义的宏，如果定义宏使用下划线开头容易与之混淆。

正例：
```
#define BUFF_MAX_SIZE 1024
```

反例：
```
#define _BUFF_MAX_SIZE 1024 // 下划线开头
#define buff_max_size // 使用了小写字母
```


1-1-2-2、\[ES] 宏函数命名与宏常量基本一致，宏函数参数命名用小写字母，并且尽量用一个单词，如果有多个单词，用下划线分隔。

正例：
```
#define ARRAY_SIZE(x) (sizeof(x) / sizeof(x[0]))
#define UNUSED(x) (x)
#define LOG_DEBUG(format, args...) print("[DEBUG][FILE:%s][LINE:%d][%s]"\
            format "\n", __FILE__, __LINE__, __FUNCTION__, ##__VA__ARGS__)
```

1-1-2-3、\[ES] 条件选择编译类宏命名时，请不要使用带有否定类词语。
说明：一般一个条件选择编译宏，值为true时，表示是什么平台、是什么产品、有什么功能/特性等表肯定的含义，并编译相关代码，如果加否定类词语，表示的含义与习惯的思维相反，容易让人误解。

正例：
```
#define LOG_LEVEL_DEBUG
#define LOG_DEBUG(format, args...) print("[DEBUG][FILE:%s][LINE:%d][%s]"\
    format "\n", __FILE__, __LINE__, __FUNCTION__, ##__VA_ARGS__)
#else
#define LOG_DEBUG
#endif
```

反例：
```
#define NOT_LOG_LEVEL_DEBUG // 使用否定类词语
#define LOG_DEBUG
#else
#define LOG_DEBUG(format, args...) print("[DEBUG][FILE:%s][LINE:%d][%s]"\
    format "\n", __FILE__, __LINE__, __FUNCTION__, ##__VA_ARGS__)
#endif
```

### 1-1-3  变量

1-1-3-1、\[ES] 局部变量的命名使用小驼峰方式命名。

正例：
```
int32_t signalValue = 0;
bool isValid = false;
```

反例：
```
int32_t signal_value = 0; // 使用下划线
bool IsValid = false; // 使用了大驼峰方式命名
```

1-1-3-2、\[ES] 变量命名请不要使用美元符"$"、下划线"\_"。
说明：虽然命名中使用美元符、下划线符合语法，但这首先与小驼峰方式命名矛盾；双下划线开头的变量是C++标准库的命名风格，如果下划线开头命名方式容易与其混淆；下划线、美元符命名不统一，增加代码杂乱感。

反例：
```
int32_t battery$level = 0; // 变量名混用美元符
```

1-1-3-3、\[ES] 变量名请不要使用拼音，国际公认拼音词、特有名词除外。
说明：业界中几乎都使用英文单词进行变量命名，且大部分现有代码都是英文单词命名，混用拼音不优雅。

正例：
```
string liuhuanHardwareVersion; // liuhuan（六环）为特有名词，可以使用拼音
```

反例：
```
int32_t sudu = 0; // 使用拼音命名变量
```


1-1-3-4、\[ES] 变量命名应该根据用途、作用范围进行命名，其中作用范围越大的变量，命名应该详细一些（宁可命名长一些也不可丢弃变量重要的含义），作用范围小的变量，命名可以简洁一些。在保证变量名含义清晰条件下尽可能简洁，但不可滥用缩写（不被公认的单词缩写）。为保证变量名长度不能过长，变量名的字符数不能超过30个（含30个），命名不能完全表示含义的，用注释加以解释。

正例：
```
// app是公认的applicable缩写，msg是公认的message缩写，recv是公认的receiver的缩写
int32_t appMsgRecvCount = 0;

void func() {
    uint32_t count = 0; // 局部变量，命名可以简洁一些
    // do some thing
}

// 变量名长度接近30个字符还不能完全表示含义的，用注释补充说明其含义
bool isLongPressPrevKeyInRadioPage = false; // 是否在收音主页中长按方控的上一曲按钮
bool isLongPressNextKeyInRadioPage = false; // 是否在收音主页中长按方控的下一曲按钮
```

反例：
```
int32_t notiNum = 0; // noti并非notification标准缩写，可读性非常差

// 变量名长度超过了30个字符
bool isLongPressPrevKeyInRadioMainPage = false;
```

1-1-3-5、\[ES] 变量的命名请不要出现拼写错误的词汇、自创词汇、自创缩写等非标准英文单词，以及非公认名词。
说明：变量名出现错误词汇，会降低代码可读性，设置误导开发者对代码的理解。

反例：
```
bool hasConFinish = false; // con到底是config，还是connection的缩写？

// 可以猜测出是config错误拼写为confit,但对于有代码洁癖的同学看起来会很难受
int32_t confitId = 0; 
```

1-1-3-6、\[ES] 变量的命名请不要带有变量类型信息（如用变量类型首字母作为前缀）,但可以带有变量的逻辑结构信息。
说明：变量的命名应当聚焦变量的逻辑用途，而不是变量的类型。对于大部分不带类型信息前缀且规范的变量命名，开发者可以通过变量名字猜测出变量的类型，也可通过代码上下文很容易的获取到变量的类型。而变量名带上类型信息，当类型需要变更时就需要同步修改，且不适用泛化与抽象等。

正例：
```
float speed = 0.0f; // 根据命名、上下文就可获知变量类型

// 布尔类型变量使用类似isXxx或hasXxx命名，开发者很容易知道这是布尔类型变量
bool isValid = false; 

/* 带ptr后缀注重描述变量的逻辑形式是指向User的指针（不限定指针具体类型，可以是裸指针、智能指针） */
std::share_ptr<User> userPtr = std::make_share<User>(User()); 

// 带list后缀注重描述变量的逻辑结构是一个列表，底层类型可以是数组、链表等
std::vector<User> userList(); 
```

反例：
```
float fSpeed = 0.0; // 表明变量是float类型变量，如果后续改为doubel类型则变量名需要修改
User* pUser = NULL; // p前缀表示指针，放在前面，不符合注重变量逻辑用途规范

/* 补充说明：前缀统一不带变量基础类型的信息，实在要带基础类型信息，请加在后缀上（后缀也尽量不要带变量基础类型信息） */
```

1-1-3-6、\[ES] 全局变量命名时加上g字母作为前缀。
说明：前缀g意为global，这与变量命名请不要使用带有变量类型信息有区别，一是全局变量前缀g不表示数据类型，二是全局变量范围太大，带有g前缀意在提醒开发者务必注意该变量作用范围。

正例：
```
static bool gIsSystemInit = false;
```

1-1-3-7、\[ES] 定义指针变量、引用时，符号*、符号&应该靠近类型，强调类型一致性。
正例：
```
uint32_t* countPtr;
uint32* const array; // 常量指针
const char* const message = "Hello";

void ProcessData(uint32_t& data) {
    // do some thing
}
```

反例：
```
uin32_t *countPtr; // *符号应该靠近类型
uin32_t* data, size; // 请不要混合声明，可读性差，指针变量一行声明1个
```

### 1-1-4 常量

1-1-4-1、\[ES] 常量命名为小驼峰风格，带有k前缀。

正例：
```
static const int32_t kTimerTimeoutMs = 1000;

void HandleData(int32_t datas) {
    const uint32_t kTaskTimeoutMs = 100;
    // do some thing...
}
```

反例：
```
static const int32_t TIMER_TIMEOUT_MS = 1000; // 不带k前缀，且为大写字母、下划线分隔
```

### 1-1-5 枚举

1-1-5-1、\[ES] 枚举命名使用大驼峰方式命名，命名中尽可能表述清晰是什么类型的枚举，避免只用Type、State、Mode、Model等。

正例：
```
// 指明是Chip的Model,而不是简单的Model
enum RadioChipModel {
    RADIO_CHIP_MODEL_NXP47901 = 0,
    RADIO_CHIP_MODEL_SILICON47901,
    RADIO_CHIP_MODEL_SILICON47902,
}; 

// 指明是band的类型，而不是简单的type
enum RadioBandType {
    RADIO_BAND_TYPE_AM = 0, // 枚举成员都有RADIO_BAND_TYPE前缀
    RADIO_BAND_TYPE_FM,
};
```

反例：
```
/* Radio有很多属性：state、band、manufacturer等，具体指什么属性（特征）的type要指明，避免    不清晰或后续产生命名冲突 */
enum RadioType {
    RADIO_TYPE_AM = 0,
    RADIO_TYPE_FM,
}; 
```


1-1-5-2、\[ES] 枚举中成员的命名为大写字母，单词之间下划线分隔，前缀统一为枚举名的一部分。

正例：
```
enum RadioBandType {
    RADIO_BAND_TYPE_AM = 0, // 枚举成员都有RADIO_BAND_TYPE前缀
    RADIO_BAND_TYPE_FM,
};
```

反例：
```
// 枚举成员不带RADIO_CHIP_MODEL前缀，不方便获悉其是RadioChipModel的枚举
enum RadioChipModel {
    RADIO_CHIP_NXP47901 = 0,
    RADIO_CHIP_SILICON47901,
    RADIO_CHIP_SILICON47902,
}; 


enum RadioBandType {
    AM = 0, // 枚举成员不带统一前缀，可读性差
    FM,
};
```

### 1-1-6 结构体

1-1-6-1、\[ES] 结构体命名使用大驼峰方式命名。

正例：
```
typedef struct {
   uint32_t arrSize;
   int arr[0];
} IntFlexibleArray;
```

反例：
```
typedef struct {
   uint32_t arrSize;
   int arr[0];
} intFlexibleArray; // 使用小驼峰风格

typedef struct {
   uint32_t arrSize;
   int arr[0];
} int_flexible_array; // 使用了下划线
```

### 1-1-7 函数

1-1-7-1、\[ES] 函数命名使用大驼峰，一般带有动词、宾语，或以Handler、Function结尾，表明该函数所做的工作、处理的对象、什么的处理器、什么的功能。为保证变量名长度不能过长，函数名的字符数不能超过50个（含50个），命名不能完全表示含义的，用注释加以解释。

正例：
```
void LoadRadioFirmwareFile(void);

void TunerIdleStatusHandler(void);
```

反例：
```
void RadioFirmwareFile(void); // 函数为名词，不容易理解其动作是什么
```


1-1-7-2、\[ES] 函数形式参数命名遵循【1-1-3、变量】的命名规则。

正例：
```
typedef bool(*ConditionFunc)(const int32_t); // 函数声明允许省略形参名

// 形参名命名规则遵循【1-1-3、变量】命名规则，采用小驼峰风格命名
uint32_t CountListByConditionFunc(const int32_t* list, const uint32_t size,
    ConditionFunc func) {
    uint32_t result = 0;
    if ((list == NULL) || (size == 0)) {
        LOG_ERROR("error: null pointer.");
        return false;
    }
    for (uint16_t i = 0; i < size; ++i) {
        if (func(list[i])) {
            ++result;
        }
    }
    return result;
}
```

### 1-1-8 C++命名空间与类

1-1-8-1、\[ES] C++命名空间使用小写字母单词，单词之间用下划线分隔。
说明：不选择驼峰方式命名，一是与标准库命名空间对齐，二是使用域访问符::时可以快速区分是命名空间，还是类（类名大驼峰方式命名）。

正例：
```
namespace project_namespace
{
    // content
}
```

反例：
```
namespace ProjectNamespace // 使用了大驼峰风格命名
{
    // content
}
```

1-1-8-2、 \[ES] C++类的命名使用大驼峰方式命名。

正例：
```
class RadioChip {
    // members
};
```

反例：
```
class radioChip {
    // members
}; // 使用小驼峰

class radio_chip {
    // members
}; // 使用下划线
```

1-1-8-3、\[ES] 带有纯虚函数的类（接口类）需带有IF(interface)后缀

正例：
```
class ConnectionIF {
    virtual void connectByIP(std::string ip) = 0;
};
```

1-1-8-4、\[ES] 类中变量命名遵循【1-1-3、变量】的命名规则，类的成员变量不需要带有m前缀等表示指明其是成员变量的信息。
说明：类的成员变量根据上下文很容易获知，所以不需要带m前缀。

1-1-8-5、\[ES] 类中常量命名遵循【1-1-4、常量】的命名规则。

1-1-8-6、\[ES] 类中函数命名遵循【1-1-7、函数】的命名规则。

### 1-1-9 综合

1-1-9-1、\[ES] 如果代码中使用了设计模式，对应的文件名、类名、函数名等可以体现设计模式，可以快速帮助开发者快速了解模块架构。

正例：
```
// 工厂模式
class ComponentFactory {
    // members
};

// 策略模式
class ProcessDataStrategyIF {
public:
    virtual void Before() = 0;
    virtual void Process() = 0;
    virtual void After() = 0;
}

// 胶水层
hardware_glue_layer.h
hardware_glue_layer.cpp
```

1-1-9-2、 \[ES] boolean类型变量、常量的命名，请不要使用带否定类词语。
说明：布尔类型变量、常量一般为true是表示是什么、有什么、已经什么、能够什么、满足什么等表肯定的含义，如果加入否定词语，则表示的含义与习惯的思维相反，容易让人误解。

1-1-9-3、 \[ES] 命名中请不要使用意义不明的数字，可以描述为具体的业务、场景、类型含义等。

反例：
```
#defind STATUS_TYPE_1 // 具体描述是什么状态
#defind STATUS_TYPE_2

void ServiceInitStep1() { // 可以描述这个阶段主要做了什么
    // do some thing...
}
```



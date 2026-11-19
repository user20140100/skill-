<!--
Split from: ./source-of-truth/C&Cpp编程规范-初稿v0.3.md
This file is intended for on-demand loading during style reviews.
Do not use the archived source-of-truth as runtime input.
-->

> Note: Chapter "二. 实践规约" section "2-2 预处理与宏运用".

## 2-2 预处理与宏运用

### 2-2-1 条件编译宏

2-2-1-1、\[ES] 使用多分支的条件编译预处理指令，如：#if - \#elif - \#endif，后续关联的预处理指令都必须带上对应的条件控制分支中首个预处理分支关联的宏名作为注释。
说明：预处理指令缺少缩进，如果没有注释辅助体现预处理指令的关联关系，可读性非常差。

正例：
```
#if (QCM6125)

// code...

#elif (BCM2835) // (QCM6125)

// code...

#else // (QCM6125)

#error "Error: please check platform macro!"

#endif // (QCM6125)
```

2-2-1-2、 \[SC] 请不要在预处理指令中使用魔鬼数字起到注释代码段或选用代码段的作用。

反例：
```
#if 0

// code paragraph 1

#else

// code paragraph 2

#endif

```
如果不需要代码段 'code paragraph 1'请直接删除，并去掉预处理指令；如果确实有存在的必要，请使用具体的宏进行控制。


2-2-1-3、\[SC] 预处理指令 '\#else' 分支下不写默认被编入的项目代码，而是增加编译报错信息。
说明：如果 '#else' 分支中 写的是默认被编入项目的代码，当相关的宏值错误、或者新增加了对应的类型却没有增加分支的情况就不能被发现；相反增加编译报错信息，可以及时发现相关的宏值存在错误、或新增宏值没有对应的新分支。

正例：
```
#if (QCM6125)

// code...

#elif (BCM2835) // (QCM6125)

// code...

#else // (QCM6125)

#error "Error: please check platform macro!"  // 当平台宏定义错误时，可以及时发现问题

#endif // (QCM6125)
```

### 2-2-2 宏常量与宏函数

2-2-2-1、\[SC] 尽可能不使用宏常量，一般使用宏常量场景为跨设备间的协议、跨模块通用常量、汇编可能使用到的常量等。其他场景请使用常量const，或常量表达式constexprt。
说明：宏常量本质是文本替换，没有类型，在不同平台可能被解释为不同的类型，编译器不做类型检查，可能产生隐性问题。

2-2-2-2、\[SC] 宏常量定义时，常量值部分必须加上小括号。
说明：不加括号的宏常量值、常量表达式，可能在代码使用中产生隐形问题。

正例：
```
#define EXECUTE_ERROR (-1)
```

反例：
```
#define XXX_PER_DECREASE_NUMBER -100
// 如果在代码用，使用到这个宏常量用于计算，就可能出现问题。
```

2-2-2-3、\[SC] 尽量避免定义宏函数，宏函数一般为简单且重复的代码，如日志打印、数组长度计算、参数不使用声明、入参校验等。
说明：宏函数的弊端与宏常量类似，都可能产生隐形问题。
【建议】

2-2-2-4、\[SC] 宏表达式、宏函数存在多条语句时，必须用do {} while(0) 囊括。

正例：
```
#define POINTER_VERIFY(ptr) do {\
    if (prt == NULL) {\
        LOG_WARN(“null pointer.”);\
        return;\
    }\
} while(0)
```

2-2-2-5、\[SC] 定义宏表达式、宏函数末尾处不需要带有分号，在调用处添加分号。

反例：
```
#define ARRAY_SIZE(arr) ((sizeof(arr)) / (sizeof(arr[0])));
// 定义宏函数ARRAY_SIZE的末尾处不需要带有分号
```


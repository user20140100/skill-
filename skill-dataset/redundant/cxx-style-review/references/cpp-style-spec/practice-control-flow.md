<!--
Split from: ./source-of-truth/C&Cpp编程规范-初稿v0.3.md
This file is intended for on-demand loading during style reviews.
Do not use the archived source-of-truth as runtime input.
-->

> Note: Chapter "二. 实践规约" sections "2-3 条件控制语句" + "2-4 循环".

## 2-3 条件控制语句

### 2-3-1 if/if-else/if-else if-else 与 bool表达式

2-3-1-1、\[ES]\[DS] if-else if-else条件分支语句中，分支数不允许超过5个(不包含5个)。
说明：分支数过多时，会让代码变的冗长、可读性差、更容易出错。当遇到超过5个分支业务场景时，可以使用设计模式中的策略模式（Strategy Pattern）转换、解决。复杂的多条件分支场景，通过策略模式、条件对像（谓词、lambda表达式）、条件对象<->策略对象映射表，最终都能转化为表的遍历。

2-3-1-2、\[SC] 条件判断中，请不要出现boolean常量，或boolean常量表达式。
说明：判断条件中为boolean常量，则代码是否被执行，在编译期就已经确定，条件判断没有任何意义。
反例：
```
if (true) {
    // do some thing
}

if (BUFF_SIZE > ARRAY_MAX_SIZE) { // 这里的BUFF_SIZE、ARRAY_MAX_SIZE都是常量
    // do some thing
}
```

2-3-1-3、\[ES] boolean类型变量不需要再与boolean常量进行比较，这样多此一举。

反例：
if (isValid == true) {
    // do some thing
}

2-3-1-4、\[ES] 数值类变量，请不要直接用于逻辑判断。
说明：C语言中，虽然语法定义0为假，非0为真，但数值直接用于逻辑判断（当成boolean值使用），代码可读性会降低。

正例：
```
if (dataPtr == nullptr) {
    return;
}

if (count != 0) {
    // do some thing
}
```

反例：
```
if (count) { // count为int类型变量
    // do some thing
}
```

2-3-1-5、\[ES] 带有比较运算符（'\=='、'>'、'<'等）的bool表达式中，待比较的变量应该放在左侧，被比较的变量或常量应该放在右侧，一般来说被比较的变量值相对固定或者是常量。

正例：
```
// currentStatus是待比较变量，应该放在左侧
if (currrentStatus == NET_DIAG_STATUS_IDLE) {
    // do some thing
}
```



2-3-1-6、\[ES] 过于复杂的判断条件，不要堆砌式的放在if的小括号中，可读性很差。可以声明为boolean变量，或封装为函数，并适当添加注释。
【建议】

### 2-3-2 switch-case

2-3-2-1、\[ES]\[DS] switch-case中的case分支不允许超过5个，超过5个的，转化为静态表+表遍历。
说明：case分支过多时，与if-else if-else分支过多的弊端一致。

2-3-2-2、\[ES] switch-case中，每一个case中的代码都必须使用大括号’{}’囊括，请不要在case大括号外出现代码。

2-3-2-3、\[ES] switch-case中，每一个case大括号中最后一条语句必须是break,不允许出现执行完一个case后，继续往后执行剩余case的代码。
说明：虽然在语法上switch-case允许执行完一个case不break可以往下执行剩余case，但业界默认将switch-case视作一次执行一个分支的条件控制语法关键字。如果允许往下执行剩余case会使得代码可读性降低，不利于后续维护扩展（如还需考虑case顺序等）。实在需要往下执行剩余case逻辑的，可以通过外层套一个while循环+case中修改控制while的变量来实现。

正例：
```
bool isContinue = true;
while (isContinue) {
    isContinue = false;
    switch (currentStatus) {
        case NET_DIAG_STATUS_IDLE : {
            // do some thing
            break;
        }
        
        case NET_DIAG_STATUS_WORK_END : {
            (GetFaultCode() != NET_DIAG_CODE_NORMAL) {
                // 要继续执行一次switch(或者说想继续走后面的case)
                currentStatus = NET_DIAG_STATUS_HEALING;
                isContinue = false;
            }
            break;
        }

        case NET_DIAG_STATUS_HEALING : {
            // do some thing
            break;
        }
        
        default : {
            LOG_ERROR("invalid net diag status.");
            break;
        }
    }
}

```


2-3-2-4、\[ES] switch-case中，最后必须有default分支作为结尾，并添加日志。
说明：方便统一处理未考虑的case值、无效case值。

## 2-4 循环

### 2-4-1 通用规则

2-4-1-1、\[ES] 循环体中应该遵循最少内容原则，不必要在循环中做的工作应该提到循环体外。

2-4-1-2、\[SC] 控制循环的逻辑条件中，应当遵守【2-3-1】中的规则。如：
控制循环的逻辑条件中，请不要使用boolean常量、boolean常量表达式。(宏函数中用于囊括多行代码的do {} while(0) 除外)。
说明：如果循环条件中使用boolean值为true的常量，循环变为死循环，后期扩展、维护非常不利（线程退出控制等）；如果循环条件中使用boolean值为false的常量，则这个循环体执行0次或1次，不需要使用循环控制。

反例：
```
while (1) {
    // do some thing
}
```
### 2-4-2 C++规则

2-4-2-1、\[DS] 当使用C++增强for循环遍历数组、容器中的元素时，应该使用引用类型，如果不涉及修改，还应该加上const关键字修饰。
说明：使用引用类型，可以减少不必要的对象拷贝，尤其对于大对象，多余拷贝增加性能损耗。

正例：
```
for (const auto& item : list) {
    // do some thing
}
```


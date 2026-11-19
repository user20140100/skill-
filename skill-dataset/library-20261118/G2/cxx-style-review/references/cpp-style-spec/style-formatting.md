<!--
Split from: ./source-of-truth/C&Cpp编程规范-初稿v0.3.md
This file is intended for on-demand loading during style reviews.
Do not use the archived source-of-truth as runtime input.
-->

> Note: Chapter "一. 风格规约" section "1-2 格式".

## 1-2 格式
说明：格式的总体原则使代码工整美观，可以很大程度减少开发者阅读代码时的疲劳。

### 1-2-1 空格
说明：总体原则为遵循空格使用规定，任何情况下不多1个空格，也不少1个空格。

1-2-1-1、\[ES] 如果左大括号’{‘前不换行、左大括号’{’后不换行、右大括号’}’前不换行，则留1个空格。特殊情况，如果大括号内没有内容，则括号内不留空格。

正例：
```
// 左括号前不换行，留1个空格
class DataMgr {
    // members
};

std::vector<int> v { 1, 2, 3, 4, 5 }; // 左大括号后不换行、右大括号前不换行，留1个空格

virtual void Func(void) {} // 大括号内没有内容，不留空格
```

1-2-1-2、\[ES] 关键字if、for、while、do、switch与左小括号'('之间留1个空格。

正例：
```
// if关键字与小括号之间留1个空格
if (condition) {
    // do some thing...
}
```

1-2-1-3、\[ES] 除【1-2-1-1】、【1-2-1-2】外，其余情况下，小括号’()’前后都不留空格。

反例：
```
// 小括号中，前后不留空格
for ( int i = 0; i < size; ++i ) {
    // do some thing.
}
```

1-2-1-4、\[ES] 多元运算符前后留1个空格，包括'='、'\=='、'+'、'-'、'+'、'/'、'%'、' ?  :  '（三元条件选择运算符）等等，与操作数关系密切、从属关系的则不需要留空格，如自增、自减、指针符、域访问符等。

正例：
```
uint32_t CountLessThanNumber(const int32_t* arr, const uint32_t arrSize,
    const int32_t min) {
    if (arr == NULL) { // 双等号==前、后都留1个空格
        return 0;
    }
    int count = 0; // 等号=前、后都留1个空格
    for (uint_32_t i = 0; i < arrSize; ++i) {
        // +=号、<=号、条件选择运算符' ? : '前、后留1个空格
        count += (arr[i] <= min) ? 1 : 0;
    }
    return count;
}
```

反例：
```
++ i; // 一元运算符与变量间不需要加空格
userPtr -> name; // userPtr指针与其属性是从属关系，使用指针符->前后不需要留1个空格
```

1-2-1-5、\[ES] 在使用逗号、分号分隔并列关系的元素中，逗号、分号与后面的变量、表达式之间留1个空格。
正例：
```
// 分隔参数的逗号与后面的参数保留1个空格
uint32_t CountLessThanNumber(const int32_t* arr, const uint32_t arrSize,
    const int32_t min) {
    if (arr == NULL) {
        return 0;
    }
    int count = 0;
    for (uint_32_t i = 0; i < arrSize; ++i) { // for中分号";"与前面内容留有1个空格
        count += (arr[i] <= min) ? 1 : 0;
    }
    return count;
}
```

1-2-1-6、\[ES] 变量声明定义时，变量类型与变量之间有且仅有1个空格。

反例：
```
int32_t  count = 0; // 这里类型名与变量名是2个空格，不符合有且仅有1个空格
```

1-2-1-7、\[ES] 单行注释符，如果同一行前面有代码，注释符'//'与代码之间最少保留1个空格，与注释内容之间留1个空格；多行注释符，如果同一行前面有代码，注释符'/\*' 左侧与代码之间保留1个空格，与注释内容之间保留1个空格。

正例
```
// 单行注释符
int32_t value; // 单行注释符

/* 多行注释符 */
int32_t value; /* 多行注释符 */
```

1-2-1-8、\[ES] 空白行不能留有空格。

反例：
```
void Func(void* param) {
    if (param == NULL) {
        return;
    } // 下一行空白行留有空格，可能因为缩进而无意留下
    
    // do some thing...
}
```


1-2-1-9、\[ES] 换行前不能留有空格。

反例：
```
// 左大括号{换行前留了空格
void func() { 
    // do some thing...
}
```


1-2-1-10、\[ES] 静态表、宏、注释等行数较少需要对齐情况下允许多加空格。变量的声明不需要多加空格对齐。
说明：静态表、宏、注释等对齐会后代码工整美观，且每一列含义相同，有助于增加了可读性。变量每一列含义不一定相同，没有对齐的必要。

正例：
```
Static RadioStatusAndHandler radioStatusAndHandler[] = {
    { RADIO_STATUS_NO_READY, RadioInit(void* param, uint32_t paramSize)      },
    { RADIO_STATUS_READY,    RadioBeginWork(void* param, uint32_t paramSize) },
}

#define NET_DIAGNOSE_PROTOCAL_BEGING_DIAGNOSE  901
#define NET_DIAGNOSE_PROTOCAL_PROCESS_DIAGNOSE 902
#define NET_DIAGNOSE_PROTOCAL_FINISH_DIAGNOSE  902
```


反例：
```
int32_t quality = 0;
int32_t price   = 0; // 变量声明为了对齐加多了2个空格
```

### 1-2-2 缩进与换行

1-2-2-1、\[ES] 一次缩进统一为4个空格，请不要使用tab符缩进（IDE可以打开显示制表符的选项，如果代码中存在制表符，则不符合规范）。
说明：tab符号在不同IDE中显示宽度不一致，混用空格和tab符做缩进，会导致代码参差不齐。

1-2-2-2、\[ES] 预编译指令任何时候都不缩进。
说明：预编译指令不属于代码逻辑，与代码一起缩进，混在代码中不能让开发者非常醒目的阅读到。

正例：
```
void DataProcess(int* data, bool condition) {
    if (data == NULL) {
        return;
    }
    if (condition) {
    // 预编译指令不和代码一起缩进，正确
#ifdef DEBUG
        DEBUG_LOG(“condition is true.”);
#endif // DEBUG
        // do some thing...
    }
}
```

反例：
```
void DataProcess(int* data, bool condition) {
    if (data == NULL) {
        return;
    }
    if (condition) {
        // 预编译指令和代码一起缩进，错误
        #ifdef DEBUG
        DEBUG_LOG(“condition is true.”);
        #endif // DENUG
        // do some thing...
    }
}
```

1-2-2-3、\[ES] 每个左大括号’{’后换行，括号内的代码增加1个缩进，大括号中内容为空则不换行，大括号内也不留空格。

1-2-2-4、\[ES] 每个右大括号'}'前换行，换行后的'}'比括号内的代码减少1个缩进（对齐左大括号所在列），大括号中内容为空的情况除外；右大括号后，如果是else、else if则与右大括号同行(之间留1个空格)，否则右大括号独立为一行。

1-2-2-5、\[ES] 以分号结束、或必须换行缩进的1行代码中，未超过120个字符不允许换行；相反超过120个字符的必须换行，换行细则：
（1）如果换行超过2行，则只在第1次换行时增加1个缩进，之后的换行与第2行对齐，不再增加缩进；
（2）运算符、成员访问符'.'、域访问符'::'、指针访问符'->'、参数分隔的逗号',' 保留在上一行;
（3）左括号前不换行。
（4）如果第1次换行为小括号中的内容，则换行开始位置可以是1个缩进，也可以在上一行左括号后1个字符的位置。
说明：统一行宽为120个字符，一是大部分屏幕的宽度一般足够看清行宽为120个字符代码。二是如果行宽不一致，会增加了代码参差不齐的杂乱感，且开发者阅读行宽超过屏幕宽度的代码时，需要反复的左右滚动，影响阅读效率。

补充：判断是否超过120个字符，可以通过IDE设置开启行宽辅助线，这样就可以很明确的知道是否超过120个字符，以VS Code为例：
a.打开设置
 ![[设置行宽线1.png]]

b.搜索框输入rulers，选择用户，点击【在settings.json中编辑】
 ![[设置行宽线2.png]]

c.跳转到【settings.json】文件后在大括号中添加规则
```
"editor.renderWhitespace": "all",
    "editor.rulers": [
        { "column": 120, "color": "#ff0000" },
],
```
 ![[设置行宽线3.png]]


d.保存配置，重启VS Code，检查代码编辑区中是否多了一条红色的竖线，存在则设置成功
 ![[设置行宽线4.png]]


1-2-2-6、\[ES]在代码中，为了让变量、代码块等对象的分类、逻辑、归属等更加清晰的，可以使用空行间隔开来，但有且只能加1个空行，请不要随意乱加空行、多加空行。

正例：
```
void Func(void* arg, const uint32_t size) {
    if ((arg == nullptr) || (size == 0)) {
        return;
    } // 参数校验和业务逻辑分开一行，增加可读性

    // do some thing.
}
```

反例：
```
void Func1() {
    // do some thing.
}


void Fun2() {
    // do some thing
}
// func1、func2之间加了1个空行就能醒目看法两个函数的范围，加2行没有必要。
```

1-2-2-7、\[ES] 如果注释不是加在代码末尾，则注释缩进与被解释的代码缩进一致。

### 1-2-3 括号

1-2-3-1、\[ES] if、for、while、do、case、default后的代码中，就算只有1行代码，也必须加大括号。

正例：
```
if (!isValid) {
    return;
}
```

反例：只有缩进，没有大括号，可读性差，且容易出现逻辑错误。
```
for (uint32_t i = 0; i < size; ++i)
    if (condition)
        count++;
```

1-2-3-2、\[ES] 一次计算出现多个不同优先级的运算符时，通过加括号方式来控制我们需要的运算符执行优先级次序。
说明：开发者对运算符优先级的记忆可能会出错，通过括号控制计算的优先级，一是不容易出错，二是增加代码可读性。

1-2-3-3、\[ES] if、for、while、bool类型函数参数入参等的逻辑表达式中，如果有多个逻辑对象的计算，要恰当的使用小括号，使得逻辑运算的层级关系更清晰、可读性更好。

正例：
```
if ((a > c) || (b > c)) { // 给a>c与b>c这两个逻辑表达式都加一个括号，层级关系更清晰明显
    // do some thing...
}
```

1-2-3-4、\[ES] 除接口类函数空实现外，其他地方请不要留有空的大括号。

反例：
```
if (condition) {

    // do some thing...

} else {
} // 这里留一个空的else分支与空的大括号没有任何意义
```


---
name: data-analysis
label: 数据分析
description: >-
  全面的数据分析技能，支持数据清洗、探索性分析、统计建模、时间序列分析、机器学习和可视化。当用户需要处理数据分析任务时使用此技能，包括：(1)
  从CSV/Excel/JSON/数据库等源加载数据，(2) 清洗和预处理数据，(3) 进行探索性数据分析（统计描述、相关性、分布），(4)
  创建可视化图表和仪表板，(5) 构建统计或机器学习模型，(6) 生成结构化分析报告。适用于数值数据、分类数据、时间序列数据、文本数据和混合数据类型。
version: 1.0.0
author: zhaoxiuquan
---

# 数据分析技能

## 核心能力

### 1. 多源数据加载
- CSV/Excel/JSON 文件读取
- 数据库连接（SQL查询）
- API接口数据获取
- 飞书多维表格导入
- 实时数据流接入

### 2. 数据清洗与预处理
- 缺失值处理（删除、填充、插值）
- 异常值检测和处理
- 数据类型转换
- 重复数据识别
- 数据标准化和归一化
- 特征工程（编码、缩放、创建）

### 3. 探索性数据分析（EDA）
- 统计描述（均值、中位数、标准差、分位数）
- 数据分布可视化
- 相关性分析
- 交叉分析和分组聚合
- 时间序列分解
- 文本数据探索（词频、主题）

### 4. 统计分析
- 描述性统计
- 假设检验（t检验、卡方检验、ANOVA）
- 回归分析（线性、逻辑、多元）
- 时间序列分析（ARIMA、指数平滑）
- 聚类分析（K-means、层次聚类）
- 分类和预测模型

### 5. 数据可视化
- 基础图表（柱状图、折线图、散点图、饼图）
- 高级可视化（热力图、箱线图、小提琴图）
- 交互式图表（Plotly、Bokeh）
- 仪表板创建
- 地理空间可视化

### 6. 报告生成
- 飞书云文档格式报告
- Excel/CSV数据导出
- PDF格式报告
- 交互式HTML报告
- Jupyter Notebook分析

## 系统工作流程

### 阶段1：数据导入与理解
**目标**：理解数据源、数据类型、数据结构和业务背景
**检查点**：
- 数据源类型和格式是否明确？
- 数据维度（行数、列数）是否清楚？
- 各列数据类型和含义是否理解？
- 业务问题和分析目标是否明确？

### 阶段2：数据清洗与整理
**目标**：将原始数据转换为整洁格式，处理质量问题
**检查点**：
- 缺失值是否已识别和处理？
- 异常值是否已检测和处理？
- 数据类型是否正确转换？
- 数据格式是否一致？
- 重复记录是否已处理？

### 阶段3：数据转换与特征工程
**目标**：创建新特征，转换数据以适应分析需求
**检查点**：
- 是否需要创建衍生特征？
- 分类变量是否已编码？
- 数值特征是否已标准化？
- 时间特征是否已提取？
- 文本特征是否已处理？

### 阶段4：探索性分析与可视化
**目标**：发现数据模式、关系和异常
**检查点**：
- 数据分布是否已可视化？
- 变量间关系是否已探索？
- 关键统计指标是否已计算？
- 时间趋势是否已分析？
- 异常模式是否已识别？

### 阶段5：建模与分析
**目标**：应用统计或机器学习方法解决问题
**检查点**：
- 分析方法是否适合业务问题？
- 模型假设是否满足？
- 模型性能是否评估？
- 结果是否可解释？
- 局限性是否明确？

### 阶段6：结果沟通与报告
**目标**：清晰传达分析结果和业务建议
**检查点**：
- 关键发现是否突出？
- 可视化是否有效支持结论？
- 建议是否具体可行？
- 局限性是否明确说明？
- 报告结构是否清晰？

## 分析策略库

### 按数据类型选择方法

#### 数值数据
- **描述性分析**：均值、中位数、标准差、分位数
- **分布分析**：直方图、密度图、Q-Q图
- **相关性分析**：皮尔逊相关系数、散点图矩阵
- **异常检测**：箱线图、Z-score、IQR方法
- **时间序列**：趋势分析、季节性分解、自相关

#### 分类数据
- **频次分析**：计数、百分比、条形图
- **交叉分析**：列联表、堆叠条形图
- **关联分析**：卡方检验、Cramer's V
- **文本分析**：词频统计、词云、主题建模

#### 时间序列数据
- **趋势分析**：移动平均、指数平滑
- **季节性分析**：季节性分解、周期图
- **平稳性检验**：ADF检验、差分处理
- **预测模型**：ARIMA、SARIMA、Prophet

#### 混合数据类型
- **分组分析**：按分类变量分组统计
- **交互效应**：分类变量与数值变量交互
- **多变量分析**：主成分分析、因子分析

### 按业务场景选择路径

#### 销售分析场景
1. 销售数据加载（订单、产品、客户）
2. 销售趋势分析（时间序列）
3. 产品表现分析（分类分析）
4. 客户细分分析（聚类分析）
5. 销售预测（时间序列预测）
6. 建议生成（产品推荐、促销策略）

#### 客户分析场景
1. 客户数据整合（人口统计、行为、交易）
2. 客户细分（RFM分析、聚类）
3. 客户价值分析（LTV计算）
4. 流失预警（分类模型）
5. 个性化推荐（协同过滤）
6. 客户旅程分析（序列分析）

#### 市场分析场景
1. 市场数据收集（竞品、渠道、活动）
2. 市场份额分析（分类分析）
3. 营销效果评估（A/B测试）
4. 渠道归因分析（马尔可夫链）
5. 市场趋势预测（时间序列）
6. 预算优化建议（线性规划）

#### 财务分析场景
1. 财务报表数据提取
2. 财务比率计算
3. 现金流分析（时间序列）
4. 风险评估（波动率分析）
5. 投资组合优化（均值-方差）
6. 财务预测（回归模型）

## 代码规范库

### 数据加载标准代码

#### CSV文件加载
```python
import pandas as pd

# 标准CSV加载
df = pd.read_csv('data.csv', encoding='utf-8')

# 带参数的高级加载
df = pd.read_csv(
    'data.csv',
    encoding='utf-8',
    delimiter=',',
    header=0,
    na_values=['NA', 'null', 'NaN'],
    parse_dates=['date_column']
)
```

#### Excel文件加载
```python
import pandas as pd

# 加载单个sheet
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# 加载多个sheet
excel_file = pd.ExcelFile('data.xlsx')
sheets = {sheet: pd.read_excel(excel_file, sheet_name=sheet) 
          for sheet in excel_file.sheet_names}
```

#### 数据库连接
```python
import pandas as pd
import sqlite3

# SQLite连接
conn = sqlite3.connect('database.db')
df = pd.read_sql_query("SELECT * FROM table_name", conn)
conn.close()

# PostgreSQL连接（需要psycopg2）
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    database="dbname",
    user="user",
    password="password"
)
df = pd.read_sql_query("SELECT * FROM table_name", conn)
conn.close()
```

### 数据清洗标准代码

#### 缺失值处理
```python
import pandas as pd
import numpy as np

# 识别缺失值
missing_counts = df.isnull().sum()
missing_percent = df.isnull().mean() * 100

# 删除缺失值
df_clean = df.dropna()  # 删除任何包含缺失值的行
df_clean = df.dropna(subset=['important_column'])  # 删除特定列的缺失值

# 填充缺失值
df_filled = df.fillna({
    'numeric_column': df['numeric_column'].median(),
    'categorical_column': df['categorical_column'].mode()[0],
    'date_column': df['date_column'].ffill()  # 前向填充
})
```

#### 异常值处理
```python
import numpy as np

# IQR方法识别异常值
Q1 = df['column'].quantile(0.25)
Q3 = df['column'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = df[(df['column'] < lower_bound) | (df['column'] > upper_bound)]

# Z-score方法
from scipy import stats
z_scores = np.abs(stats.zscore(df['column']))
outliers_z = df[z_scores > 3]

# 处理异常值（替换为边界值）
df['column'] = np.where(df['column'] < lower_bound, lower_bound, df['column'])
df['column'] = np.where(df['column'] > upper_bound, upper_bound, df['column'])
```

#### 数据类型转换
```python
# 转换为数值类型
df['numeric_column'] = pd.to_numeric(df['numeric_column'], errors='coerce')

# 转换为日期时间
df['date_column'] = pd.to_datetime(df['date_column'], errors='coerce')

# 转换为分类类型
df['category_column'] = df['category_column'].astype('category')

# 布尔转换
df['bool_column'] = df['bool_column'].map({'Yes': True, 'No': False})
```

### 探索性分析标准代码

#### 统计描述
```python
# 基本统计
desc_stats = df.describe(include='all')

# 分位数
quantiles = df['column'].quantile([0.25, 0.5, 0.75, 0.95, 0.99])

# 偏度和峰度
from scipy.stats import skew, kurtosis
skewness = df['column'].apply(skew)
kurt = df['column'].apply(kurtosis)

# 相关性矩阵
correlation_matrix = df.corr()
```

#### 数据分布可视化
```python
import matplotlib.pyplot as plt
import seaborn as sns

# 直方图
plt.figure(figsize=(10, 6))
sns.histplot(df['column'], kde=True, bins=30)
plt.title('Distribution of Column')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.show()

# 箱线图
plt.figure(figsize=(8, 6))
sns.boxplot(data=df, x='category_column', y='numeric_column')
plt.title('Box Plot by Category')
plt.xticks(rotation=45)
plt.show()

# 散点图矩阵
sns.pairplot(df[['col1', 'col2', 'col3', 'col4']])
plt.suptitle('Pair Plot of Numerical Columns', y=1.02)
plt.show()
```

### 时间序列分析代码

```python
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

# 设置时间索引
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# 重采样（日到月）
monthly_data = df['value'].resample('M').mean()

# 时间序列分解
decomposition = seasonal_decompose(monthly_data, model='additive', period=12)

# 绘制分解结果
fig, axes = plt.subplots(4, 1, figsize=(12, 10))
decomposition.observed.plot(ax=axes[0], title='Observed')
decomposition.trend.plot(ax=axes[1], title='Trend')
decomposition.seasonal.plot(ax=axes[2], title='Seasonal')
decomposition.resid.plot(ax=axes[3], title='Residual')
plt.tight_layout()
plt.show()
```

### 机器学习建模代码

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

# 回归问题示例
# 准备数据
X = df.drop('target', axis=1)
y = df['target']

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 训练模型
model = LinearRegression()
model.fit(X_train_scaled, y_train)

# 预测和评估
y_pred = model.predict(X_test_scaled)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# 分类问题示例
classifier = RandomForestClassifier(n_estimators=100, random_state=42)
classifier.fit(X_train_scaled, y_train)
y_pred_class = classifier.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred_class)
report = classification_report(y_test, y_pred_class)
```

## 质量检查清单

### 分析过程自检（10条）
1. 数据源和业务目标是否明确？
2. 数据质量和完整性是否已评估？
3. 分析方法是否适合数据类型和问题？
4. 统计假设是否已检验？
5. 异常值和缺失值是否已合理处理？
6. 特征工程是否充分考虑了业务逻辑？
7. 模型选择是否有理论依据？
8. 模型性能是否在独立测试集上验证？
9. 结果是否可解释和可操作？
10. 局限性和假设是否明确说明？

### 报告交付自检（6条）
1. 报告结构是否清晰（问题→方法→结果→建议）？
2. 关键发现是否突出显示？
3. 可视化是否有效支持结论？
4. 技术细节是否适当详细？
5. 业务建议是否具体可行？
6. 是否有明确的后续步骤？

### 反模式清单（10条）
1. **数据泄漏**：在特征工程或预处理中使用测试集信息
2. **过拟合**：模型在训练集表现完美但测试集差
3. **多重共线性**：特征间高度相关导致模型不稳定
4. **样本不平衡**：分类问题中类别分布严重不均衡
5. **幸存者偏差**：只分析成功案例忽略失败案例
6. **相关≠因果**：错误解释相关关系为因果关系
7. **p-hacking**：多次测试直到获得显著结果
8. **忽略时间依赖**：时间序列数据中使用未来信息
9. **过度工程化**：创建过多无业务意义的特征
10. **缺乏基准**：没有与简单基准模型比较

## Few-shot示例

### 示例1：销售数据分析

**用户查询**："分析这份销售数据，找出最畅销的产品类别和月度趋势"

**分析过程**：
1. 加载CSV销售数据
2. 检查数据质量（缺失值、异常值）
3. 按产品类别聚合销售额
4. 计算月度销售趋势
5. 创建可视化图表
6. 生成分析报告

**代码实现**：
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 加载数据
sales_df = pd.read_csv('sales_data.csv', parse_dates=['order_date'])

# 2. 数据清洗
sales_df = sales_df.dropna(subset=['product_category', 'sales_amount'])
sales_df['month'] = sales_df['order_date'].dt.to_period('M')

# 3. 按类别聚合
category_sales = sales_df.groupby('product_category')['sales_amount'].sum().sort_values(ascending=False)

# 4. 月度趋势
monthly_sales = sales_df.groupby('month')['sales_amount'].sum()

# 5. 可视化
fig, axes = plt.subplots(2, 1, figsize=(12, 10))

# 畅销类别
sns.barplot(x=category_sales.index[:10], y=category_sales.values[:10], ax=axes[0])
axes[0].set_title('Top 10 Product Categories by Sales')
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=45)

# 月度趋势
monthly_sales.plot(ax=axes[1], marker='o')
axes[1].set_title('Monthly Sales Trend')
axes[1].set_xlabel('Month')
axes[1].set_ylabel('Sales Amount')

plt.tight_layout()
plt.show()

# 6. 生成报告
print(f"总销售额: ${sales_df['sales_amount'].sum():,.2f}")
print(f"最畅销类别: {category_sales.index[0]} (${category_sales.iloc[0]:,.2f})")
print(f"月度平均增长: {monthly_sales.pct_change().mean():.2%}")
```

**报告输出**：
- 关键发现：电子产品类别贡献了45%的总销售额
- 趋势：销售额在11月达到峰值（黑色星期五促销）
- 建议：增加电子产品的库存，并在旺季前加强营销
- 局限性：数据仅包含过去12个月，无法分析长期趋势

### 示例2：客户流失分析

**用户查询**："分析客户数据，预测哪些客户可能流失"

**分析过程**：
1. 加载客户数据（人口统计、交易、交互）
2. 定义流失标签（90天无交易）
3. 特征工程（RFM特征、行为特征）
4. 构建分类模型（逻辑回归、随机森林）
5. 评估模型性能
6. 识别高风险客户特征

**代码实现**：
```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import shap

# 1. 加载和准备数据
customers = pd.read_csv('customer_data.csv', parse_dates=['last_transaction_date'])

# 2. 定义流失
current_date = customers['last_transaction_date'].max()
customers['days_since_last'] = (current_date - customers['last_transaction_date']).dt.days
customers['churn'] = (customers['days_since_last'] > 90).astype(int)

# 3. 特征工程
features = ['age', 'income', 'tenure_months', 'total_spent', 
            'transaction_count', 'avg_transaction_value', 
            'days_since_last', 'support_tickets']

X = customers[features]
y = customers['churn']

# 4. 划分数据集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 5. 训练模型
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# 6. 评估
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

print("Classification Report:")
print(classification_report(y_test, y_pred))
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")

# 7. 特征重要性
importances = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 5 Important Features:")
print(importances.head())
```

**报告输出**：
- 关键发现：模型准确率85%，最重要的流失预测因子是"days_since_last"
- 高风险特征：超过60天无交易、支持工单数量多、交易频率低
- 建议：针对高风险客户实施保留计划（个性化优惠、主动联系）
- 业务价值：减少10%流失率可增加$500K年收入
- 局限性：模型基于历史数据，需要定期重新训练

## 资源文件说明

### scripts/ 目录
包含可执行的数据分析脚本，如：
- `data_cleaning.py`: 数据清洗自动化脚本
- `feature_engineering.py`: 特征工程模板
- `model_training.py`: 模型训练和评估脚本
- `report_generator.py`: 报告生成脚本

### references/ 目录
包含参考文档：
- `statistical_methods.md`: 统计方法选择指南
- `visualization_guide.md`: 可视化最佳实践
- `model_selection.md`: 模型选择标准
- `business_context.md`: 常见业务场景分析框架

### assets/ 目录
包含模板和资源：
- `report_template.docx`: 报告模板
- `dashboard_template.html`: 仪表板HTML模板
- `color_palettes.json`: 可视化配色方案
- `sample_datasets/`: 示例数据集

---

## 使用提示

1. **明确业务目标**：在开始分析前，确保理解用户的具体需求和业务背景
2. **逐步验证**：每个分析阶段结束后进行质量检查
3. **保持透明**：明确说明分析假设、局限性和不确定性
4. **关注可操作性**：确保分析结果能转化为具体的业务建议
5. **持续学习**：根据反馈不断优化分析方法和报告质量

**触发场景关键词**：数据分析、数据清洗、探索性分析、统计建模、机器学习、可视化、报告生成、销售分析、客户分析、市场分析、财务分析、时间序列、预测模型。

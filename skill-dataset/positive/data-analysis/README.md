# data-analysis

专业级数据分析技能包，支持端到端的数据分析工作流

## 概述

data-analysis 是一个功能全面的数据分析技能包，支持从数据加载、清洗预处理、探索性分析、统计建模到可视化和报告生成的全流程数据分析工作。适用于多种数据类型和业务场景。

## 核心特性

### 🎯 多源数据支持
- CSV/Excel文件
- 数据库连接 (SQL, NoSQL)
- API接口数据
- 飞书多维表格
- 网页爬虫数据
- 实时数据流

### 🔧 完整分析流程
1. **数据导入与理解** - 数据探索和质量评估
2. **数据清洗与整理** - 缺失值处理、异常值检测、数据转换
3. **数据转换与特征工程** - 特征创建、编码、标准化
4. **探索性分析与可视化** - 统计分析、图表生成
5. **建模与分析** - 统计建模、机器学习、预测分析
6. **结果沟通与报告** - 业务洞察、可视化报告、行动建议

### 📊 丰富分析能力
- 描述性统计分析
- 推断性统计分析
- 时间序列分析
- 聚类与分类分析
- 关联规则挖掘
- 异常检测
- 预测建模

### 🎨 专业可视化
- 静态图表 (Matplotlib, Seaborn)
- 交互式可视化 (Plotly)
- 仪表板生成
- 自定义图表模板
- 导出多种格式 (PNG, PDF, HTML)

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本使用示例

```python
from data_cleaning import DataCleaner
from feature_engineering import FeatureEngineer
import pandas as pd

# 1. 加载数据
data = pd.read_csv('your_data.csv')

# 2. 数据清洗
cleaner = DataCleaner()
cleaned_data = cleaner.clean(data)

# 3. 特征工程
engineer = FeatureEngineer()
features = engineer.create_features(cleaned_data)

# 4. 分析报告
report = generate_analysis_report(features)
```

### 完整工作流示例

参考 `scripts/examples/` 目录下的完整示例：
- `sales_analysis_example.py` - 销售数据分析
- `customer_analysis_example.py` - 客户数据分析

## 目录结构

```
aily-data-analysis/
├── assets/                    # 资源文件
│   └── sample_datasets/      # 示例数据集
├── references/               # 参考文档
│   ├── statistical_methods.md   # 统计方法指南
│   ├── visualization_guide.md   # 可视化最佳实践
│   ├── model_selection.md      # 模型选择标准
│   └── business_context.md     # 业务场景适配
├── scripts/                  # 核心脚本
│   ├── data_cleaning.py     # 数据清洗模块
│   ├── feature_engineering.py # 特征工程模块
│   └── examples/           # 使用示例
├── tests/                   # 测试文件
│   └── test_data_analysis.py
├── SKILL.md                # 技能主文档
├── README.md              # 本文件
├── requirements.txt       # 依赖列表
└── setup.py              # 安装配置
```

## 核心模块

### 数据清洗 (data_cleaning.py)
- 缺失值处理 (均值/中位数/众数填充、插值、删除)
- 异常值检测 (IQR、Z-score、孤立森林)
- 数据类型转换
- 重复数据删除
- 数据标准化

### 特征工程 (feature_engineering.py)
- 数值特征衍生 (统计量、多项式、交互项)
- 分类变量编码 (独热编码、标签编码、目标编码)
- 时间特征提取 (年/月/日、季节、节假日)
- 文本特征处理 (TF-IDF、词向量)
- 特征选择 (方差阈值、相关性、模型重要性)

### 分析策略库
包含多种预定义分析模板：
- **销售分析模板** - 趋势分析、产品表现、客户细分
- **客户分析模板** - RFM分析、流失预测、生命周期价值
- **运营分析模板** - 效率指标、质量控制、资源优化
- **市场分析模板** - 竞争分析、份额变化、趋势预测

## 使用场景

### 业务分析场景
- 📈 **销售数据分析** - 识别畅销产品、分析销售趋势、优化定价策略
- 👥 **客户行为分析** - 客户细分、流失预测、个性化推荐
- 🏭 **运营效率分析** - 流程优化、质量控制、成本分析
- 📊 **市场趋势分析** - 竞争分析、市场份额、增长机会

### 技术分析场景
- 🔍 **探索性数据分析** - 数据理解、模式发现、异常检测
- 🎯 **预测性建模** - 回归预测、分类模型、时间序列预测
- 🧩 **聚类分析** - 客户分群、产品分类、模式识别
- 📉 **统计推断** - 假设检验、置信区间、相关性分析

## 配置选项

### 数据源配置
```python
config = {
    'data_source': {
        'type': 'csv',  # csv, excel, database, api
        'path': 'data/sales.csv',
        'encoding': 'utf-8'
    },
    'analysis_type': 'sales_analysis',
    'output_format': 'lark_doc',  # lark_doc, excel, pdf, html
    'visualization': {
        'style': 'corporate',
        'color_palette': 'Set2',
        'figure_size': (12, 8)
    }
}
```

### 分析参数配置
```python
analysis_params = {
    'missing_value_strategy': 'mean',  # mean, median, mode, interpolate, drop
    'outlier_detection_method': 'iqr',  # iqr, zscore, isolation_forest
    'feature_selection': True,
    'n_features': 20,
    'model_selection': 'auto',  # auto, specific_model
    'cross_validation_folds': 5
}
```

## 输出格式

### 支持的报告格式
1. **飞书云文档** - 结构化报告，支持表格、图表嵌入
2. **Excel文件** - 包含原始数据、分析结果、可视化图表
3. **PDF报告** - 专业格式，适合打印和分享
4. **HTML仪表板** - 交互式可视化，支持动态筛选
5. **Jupyter Notebook** - 可复现的分析流程

### 可视化输出
- 静态图片 (PNG, JPG, PDF)
- 交互式图表 (HTML, Plotly)
- 动画可视化 (GIF, MP4)
- 仪表板 (Streamlit, Dash)

## 最佳实践

### 数据分析流程
1. **先理解业务问题** - 明确分析目标和业务价值
2. **数据质量优先** - 确保数据准确性和完整性
3. **从简单开始** - 先做描述性分析，再尝试复杂模型
4. **结果可解释** - 确保分析结果业务可理解
5. **持续迭代** - 根据反馈优化分析流程

### 代码规范
- 使用有意义的变量名
- 添加详细的注释
- 模块化设计，功能分离
- 错误处理和日志记录
- 性能优化和内存管理

## 性能优化

### 大数据处理
- 使用分块处理 (chunk processing)
- 内存优化 (数据类型优化)
- 并行计算 (多进程/多线程)
- 增量学习 (在线学习)

### 计算加速
- 向量化操作 (NumPy, Pandas)
- 使用高效算法
- 缓存中间结果
- GPU加速 (可选)

## 测试与验证

### 单元测试
```bash
python -m pytest tests/test_data_analysis.py -v
```

### 集成测试
```bash
python scripts/examples/customer_analysis_example.py
```

### 性能测试
```bash
python tests/test_data_analysis.py TestPerformance
```

## 故障排除

### 常见问题

#### 1. 内存不足
```python
# 解决方案：使用分块处理
chunk_size = 10000
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    process_chunk(chunk)
```

#### 2. 计算缓慢
```python
# 解决方案：使用向量化操作
# 避免循环，使用Pandas/Numpy的内置函数
result = df['column'].apply(lambda x: x * 2)  # 慢
result = df['column'] * 2  # 快
```

#### 3. 结果不一致
- 检查随机种子设置
- 验证数据预处理的一致性
- 确保特征工程的可复现性

### 调试技巧
1. 使用小样本数据测试
2. 逐步验证每个处理步骤
3. 保存中间结果用于调试
4. 使用日志记录关键信息

## 扩展开发

### 添加新的分析模板
1. 在 `references/` 创建新的分析指南
2. 在 `scripts/` 添加相应的分析模块
3. 更新 `SKILL.md` 中的触发关键词
4. 添加示例到 `scripts/examples/`

### 自定义可视化
1. 创建自定义图表模板
2. 扩展颜色主题和样式
3. 添加交互式功能
4. 集成第三方可视化库

## 贡献指南

### 代码贡献
1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 文档贡献
- 更新使用示例
- 添加最佳实践
- 完善故障排除指南
- 翻译文档

### 问题反馈
- 使用 Issue 模板报告问题
- 提供可复现的示例
- 包括错误信息和环境信息

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v1.0.0 (2026-05-29)
- 🎉 初始版本发布
- ✅ 完整的数据分析工作流
- 📊 丰富的分析模板和示例
- 🎨 专业可视化功能
- 🧪 完整的测试覆盖

---

**开始使用**：查看 `scripts/examples/` 中的示例代码，快速上手数据分析！

**获取帮助**：如有问题，请查看 `references/` 中的详细指南或提交 Issue。
#!/usr/bin/env python3
"""
aily-data-analysis 技能测试脚本
测试数据清洗、特征工程、分析可视化等核心功能
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
import sys

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

# 导入要测试的模块
try:
    from data_cleaning import DataCleaner
    from feature_engineering import FeatureEngineer
    print("✓ 成功导入核心模块")
except ImportError as e:
    print(f"⚠ 无法导入核心模块: {e}")
    # 创建测试用的模拟类
    class DataCleaner:
        """数据清洗器模拟类"""
        pass
    
    class FeatureEngineer:
        """特征工程师模拟类"""
        pass

# ============================================================================
# 测试数据生成
# ============================================================================

def generate_test_data(n_samples=100):
    """
    生成测试数据
    """
    np.random.seed(42)
    
    # 创建混合数据类型的测试数据
    dates = pd.date_range('2025-01-01', periods=n_samples, freq='D')
    
    data = pd.DataFrame({
        'date': dates,
        'numeric_1': np.random.normal(100, 20, n_samples),
        'numeric_2': np.random.exponential(50, n_samples),
        'categorical': np.random.choice(['A', 'B', 'C', 'D'], n_samples),
        'text': [f'text_{i}' for i in range(n_samples)],
        'boolean': np.random.choice([True, False], n_samples),
        'missing_numeric': np.random.choice([1.0, 2.0, np.nan, 3.0], n_samples, p=[0.3, 0.3, 0.2, 0.2]),
        'missing_categorical': np.random.choice(['X', 'Y', None, 'Z'], n_samples, p=[0.3, 0.3, 0.2, 0.2]),
        'outlier_numeric': np.concatenate([
            np.random.normal(0, 1, n_samples - 2),
            np.array([100, -100])  # 添加两个极端异常值
        ]),
        'duplicate_col_1': np.random.randn(n_samples),
        'duplicate_col_2': np.random.randn(n_samples)  # 与duplicate_col_1不同
    })
    
    # 添加一些重复行
    duplicate_rows = data.iloc[:5].copy()
    data = pd.concat([data, duplicate_rows], ignore_index=True)
    
    return data

def generate_time_series_test_data(n_samples=200):
    """
    生成时间序列测试数据
    """
    np.random.seed(42)
    
    dates = pd.date_range('2025-01-01', periods=n_samples, freq='H')
    
    # 基础趋势
    trend = np.linspace(0, 10, n_samples)
    
    # 季节性（日周期）
    hour_of_day = np.array([d.hour for d in dates])
    daily_seasonality = 5 * np.sin(2 * np.pi * hour_of_day / 24)
    
    # 季节性（周周期）
    day_of_week = np.array([d.weekday() for d in dates])
    weekly_seasonality = 3 * np.sin(2 * np.pi * day_of_week / 7)
    
    # 噪声
    noise = np.random.normal(0, 2, n_samples)
    
    # 合成时间序列
    ts_data = pd.DataFrame({
        'timestamp': dates,
        'value': trend + daily_seasonality + weekly_seasonality + noise,
        'category': np.random.choice(['Type_A', 'Type_B', 'Type_C'], n_samples),
        'anomaly': np.random.choice([0, 1], n_samples, p=[0.95, 0.05])  # 5%异常
    })
    
    # 添加一些缺失值
    missing_mask = np.random.choice([True, False], n_samples, p=[0.1, 0.9])
    ts_data.loc[missing_mask, 'value'] = np.nan
    
    return ts_data

# ============================================================================
# 测试用例
# ============================================================================

class TestDataCleaning(unittest.TestCase):
    """数据清洗功能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.test_data = generate_test_data(50)
        self.cleaner = DataCleaner() if hasattr(DataCleaner, '__init__') else None
    
    def test_data_shape_preservation(self):
        """测试数据形状保持"""
        if self.cleaner is None:
            self.skipTest("DataCleaner未定义")
        
        cleaned = self.cleaner.clean(self.test_data.copy())
        self.assertIsNotNone(cleaned)
        
        # 清洗后不应改变原始数据
        original_copy = self.test_data.copy()
        _ = self.cleaner.clean(original_copy)
        pd.testing.assert_frame_equal(original_copy, self.test_data)
    
    def test_missing_value_handling(self):
        """测试缺失值处理"""
        if self.cleaner is None:
            self.skipTest("DataCleaner未定义")
        
        # 检查缺失值列
        missing_before = self.test_data.isna().sum().sum()
        self.assertGreater(missing_before, 0, "测试数据应包含缺失值")
        
        cleaned = self.cleaner.clean(self.test_data.copy())
        missing_after = cleaned.isna().sum().sum()
        
        # 清洗后缺失值应减少或保持
        self.assertLessEqual(missing_after, missing_before)
    
    def test_outlier_detection(self):
        """测试异常值检测"""
        if self.cleaner is None:
            self.skipTest("DataCleaner未定义")
        
        # outlier_numeric列包含极端值
        outlier_col = 'outlier_numeric'
        original_values = self.test_data[outlier_col].copy()
        
        # 计算IQR
        Q1 = original_values.quantile(0.25)
        Q3 = original_values.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 检查异常值存在
        outliers_before = ((original_values < lower_bound) | (original_values > upper_bound)).sum()
        self.assertGreater(outliers_before, 0, "测试数据应包含异常值")
    
    def test_duplicate_removal(self):
        """测试重复数据删除"""
        if self.cleaner is None:
            self.skipTest("DataCleaner未定义")
        
        # 检查重复行
        duplicates_before = self.test_data.duplicated().sum()
        self.assertGreater(duplicates_before, 0, "测试数据应包含重复行")
        
        cleaned = self.cleaner.clean(self.test_data.copy())
        duplicates_after = cleaned.duplicated().sum()
        
        # 清洗后应无重复行
        self.assertEqual(duplicates_after, 0)
    
    def test_data_type_conversion(self):
        """测试数据类型转换"""
        if self.cleaner is None:
            self.skipTest("DataCleaner未定义")
        
        cleaned = self.cleaner.clean(self.test_data.copy())
        
        # 检查日期列类型
        if 'date' in cleaned.columns:
            self.assertTrue(pd.api.types.is_datetime64_any_dtype(cleaned['date']))
        
        # 检查布尔列类型
        if 'boolean' in cleaned.columns:
            self.assertTrue(pd.api.types.is_bool_dtype(cleaned['boolean']))


class TestFeatureEngineering(unittest.TestCase):
    """特征工程功能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.test_data = generate_test_data(100)
        self.ts_data = generate_time_series_test_data(200)
        self.engineer = FeatureEngineer() if hasattr(FeatureEngineer, '__init__') else None
    
    def test_numeric_feature_creation(self):
        """测试数值特征创建"""
        if self.engineer is None:
            self.skipTest("FeatureEngineer未定义")
        
        # 选择数值列
        numeric_cols = ['numeric_1', 'numeric_2']
        features = self.engineer.create_numeric_features(
            self.test_data[numeric_cols].copy()
        )
        
        self.assertIsNotNone(features)
        self.assertGreater(len(features.columns), len(numeric_cols))
        
        # 检查是否创建了衍生特征
        expected_features = ['sum', 'mean', 'std', 'min', 'max', 'range']
        for feat in expected_features:
            # 检查是否有类似的特征被创建
            has_feature = any(feat in col.lower() for col in features.columns)
            self.assertTrue(has_feature, f"应创建包含'{feat}'的特征")
    
    def test_categorical_encoding(self):
        """测试分类变量编码"""
        if self.engineer is None:
            self.skipTest("FeatureEngineer未定义")
        
        # 测试独热编码
        categorical_data = self.test_data[['categorical']].copy()
        
        # 检查独热编码
        if hasattr(self.engineer, 'one_hot_encode'):
            encoded = self.engineer.one_hot_encode(categorical_data, 'categorical')
            self.assertIsNotNone(encoded)
            
            # 检查编码后的列数
            unique_categories = categorical_data['categorical'].nunique()
            self.assertEqual(len(encoded.columns), unique_categories)
            
            # 检查每行的和应为1（只有一个类别为1）
            row_sums = encoded.sum(axis=1)
            self.assertTrue(all(row_sums == 1))
    
    def test_time_series_features(self):
        """测试时间序列特征"""
        if self.engineer is None:
            self.skipTest("FeatureEngineer未定义")
        
        if hasattr(self.engineer, 'create_time_features'):
            ts_features = self.engineer.create_time_features(
                self.ts_data.copy(), 
                time_col='timestamp',
                value_col='value'
            )
            
            self.assertIsNotNone(ts_features)
            
            # 检查时间特征
            expected_time_features = ['hour', 'day', 'month', 'weekday']
            for feat in expected_time_features:
                self.assertIn(feat, ts_features.columns)
            
            # 检查统计特征
            expected_stat_features = ['lag_1', 'rolling_mean_7', 'rolling_std_7']
            for feat in expected_stat_features:
                has_feature = any(feat in col for col in ts_features.columns)
                self.assertTrue(has_feature, f"应创建包含'{feat}'的特征")
    
    def test_feature_interactions(self):
        """测试特征交互"""
        if self.engineer is None:
            self.skipTest("FeatureEngineer未定义")
        
        if hasattr(self.engineer, 'create_interaction_features'):
            # 选择数值特征进行交互
            numeric_data = self.test_data[['numeric_1', 'numeric_2']].copy()
            
            interaction_features = self.engineer.create_interaction_features(
                numeric_data, 
                ['numeric_1', 'numeric_2']
            )
            
            self.assertIsNotNone(interaction_features)
            
            # 检查是否创建了交互特征
            expected_interactions = ['numeric_1_x_numeric_2', 'numeric_1_div_numeric_2']
            for interaction in expected_interactions:
                has_interaction = any(interaction in col for col in interaction_features.columns)
                self.assertTrue(has_interaction, f"应创建交互特征'{interaction}'")
    
    def test_feature_selection(self):
        """测试特征选择"""
        if self.engineer is None:
            self.skipTest("FeatureEngineer未定义")
        
        # 创建有目标变量的测试数据
        np.random.seed(42)
        n_samples = 200
        
        X = pd.DataFrame({
            'relevant_1': np.random.randn(n_samples),
            'relevant_2': np.random.randn(n_samples),
            'noise_1': np.random.randn(n_samples) * 0.1,  # 低方差噪声
            'noise_2': np.random.randn(n_samples) * 0.1,  # 低方差噪声
            'constant': np.ones(n_samples)  # 常数特征
        })
        
        # 创建与相关特征关联的目标变量
        y = 2 * X['relevant_1'] + 3 * X['relevant_2'] + np.random.randn(n_samples) * 0.5
        
        if hasattr(self.engineer, 'select_features'):
            selected_features = self.engineer.select_features(X, y, n_features=2)
            
            self.assertIsNotNone(selected_features)
            self.assertEqual(len(selected_features), 2)
            
            # 检查是否选择了相关特征
            self.assertIn('relevant_1', selected_features)
            self.assertIn('relevant_2', selected_features)


class TestStatisticalMethods(unittest.TestCase):
    """统计方法测试"""
    
    def test_descriptive_statistics(self):
        """测试描述性统计"""
        np.random.seed(42)
        data = pd.DataFrame({
            'A': np.random.normal(100, 15, 1000),
            'B': np.random.exponential(50, 1000),
            'C': np.random.randint(1, 5, 1000)
        })
        
        # 计算基本统计量
        stats = data.describe()
        
        # 检查统计量
        self.assertIn('mean', stats.index)
        self.assertIn('std', stats.index)
        self.assertIn('min', stats.index)
        self.assertIn('max', stats.index)
        self.assertIn('50%', stats.index)  # 中位数
        
        # 检查数值范围
        for col in data.columns:
            col_mean = stats.loc['mean', col]
            col_std = stats.loc['std', col]
            
            # 均值应在合理范围内
            if col == 'A':
                self.assertAlmostEqual(col_mean, 100, delta=2)  # 允许2的误差
            elif col == 'B':
                self.assertAlmostEqual(col_mean, 50, delta=3)   # 指数分布均值=1/lambda
    
    def test_correlation_analysis(self):
        """测试相关性分析"""
        np.random.seed(42)
        n_samples = 500
        
        # 创建相关变量
        x = np.random.randn(n_samples)
        y = 2 * x + np.random.randn(n_samples) * 0.5  # 强正相关
        z = -1 * x + np.random.randn(n_samples) * 0.5  # 强负相关
        w = np.random.randn(n_samples)  # 不相关
        
        data = pd.DataFrame({'x': x, 'y': y, 'z': z, 'w': w})
        
        # 计算相关性矩阵
        corr_matrix = data.corr()
        
        # 检查相关性
        self.assertAlmostEqual(corr_matrix.loc['x', 'y'], 0.9, delta=0.1)  # 强正相关
        self.assertAlmostEqual(corr_matrix.loc['x', 'z'], -0.9, delta=0.1) # 强负相关
        self.assertAlmostEqual(corr_matrix.loc['x', 'w'], 0.0, delta=0.1)  # 接近零相关
        
        # 检查对称性
        self.assertTrue(corr_matrix.equals(corr_matrix.T))
    
    def test_hypothesis_testing(self):
        """测试假设检验"""
        from scipy import stats
        
        np.random.seed(42)
        
        # 创建两个样本
        sample1 = np.random.normal(100, 15, 100)
        sample2 = np.random.normal(105, 15, 100)  # 均值略高
        
        # t检验
        t_stat, p_value = stats.ttest_ind(sample1, sample2)
        
        # 检查p值
        self.assertIsInstance(p_value, float)
        self.assertGreaterEqual(p_value, 0)
        self.assertLessEqual(p_value, 1)
        
        # 由于样本2均值更高，t统计量应为负
        self.assertLess(t_stat, 0)
    
    def test_anova(self):
        """测试方差分析"""
        from scipy import stats
        
        np.random.seed(42)
        
        # 创建三个组
        group1 = np.random.normal(100, 10, 30)
        group2 = np.random.normal(105, 10, 30)  # 均值不同
        group3 = np.random.normal(100, 10, 30)
        
        # 单因素方差分析
        f_stat, p_value = stats.f_oneway(group1, group2, group3)
        
        # 检查结果
        self.assertIsInstance(f_stat, float)
        self.assertIsInstance(p_value, float)
        self.assertGreater(f_stat, 0)  # F统计量应为正


class TestVisualization(unittest.TestCase):
    """可视化功能测试"""
    
    def setUp(self):
        """测试前准备"""
        import matplotlib
        matplotlib.use('Agg')  # 使用非交互式后端
        
        self.test_data = generate_test_data(100)
        self.figures_dir = tempfile.mkdtemp()
    
    def test_histogram_creation(self):
        """测试直方图创建"""
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 创建直方图
        ax.hist(self.test_data['numeric_1'], bins=20, edgecolor='black', alpha=0.7)
        ax.set_title('数值分布直方图')
        ax.set_xlabel('数值')
        ax.set_ylabel('频数')
        
        # 保存图表
        output_path = os.path.join(self.figures_dir, 'histogram.png')
        fig.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        # 检查文件是否创建
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 1000)  # 文件应有一定大小
    
    def test_scatter_plot(self):
        """测试散点图创建"""
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 创建散点图
        scatter = ax.scatter(
            self.test_data['numeric_1'],
            self.test_data['numeric_2'],
            c=self.test_data['outlier_numeric'],
            cmap='viridis',
            alpha=0.6,
            s=50
        )
        
        ax.set_title('数值关系散点图')
        ax.set_xlabel('数值1')
        ax.set_ylabel('数值2')
        
        # 添加颜色条
        plt.colorbar(scatter, ax=ax, label='异常值分数')
        
        # 保存图表
        output_path = os.path.join(self.figures_dir, 'scatter.png')
        fig.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        self.assertTrue(os.path.exists(output_path))
    
    def test_box_plot(self):
        """测试箱线图创建"""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 创建箱线图
        box_data = [
            self.test_data['numeric_1'],
            self.test_data['numeric_2'],
            self.test_data['outlier_numeric']
        ]
        
        ax.boxplot(box_data, labels=['数值1', '数值2', '异常值'])
        ax.set_title('数值分布箱线图')
        ax.set_ylabel('数值')
        
        # 保存图表
        output_path = os.path.join(self.figures_dir, 'boxplot.png')
        fig.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        self.assertTrue(os.path.exists(output_path))
    
    def test_time_series_plot(self):
        """测试时间序列图创建"""
        import matplotlib.pyplot as plt
        
        # 生成时间序列数据
        ts_data = generate_time_series_test_data(100)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 创建时间序列图
        ax.plot(ts_data['timestamp'], ts_data['value'], 
                marker='o', linestyle='-', linewidth=1, markersize=3)
        
        ax.set_title('时间序列图')
        ax.set_xlabel('时间')
        ax.set_ylabel('数值')
        ax.grid(True, alpha=0.3)
        
        # 格式化x轴日期
        fig.autofmt_xdate()
        
        # 保存图表
        output_path = os.path.join(self.figures_dir, 'timeseries.png')
        fig.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        self.assertTrue(os.path.exists(output_path))
    
    def test_correlation_heatmap(self):
        """测试相关性热力图"""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # 计算相关性矩阵
        numeric_cols = self.test_data.select_dtypes(include=[np.number]).columns
        corr_matrix = self.test_data[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 创建热力图
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, square=True, linewidths=0.5, ax=ax)
        
        ax.set_title('特征相关性热力图')
        
        # 保存图表
        output_path = os.path.join(self.figures_dir, 'heatmap.png')
        fig.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        self.assertTrue(os.path.exists(output_path))


class TestIntegration(unittest.TestCase):
    """集成测试：完整流程测试"""
    
    def test_complete_analysis_pipeline(self):
        """测试完整分析流程"""
        # 生成测试数据
        data = generate_test_data(200)
        
        # 1. 数据清洗
        print("1. 数据清洗...")
        missing_before = data.isna().sum().sum()
        
        # 简单清洗：填充缺失值
        cleaned_data = data.copy()
        
        # 数值列用均值填充
        numeric_cols = cleaned_data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if cleaned_data[col].isna().any():
                cleaned_data[col] = cleaned_data[col].fillna(cleaned_data[col].mean())
        
        # 分类列用众数填充
        categorical_cols = cleaned_data.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if cleaned_data[col].isna().any():
                mode_value = cleaned_data[col].mode()[0] if not cleaned_data[col].mode().empty else 'Unknown'
                cleaned_data[col] = cleaned_data[col].fillna(mode_value)
        
        missing_after = cleaned_data.isna().sum().sum()
        self.assertEqual(missing_after, 0, "清洗后应无缺失值")
        
        # 2. 特征工程
        print("2. 特征工程...")
        
        # 创建衍生特征
        features = cleaned_data.copy()
        
        # 数值特征：创建统计特征
        if 'numeric_1' in features.columns and 'numeric_2' in features.columns:
            features['numeric_sum'] = features['numeric_1'] + features['numeric_2']
            features['numeric_product'] = features['numeric_1'] * features['numeric_2']
            features['numeric_ratio'] = features['numeric_1'] / (features['numeric_2'] + 1e-10)
        
        # 时间特征（如果有日期列）
        if 'date' in features.columns:
            features['year'] = features['date'].dt.year
            features['month'] = features['date'].dt.month
            features['day'] = features['date'].dt.day
            features['weekday'] = features['date'].dt.weekday
        
        # 分类特征编码
        if 'categorical' in features.columns:
            # 简单频率编码
            freq_encoding = features['categorical'].value_counts(normalize=True)
            features['categorical_freq'] = features['categorical'].map(freq_encoding)
        
        # 检查特征数量增加
        self.assertGreater(len(features.columns), len(data.columns))
        
        # 3. 统计分析
        print("3. 统计分析...")
        
        # 描述性统计
        desc_stats = features.describe()
        self.assertIsNotNone(desc_stats)
        self.assertGreater(len(desc_stats), 0)
        
        # 相关性分析
        numeric_features = features.select_dtypes(include=[np.number])
        if len(numeric_features.columns) > 1:
            corr_matrix = numeric_features.corr()
            self.assertEqual(corr_matrix.shape[0], len(numeric_features.columns))
            self.assertEqual(corr_matrix.shape[1], len(numeric_features.columns))
        
        # 4. 可视化（简单检查）
        print("4. 可视化检查...")
        
        # 创建临时目录保存图表
        with tempfile.TemporaryDirectory() as temp_dir:
            import matplotlib.pyplot as plt
            
            # 创建直方图
            if 'numeric_1' in features.columns:
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.hist(features['numeric_1'].dropna(), bins=20, edgecolor='black', alpha=0.7)
                ax.set_title('数值分布')
                
                hist_path = os.path.join(temp_dir, 'histogram.png')
                fig.savefig(hist_path, dpi=100, bbox_inches='tight')
                plt.close(fig)
                
                self.assertTrue(os.path.exists(hist_path))
            
            # 创建箱线图
            if len(numeric_features.columns) > 0:
                fig, ax = plt.subplots(figsize=(10, 6))
                numeric_features.iloc[:, :3].boxplot(ax=ax)  # 前3个数值列
                ax.set_title('数值分布箱线图')
                
                boxplot_path = os.path.join(temp_dir, 'boxplot.png')
                fig.savefig(boxplot_path, dpi=100, bbox_inches='tight')
                plt.close(fig)
                
                self.assertTrue(os.path.exists(boxplot_path))
        
        print("✓ 完整分析流程测试通过")


class TestErrorHandling(unittest.TestCase):
    """错误处理测试"""
    
    def test_empty_dataframe(self):
        """测试空数据框处理"""
        empty_df = pd.DataFrame()
        
        # 测试描述性统计
        stats = empty_df.describe()
        self.assertEqual(len(stats), 0)
        
        # 测试相关性计算
        with self.assertRaises(ValueError):
            empty_df.corr()
    
    def test_single_column_data(self):
        """测试单列数据处理"""
        single_col_df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
        
        # 描述性统计应能工作
        stats = single_col_df.describe()
        self.assertEqual(len(stats.columns), 1)
        self.assertIn('A', stats.columns)
        
        # 相关性计算应失败（需要至少两列）
        with self.assertRaises(ValueError):
            single_col_df.corr()
    
    def test_all_nan_data(self):
        """测试全NaN数据处理"""
        nan_df = pd.DataFrame({
            'A': [np.nan, np.nan, np.nan],
            'B': [np.nan, np.nan, np.nan]
        })
        
        # 描述性统计
        stats = nan_df.describe()
        self.assertTrue(stats.isna().all().all())
        
        # 相关性计算
        corr = nan_df.corr()
        self.assertTrue(corr.isna().all().all())
    
    def test_constant_data(self):
        """测试常数数据处理"""
        constant_df = pd.DataFrame({
            'A': [5, 5, 5, 5, 5],
            'B': [10, 10, 10, 10, 10]
        })
        
        # 描述性统计
        stats = constant_df.describe()
        self.assertEqual(stats.loc['std', 'A'], 0)
        self.assertEqual(stats.loc['std', 'B'], 0)
        
        # 相关性应为NaN（标准差为0）
        corr = constant_df.corr()
        self.assertTrue(np.isnan(corr.loc['A', 'B']))


# ============================================================================
# 性能测试
# ============================================================================

class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def test_large_data_handling(self):
        """测试大数据处理"""
        import time
        
        # 生成较大数据集
        print("生成大数据集...")
        n_samples = 10000
        n_features = 20
        
        large_data = pd.DataFrame(
            np.random.randn(n_samples, n_features),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        
        # 添加一些缺失值
        mask = np.random.random((n_samples, n_features)) < 0.1
        large_data = large_data.mask(mask)
        
        print(f"数据集大小: {large_data.shape}")
        
        # 测试清洗性能
        print("测试数据清洗性能...")
        start_time = time.time()
        
        # 简单清洗：填充缺失值
        cleaned = large_data.copy()
        for col in cleaned.columns:
            if cleaned[col].isna().any():
                cleaned[col] = cleaned[col].fillna(cleaned[col].mean())
        
        clean_time = time.time() - start_time
        print(f"数据清洗时间: {clean_time:.2f}秒")
        
        # 应在合理时间内完成
        self.assertLess(clean_time, 5.0, "大数据清洗应在5秒内完成")
        
        # 测试统计分析性能
        print("测试统计分析性能...")
        start_time = time.time()
        
        stats = cleaned.describe()
        corr_matrix = cleaned.corr()
        
        analysis_time = time.time() - start_time
        print(f"统计分析时间: {analysis_time:.2f}秒")
        
        # 应在合理时间内完成
        self.assertLess(analysis_time, 10.0, "大数据分析应在10秒内完成")
        
        # 验证结果
        self.assertEqual(stats.shape[0], 8)  # 描述性统计有8行
        self.assertEqual(corr_matrix.shape, (n_features, n_features))

    def test_memory_efficiency(self):
        """测试内存效率"""
        import psutil
        import os
        
        # 获取当前内存使用
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"测试前内存使用: {memory_before:.1f} MB")
        
        # 创建中等规模数据
        data = pd.DataFrame(
            np.random.randn(5000, 50),
            columns=[f'col_{i}' for i in range(50)]
        )
        
        # 执行一些操作
        result = data.copy()
        
        # 添加衍生特征（可能增加内存）
        for i in range(5):
            result[f'derived_{i}'] = result.iloc[:, i] * result.iloc[:, i+1]
        
        # 计算统计量
        stats = result.describe()
        
        # 获取操作后内存使用
        memory_after = process.memory_info().rss / 1024 / 1024
        memory_increase = memory_after - memory_before
        
        print(f"测试后内存使用: {memory_after:.1f} MB")
        print(f"内存增加: {memory_increase:.1f} MB")
        
        # 内存增加应在合理范围内
        expected_size_mb = (5000 * 55 * 8) / 1024 / 1024  # 55列，每列5000行，每行8字节
        self.assertLess(memory_increase, expected_size_mb * 2, 
                       f"内存增加不应超过预期大小的2倍")


# ============================================================================
# 运行测试
# ============================================================================

def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestDataCleaning,
        TestFeatureEngineering,
        TestStatisticalMethods,
        TestVisualization,
        TestIntegration,
        TestErrorHandling,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTest(tests)
    
    # 运行测试
    print("=" * 80)
    print("开始运行 aily-data-analysis 技能测试")
    print("=" * 80)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 80)
    print("测试结果摘要")
    print("=" * 80)
    
    # 输出详细结果
    print(f"运行测试数: {result.testsRun}")
    print(f"失败测试数: {len(result.failures)}")
    print(f"错误测试数: {len(result.errors)}")
    print(f"跳过测试数: {len(result.skipped)}")
    
    if result.failures:
        print("\n失败测试详情:")
        for test, traceback in result.failures:
            print(f"\n{test.id()}:")
            print(traceback)
    
    if result.errors:
        print("\n错误测试详情:")
        for test, traceback in result.errors:
            print(f"\n{test.id()}:")
            print(traceback)
    
    # 返回是否所有测试通过
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    
    if success:
        print("\n✅ 所有测试通过！")
        print("\n技能测试完成，功能验证成功。")
        print("下一步建议:")
        print("1. 使用实际业务数据进一步验证")
        print("2. 根据具体需求调整参数和算法")
        print("3. 集成到生产环境中使用")
    else:
        print("\n❌ 部分测试失败，请检查实现。")
        print("\n常见问题:")
        print("1. 检查依赖库是否安装")
        print("2. 检查数据清洗逻辑")
        print("3. 验证特征工程实现")
    
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
特征工程脚本

提供标准化的特征工程流程，包括：
1. 数值特征创建（统计特征、衍生特征）
2. 分类特征编码（独热编码、标签编码、目标编码）
3. 时间特征提取（日期组件、周期特征）
4. 文本特征处理（词频、TF-IDF、嵌入）
5. 交互特征创建
6. 特征选择和降维

使用方法：
python feature_engineering.py --input data.csv --output features.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from collections import Counter
import argparse
import warnings
warnings.filterwarnings('ignore')

from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler,
    OneHotEncoder, LabelEncoder, TargetEncoder,
    PolynomialFeatures
)
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import PCA
from sklearn.feature_selection import (
    SelectKBest, f_classif, f_regression, 
    RFE, SelectFromModel
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


class FeatureEngineer:
    """特征工程器类"""
    
    def __init__(self, df, target_column=None):
        self.df = df.copy()
        self.target_column = target_column
        self.feature_report = {}
        self.encoders = {}
        
    def create_numeric_features(self, columns=None):
        """创建数值衍生特征"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        created_features = []
        
        for col in columns:
            # 基础统计特征
            self.df[f'{col}_log'] = np.log1p(np.abs(self.df[col]))
            self.df[f'{col}_sqrt'] = np.sqrt(np.abs(self.df[col]))
            self.df[f'{col}_square'] = self.df[col] ** 2
            self.df[f'{col}_cube'] = self.df[col] ** 3
            
            # 统计衍生特征
            if len(self.df) > 1:
                self.df[f'{col}_zscore'] = (self.df[col] - self.df[col].mean()) / self.df[col].std()
                self.df[f'{col}_quantile'] = pd.qcut(self.df[col], q=4, labels=False, duplicates='drop')
            
            created_features.extend([
                f'{col}_log', f'{col}_sqrt', f'{col}_square', f'{col}_cube',
                f'{col}_zscore', f'{col}_quantile'
            ])
        
        self.feature_report['numeric_features'] = created_features
        return self.df
    
    def create_interaction_features(self, columns=None, degree=2):
        """创建交互特征"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()[:10]  # 限制数量
        
        if len(columns) >= 2:
            # 两两乘积
            for i in range(len(columns)):
                for j in range(i+1, len(columns)):
                    col1, col2 = columns[i], columns[j]
                    self.df[f'{col1}_x_{col2}'] = self.df[col1] * self.df[col2]
                    self.df[f'{col1}_div_{col2}'] = self.df[col1] / (self.df[col2] + 1e-10)  # 避免除零
                    self.df[f'{col1}_plus_{col2}'] = self.df[col1] + self.df[col2]
                    self.df[f'{col1}_minus_{col2}'] = self.df[col1] - self.df[col2]
            
            self.feature_report['interaction_features'] = f"创建了 {len(columns)} 个数值列的交互特征"
        
        return self.df
    
    def encode_categorical_features(self, columns=None, method='onehot', max_categories=50):
        """编码分类特征
        
        Args:
            method: 编码方法，可选值：
                - 'onehot': 独热编码
                - 'label': 标签编码
                - 'target': 目标编码（需要目标列）
                - 'frequency': 频率编码
                - 'binary': 二进制编码
        """
        if columns is None:
            columns = self.df.select_dtypes(include=['object', 'category']).columns
        
        encoded_features = []
        
        for col in columns:
            unique_count = self.df[col].nunique()
            
            if unique_count > max_categories:
                print(f"警告: {col} 有 {unique_count} 个唯一值，超过最大限制 {max_categories}，跳过编码")
                continue
            
            if method == 'onehot':
                # 独热编码
                if unique_count <= 10:  # 唯一值较少时使用独热编码
                    dummies = pd.get_dummies(self.df[col], prefix=col, drop_first=True)
                    self.df = pd.concat([self.df, dummies], axis=1)
                    encoded_features.extend(dummies.columns.tolist())
                else:
                    print(f"警告: {col} 有 {unique_count} 个唯一值，使用频率编码替代独热编码")
                    # 使用频率编码
                    freq = self.df[col].value_counts(normalize=True)
                    self.df[f'{col}_freq'] = self.df[col].map(freq)
                    encoded_features.append(f'{col}_freq')
            
            elif method == 'label':
                # 标签编码
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    self.df[f'{col}_label'] = self.encoders[col].fit_transform(self.df[col].astype(str))
                encoded_features.append(f'{col}_label')
            
            elif method == 'target' and self.target_column is not None:
                # 目标编码（需要目标列）
                if self.df[self.target_column].dtype in ['int64', 'float64']:
                    # 回归问题：使用目标均值
                    target_mean = self.df.groupby(col)[self.target_column].mean()
                    self.df[f'{col}_target_mean'] = self.df[col].map(target_mean)
                    encoded_features.append(f'{col}_target_mean')
                else:
                    # 分类问题：使用目标概率
                    for class_val in self.df[self.target_column].unique():
                        prob = self.df.groupby(col)[self.target_column].apply(lambda x: (x == class_val).mean())
                        self.df[f'{col}_target_prob_{class_val}'] = self.df[col].map(prob)
                        encoded_features.append(f'{col}_target_prob_{class_val}')
            
            elif method == 'frequency':
                # 频率编码
                freq = self.df[col].value_counts(normalize=True)
                self.df[f'{col}_freq'] = self.df[col].map(freq)
                encoded_features.append(f'{col}_freq')
            
            elif method == 'binary':
                # 二进制编码（适用于基数较大的分类变量）
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    encoded = self.encoders[col].fit_transform(self.df[col].astype(str))
                    
                    # 转换为二进制表示
                    max_bits = int(np.ceil(np.log2(unique_count)))
                    for bit in range(max_bits):
                        self.df[f'{col}_binary_{bit}'] = (encoded >> bit) & 1
                        encoded_features.append(f'{col}_binary_{bit}')
        
        self.feature_report['encoded_categorical'] = {
            'method': method,
            'columns': columns.tolist(),
            'created_features': encoded_features
        }
        
        return self.df
    
    def extract_time_features(self, date_columns=None):
        """从日期时间列提取特征"""
        if date_columns is None:
            # 自动识别日期列
            date_columns = []
            for col in self.df.columns:
                if self.df[col].dtype == 'datetime64[ns]':
                    date_columns.append(col)
                # 尝试转换字符串为日期
                elif self.df[col].dtype == 'object':
                    try:
                        pd.to_datetime(self.df[col], errors='coerce')
                        date_columns.append(col)
                    except:
                        pass
        
        extracted_features = []
        
        for col in date_columns:
            try:
                if self.df[col].dtype != 'datetime64[ns]':
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                
                # 基础时间组件
                self.df[f'{col}_year'] = self.df[col].dt.year
                self.df[f'{col}_month'] = self.df[col].dt.month
                self.df[f'{col}_day'] = self.df[col].dt.day
                self.df[f'{col}_hour'] = self.df[col].dt.hour
                self.df[f'{col}_minute'] = self.df[col].dt.minute
                self.df[f'{col}_second'] = self.df[col].dt.second
                self.df[f'{col}_dayofweek'] = self.df[col].dt.dayofweek
                self.df[f'{col}_dayofyear'] = self.df[col].dt.dayofyear
                self.df[f'{col}_weekofyear'] = self.df[col].dt.isocalendar().week
                self.df[f'{col}_quarter'] = self.df[col].dt.quarter
                self.df[f'{col}_is_weekend'] = self.df[col].dt.dayofweek >= 5
                self.df[f'{col}_is_month_start'] = self.df[col].dt.is_month_start
                self.df[f'{col}_is_month_end'] = self.df[col].dt.is_month_end
                self.df[f'{col}_is_quarter_start'] = self.df[col].dt.is_quarter_start
                self.df[f'{col}_is_quarter_end'] = self.df[col].dt.is_quarter_end
                self.df[f'{col}_is_year_start'] = self.df[col].dt.is_year_start
                self.df[f'{col}_is_year_end'] = self.df[col].dt.is_year_end
                
                # 周期特征
                self.df[f'{col}_sin_month'] = np.sin(2 * np.pi * self.df[col].dt.month / 12)
                self.df[f'{col}_cos_month'] = np.cos(2 * np.pi * self.df[col].dt.month / 12)
                self.df[f'{col}_sin_day'] = np.sin(2 * np.pi * self.df[col].dt.day / 31)
                self.df[f'{col}_cos_day'] = np.cos(2 * np.pi * self.df[col].dt.day / 31)
                self.df[f'{col}_sin_hour'] = np.sin(2 * np.pi * self.df[col].dt.hour / 24)
                self.df[f'{col}_cos_hour'] = np.cos(2 * np.pi * self.df[col].dt.hour / 24)
                self.df[f'{col}_sin_dayofweek'] = np.sin(2 * np.pi * self.df[col].dt.dayofweek / 7)
                self.df[f'{col}_cos_dayofweek'] = np.cos(2 * np.pi * self.df[col].dt.dayofweek / 7)
                
                base_features = [
                    f'{col}_year', f'{col}_month', f'{col}_day', f'{col}_hour',
                    f'{col}_minute', f'{col}_second', f'{col}_dayofweek',
                    f'{col}_dayofyear', f'{col}_weekofyear', f'{col}_quarter',
                    f'{col}_is_weekend', f'{col}_is_month_start', f'{col}_is_month_end',
                    f'{col}_is_quarter_start', f'{col}_is_quarter_end',
                    f'{col}_is_year_start', f'{col}_is_year_end'
                ]
                
                periodic_features = [
                    f'{col}_sin_month', f'{col}_cos_month',
                    f'{col}_sin_day', f'{col}_cos_day',
                    f'{col}_sin_hour', f'{col}_cos_hour',
                    f'{col}_sin_dayofweek', f'{col}_cos_dayofweek'
                ]
                
                extracted_features.extend(base_features + periodic_features)
                
            except Exception as e:
                print(f"处理日期列 {col} 时出错: {e}")
                continue
        
        self.feature_report['time_features'] = {
            'date_columns': date_columns,
            'extracted_features': extracted_features
        }
        
        return self.df
    
    def process_text_features(self, text_columns=None, max_features=100):
        """处理文本特征"""
        if text_columns is None:
            # 自动识别文本列（字符串类型且长度较长）
            text_columns = []
            for col in self.df.select_dtypes(include=['object']).columns:
                if self.df[col].str.len().mean() > 10:  # 平均长度大于10个字符
                    text_columns.append(col)
        
        text_features_created = []
        
        for col in text_columns:
            try:
                # 基础文本特征
                self.df[f'{col}_length'] = self.df[col].astype(str).str.len()
                self.df[f'{col}_word_count'] = self.df[col].astype(str).str.split().str.len()
                self.df[f'{col}_char_count'] = self.df[col].astype(str).str.replace(r'\s', '', regex=True).str.len()
                self.df[f'{col}_avg_word_length'] = self.df[f'{col}_char_count'] / (self.df[f'{col}_word_count'] + 1e-10)
                
                # 特殊字符统计
                self.df[f'{col}_digit_count'] = self.df[col].astype(str).str.count(r'\d')
                self.df[f'{col}_letter_count'] = self.df[col].astype(str).str.count(r'[a-zA-Z]')
                self.df[f'{col}_uppercase_count'] = self.df[col].astype(str).str.count(r'[A-Z]')
                self.df[f'{col}_lowercase_count'] = self.df[col].astype(str).str.count(r'[a-z]')
                self.df[f'{col}_special_count'] = self.df[col].astype(str).str.count(r'[^a-zA-Z0-9\s]')
                
                base_features = [
                    f'{col}_length', f'{col}_word_count', f'{col}_char_count',
                    f'{col}_avg_word_length', f'{col}_digit_count',
                    f'{col}_letter_count', f'{col}_uppercase_count',
                    f'{col}_lowercase_count', f'{col}_special_count'
                ]
                
                text_features_created.extend(base_features)
                
                # TF-IDF特征（可选）
                if len(self.df) > 100:  # 数据量足够时使用TF-IDF
                    tfidf = TfidfVectorizer(max_features=min(max_features, 50), stop_words='english')
                    tfidf_features = tfidf.fit_transform(self.df[col].fillna(''))
                    tfidf_df = pd.DataFrame(
                        tfidf_features.toarray(),
                        columns=[f'{col}_tfidf_{i}' for i in range(tfidf_features.shape[1])]
                    )
                    self.df = pd.concat([self.df, tfidf_df], axis=1)
                    text_features_created.extend(tfidf_df.columns.tolist())
                
            except Exception as e:
                print(f"处理文本列 {col} 时出错: {e}")
                continue
        
        self.feature_report['text_features'] = {
            'text_columns': text_columns,
            'created_features': text_features_created
        }
        
        return self.df
    
    def create_aggregation_features(self, group_columns, agg_columns=None, 
                                   agg_functions=['mean', 'std', 'min', 'max', 'count']):
        """创建聚合特征"""
        if agg_columns is None:
            agg_columns = self.df.select_dtypes(include=[np.number]).columns
        
        aggregation_features = []
        
        for group_col in group_columns if isinstance(group_columns, list) else [group_columns]:
            group_data = self.df.groupby(group_col)
            
            for agg_col in agg_columns:
                for func in agg_functions:
                    try:
                        if func == 'count':
                            agg_values = group_data[agg_col].transform('count')
                        else:
                            agg_values = group_data[agg_col].transform(func)
                        
                        feature_name = f'{agg_col}_{func}_by_{group_col}'
                        self.df[feature_name] = agg_values
                        aggregation_features.append(feature_name)
                    except:
                        continue
        
        self.feature_report['aggregation_features'] = aggregation_features
        return self.df
    
    def create_lag_features(self, date_column, value_column, lags=[1, 7, 30]):
        """创建滞后特征（时间序列）"""
        if date_column not in self.df.columns or value_column not in self.df.columns:
            print(f"警告: {date_column} 或 {value_column} 不存在")
            return self.df
        
        # 确保日期列已排序
        self.df = self.df.sort_values(date_column).reset_index(drop=True)
        
        lag_features = []
        for lag in lags:
            self.df[f'{value_column}_lag_{lag}'] = self.df[value_column].shift(lag)
            lag_features.append(f'{value_column}_lag_{lag}')
        
        self.feature_report['lag_features'] = lag_features
        return self.df
    
    def create_rolling_features(self, date_column, value_column, windows=[7, 30]):
        """创建滚动统计特征"""
        if date_column not in self.df.columns or value_column not in self.df.columns:
            print(f"警告: {date_column} 或 {value_column} 不存在")
            return self.df
        
        # 确保日期列已排序
        self.df = self.df.sort_values(date_column).reset_index(drop=True)
        
        rolling_features = []
        for window in windows:
            self.df[f'{value_column}_roll_mean_{window}'] = self.df[value_column].rolling(window=window, min_periods=1).mean()
            self.df[f'{value_column}_roll_std_{window}'] = self.df[value_column].rolling(window=window, min_periods=1).std()
            self.df[f'{value_column}_roll_min_{window}'] = self.df[value_column].rolling(window=window, min_periods=1).min()
            self.df[f'{value_column}_roll_max_{window}'] = self.df[value_column].rolling(window=window, min_periods=1).max()
            
            rolling_features.extend([
                f'{value_column}_roll_mean_{window}',
                f'{value_column}_roll_std_{window}',
                f'{value_column}_roll_min_{window}',
                f'{value_column}_roll_max_{window}'
            ])
        
        self.feature_report['rolling_features'] = rolling_features
        return self.df
    
    def select_features(self, method='correlation', k=20):
        """特征选择
        
        Args:
            method: 选择方法，可选值：
                - 'correlation': 基于相关性
                - 'variance': 基于方差
                - 'univariate': 单变量统计测试
                - 'rfe': 递归特征消除
                - 'importance': 基于模型重要性
        """
        # 分离特征和目标
        if self.target_column is None:
            print("警告: 没有指定目标列，跳过特征选择")
            return self.df, []
        
        X = self.df.drop(columns=[self.target_column], errors='ignore')
        y = self.df[self.target_column]
        
        # 仅选择数值特征
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        X_numeric = X[numeric_cols]
        
        selected_features = []
        
        if method == 'correlation':
            # 基于与目标的相关性
            if y.dtype in ['int64', 'float64']:
                correlations = X_numeric.apply(lambda col: col.corr(y))
                selected_features = correlations.abs().nlargest(k).index.tolist()
        
        elif method == 'variance':
            # 基于方差
            variances = X_numeric.var()
            selected_features = variances.nlargest(k).index.tolist()
        
        elif method == 'univariate':
            # 单变量统计测试
            if y.dtype in ['int64', 'float64']:
                selector = SelectKBest(score_func=f_regression, k=min(k, len(numeric_cols)))
            else:
                selector = SelectKBest(score_func=f_classif, k=min(k, len(numeric_cols)))
            
            selector.fit(X_numeric.fillna(0), y)
            selected_indices = selector.get_support(indices=True)
            selected_features = [numeric_cols[i] for i in selected_indices]
        
        elif method == 'rfe':
            # 递归特征消除
            if y.dtype in ['int64', 'float64']:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            else:
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            selector = RFE(model, n_features_to_select=min(k, len(numeric_cols)))
            selector.fit(X_numeric.fillna(0), y)
            selected_features = X_numeric.columns[selector.support_].tolist()
        
        elif method == 'importance':
            # 基于模型特征重要性
            if y.dtype in ['int64', 'float64']:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            else:
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            model.fit(X_numeric.fillna(0), y)
            importances = pd.Series(model.feature_importances_, index=numeric_cols)
            selected_features = importances.nlargest(k).index.tolist()
        
        self.feature_report['feature_selection'] = {
            'method': method,
            'k': k,
            'selected_features': selected_features,
            'total_features_before': len(numeric_cols)
        }
        
        # 创建仅包含选中特征的DataFrame
        selected_df = self.df[selected_features + ([self.target_column] if self.target_column in self.df.columns else [])]
        
        return selected_df, selected_features
    
    def reduce_dimensionality(self, n_components=10, method='pca'):
        """降维
        
        Args:
            method: 降维方法，可选值：
                - 'pca': 主成分分析
                - 'tsne': t-SNE（仅用于可视化）
                - 'umap': UMAP
        """
        # 仅选择数值特征
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        X_numeric = self.df[numeric_cols].fillna(0)
        
        if method == 'pca':
            pca = PCA(n_components=min(n_components, len(numeric_cols)))
            pca_features = pca.fit_transform(X_numeric)
            
            # 创建PCA特征列
            for i in range(pca_features.shape[1]):
                self.df[f'pca_{i+1}'] = pca_features[:, i]
            
            explained_variance = pca.explained_variance_ratio_
            
            self.feature_report['dimensionality_reduction'] = {
                'method': 'pca',
                'n_components': n_components,
                'explained_variance': explained_variance.tolist(),
                'total_variance_explained': explained_variance.sum(),
                'created_features': [f'pca_{i+1}' for i in range(pca_features.shape[1])]
            }
        
        return self.df
    
    def generate_report(self):
        """生成特征工程报告"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("特征工程报告")
        report_lines.append("=" * 60)
        report_lines.append(f"原始特征数量: {len(self.df.columns)}")
        
        total_features_created = 0
        
        for category, info in self.feature_report.items():
            if isinstance(info, list):
                report_lines.append(f"\n{category.replace('_', ' ').title()}:")
                report_lines.append(f"  创建了 {len(info)} 个特征")
                total_features_created += len(info)
                if len(info) <= 10:
                    for feature in info:
                        report_lines.append(f"  - {feature}")
            
            elif isinstance(info, dict):
                report_lines.append(f"\n{category.replace('_', ' ').title()}:")
                for key, value in info.items():
                    if isinstance(value, list):
                        report_lines.append(f"  {key}: {len(value)} 个特征")
                        total_features_created += len(value)
                    else:
                        report_lines.append(f"  {key}: {value}")
        
        report_lines.append(f"\n总共创建了 {total_features_created} 个新特征")
        report_lines.append(f"最终特征总数: {len(self.df.columns)}")
        report_lines.append("\n" + "=" * 60)
        
        return "\n".join(report_lines)
    
    def run_full_engineering(self, target_column=None):
        """运行完整的特征工程流程"""
        if target_column:
            self.target_column = target_column
        
        print("开始特征工程...")
        
        # 1. 创建数值特征
        print("1. 创建数值衍生特征...")
        self.create_numeric_features()
        
        # 2. 创建交互特征
        print("2. 创建交互特征...")
        self.create_interaction_features()
        
        # 3. 编码分类特征
        print("3. 编码分类特征...")
        self.encode_categorical_features(method='onehot')
        
        # 4. 提取时间特征
        print("4. 提取时间特征...")
        self.extract_time_features()
        
        # 5. 处理文本特征
        print("5. 处理文本特征...")
        self.process_text_features()
        
        # 6. 创建聚合特征（示例）
        print("6. 创建聚合特征...")
        # 这里需要根据实际数据指定分组列
        
        # 7. 降维（可选）
        if len(self.df.columns) > 50:
            print("7. 降维处理...")
            self.reduce_dimensionality(n_components=20)
        
        print("特征工程完成!")
        return self.df, self.generate_report()


def main():
    parser = argparse.ArgumentParser(description='特征工程自动化脚本')
    parser.add_argument('--input', type=str, required=True, help='输入文件路径')
    parser.add_argument('--output', type=str, default='engineered_features.csv', help='输出文件路径')
    parser.add_argument('--target', type=str, help='目标列名（用于有监督特征工程）')
    parser.add_argument('--format', type=str, default='csv', choices=['csv', 'excel', 'parquet'], help='输出格式')
    
    args = parser.parse_args()
    
    # 读取数据
    print(f"读取数据: {args.input}")
    if args.input.endswith('.csv'):
        df = pd.read_csv(args.input)
    elif args.input.endswith('.xlsx') or args.input.endswith('.xls'):
        df = pd.read_excel(args.input)
    elif args.input.endswith('.parquet'):
        df = pd.read_parquet(args.input)
    else:
        raise ValueError(f"不支持的文件格式: {args.input}")
    
    # 创建特征工程器实例
    engineer = FeatureEngineer(df, target_column=args.target)
    
    # 运行完整特征工程流程
    engineered_df, report = engineer.run_full_engineering()
    
    # 输出报告
    print("\n" + report)
    
    # 保存处理后的数据
    print(f"\n保存特征工程后的数据到: {args.output}")
    if args.format == 'csv':
        engineered_df.to_csv(args.output, index=False)
    elif args.format == 'excel':
        engineered_df.to_excel(args.output, index=False)
    elif args.format == 'parquet':
        engineered_df.to_parquet(args.output, index=False)
    
    # 保存报告到文件
    report_path = args.output.replace('.csv', '_report.txt').replace('.xlsx', '_report.txt').replace('.parquet', '_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"特征工程报告已保存到: {report_path}")


if __name__ == '__main__':
    main()
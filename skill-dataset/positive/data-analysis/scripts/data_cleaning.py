#!/usr/bin/env python3
"""
数据清洗自动化脚本

提供标准化的数据清洗流程，包括：
1. 缺失值检测和处理
2. 异常值检测和处理
3. 数据类型转换
4. 重复数据识别
5. 数据标准化

使用方法：
python data_cleaning.py --input data.csv --output cleaned_data.csv
"""

import pandas as pd
import numpy as np
import argparse
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class DataCleaner:
    """数据清洗器类"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.original_shape = df.shape
        self.cleaning_report = {}
        
    def detect_missing_values(self):
        """检测缺失值"""
        missing_counts = self.df.isnull().sum()
        missing_percent = (missing_counts / len(self.df)) * 100
        
        missing_df = pd.DataFrame({
            'column': missing_counts.index,
            'missing_count': missing_counts.values,
            'missing_percent': missing_percent.values
        })
        
        self.cleaning_report['missing_values'] = missing_df
        return missing_df
    
    def handle_missing_values(self, strategy='auto'):
        """处理缺失值
        
        Args:
            strategy: 处理策略，可选值：
                - 'auto': 根据数据类型自动选择
                - 'drop': 删除包含缺失值的行
                - 'fill': 填充缺失值
                - 'interpolate': 插值
        """
        if strategy == 'auto':
            # 自动策略：数值列用中位数填充，分类列用众数填充
            for col in self.df.columns:
                if self.df[col].dtype in ['int64', 'float64']:
                    self.df[col] = self.df[col].fillna(self.df[col].median())
                elif self.df[col].dtype == 'object':
                    self.df[col] = self.df[col].fillna(self.df[col].mode()[0] if not self.df[col].mode().empty else 'Unknown')
                elif self.df[col].dtype.name == 'category':
                    self.df[col] = self.df[col].fillna(self.df[col].mode()[0] if not self.df[col].mode().empty else 'Unknown')
        elif strategy == 'drop':
            self.df = self.df.dropna()
        elif strategy == 'fill':
            # 用户指定填充值
            pass
        
        self.cleaning_report['missing_handling'] = f"使用策略: {strategy}"
        return self.df
    
    def detect_outliers_iqr(self, columns=None, threshold=1.5):
        """使用IQR方法检测异常值"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        outliers_report = {}
        
        for col in columns:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
            outliers_report[col] = {
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'outlier_count': len(outliers),
                'outlier_percent': (len(outliers) / len(self.df)) * 100,
                'outliers': outliers[col].tolist()
            }
        
        self.cleaning_report['outliers_iqr'] = outliers_report
        return outliers_report
    
    def detect_outliers_zscore(self, columns=None, threshold=3):
        """使用Z-score方法检测异常值"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        outliers_report = {}
        
        for col in columns:
            z_scores = np.abs(stats.zscore(self.df[col].dropna()))
            outliers = self.df.iloc[np.where(z_scores > threshold)[0]]
            outliers_report[col] = {
                'threshold': threshold,
                'outlier_count': len(outliers),
                'outlier_percent': (len(outliers) / len(self.df)) * 100,
                'outliers': outliers[col].tolist()
            }
        
        self.cleaning_report['outliers_zscore'] = outliers_report
        return outliers_report
    
    def handle_outliers(self, method='cap', columns=None):
        """处理异常值
        
        Args:
            method: 处理方法，可选值：
                - 'cap': 将异常值限制在边界内
                - 'remove': 删除异常值
                - 'transform': 使用对数转换等
        """
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        original_rows = len(self.df)
        
        if method == 'cap':
            for col in columns:
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                self.df[col] = np.where(self.df[col] < lower_bound, lower_bound, self.df[col])
                self.df[col] = np.where(self.df[col] > upper_bound, upper_bound, self.df[col])
                
        elif method == 'remove':
            for col in columns:
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                self.df = self.df[(self.df[col] >= lower_bound) & (self.df[col] <= upper_bound)]
        
        removed_rows = original_rows - len(self.df)
        self.cleaning_report['outliers_handling'] = {
            'method': method,
            'original_rows': original_rows,
            'remaining_rows': len(self.df),
            'removed_rows': removed_rows,
            'removed_percent': (removed_rows / original_rows) * 100
        }
        
        return self.df
    
    def convert_data_types(self):
        """自动转换数据类型"""
        type_conversions = {}
        
        for col in self.df.columns:
            original_dtype = str(self.df[col].dtype)
            
            # 尝试转换为数值类型
            try:
                numeric_series = pd.to_numeric(self.df[col], errors='coerce')
                if numeric_series.notna().mean() > 0.8:  # 80%以上可以转换
                    self.df[col] = numeric_series
                    new_dtype = str(self.df[col].dtype)
                    type_conversions[col] = f"{original_dtype} -> {new_dtype}"
                    continue
            except:
                pass
            
            # 尝试转换为日期时间
            try:
                date_series = pd.to_datetime(self.df[col], errors='coerce')
                if date_series.notna().mean() > 0.5:  # 50%以上可以转换
                    self.df[col] = date_series
                    new_dtype = str(self.df[col].dtype)
                    type_conversions[col] = f"{original_dtype} -> {new_dtype}"
                    continue
            except:
                pass
            
            # 对于文本列，如果唯一值数量少，转换为分类
            if self.df[col].dtype == 'object':
                unique_ratio = self.df[col].nunique() / len(self.df[col])
                if unique_ratio < 0.1:  # 唯一值比例小于10%
                    self.df[col] = self.df[col].astype('category')
                    new_dtype = str(self.df[col].dtype)
                    type_conversions[col] = f"{original_dtype} -> {new_dtype}"
        
        self.cleaning_report['type_conversions'] = type_conversions
        return self.df
    
    def remove_duplicates(self, subset=None, keep='first'):
        """删除重复行"""
        original_rows = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        removed_duplicates = original_rows - len(self.df)
        
        self.cleaning_report['duplicates'] = {
            'original_rows': original_rows,
            'remaining_rows': len(self.df),
            'removed_duplicates': removed_duplicates,
            'removed_percent': (removed_duplicates / original_rows) * 100
        }
        
        return self.df
    
    def standardize_numeric(self, columns=None):
        """标准化数值列（z-score标准化）"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        standardized_cols = []
        for col in columns:
            if self.df[col].std() > 0:  # 避免除零
                self.df[f'{col}_standardized'] = (self.df[col] - self.df[col].mean()) / self.df[col].std()
                standardized_cols.append(col)
        
        self.cleaning_report['standardized_columns'] = standardized_cols
        return self.df
    
    def normalize_numeric(self, columns=None, method='minmax'):
        """归一化数值列"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        normalized_cols = []
        for col in columns:
            if method == 'minmax':
                col_min = self.df[col].min()
                col_max = self.df[col].max()
                if col_max > col_min:  # 避免除零
                    self.df[f'{col}_normalized'] = (self.df[col] - col_min) / (col_max - col_min)
                    normalized_cols.append(col)
            elif method == 'robust':
                col_median = self.df[col].median()
                col_iqr = self.df[col].quantile(0.75) - self.df[col].quantile(0.25)
                if col_iqr > 0:  # 避免除零
                    self.df[f'{col}_robust_scaled'] = (self.df[col] - col_median) / col_iqr
                    normalized_cols.append(col)
        
        self.cleaning_report['normalized_columns'] = normalized_cols
        return self.df
    
    def generate_report(self):
        """生成清洗报告"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("数据清洗报告")
        report_lines.append("=" * 60)
        report_lines.append(f"原始数据形状: {self.original_shape}")
        report_lines.append(f"清洗后形状: {self.df.shape}")
        report_lines.append(f"删除行数: {self.original_shape[0] - self.df.shape[0]}")
        report_lines.append(f"删除列数: {self.original_shape[1] - self.df.shape[1]}")
        
        if 'missing_values' in self.cleaning_report:
            report_lines.append("\n缺失值分析:")
            missing_df = self.cleaning_report['missing_values']
            for _, row in missing_df.iterrows():
                if row['missing_count'] > 0:
                    report_lines.append(f"  {row['column']}: {row['missing_count']} 个 ({row['missing_percent']:.1f}%)")
        
        if 'duplicates' in self.cleaning_report:
            dup_info = self.cleaning_report['duplicates']
            report_lines.append(f"\n重复数据: 删除了 {dup_info['removed_duplicates']} 行 ({dup_info['removed_percent']:.1f}%)")
        
        if 'type_conversions' in self.cleaning_report:
            report_lines.append("\n数据类型转换:")
            for col, conversion in self.cleaning_report['type_conversions'].items():
                report_lines.append(f"  {col}: {conversion}")
        
        if 'standardized_columns' in self.cleaning_report:
            report_lines.append(f"\n标准化列: {', '.join(self.cleaning_report['standardized_columns'])}")
        
        if 'normalized_columns' in self.cleaning_report:
            report_lines.append(f"\n归一化列: {', '.join(self.cleaning_report['normalized_columns'])}")
        
        report_lines.append("\n" + "=" * 60)
        return "\n".join(report_lines)
    
    def run_full_cleaning(self):
        """运行完整的清洗流程"""
        print("开始数据清洗...")
        
        # 1. 检测缺失值
        print("1. 检测缺失值...")
        self.detect_missing_values()
        
        # 2. 处理缺失值
        print("2. 处理缺失值...")
        self.handle_missing_values(strategy='auto')
        
        # 3. 检测异常值
        print("3. 检测异常值...")
        self.detect_outliers_iqr()
        
        # 4. 处理异常值
        print("4. 处理异常值...")
        self.handle_outliers(method='cap')
        
        # 5. 转换数据类型
        print("5. 转换数据类型...")
        self.convert_data_types()
        
        # 6. 删除重复数据
        print("6. 删除重复数据...")
        self.remove_duplicates()
        
        # 7. 标准化数值列
        print("7. 标准化数值列...")
        self.standardize_numeric()
        
        print("数据清洗完成!")
        return self.df, self.generate_report()


def main():
    parser = argparse.ArgumentParser(description='数据清洗自动化脚本')
    parser.add_argument('--input', type=str, required=True, help='输入文件路径')
    parser.add_argument('--output', type=str, default='cleaned_data.csv', help='输出文件路径')
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
    
    # 创建清洗器实例
    cleaner = DataCleaner(df)
    
    # 运行完整清洗流程
    cleaned_df, report = cleaner.run_full_cleaning()
    
    # 输出报告
    print("\n" + report)
    
    # 保存清洗后的数据
    print(f"\n保存清洗后的数据到: {args.output}")
    if args.format == 'csv':
        cleaned_df.to_csv(args.output, index=False)
    elif args.format == 'excel':
        cleaned_df.to_excel(args.output, index=False)
    elif args.format == 'parquet':
        cleaned_df.to_parquet(args.output, index=False)
    
    # 保存报告到文件
    report_path = args.output.replace('.csv', '_report.txt').replace('.xlsx', '_report.txt').replace('.parquet', '_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"清洗报告已保存到: {report_path}")


if __name__ == '__main__':
    main()
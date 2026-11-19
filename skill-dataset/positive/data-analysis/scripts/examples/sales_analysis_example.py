#!/usr/bin/env python3
"""
销售数据分析示例

展示如何使用数据分析技能进行完整的销售数据分析
包括：数据加载、清洗、探索性分析、可视化、建模和报告生成
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
sns.set_palette("husl")

class SalesAnalysis:
    """销售数据分析类"""
    
    def __init__(self, data_path):
        """初始化分析器"""
        self.data_path = data_path
        self.df = None
        self.analysis_results = {}
        
    def load_data(self):
        """加载销售数据"""
        print("1. 加载数据...")
        self.df = pd.read_csv(self.data_path, parse_dates=['order_date'])
        print(f"   加载了 {len(self.df)} 行数据，{len(self.df.columns)} 列")
        print(f"   数据时间范围: {self.df['order_date'].min()} 到 {self.df['order_date'].max()}")
        return self.df
    
    def explore_data(self):
        """探索性数据分析"""
        print("\n2. 探索性数据分析...")
        
        # 基本统计信息
        print("   - 基本统计信息:")
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        print(self.df[numeric_cols].describe().round(2))
        
        # 缺失值检查
        print("\n   - 缺失值检查:")
        missing = self.df.isnull().sum()
        missing_pct = (missing / len(self.df)) * 100
        missing_df = pd.DataFrame({
            '缺失数量': missing,
            '缺失比例%': missing_pct.round(2)
        })
        print(missing_df[missing_df['缺失数量'] > 0])
        
        # 数据分布概览
        print("\n   - 分类变量分布:")
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col != 'order_id' and col != 'customer_id':
                print(f"\n     {col}:")
                value_counts = self.df[col].value_counts()
                for val, count in value_counts.head(5).items():
                    pct = (count / len(self.df)) * 100
                    print(f"       {val}: {count} ({pct:.1f}%)")
        
        return self.df
    
    def clean_data(self):
        """数据清洗"""
        print("\n3. 数据清洗...")
        
        original_shape = self.df.shape
        
        # 检查异常值（销售额和利润）
        print("   - 检查异常值:")
        for col in ['sales_amount', 'profit']:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
            print(f"     {col}: 发现 {len(outliers)} 个异常值 ({len(outliers)/len(self.df)*100:.1f}%)")
        
        # 检查负值（不应该有负的销售额或利润）
        negative_sales = self.df[self.df['sales_amount'] < 0]
        negative_profit = self.df[self.df['profit'] < 0]
        print(f"     负销售额: {len(negative_sales)} 行")
        print(f"     负利润: {len(negative_profit)} 行")
        
        # 检查数量为0或负值
        invalid_quantity = self.df[self.df['quantity'] <= 0]
        print(f"     无效数量: {len(invalid_quantity)} 行")
        
        # 实际清洗（这里只是示例，不真正删除）
        print("   - 清洗建议:")
        print("     1. 删除数量为0或负值的记录")
        print("     2. 检查负销售额和利润的数据质量")
        print("     3. 考虑处理异常值（根据业务逻辑）")
        
        return self.df
    
    def analyze_sales_trends(self):
        """分析销售趋势"""
        print("\n4. 分析销售趋势...")
        
        # 按月份聚合
        self.df['month'] = self.df['order_date'].dt.to_period('M')
        monthly_sales = self.df.groupby('month').agg({
            'sales_amount': 'sum',
            'profit': 'sum',
            'order_id': 'count',
            'quantity': 'sum'
        }).rename(columns={'order_id': 'order_count'})
        
        # 计算增长率
        monthly_sales['sales_growth'] = monthly_sales['sales_amount'].pct_change() * 100
        monthly_sales['profit_margin'] = (monthly_sales['profit'] / monthly_sales['sales_amount']) * 100
        
        print("   - 月度销售汇总:")
        print(monthly_sales.round(2))
        
        # 存储结果
        self.analysis_results['monthly_sales'] = monthly_sales
        
        # 趋势分析
        print("\n   - 趋势分析:")
        sales_growth_avg = monthly_sales['sales_growth'].mean()
        profit_margin_avg = monthly_sales['profit_margin'].mean()
        print(f"     平均月销售增长率: {sales_growth_avg:.2f}%")
        print(f"     平均利润率: {profit_margin_avg:.2f}%")
        
        # 最佳和最差月份
        best_month = monthly_sales['sales_amount'].idxmax()
        worst_month = monthly_sales['sales_amount'].idxmin()
        best_sales = monthly_sales.loc[best_month, 'sales_amount']
        worst_sales = monthly_sales.loc[worst_month, 'sales_amount']
        print(f"     销售最高月份: {best_month} (¥{best_sales:,.2f})")
        print(f"     销售最低月份: {worst_month} (¥{worst_sales:,.2f})")
        
        return monthly_sales
    
    def analyze_product_performance(self):
        """分析产品表现"""
        print("\n5. 分析产品表现...")
        
        # 按产品类别分析
        category_performance = self.df.groupby('product_category').agg({
            'sales_amount': ['sum', 'mean', 'count'],
            'profit': 'sum',
            'quantity': 'sum'
        }).round(2)
        
        # 重命名列
        category_performance.columns = [
            'total_sales', 'avg_sales', 'order_count',
            'total_profit', 'total_quantity'
        ]
        
        # 计算利润率
        category_performance['profit_margin'] = (
            category_performance['total_profit'] / category_performance['total_sales']
        ) * 100
        
        # 排序
        category_performance = category_performance.sort_values('total_sales', ascending=False)
        
        print("   - 产品类别表现:")
        print(category_performance.round(2))
        
        # 存储结果
        self.analysis_results['category_performance'] = category_performance
        
        # 畅销产品分析
        product_performance = self.df.groupby(['product_category', 'product_name']).agg({
            'sales_amount': 'sum',
            'profit': 'sum',
            'order_id': 'count'
        }).rename(columns={'order_id': 'order_count'})
        
        product_performance['profit_margin'] = (
            product_performance['profit'] / product_performance['sales_amount']
        ) * 100
        
        # 找出每个类别的前3名产品
        top_products_by_category = {}
        for category in self.df['product_category'].unique():
            category_products = product_performance.loc[category]
            top_3 = category_products.nlargest(3, 'sales_amount')
            top_products_by_category[category] = top_3
        
        print("\n   - 各类别畅销产品前3名:")
        for category, top_products in top_products_by_category.items():
            print(f"\n     {category}:")
            for product_name, row in top_products.iterrows():
                print(f"       {product_name}: ¥{row['sales_amount']:,.2f} "
                      f"({row['order_count']}单, 利润率{row['profit_margin']:.1f}%)")
        
        return category_performance, product_performance
    
    def analyze_regional_performance(self):
        """分析区域表现"""
        print("\n6. 分析区域表现...")
        
        # 按区域分析
        regional_performance = self.df.groupby('region').agg({
            'sales_amount': ['sum', 'mean', 'count'],
            'profit': 'sum',
            'customer_id': 'nunique'
        }).round(2)
        
        # 重命名列
        regional_performance.columns = [
            'total_sales', 'avg_order_value', 'order_count',
            'total_profit', 'unique_customers'
        ]
        
        # 计算人均销售额和利润率
        regional_performance['sales_per_customer'] = (
            regional_performance['total_sales'] / regional_performance['unique_customers']
        )
        regional_performance['profit_margin'] = (
            regional_performance['total_profit'] / regional_performance['total_sales']
        ) * 100
        
        # 排序
        regional_performance = regional_performance.sort_values('total_sales', ascending=False)
        
        print("   - 区域表现:")
        print(regional_performance.round(2))
        
        # 存储结果
        self.analysis_results['regional_performance'] = regional_performance
        
        # 区域对比分析
        print("\n   - 区域对比:")
        best_region = regional_performance['total_sales'].idxmax()
        best_sales = regional_performance.loc[best_region, 'total_sales']
        best_margin = regional_performance.loc[best_region, 'profit_margin']
        
        worst_region = regional_performance['total_sales'].idxmin()
        worst_sales = regional_performance.loc[worst_region, 'total_sales']
        worst_margin = regional_performance.loc[worst_region, 'profit_margin']
        
        print(f"     最佳销售区域: {best_region} (¥{best_sales:,.2f}, 利润率{best_margin:.1f}%)")
        print(f"     最差销售区域: {worst_region} (¥{worst_sales:,.2f}, 利润率{worst_margin:.1f}%)")
        
        # 计算区域间差异
        sales_range = best_sales - worst_sales
        sales_ratio = best_sales / worst_sales if worst_sales > 0 else float('inf')
        print(f"     区域销售差距: ¥{sales_range:,.2f} ({sales_ratio:.1f}倍)")
        
        return regional_performance
    
    def create_visualizations(self, output_dir='.'):
        """创建可视化图表"""
        print("\n7. 创建可视化图表...")
        
        # 创建图表目录
        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 1. 月度销售趋势图
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1.1 月度销售额趋势
        monthly_sales = self.analysis_results['monthly_sales']
        axes[0, 0].plot(monthly_sales.index.astype(str), monthly_sales['sales_amount'], 
                       marker='o', linewidth=2, color='#1f77b4')
        axes[0, 0].set_title('月度销售额趋势', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('月份', fontsize=12)
        axes[0, 0].set_ylabel('销售额 (¥)', fontsize=12)
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3)
        
        # 添加数值标签
        for i, (idx, row) in enumerate(monthly_sales.iterrows()):
            axes[0, 0].annotate(f'¥{row["sales_amount"]:,.0f}',
                              (i, row['sales_amount']),
                              textcoords="offset points",
                              xytext=(0,10), ha='center', fontsize=9)
        
        # 1.2 产品类别销售额分布
        category_performance = self.analysis_results['category_performance']
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_performance)))
        axes[0, 1].bar(category_performance.index, category_performance['total_sales'],
                      color=colors, edgecolor='black')
        axes[0, 1].set_title('产品类别销售额分布', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('产品类别', fontsize=12)
        axes[0, 1].set_ylabel('销售额 (¥)', fontsize=12)
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for i, (category, row) in enumerate(category_performance.iterrows()):
            axes[0, 1].annotate(f'¥{row["total_sales"]:,.0f}',
                              (i, row['total_sales']),
                              textcoords="offset points",
                              xytext=(0,5), ha='center', fontsize=9)
        
        # 1.3 区域销售额分布
        regional_performance = self.analysis_results['regional_performance']
        wedges, texts, autotexts = axes[1, 0].pie(regional_performance['total_sales'],
                                                 labels=regional_performance.index,
                                                 autopct='%1.1f%%',
                                                 startangle=90,
                                                 colors=plt.cm.Pastel1(np.arange(len(regional_performance))))
        axes[1, 0].set_title('区域销售额分布', fontsize=14, fontweight='bold')
        
        # 美化饼图文本
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        # 1.4 销售额与利润关系
        scatter = axes[1, 1].scatter(self.df['sales_amount'], self.df['profit'],
                                    c=self.df['quantity'], cmap='viridis',
                                    alpha=0.6, edgecolors='black', linewidth=0.5)
        axes[1, 1].set_title('销售额与利润关系', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('销售额 (¥)', fontsize=12)
        axes[1, 1].set_ylabel('利润 (¥)', fontsize=12)
        axes[1, 1].grid(True, alpha=0.3)
        
        # 添加颜色条
        cbar = plt.colorbar(scatter, ax=axes[1, 1])
        cbar.set_label('购买数量', fontsize=12)
        
        # 添加趋势线
        z = np.polyfit(self.df['sales_amount'], self.df['profit'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(self.df['sales_amount'].min(), self.df['sales_amount'].max(), 100)
        axes[1, 1].plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2,
                       label=f'趋势线: y = {z[0]:.3f}x + {z[1]:.2f}')
        axes[1, 1].legend(fontsize=10)
        
        plt.suptitle('销售数据分析仪表板', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        # 保存图表
        chart_path = os.path.join(output_dir, 'sales_analysis_dashboard.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"   图表已保存到: {chart_path}")
        plt.show()
        
        # 2. 创建详细报告图
        self._create_detailed_visualizations(output_dir)
        
        return chart_path
    
    def _create_detailed_visualizations(self, output_dir):
        """创建详细的可视化图表"""
        fig, axes = plt.subplots(3, 2, figsize=(16, 18))
        
        # 2.1 月度订单数量趋势
        monthly_sales = self.analysis_results['monthly_sales']
        axes[0, 0].bar(monthly_sales.index.astype(str), monthly_sales['order_count'],
                      color='skyblue', edgecolor='black')
        axes[0, 0].set_title('月度订单数量趋势', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('月份', fontsize=12)
        axes[0, 0].set_ylabel('订单数量', fontsize=12)
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # 2.2 利润率趋势
        axes[0, 1].plot(monthly_sales.index.astype(str), monthly_sales['profit_margin'],
                       marker='s', linewidth=2, color='green')
        axes[0, 1].axhline(y=monthly_sales['profit_margin'].mean(), color='red',
                          linestyle='--', alpha=0.7, label='平均利润率')
        axes[0, 1].fill_between(monthly_sales.index.astype(str),
                               monthly_sales['profit_margin'].min(),
                               monthly_sales['profit_margin'].max(),
                               alpha=0.1, color='green')
        axes[0, 1].set_title('月度利润率趋势', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('月份', fontsize=12)
        axes[0, 1].set_ylabel('利润率 (%)', fontsize=12)
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 2.3 产品类别利润率对比
        category_performance = self.analysis_results['category_performance']
        bars = axes[1, 0].barh(category_performance.index, category_performance['profit_margin'],
                              color=plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(category_performance))))
        axes[1, 0].set_title('产品类别利润率对比', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('利润率 (%)', fontsize=12)
        axes[1, 0].invert_yaxis()  # 最高在上
        
        # 添加数值标签
        for bar in bars:
            width = bar.get_width()
            axes[1, 0].text(width + 0.5, bar.get_y() + bar.get_height()/2,
                          f'{width:.1f}%', va='center', fontsize=10)
        
        # 2.4 区域客户分布
        regional_performance = self.analysis_results['regional_performance']
        x = np.arange(len(regional_performance))
        width = 0.35
        
        bars1 = axes[1, 1].bar(x - width/2, regional_performance['unique_customers'],
                              width, label='客户数量', color='lightblue')
        bars2 = axes[1, 1].bar(x + width/2, regional_performance['order_count'],
                              width, label='订单数量', color='lightcoral')
        
        axes[1, 1].set_title('区域客户与订单分布', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('区域', fontsize=12)
        axes[1, 1].set_ylabel('数量', fontsize=12)
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(regional_performance.index, rotation=45)
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        # 2.5 销售额与数量关系（按类别）
        for i, category in enumerate(category_performance.index[:4]):  # 只显示前4个类别
            category_data = self.df[self.df['product_category'] == category]
            axes[2, 0].scatter(category_data['quantity'], category_data['sales_amount'],
                             alpha=0.6, s=50, label=category)
        
        axes[2, 0].set_title('各类别销售额与数量关系', fontsize=14, fontweight='bold')
        axes[2, 0].set_xlabel('购买数量', fontsize=12)
        axes[2, 0].set_ylabel('销售额 (¥)', fontsize=12)
        axes[2, 0].legend()
        axes[2, 0].grid(True, alpha=0.3)
        
        # 2.6 相关性热力图
        numeric_cols = ['sales_amount', 'profit', 'quantity']
        corr_matrix = self.df[numeric_cols].corr()
        
        im = axes[2, 1].imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        axes[2, 1].set_title('数值变量相关性热力图', fontsize=14, fontweight='bold')
        axes[2, 1].set_xticks(np.arange(len(numeric_cols)))
        axes[2, 1].set_yticks(np.arange(len(numeric_cols)))
        axes[2, 1].set_xticklabels(numeric_cols)
        axes[2, 1].set_yticklabels(numeric_cols)
        
        # 添加数值标签
        for i in range(len(numeric_cols)):
            for j in range(len(numeric_cols)):
                text = axes[2, 1].text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                                      ha="center", va="center", color="w",
                                      fontsize=11, fontweight='bold')
        
        plt.colorbar(im, ax=axes[2, 1])
        
        plt.suptitle('销售数据分析详细报告', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        # 保存详细图表
        detailed_chart_path = os.path.join(output_dir, 'sales_analysis_detailed.png')
        plt.savefig(detailed_chart_path, dpi=300, bbox_inches='tight')
        print(f"   详细图表已保存到: {detailed_chart_path}")
        plt.show()
        
        return detailed_chart_path
    
    def generate_report(self):
        """生成分析报告"""
        print("\n8. 生成分析报告...")
        
        report = []
        report.append("=" * 70)
        report.append("销售数据分析报告")
        report.append("=" * 70)
        report.append(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"分析数据范围: {len(self.df)} 条销售记录")
        report.append(f"时间范围: {self.df['order_date'].min().strftime('%Y-%m-%d')} "
                     f"到 {self.df['order_date'].max().strftime('%Y-%m-%d')}")
        report.append("")
        
        # 1. 总体表现
        report.append("1. 总体表现")
        report.append("-" * 40)
        total_sales = self.df['sales_amount'].sum()
        total_profit = self.df['profit'].sum()
        avg_order_value = self.df['sales_amount'].mean()
        total_orders = len(self.df)
        profit_margin = (total_profit / total_sales) * 100
        
        report.append(f"总销售额: ¥{total_sales:,.2f}")
        report.append(f"总利润: ¥{total_profit:,.2f}")
        report.append(f"平均订单价值: ¥{avg_order_value:,.2f}")
        report.append(f"总订单数: {total_orders}")
        report.append(f"整体利润率: {profit_margin:.2f}%")
        report.append("")
        
        # 2. 趋势分析
        report.append("2. 销售趋势分析")
        report.append("-" * 40)
        monthly_sales = self.analysis_results['monthly_sales']
        
        if len(monthly_sales) > 1:
            # 计算整体趋势
            first_month_sales = monthly_sales.iloc[0]['sales_amount']
            last_month_sales = monthly_sales.iloc[-1]['sales_amount']
            total_growth = ((last_month_sales - first_month_sales) / first_month_sales) * 100
            
            avg_monthly_growth = monthly_sales['sales_growth'].mean()
            avg_profit_margin = monthly_sales['profit_margin'].mean()
            
            report.append(f"总体增长: {total_growth:.1f}% "
                         f"(从¥{first_month_sales:,.0f}到¥{last_month_sales:,.0f})")
            report.append(f"平均月增长率: {avg_monthly_growth:.1f}%")
            report.append(f"平均月利润率: {avg_profit_margin:.1f}%")
            
            # 识别最佳和最差月份
            best_month_idx = monthly_sales['sales_amount'].idxmax()
            best_month_sales = monthly_sales.loc[best_month_idx, 'sales_amount']
            worst_month_idx = monthly_sales['sales_amount'].idxmin()
            worst_month_sales = monthly_sales.loc[worst_month_idx, 'sales_amount']
            
            report.append(f"销售最佳月份: {best_month_idx} (¥{best_month_sales:,.0f})")
            report.append(f"销售最差月份: {worst_month_idx} (¥{worst_month_sales:,.0f})")
        report.append("")
        
        # 3. 产品分析
        report.append("3. 产品表现分析")
        report.append("-" * 40)
        category_performance = self.analysis_results['category_performance']
        
        report.append("按类别销售额排名:")
        for i, (category, row) in enumerate(category_performance.iterrows(), 1):
            sales_pct = (row['total_sales'] / total_sales) * 100
            report.append(f"  {i}. {category}: ¥{row['total_sales']:,.0f} "
                         f"({sales_pct:.1f}%), 利润率: {row['profit_margin']:.1f}%")
        report.append("")
        
        # 4. 区域分析
        report.append("4. 区域表现分析")
        report.append("-" * 40)
        regional_performance = self.analysis_results['regional_performance']
        
        report.append("区域表现对比:")
        for region, row in regional_performance.iterrows():
            region_sales_pct = (row['total_sales'] / total_sales) * 100
            report.append(f"  {region}: ¥{row['total_sales']:,.0f} "
                         f"({region_sales_pct:.1f}%), {row['unique_customers']}个客户, "
                         f"利润率: {row['profit_margin']:.1f}%")
        report.append("")
        
        # 5. 关键发现
        report.append("5. 关键发现与建议")
        report.append("-" * 40)
        
        # 自动生成洞察
        insights = self._generate_insights()
        for i, insight in enumerate(insights, 1):
            report.append(f"{i}. {insight}")
        report.append("")
        
        # 6. 建议行动
        report.append("6. 建议行动")
        report.append("-" * 40)
        recommendations = self._generate_recommendations()
        for i, recommendation in enumerate(recommendations, 1):
            report.append(f"{i}. {recommendation}")
        report.append("")
        
        report.append("=" * 70)
        report.append("报告结束")
        report.append("=" * 70)
        
        # 保存报告
        report_text = "\n".join(report)
        report_path = os.path.join('.', 'sales_analysis_report.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"   报告已保存到: {report_path}")
        print("\n" + report_text)
        
        return report_text, report_path
    
    def _generate_insights(self):
        """自动生成洞察"""
        insights = []
        
        # 从分析结果中提取洞察
        category_performance = self.analysis_results['category_performance']
        regional_performance = self.analysis_results['regional_performance']
        monthly_sales = self.analysis_results['monthly_sales']
        
        # 1. 最佳表现类别
        best_category = category_performance.iloc[0]
        best_category_name = category_performance.index[0]
        insights.append(f"{best_category_name}是销售额最高的类别，贡献了"
                       f"¥{best_category['total_sales']:,.0f}的销售额，"
                       f"利润率为{best_category['profit_margin']:.1f}%")
        
        # 2. 最高利润率类别
        highest_margin_category = category_performance.loc[category_performance['profit_margin'].idxmax()]
        highest_margin_name = category_performance['profit_margin'].idxmax()
        if highest_margin_name != best_category_name:
            insights.append(f"{highest_margin_name}的利润率最高，达到"
                          f"{highest_margin_category['profit_margin']:.1f}%，"
                          "但销售额相对较低，有提升潜力")
        
        # 3. 区域表现差异
        best_region = regional_performance.iloc[0]
        best_region_name = regional_performance.index[0]
        worst_region = regional_performance.iloc[-1]
        worst_region_name = regional_performance.index[-1]
        
        sales_ratio = best_region['total_sales'] / worst_region['total_sales']
        insights.append(f"区域表现差异显著：{best_region_name}的销售额是"
                       f"{worst_region_name}的{sales_ratio:.1f}倍")
        
        # 4. 趋势洞察
        if len(monthly_sales) >= 3:
            recent_growth = monthly_sales['sales_growth'].iloc[-1]
            if recent_growth > 0:
                insights.append(f"最近月份销售额增长{recent_growth:.1f}%，"
                              "显示积极趋势")
            else:
                insights.append(f"最近月份销售额下降{abs(recent_growth):.1f}%，"
                              "需要关注")
        
        # 5. 客户价值洞察
        if 'customer_data.csv' in self.data_path:
            # 如果有客户数据，添加客户相关洞察
            customer_df = pd.read_csv('customer_data.csv')
            avg_customer_value = customer_df['total_spent'].mean()
            insights.append(f"平均客户价值为¥{avg_customer_value:,.0f}，"
                          f"共有{customer_df['churn'].sum()}个客户流失")
        
        return insights
    
    def _generate_recommendations(self):
        """自动生成建议"""
        recommendations = []
        
        category_performance = self.analysis_results['category_performance']
        regional_performance = self.analysis_results['regional_performance']
        monthly_sales = self.analysis_results['monthly_sales']
        
        # 1. 产品策略建议
        best_category = category_performance.iloc[0]
        best_category_name = category_performance.index[0]
        recommendations.append(f"加强{best_category_name}的库存和营销，"
                             "这是最主要的收入来源")
        
        # 寻找有潜力的类别（利润率高但销售额中等）
        potential_categories = category_performance[
            (category_performance['profit_margin'] > category_performance['profit_margin'].median()) &
            (category_performance['total_sales'] < category_performance['total_sales'].median())
        ]
        
        if not potential_categories.empty:
            for category, row in potential_categories.iterrows():
                recommendations.append(f"考虑提升{category}的营销投入，"
                                     f"其利润率高达{row['profit_margin']:.1f}%但销售额较低")
        
        # 2. 区域策略建议
        worst_region = regional_performance.iloc[-1]
        worst_region_name = regional_performance.index[-1]
        recommendations.append(f"调查{worst_region_name}区域表现不佳的原因，"
                             "考虑调整该区域的销售策略或资源分配")
        
        # 3. 时间策略建议
        if len(monthly_sales) >= 6:
            # 分析季节性
            avg_by_month = {}
            for idx, row in monthly_sales.iterrows():
                month_num = idx.month
                if month_num not in avg_by_month:
                    avg_by_month[month_num] = []
                avg_by_month[month_num].append(row['sales_amount'])
            
            # 找出季节性模式
            seasonal_pattern = {month: np.mean(sales) for month, sales in avg_by_month.items()}
            best_month = max(seasonal_pattern, key=seasonal_pattern.get)
            worst_month = min(seasonal_pattern, key=seasonal_pattern.get)
            
            month_names = ['一月', '二月', '三月', '四月', '五月', '六月',
                          '七月', '八月', '九月', '十月', '十一月', '十二月']
            
            recommendations.append(f"{month_names[best_month-1]}通常是销售旺季，"
                                 "应提前准备库存和促销活动")
            recommendations.append(f"{month_names[worst_month-1]}销售相对较弱，"
                                 "可考虑推出特别促销活动刺激需求")
        
        # 4. 运营建议
        avg_order_value = self.df['sales_amount'].mean()
        recommendations.append(f"当前平均订单价值为¥{avg_order_value:,.0f}，"
                             "可考虑通过交叉销售和提升销售提高客单价")
        
        # 5. 数据质量建议
        if self.df.isnull().sum().sum() > 0:
            recommendations.append("发现数据中存在缺失值，建议完善数据收集流程，"
                                 "确保数据完整性")
        
        return recommendations
    
    def save_results(self, output_dir='results'):
        """保存所有分析结果"""
        import os
        import json
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 1. 保存数据
        data_path = os.path.join(output_dir, 'processed_data.csv')
        self.df.to_csv(data_path, index=False, encoding='utf-8-sig')
        
        # 2. 保存分析结果（JSON格式）
        results_dict = {}
        for key, value in self.analysis_results.items():
            if hasattr(value, 'to_dict'):
                results_dict[key] = value.to_dict()
            else:
                results_dict[key] = value
        
        results_path = os.path.join(output_dir, 'analysis_results.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, ensure_ascii=False, indent=2, default=str)
        
        # 3. 保存报告
        report_text, report_path = self.generate_report()
        
        print(f"\n所有结果已保存到目录: {output_dir}")
        print(f"  处理后的数据: {data_path}")
        print(f"  分析结果JSON: {results_path}")
        print(f"  分析报告文本: {report_path}")
        
        return output_dir
    
    def run_full_analysis(self):
        """运行完整分析流程"""
        print("开始销售数据分析...")
        print("=" * 70)
        
        # 1. 加载数据
        self.load_data()
        
        # 2. 探索数据
        self.explore_data()
        
        # 3. 清洗数据
        self.clean_data()
        
        # 4. 分析趋势
        self.analyze_sales_trends()
        
        # 5. 分析产品表现
        self.analyze_product_performance()
        
        # 6. 分析区域表现
        self.analyze_regional_performance()
        
        # 7. 创建可视化
        self.create_visualizations('results')
        
        # 8. 生成报告
        report_text, report_path = self.generate_report()
        
        # 9. 保存所有结果
        self.save_results('results')
        
        print("\n" + "=" * 70)
        print("销售数据分析完成!")
        
        return self.analysis_results


def main():
    """主函数"""
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='销售数据分析工具')
    parser.add_argument('--input', type=str, default='sales_data.csv',
                       help='输入数据文件路径')
    parser.add_argument('--output', type=str, default='results',
                       help='输出目录路径')
    
    args = parser.parse_args()
    
    # 创建分析器实例
    analyzer = SalesAnalysis(args.input)
    
    try:
        # 运行完整分析
        results = analyzer.run_full_analysis()
        
        print(f"\n分析完成！结果已保存到 '{args.output}' 目录")
        print("包含以下文件：")
        print("  - processed_data.csv: 处理后的数据")
        print("  - analysis_results.json: 分析结果")
        print("  - sales_analysis_report.txt: 分析报告")
        print("  - sales_analysis_dashboard.png: 主要图表")
        print("  - sales_analysis_detailed.png: 详细图表")
        
    except FileNotFoundError:
        print(f"错误：找不到文件 '{args.input}'")
        print("请确保文件存在或使用 --input 参数指定正确路径")
    except Exception as e:
        print(f"分析过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
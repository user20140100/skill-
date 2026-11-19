#!/usr/bin/env python3
"""
客户数据分析完整示例
展示如何使用aily-data-analysis技能进行端到端的客户分析
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体和图表样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
sns.set_palette("husl")

# ============================================================================
# 第一阶段：数据准备与理解
# ============================================================================

def generate_sample_customer_data(n_customers=1000):
    """
    生成模拟客户数据用于演示
    包含：基本信息、交易数据、行为数据、反馈数据
    """
    np.random.seed(42)
    
    # 生成客户基本信息
    customer_ids = [f'CUST{str(i).zfill(5)}' for i in range(1, n_customers + 1)]
    registration_dates = pd.date_range(
        start='2025-01-01', 
        end='2026-05-28', 
        periods=n_customers
    )
    
    # 客户属性
    ages = np.random.normal(35, 10, n_customers).astype(int)
    ages = np.clip(ages, 18, 70)
    
    genders = np.random.choice(['男', '女'], n_customers, p=[0.52, 0.48])
    
    cities = np.random.choice(
        ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安'],
        n_customers,
        p=[0.2, 0.2, 0.15, 0.15, 0.1, 0.1, 0.05, 0.05]
    )
    
    membership_levels = np.random.choice(
        ['普通', '白银', '黄金', '铂金', '钻石'],
        n_customers,
        p=[0.4, 0.3, 0.15, 0.1, 0.05]
    )
    
    # 生成交易数据（每个客户多条交易记录）
    transactions = []
    for i, cust_id in enumerate(customer_ids):
        # 每个客户的交易次数（泊松分布）
        n_transactions = np.random.poisson(8)
        if n_transactions == 0:
            n_transactions = 1  # 确保至少有一次交易
        
        customer_value = np.random.exponential(500) + 100  # 客户价值基础
        
        for t in range(n_transactions):
            # 交易时间（在注册后随机分布）
            days_after_reg = np.random.exponential(180)
            transaction_date = registration_dates[i] + timedelta(days=min(days_after_reg, 365))
            
            # 交易金额（基于客户价值和会员等级）
            base_amount = customer_value * (1 + np.random.normal(0, 0.3))
            
            # 会员等级加成
            level_multiplier = {
                '普通': 1.0, '白银': 1.2, '黄金': 1.5, '铂金': 2.0, '钻石': 3.0
            }[membership_levels[i]]
            
            amount = round(base_amount * level_multiplier * (0.8 + np.random.random() * 0.4), 2)
            
            # 产品类别
            categories = ['电子产品', '服装', '家居', '食品', '图书', '美妆']
            category = np.random.choice(categories, p=[0.3, 0.2, 0.15, 0.15, 0.1, 0.1])
            
            # 支付方式
            payment_methods = ['支付宝', '微信支付', '信用卡', '银行卡']
            payment_method = np.random.choice(payment_methods, p=[0.4, 0.3, 0.2, 0.1])
            
            # 满意度评分（如果有反馈）
            rating = np.random.choice([None, 1, 2, 3, 4, 5], p=[0.7, 0.02, 0.03, 0.05, 0.1, 0.1])
            
            transactions.append({
                'customer_id': cust_id,
                'transaction_id': f'TXN{cust_id[4:]}{str(t).zfill(3)}',
                'transaction_date': transaction_date,
                'amount': amount,
                'category': category,
                'payment_method': payment_method,
                'rating': rating,
                'city': cities[i],
                'membership_level': membership_levels[i]
            })
    
    # 生成行为数据
    behaviors = []
    for cust_id in customer_ids:
        # 登录次数（幂律分布）
        login_count = np.random.zipf(1.5)
        if login_count > 100:
            login_count = 100
        
        # 页面浏览（与登录次数相关）
        page_views = login_count * np.random.randint(5, 20)
        
        # 购物车添加（部分登录会有）
        cart_adds = int(login_count * np.random.random() * 0.5)
        
        # 收藏商品
        favorites = int(login_count * np.random.random() * 0.3)
        
        behaviors.append({
            'customer_id': cust_id,
            'login_count': login_count,
            'page_views': page_views,
            'cart_adds': cart_adds,
            'favorites': favorites,
            'last_login': registration_dates[np.random.randint(0, n_customers)] + 
                         timedelta(days=np.random.randint(0, 365))
        })
    
    # 生成客户流失标签（基于多种因素）
    churn_labels = []
    for i, cust_id in enumerate(customer_ids):
        # 流失概率基于多个因素
        risk_factors = []
        
        # 最近登录时间（越久风险越高）
        last_login_days = (datetime(2026, 5, 28) - behaviors[i]['last_login']).days
        risk_factors.append(min(last_login_days / 180, 1.0))
        
        # 交易频率（频率低风险高）
        customer_transactions = [t for t in transactions if t['customer_id'] == cust_id]
        transaction_count = len(customer_transactions)
        if transaction_count > 0:
            avg_days_between = 365 / transaction_count
            risk_factors.append(min(avg_days_between / 90, 1.0))
        else:
            risk_factors.append(1.0)
        
        # 满意度（评分低风险高）
        customer_ratings = [t['rating'] for t in customer_transactions if t['rating'] is not None]
        if customer_ratings:
            avg_rating = np.mean(customer_ratings)
            risk_factors.append(1 - avg_rating / 5)
        else:
            risk_factors.append(0.5)  # 无评分中等风险
        
        # 综合风险评分
        risk_score = np.mean(risk_factors)
        
        # 生成流失标签（风险>0.6的标记为流失）
        churn = 1 if risk_score > 0.6 else 0
        
        churn_labels.append({
            'customer_id': cust_id,
            'churn': churn,
            'risk_score': round(risk_score, 3),
            'last_transaction_date': max([t['transaction_date'] for t in customer_transactions]) 
                                    if customer_transactions else registration_dates[i]
        })
    
    # 创建DataFrame
    customers_df = pd.DataFrame({
        'customer_id': customer_ids,
        'registration_date': registration_dates,
        'age': ages,
        'gender': genders,
        'city': cities,
        'membership_level': membership_levels
    })
    
    transactions_df = pd.DataFrame(transactions)
    behaviors_df = pd.DataFrame(behaviors)
    churn_df = pd.DataFrame(churn_labels)
    
    return customers_df, transactions_df, behaviors_df, churn_df

# ============================================================================
# 第二阶段：数据清洗与整理
# ============================================================================

def clean_and_prepare_data(customers_df, transactions_df, behaviors_df, churn_df):
    """
    数据清洗与预处理
    """
    print("=" * 60)
    print("数据清洗与预处理")
    print("=" * 60)
    
    # 1. 检查数据质量
    print("\n1. 数据质量检查:")
    print(f"客户数据行数: {len(customers_df)}, 列数: {len(customers_df.columns)}")
    print(f"交易数据行数: {len(transactions_df)}, 列数: {len(transactions_df.columns)}")
    print(f"行为数据行数: {len(behaviors_df)}, 列数: {len(behaviors_df.columns)}")
    print(f"流失标签行数: {len(churn_df)}, 列数: {len(churn_df.columns)}")
    
    # 2. 处理缺失值
    print("\n2. 缺失值处理:")
    
    # 交易数据中的评分缺失
    rating_missing = transactions_df['rating'].isna().sum()
    rating_total = len(transactions_df)
    print(f"交易评分缺失: {rating_missing}/{rating_total} ({rating_missing/rating_total*100:.1f}%)")
    
    # 用类别平均值填充评分缺失
    if rating_missing > 0:
        # 按产品类别计算平均评分
        category_avg_rating = transactions_df.groupby('category')['rating'].mean()
        
        def fill_rating(row):
            if pd.isna(row['rating']):
                return category_avg_rating.get(row['category'], 3.0)
            return row['rating']
        
        transactions_df['rating'] = transactions_df.apply(fill_rating, axis=1)
        print(f"已用类别平均值填充 {rating_missing} 个缺失评分")
    
    # 3. 处理异常值
    print("\n3. 异常值检测:")
    
    # 交易金额异常值（使用IQR方法）
    Q1 = transactions_df['amount'].quantile(0.25)
    Q3 = transactions_df['amount'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = transactions_df[
        (transactions_df['amount'] < lower_bound) | 
        (transactions_df['amount'] > upper_bound)
    ]
    
    print(f"交易金额异常值数量: {len(outliers)} ({len(outliers)/len(transactions_df)*100:.1f}%)")
    
    if len(outliers) > 0:
        # 对异常值进行Winsorization处理（缩尾处理）
        transactions_df['amount_original'] = transactions_df['amount']
        transactions_df['amount'] = transactions_df['amount'].clip(lower_bound, upper_bound)
        print(f"已对交易金额进行缩尾处理（Winsorization）")
    
    # 4. 数据一致性检查
    print("\n4. 数据一致性检查:")
    
    # 检查客户ID的一致性
    customers_in_transactions = set(transactions_df['customer_id'].unique())
    customers_in_behaviors = set(behaviors_df['customer_id'].unique())
    customers_in_churn = set(churn_df['customer_id'].unique())
    all_customers = set(customers_df['customer_id'])
    
    print(f"客户数据中的客户数: {len(all_customers)}")
    print(f"交易数据中的客户数: {len(customers_in_transactions)}")
    print(f"行为数据中的客户数: {len(customers_in_behaviors)}")
    print(f"流失数据中的客户数: {len(customers_in_churn)}")
    
    # 找出只在某些数据集中出现的客户
    only_in_customers = all_customers - customers_in_transactions
    if len(only_in_customers) > 0:
        print(f"警告: {len(only_in_customers)} 个客户没有交易记录")
    
    # 5. 创建衍生特征
    print("\n5. 创建衍生特征:")
    
    # 客户级聚合特征
    customer_features = customers_df.copy()
    
    # 交易聚合特征
    transaction_agg = transactions_df.groupby('customer_id').agg({
        'amount': ['sum', 'mean', 'count', 'std'],
        'transaction_date': ['min', 'max'],
        'rating': 'mean',
        'category': lambda x: x.nunique()  # 购买品类数
    }).round(2)
    
    # 扁平化多级列索引
    transaction_agg.columns = [
        'total_spent', 'avg_transaction', 'transaction_count', 
        'transaction_std', 'first_purchase', 'last_purchase',
        'avg_rating', 'category_count'
    ]
    
    # 计算购买频率（天/次）
    transaction_agg['purchase_frequency'] = (
        (transaction_agg['last_purchase'] - transaction_agg['first_purchase']).dt.days / 
        transaction_agg['transaction_count']
    ).round(1)
    
    # 合并行为数据
    behavior_features = behaviors_df.set_index('customer_id')
    
    # 合并所有特征
    customer_features = customer_features.set_index('customer_id')
    customer_features = customer_features.join(transaction_agg, how='left')
    customer_features = customer_features.join(behavior_features, how='left')
    customer_features = customer_features.join(churn_df.set_index('customer_id')[['churn', 'risk_score']], how='left')
    
    # 填充缺失值
    numeric_cols = customer_features.select_dtypes(include=[np.number]).columns
    customer_features[numeric_cols] = customer_features[numeric_cols].fillna(0)
    
    # 分类变量编码
    categorical_cols = ['gender', 'city', 'membership_level']
    for col in categorical_cols:
        if col in customer_features.columns:
            # 使用目标编码（考虑流失率）
            if 'churn' in customer_features.columns:
                encoding = customer_features.groupby(col)['churn'].mean()
                customer_features[f'{col}_encoded'] = customer_features[col].map(encoding)
            else:
                # 使用频率编码
                encoding = customer_features[col].value_counts(normalize=True)
                customer_features[f'{col}_encoded'] = customer_features[col].map(encoding)
    
    print(f"特征工程完成，创建了 {len(customer_features.columns)} 个特征")
    print(f"最终数据集形状: {customer_features.shape}")
    
    return customer_features, transactions_df

# ============================================================================
# 第三阶段：探索性分析与可视化
# ============================================================================

def exploratory_data_analysis(customer_features, transactions_df):
    """
    探索性数据分析和可视化
    """
    print("\n" + "=" * 60)
    print("探索性数据分析")
    print("=" * 60)
    
    # 创建可视化目录
    import os
    os.makedirs('visualizations', exist_ok=True)
    
    # 1. 客户分布分析
    print("\n1. 客户分布分析:")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('客户分布分析', fontsize=16, fontweight='bold')
    
    # 年龄分布
    axes[0, 0].hist(customer_features['age'].dropna(), bins=20, edgecolor='black', alpha=0.7)
    axes[0, 0].set_title('年龄分布')
    axes[0, 0].set_xlabel('年龄')
    axes[0, 0].set_ylabel('客户数')
    axes[0, 0].axvline(customer_features['age'].mean(), color='red', linestyle='--', 
                      label=f'平均: {customer_features["age"].mean():.1f}')
    axes[0, 0].legend()
    
    # 性别分布
    gender_counts = customer_features['gender'].value_counts()
    axes[0, 1].pie(gender_counts.values, labels=gender_counts.index, autopct='%1.1f%%',
                  startangle=90, colors=['lightblue', 'lightcoral'])
    axes[0, 1].set_title('性别分布')
    
    # 城市分布
    city_counts = customer_features['city'].value_counts().head(8)
    axes[0, 2].barh(city_counts.index, city_counts.values, color='skyblue')
    axes[0, 2].set_title('城市分布（Top 8）')
    axes[0, 2].set_xlabel('客户数')
    
    # 会员等级分布
    membership_counts = customer_features['membership_level'].value_counts()
    colors = ['lightgray', 'silver', 'gold', 'plum', 'lightblue']
    axes[1, 0].bar(membership_counts.index, membership_counts.values, color=colors)
    axes[1, 0].set_title('会员等级分布')
    axes[1, 0].set_xlabel('会员等级')
    axes[1, 0].set_ylabel('客户数')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 注册时间分布
    if 'registration_date' in customer_features.columns:
        registration_monthly = customer_features['registration_date'].dt.to_period('M').value_counts().sort_index()
        axes[1, 1].plot(registration_monthly.index.astype(str), registration_monthly.values, 
                       marker='o', linewidth=2)
        axes[1, 1].set_title('月度注册趋势')
        axes[1, 1].set_xlabel('年月')
        axes[1, 1].set_ylabel('注册数')
        axes[1, 1].tick_params(axis='x', rotation=45)
    
    # 流失率分布
    if 'churn' in customer_features.columns:
        churn_rate = customer_features['churn'].mean() * 100
        axes[1, 2].bar(['留存客户', '流失客户'], 
                      [100 - churn_rate, churn_rate],
                      color=['lightgreen', 'lightcoral'])
        axes[1, 2].set_title(f'客户流失率: {churn_rate:.1f}%')
        axes[1, 2].set_ylabel('百分比')
        for i, v in enumerate([100 - churn_rate, churn_rate]):
            axes[1, 2].text(i, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('visualizations/customer_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. 交易行为分析
    print("\n2. 交易行为分析:")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 交易金额分布
    axes[0, 0].hist(transactions_df['amount'], bins=50, edgecolor='black', alpha=0.7)
    axes[0, 0].set_title('交易金额分布')
    axes[0, 0].set_xlabel('交易金额（元）')
    axes[0, 0].set_ylabel('交易次数')
    axes[0, 0].axvline(transactions_df['amount'].mean(), color='red', linestyle='--',
                      label=f'平均: ¥{transactions_df["amount"].mean():.2f}')
    axes[0, 0].legend()
    
    # 产品类别销售分布
    category_sales = transactions_df.groupby('category')['amount'].sum().sort_values(ascending=False)
    axes[0, 1].barh(category_sales.index, category_sales.values, color='lightseagreen')
    axes[0, 1].set_title('各品类销售总额')
    axes[0, 1].set_xlabel('销售总额（元）')
    for i, v in enumerate(category_sales.values):
        axes[0, 1].text(v, i, f'¥{v:,.0f}', va='center', fontsize=9)
    
    # 支付方式分布
    payment_counts = transactions_df['payment_method'].value_counts()
    axes[1, 0].pie(payment_counts.values, labels=payment_counts.index, autopct='%1.1f%%',
                  startangle=90, colors=['lightblue', 'lightgreen', 'lightcoral', 'lightsalmon'])
    axes[1, 0].set_title('支付方式分布')
    
    # 月度销售趋势
    if 'transaction_date' in transactions_df.columns:
        monthly_sales = transactions_df.set_index('transaction_date').resample('M')['amount'].sum()
        axes[1, 1].plot(monthly_sales.index, monthly_sales.values, marker='o', linewidth=2, color='darkorange')
        axes[1, 1].set_title('月度销售趋势')
        axes[1, 1].set_xlabel('月份')
        axes[1, 1].set_ylabel('销售总额（元）')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('visualizations/transaction_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 3. 客户价值分析
    print("\n3. 客户价值分析:")
    
    # 计算RFM指标
    if 'last_purchase' in customer_features.columns and 'transaction_count' in customer_features.columns:
        # 计算Recency（最近购买天数）
        latest_date = customer_features['last_purchase'].max()
        customer_features['recency'] = (latest_date - customer_features['last_purchase']).dt.days
        
        # 计算Frequency（购买频率）
        customer_features['frequency'] = customer_features['transaction_count']
        
        # 计算Monetary（消费金额）
        customer_features['monetary'] = customer_features['total_spent']
        
        # RFM分箱
        customer_features['R_score'] = pd.qcut(customer_features['recency'], 4, labels=[4, 3, 2, 1])
        customer_features['F_score'] = pd.qcut(customer_features['frequency'], 4, labels=[1, 2, 3, 4])
        customer_features['M_score'] = pd.qcut(customer_features['monetary'], 4, labels=[1, 2, 3, 4])
        
        customer_features['RFM_score'] = (
            customer_features['R_score'].astype(str) + 
            customer_features['F_score'].astype(str) + 
            customer_features['M_score'].astype(str)
        )
        
        # 计算RFM总分
        customer_features['RFM_total'] = (
            customer_features['R_score'].astype(int) + 
            customer_features['F_score'].astype(int) + 
            customer_features['M_score'].astype(int)
        )
        
        # RFM客户细分
        def segment_customer(row):
            if row['RFM_total'] >= 10:
                return '高价值客户'
            elif row['RFM_total'] >= 7:
                return '潜力客户'
            elif row['RFM_total'] >= 4:
                return '一般客户'
            else:
                return '低价值客户'
        
        customer_features['customer_segment'] = customer_features.apply(segment_customer, axis=1)
        
        # 可视化RFM分析
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        # 客户细分分布
        segment_counts = customer_features['customer_segment'].value_counts()
        colors = ['gold', 'lightgreen', 'lightblue', 'lightcoral']
        axes[0].bar(segment_counts.index, segment_counts.values, color=colors)
        axes[0].set_title('客户价值细分')
        axes[0].set_ylabel('客户数')
        axes[0].tick_params(axis='x', rotation=45)
        for i, v in enumerate(segment_counts.values):
            axes[0].text(i, v + 5, str(v), ha='center')
        
        # 各细分流失率
        if 'churn' in customer_features.columns:
            churn_by_segment = customer_features.groupby('customer_segment')['churn'].mean() * 100
            axes[1].bar(churn_by_segment.index, churn_by_segment.values, color=colors)
            axes[1].set_title('各客户细分流失率')
            axes[1].set_ylabel('流失率 (%)')
            axes[1].tick_params(axis='x', rotation=45)
            for i, v in enumerate(churn_by_segment.values):
                axes[1].text(i, v + 0.5, f'{v:.1f}%', ha='center')
        
        # RFM三维散点图（简化版）
        from mpl_toolkits.mplot3d import Axes3D
        ax = fig.add_subplot(133, projection='3d')
        
        sample_data = customer_features.sample(min(200, len(customer_features)))
        
        # 颜色映射
        segment_colors = {
            '高价值客户': 'gold',
            '潜力客户': 'lightgreen',
            '一般客户': 'lightblue',
            '低价值客户': 'lightcoral'
        }
        
        colors = [segment_colors.get(seg, 'gray') for seg in sample_data['customer_segment']]
        
        scatter = ax.scatter(
            sample_data['recency'], 
            sample_data['frequency'], 
            sample_data['monetary'],
            c=colors, alpha=0.6, s=50
        )
        
        ax.set_xlabel('Recency（天）')
        ax.set_ylabel('Frequency（次）')
        ax.set_zlabel('Monetary（元）')
        ax.set_title('RFM三维分布')
        
        # 创建图例
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='gold', label='高价值客户'),
            Patch(facecolor='lightgreen', label='潜力客户'),
            Patch(facecolor='lightblue', label='一般客户'),
            Patch(facecolor='lightcoral', label='低价值客户')
        ]
        ax.legend(handles=legend_elements, loc='upper left')
        
        plt.tight_layout()
        plt.savefig('visualizations/rfm_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    # 4. 相关性分析
    print("\n4. 特征相关性分析:")
    
    # 选择数值特征进行相关性分析
    numeric_features = customer_features.select_dtypes(include=[np.number]).columns
    # 排除ID类和其他不相关特征
    exclude_cols = ['risk_score', 'R_score', 'F_score', 'M_score', 'RFM_total']
    corr_features = [col for col in numeric_features if col not in exclude_cols and '_encoded' not in col]
    
    if len(corr_features) > 1:
        correlation_matrix = customer_features[corr_features].corr()
        
        plt.figure(figsize=(14, 12))
        sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, square=True, linewidths=0.5)
        plt.title('特征相关性热力图', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('visualizations/correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 找出与流失最相关的特征
        if 'churn' in correlation_matrix.columns:
            churn_corr = correlation_matrix['churn'].sort_values(ascending=False)
            print("\n与流失最相关的特征（正相关）:")
            for feature, corr in churn_corr.head(10).items():
                if feature != 'churn':
                    print(f"  {feature}: {corr:.3f}")
            
            print("\n与流失最相关的特征（负相关）:")
            for feature, corr in churn_corr.tail(10).items():
                if feature != 'churn':
                    print(f"  {feature}: {corr:.3f}")
    
    return customer_features

# ============================================================================
# 第四阶段：建模与分析
# ============================================================================

def predictive_modeling(customer_features):
    """
    预测性建模：客户流失预测
    """
    print("\n" + "=" * 60)
    print("预测性建模：客户流失预测")
    print("=" * 60)
    
    # 检查是否有流失标签
    if 'churn' not in customer_features.columns:
        print("警告：数据中没有流失标签，无法进行预测建模")
        return None
    
    # 准备建模数据
    # 选择特征
    exclude_cols = [
        'registration_date', 'first_purchase', 'last_purchase', 
        'last_login', 'customer_segment', 'RFM_score',
        'R_score', 'F_score', 'M_score', 'risk_score'
    ]
    
    feature_cols = [col for col in customer_features.columns 
                   if col not in exclude_cols and col != 'churn']
    
    # 分离特征和目标
    X = customer_features[feature_cols]
    y = customer_features['churn']
    
    # 处理分类变量（如果还没有编码）
    categorical_cols = X.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
    
    # 处理缺失值
    X = X.fillna(0)
    
    # 划分训练集和测试集
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    print(f"训练集大小: {X_train.shape}")
    print(f"测试集大小: {X_test.shape}")
    print(f"流失率 - 训练集: {y_train.mean():.3f}, 测试集: {y_test.mean():.3f}")
    
    # 1. 尝试多个模型
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.svm import SVC
    from sklearn.neighbors import KNeighborsClassifier
    from xgboost import XGBClassifier
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score,
        roc_auc_score, confusion_matrix, classification_report
    )
    
    models = {
        '逻辑回归': LogisticRegression(max_iter=1000, random_state=42),
        '随机森林': RandomForestClassifier(n_estimators=100, random_state=42),
        '梯度提升': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'XGBoost': XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss'),
        'K近邻': KNeighborsClassifier(n_neighbors=5)
    }
    
    results = {}
    
    print("\n模型性能比较:")
    print("-" * 80)
    print(f"{'模型':<15} {'准确率':<10} {'精确率':<10} {'召回率':<10} {'F1分数':<10} {'AUC':<10}")
    print("-" * 80)
    
    for name, model in models.items():
        # 训练模型
        model.fit(X_train, y_train)
        
        # 预测
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
        
        # 计算指标
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_pred_proba) if y_pred_proba is not None else 0
        
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'auc': auc,
            'predictions': y_pred,
            'probabilities': y_pred_proba
        }
        
        print(f"{name:<15} {accuracy:<10.4f} {precision:<10.4f} {recall:<10.4f} {f1:<10.4f} {auc:<10.4f}")
    
    print("-" * 80)
    
    # 2. 选择最佳模型
    best_model_name = max(results.keys(), key=lambda x: results[x]['f1'])
    best_model = results[best_model_name]
    
    print(f"\n最佳模型: {best_model_name} (F1分数: {best_model['f1']:.4f})")
    
    # 3. 详细评估最佳模型
    print("\n最佳模型详细评估:")
    print(classification_report(y_test, best_model['predictions']))
    
    # 混淆矩阵
    cm = confusion_matrix(y_test, best_model['predictions'])
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['非流失', '流失'], 
                yticklabels=['非流失', '流失'])
    plt.title(f'{best_model_name} - 混淆矩阵', fontsize=14, fontweight='bold')
    plt.ylabel('真实标签')
    plt.xlabel('预测标签')
    plt.tight_layout()
    plt.savefig('visualizations/confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 4. 特征重要性分析
    if hasattr(best_model['model'], 'feature_importances_'):
        # 树模型的特征重要性
        importances = best_model['model'].feature_importances_
        feature_importance_df = pd.DataFrame({
            'feature': X.columns,
            'importance': importances
        }).sort_values('importance', ascending=False).head(20)
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(feature_importance_df['feature'][::-1], 
                       feature_importance_df['importance'][::-1],
                       color='skyblue')
        plt.title(f'{best_model_name} - 特征重要性 Top 20', fontsize=14, fontweight='bold')
        plt.xlabel('重要性分数')
        plt.tight_layout()
        plt.savefig('visualizations/feature_importance.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("\nTop 10 重要特征:")
        for i, row in feature_importance_df.head(10).iterrows():
            print(f"  {row['feature']}: {row['importance']:.4f}")
    
    elif hasattr(best_model['model'], 'coef_'):
        # 线性模型的系数
        coefficients = best_model['model'].coef_[0]
        coef_df = pd.DataFrame({
            'feature': X.columns,
            'coefficient': coefficients
        }).sort_values('coefficient', ascending=False)
        
        print("\nTop 10 正系数特征（促进流失）:")
        for i, row in coef_df.head(10).iterrows():
            print(f"  {row['feature']}: {row['coefficient']:.4f}")
        
        print("\nTop 10 负系数特征（抑制流失）:")
        for i, row in coef_df.tail(10).iterrows():
            print(f"  {row['feature']}: {row['coefficient']:.4f}")
    
    # 5. ROC曲线
    if best_model['probabilities'] is not None:
        from sklearn.metrics import roc_curve
        
        fpr, tpr, thresholds = roc_curve(y_test, best_model['probabilities'])
        
        plt.figure(figsize=(10, 8))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC曲线 (AUC = {best_model["auc"]:.3f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='随机猜测')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('假正率 (False Positive Rate)')
        plt.ylabel('真正率 (True Positive Rate)')
        plt.title(f'{best_model_name} - ROC曲线', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('visualizations/roc_curve.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    return best_model, X.columns, results

# ============================================================================
# 第五阶段：业务洞察与建议
# ============================================================================

def generate_business_insights(customer_features, best_model, feature_names, transactions_df):
    """
    生成业务洞察和建议
    """
    print("\n" + "=" * 60)
    print("业务洞察与建议")
    print("=" * 60)
    
    insights = []
    
    # 1. 总体客户状况
    total_customers = len(customer_features)
    if 'churn' in customer_features.columns:
        churn_rate = customer_features['churn'].mean() * 100
        insights.append({
            'category': '总体状况',
            'insight': f'客户总数: {total_customers:,}，流失率: {churn_rate:.1f}%',
            'implication': f'当前有约{churn_rate:.1f}%的客户面临流失风险',
            'recommendation': '需要立即关注客户留存问题'
        })
    
    # 2. 高价值客户分析
    if 'customer_segment' in customer_features.columns:
        high_value_customers = customer_features[customer_features['customer_segment'] == '高价值客户']
        high_value_count = len(high_value_customers)
        high_value_ratio = high_value_count / total_customers * 100
        
        if 'churn' in customer_features.columns:
            high_value_churn_rate = high_value_customers['churn'].mean() * 100
        
        insights.append({
            'category': '客户价值',
            'insight': f'高价值客户占比: {high_value_ratio:.1f}% ({high_value_count}人)',
            'implication': f'这{high_value_count}位客户贡献了大部分收入，需要重点保护',
            'recommendation': '为高价值客户提供专属服务和个性化关怀'
        })
    
    # 3. 流失客户特征分析
    if 'churn' in customer_features.columns:
        churned_customers = customer_features[customer_features['churn'] == 1]
        retained_customers = customer_features[customer_features['churn'] == 0]
        
        if len(churned_customers) > 0 and len(retained_customers) > 0:
            # 比较关键指标
            key_metrics = ['recency', 'frequency', 'monetary', 'avg_rating', 'login_count']
            
            for metric in key_metrics:
                if metric in customer_features.columns:
                    churned_mean = churned_customers[metric].mean()
                    retained_mean = retained_customers[metric].mean()
                    
                    if pd.notna(churned_mean) and pd.notna(retained_mean):
                        diff_percent = (churned_mean - retained_mean) / retained_mean * 100
                        
                        if abs(diff_percent) > 10:  # 差异显著
                            if metric == 'recency':
                                insight_text = f'流失客户平均{churned_mean:.1f}天未购买，留存客户{retained_mean:.1f}天'
                                if diff_percent > 0:
                                    implication = '流失客户购买间隔时间明显更长'
                                    recommendation = '通过定期互动和促销活动保持客户活跃度'
                                else:
                                    implication = '留存客户购买间隔时间更长但未流失，可能有其他忠诚因素'
                                    recommendation = '研究留存客户的忠诚驱动因素并推广'
                            elif metric == 'frequency':
                                insight_text = f'流失客户平均购买{churned_mean:.1f}次，留存客户{retained_mean:.1f}次'
                                implication = '购买频率与客户留存正相关'
                                recommendation = '鼓励更频繁的购买行为，如订阅制或定期购'
                            elif metric == 'monetary':
                                insight_text = f'流失客户平均消费¥{churned_mean:,.0f}，留存客户¥{retained_mean:,.0f}'
                                implication = '消费金额与客户留存正相关'
                                recommendation = '提升客单价策略，如交叉销售和向上销售'
                            elif metric == 'avg_rating':
                                insight_text = f'流失客户平均评分{churned_mean:.1f}，留存客户{retained_mean:.1f}'
                                implication = '满意度评分对客户留存有显著影响'
                                recommendation = '加强客户满意度管理，及时解决投诉问题'
                            elif metric == 'login_count':
                                insight_text = f'流失客户平均登录{churned_mean:.1f}次，留存客户{retained_mean:.1f}次'
                                implication = '平台活跃度与客户留存正相关'
                                recommendation = '提高用户参与度，如个性化推荐和社区互动'
                            
                            insights.append({
                                'category': '流失特征',
                                'insight': insight_text,
                                'implication': implication,
                                'recommendation': recommendation
                            })
    
    # 4. 产品品类分析
    if 'category' in transactions_df.columns:
        category_analysis = transactions_df.groupby('category').agg({
            'amount': ['sum', 'mean', 'count'],
            'rating': 'mean'
        }).round(2)
        
        # 找出销售最好和最差的品类
        top_category = category_analysis[('amount', 'sum')].idxmax()
        top_sales = category_analysis.loc[top_category, ('amount', 'sum')]
        
        bottom_category = category_analysis[('amount', 'sum')].idxmin()
        bottom_sales = category_analysis.loc[bottom_category, ('amount', 'sum')]
        
        # 找出评分最高和最低的品类
        if ('rating', 'mean') in category_analysis.columns:
            top_rating_category = category_analysis[('rating', 'mean')].idxmax()
            top_rating = category_analysis.loc[top_rating_category, ('rating', 'mean')]
            
            bottom_rating_category = category_analysis[('rating', 'mean')].idxmin()
            bottom_rating = category_analysis.loc[bottom_rating_category, ('rating', 'mean')]
        
        insights.append({
            'category': '产品表现',
            'insight': f'销售最佳品类: {top_category} (¥{top_sales:,.0f})，最差品类: {bottom_category} (¥{bottom_sales:,.0f})',
            'implication': f'{top_category}品类表现突出，{bottom_category}品类需要关注',
            'recommendation': f'加大{top_category}品类的推广力度，分析{bottom_category}品类的改进空间'
        })
    
    # 5. 预测模型洞察
    if best_model is not None:
        model_name = type(best_model['model']).__name__
        model_performance = {
            '准确率': f"{best_model['accuracy']:.1%}",
            '精确率': f"{best_model['precision']:.1%}",
            '召回率': f"{best_model['recall']:.1%}",
            'F1分数': f"{best_model['f1']:.3f}",
            'AUC': f"{best_model['auc']:.3f}"
        }
        
        insights.append({
            'category': '预测能力',
            'insight': f'使用{model_name}模型，能够以{best_model["accuracy"]:.1%}的准确率预测客户流失',
            'implication': '模型可以有效识别高风险流失客户',
            'recommendation': '将模型集成到客户关系管理系统中，实现主动干预'
        })
    
    # 6. 行动建议总结
    print("\n业务洞察总结:")
    print("-" * 80)
    
    for i, insight in enumerate(insights, 1):
        print(f"\n{i}. 【{insight['category']}】")
        print(f"   洞察: {insight['insight']}")
        print(f"   含义: {insight['implication']}")
        print(f"   建议: {insight['recommendation']}")
    
    print("\n" + "-" * 80)
    
    # 7. 生成可执行建议
    print("\n可执行建议:")
    print("=" * 60)
    
    actionable_recommendations = [
        {
            'priority': '高',
            'action': '建立高风险客户预警系统',
            'owner': '数据团队',
            'timeline': '2周',
            'expected_impact': '减少20-30%的客户流失'
        },
        {
            'priority': '高',
            'action': '为高价值客户提供专属客户经理',
            'owner': '客户成功团队',
            'timeline': '1个月',
            'expected_impact': '提升高价值客户留存率15%'
        },
        {
            'priority': '中',
            'action': '优化低评分品类的产品质量和服务',
            'owner': '产品团队',
            'timeline': '3个月',
            'expected_impact': '提升客户满意度10-15%'
        },
        {
            'priority': '中',
            'action': '实施客户活跃度提升计划',
            'owner': '运营团队',
            'timeline': '1个月',
            'expected_impact': '提高用户登录频率20%'
        },
        {
            'priority': '低',
            'action': '开展客户忠诚度调研',
            'owner': '市场研究团队',
            'timeline': '2个月',
            'expected_impact': '深入理解客户需求和痛点'
        }
    ]
    
    for rec in actionable_recommendations:
        print(f"[{rec['priority']}优先级] {rec['action']}")
        print(f"   负责人: {rec['owner']} | 时间: {rec['timeline']} | 预期效果: {rec['expected_impact']}\n")
    
    return insights

# ============================================================================
# 主函数：端到端分析流程
# ============================================================================

def main():
    """
    主函数：执行完整的客户数据分析流程
    """
    print("=" * 80)
    print("客户数据分析完整示例")
    print("=" * 80)
    
    try:
        # 第一阶段：数据准备
        print("\n【第一阶段】数据准备与生成...")
        customers_df, transactions_df, behaviors_df, churn_df = generate_sample_customer_data(1000)
        
        # 第二阶段：数据清洗
        print("\n【第二阶段】数据清洗与特征工程...")
        customer_features, cleaned_transactions = clean_and_prepare_data(
            customers_df, transactions_df, behaviors_df, churn_df
        )
        
        # 第三阶段：探索性分析
        print("\n【第三阶段】探索性数据分析...")
        enriched_features = exploratory_data_analysis(customer_features, cleaned_transactions)
        
        # 第四阶段：预测建模
        print("\n【第四阶段】预测性建模...")
        if 'churn' in enriched_features.columns:
            best_model, feature_names, all_results = predictive_modeling(enriched_features)
        else:
            best_model, feature_names, all_results = None, None, None
            print("跳过预测建模（无流失标签）")
        
        # 第五阶段：业务洞察
        print("\n【第五阶段】业务洞察生成...")
        insights = generate_business_insights(
            enriched_features, 
            best_model, 
            feature_names, 
            cleaned_transactions
        )
        
        # 第六阶段：结果保存
        print("\n【第六阶段】结果保存...")
        
        # 保存处理后的数据
        enriched_features.to_csv('processed_customer_data.csv', index=True, encoding='utf-8-sig')
        cleaned_transactions.to_csv('processed_transactions.csv', index=False, encoding='utf-8-sig')
        
        # 保存分析报告
        with open('analysis_report.md', 'w', encoding='utf-8') as f:
            f.write("# 客户数据分析报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 执行摘要\n\n")
            f.write("本报告通过端到端的数据分析流程，深入研究了客户行为、交易模式和流失风险。\n\n")
            
            f.write("## 关键发现\n\n")
            for i, insight in enumerate(insights[:5], 1):
                f.write(f"{i}. {insight['insight']}\n")
            
            f.write("\n## 详细分析\n\n")
            f.write("完整的分析过程包含以下步骤:\n")
            f.write("1. 数据生成与模拟\n")
            f.write("2. 数据清洗与预处理\n")
            f.write("3. 探索性数据分析\n")
            f.write("4. 预测性建模\n")
            f.write("5. 业务洞察提取\n\n")
            
            f.write("## 可视化文件\n\n")
            f.write("分析过程中生成的可视化文件:\n")
            f.write("- `visualizations/customer_distribution.png`: 客户分布分析\n")
            f.write("- `visualizations/transaction_analysis.png`: 交易行为分析\n")
            f.write("- `visualizations/rfm_analysis.png`: RFM客户价值分析\n")
            f.write("- `visualizations/correlation_heatmap.png`: 特征相关性分析\n")
            
            if best_model is not None:
                f.write("- `visualizations/confusion_matrix.png`: 模型混淆矩阵\n")
                f.write("- `visualizations/feature_importance.png`: 特征重要性分析\n")
                f.write("- `visualizations/roc_curve.png`: ROC曲线分析\n\n")
            
            f.write("## 数据文件\n\n")
            f.write("- `processed_customer_data.csv`: 处理后的客户特征数据\n")
            f.write("- `processed_transactions.csv`: 处理后的交易数据\n\n")
            
            f.write("## 使用说明\n\n")
            f.write("1. 所有Python代码已模块化，可直接复用\n")
            f.write("2. 数据生成部分可根据实际数据替换\n")
            f.write("3. 分析流程可根据具体业务需求调整\n")
        
        print("\n✓ 分析完成！")
        print("✓ 数据已保存: processed_customer_data.csv, processed_transactions.csv")
        print("✓ 报告已生成: analysis_report.md")
        print("✓ 可视化文件已保存到 visualizations/ 目录")
        
        # 显示一些关键统计
        print("\n" + "=" * 80)
        print("关键统计摘要:")
        print("=" * 80)
        
        if 'churn' in enriched_features.columns:
            churn_rate = enriched_features['churn'].mean() * 100
            print(f"• 客户总数: {len(enriched_features):,}")
            print(f"• 流失率: {churn_rate:.1f}%")
            print(f"• 流失客户数: {enriched_features['churn'].sum():,}")
        
        if 'total_spent' in enriched_features.columns:
            total_revenue = enriched_features['total_spent'].sum()
            avg_revenue = enriched_features['total_spent'].mean()
            print(f"• 总营收: ¥{total_revenue:,.2f}")
            print(f"• 客均营收: ¥{avg_revenue:,.2f}")
        
        if 'customer_segment' in enriched_features.columns:
            segment_counts = enriched_features['customer_segment'].value_counts()
            print("\n客户价值细分:")
            for segment, count in segment_counts.items():
                percentage = count / len(enriched_features) * 100
                print(f"  • {segment}: {count:,}人 ({percentage:.1f}%)")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n✗ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

# ============================================================================
# 执行分析
# ============================================================================

if __name__ == "__main__":
    print("开始执行客户数据分析示例...")
    success = main()
    
    if success:
        print("\n🎉 客户数据分析示例执行成功！")
        print("\n下一步建议:")
        print("1. 查看 analysis_report.md 了解详细分析结果")
        print("2. 查看 visualizations/ 目录下的图表文件")
        print("3. 使用实际业务数据替换示例数据进行真实分析")
        print("4. 根据业务需求调整分析流程和模型参数")
    else:
        print("\n❌ 客户数据分析示例执行失败")
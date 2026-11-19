#!/usr/bin/env python3
"""
aily-data-analysis 技能安装配置
"""

from setuptools import setup, find_packages
import os

# 读取版本信息
with open('VERSION', 'r') as f:
    version = f.read().strip()

# 读取长描述
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# 读取依赖
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='aily-data-analysis',
    version=version,
    author='Aily Team',
    author_email='support@aily.ai',
    description='专业级数据分析技能包，支持端到端的数据分析工作流',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/aily-team/aily-data-analysis',
    packages=find_packages(include=['scripts', 'scripts.*']),
    package_dir={'': '.'},
    include_package_data=True,
    
    # 数据文件
    package_data={
        '': [
            'assets/sample_datasets/*.csv',
            'references/*.md',
            'SKILL.md',
            'README.md',
            'requirements.txt'
        ]
    },
    
    # 安装依赖
    install_requires=requirements,
    
    # 可选依赖
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
        'docs': [
            'sphinx>=7.0.0',
            'sphinx-rtd-theme>=1.3.0',
            'myst-parser>=2.0.0',
        ],
        'full': [
            'torch>=2.0.0',
            'torchvision>=0.15.0',
            'geopandas>=0.13.0',
            'streamlit>=1.25.0',
            'dash>=2.14.0',
        ]
    },
    
    # 入口点
    entry_points={
        'console_scripts': [
            'aily-data-analysis=scripts.main:main',
            'data-cleaner=scripts.data_cleaning:cli_main',
            'feature-engineer=scripts.feature_engineering:cli_main',
        ],
    },
    
    # 分类信息
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    
    # 关键词
    keywords=[
        'data-analysis',
        'machine-learning',
        'data-science',
        'business-intelligence',
        'statistics',
        'visualization',
        'feishu',
        'lark',
        'aily'
    ],
    
    # 项目URL
    project_urls={
        'Documentation': 'https://docs.aily.ai/skills/data-analysis',
        'Source': 'https://github.com/aily-team/aily-data-analysis',
        'Tracker': 'https://github.com/aily-team/aily-data-analysis/issues',
        'Changelog': 'https://github.com/aily-team/aily-data-analysis/releases',
    },
    
    # 其他设置
    python_requires='>=3.9',
    zip_safe=False,
    
    # 许可证
    license='MIT',
    
    # 平台
    platforms=['any'],
)
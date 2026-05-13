#!/usr/bin/env python3
"""
Biostats终结者 - Python统计分析引擎
Complete Statistics Analysis Engine using Python (pandas, scipy, statsmodels)
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json
import io
from datetime import datetime

class BiostatsAnalyzer:
    """完整的生物统计分析引擎"""
    
    METHODS = {
        'descriptive': '描述性统计',
        'ttest': 't检验',
        'anova': '方差分析',
        'chi_square': '卡方检验',
        'correlation': '相关分析',
        'regression': '线性回归',
        'normality': '正态性检验',
        'nonparametric': '非参数检验'
    }
    
    def __init__(self):
        self.data = None
        self.results = {}
    
    def load_data(self, file_path):
        """加载数据文件"""
        file_path = Path(file_path)
        
        try:
            if file_path.suffix.lower() == '.csv':
                self.data = pd.read_csv(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                self.data = pd.read_excel(file_path)
            elif file_path.suffix.lower() == '.txt':
                # 尝试不同的分隔符
                self.data = pd.read_csv(file_path, sep=None, engine='python')
            else:
                return False, f"不支持的文件格式: {file_path.suffix}"
            
            return True, f"成功加载数据: {self.data.shape[0]}行 x {self.data.shape[1]}列"
        
        except Exception as e:
            return False, f"加载数据失败: {str(e)}"
    
    def descriptive_statistics(self, **kwargs):
        """描述性统计分析"""
        if self.data is None:
            return {'success': False, 'error': '未加载数据'}
        
        results = {
            'success': True,
            'method': '描述性统计',
            'summary': {}
        }
        
        # 基本信息
        results['summary']['数据维度'] = f"{self.data.shape[0]}行 x {self.data.shape[1]}列"
        results['summary']['变量列表'] = list(self.data.columns)
        
        # 数值型变量的统计
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            desc = self.data[numeric_cols].describe()
            results['numeric_summary'] = desc.to_dict()
            
            # 缺失值统计
            missing = self.data[numeric_cols].isnull().sum()
            results['missing_values'] = missing.to_dict()
        
        # 分类变量的统计
        categorical_cols = self.data.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            results['categorical_summary'] = {}
            for col in categorical_cols[:5]:  # 只显示前5个
                value_counts = self.data[col].value_counts().head(10)
                results['categorical_summary'][col] = value_counts.to_dict()
        
        # 生成文本报告
        report = self._generate_descriptive_report(results)
        results['report'] = report
        
        return results
    
    def t_test(self, **kwargs):
        """t检验"""
        if self.data is None:
            return {'success': False, 'error': '未加载数据'}
        
        var1 = kwargs.get('var1')
        var2 = kwargs.get('var2')
        group_var = kwargs.get('group_var')
        test_type = kwargs.get('test_type', 'independent')
        
        results = {
            'success': True,
            'method': 't检验',
            'test_type': test_type
        }
        
        try:
            if test_type == 'independent' and group_var:
                # 独立样本t检验
                groups = self.data[group_var].unique()
                if len(groups) != 2:
                    return {'success': False, 'error': '分组变量必须恰好有2个分组'}
                
                group1_data = self.data[self.data[group_var] == groups[0]][var1].dropna()
                group2_data = self.data[self.data[group_var] == groups[1]][var1].dropna()
                
                # 执行t检验
                t_stat, p_value = stats.ttest_ind(group1_data, group2_data)
                
                results['groups'] = {
                    str(groups[0]): {
                        'n': len(group1_data),
                        'mean': float(group1_data.mean()),
                        'std': float(group1_data.std())
                    },
                    str(groups[1]): {
                        'n': len(group2_data),
                        'mean': float(group2_data.mean()),
                        'std': float(group2_data.std())
                    }
                }
                
            elif test_type == 'paired' and var1 and var2:
                # 配对样本t检验
                data1 = self.data[var1].dropna()
                data2 = self.data[var2].dropna()
                
                # 确保长度相同
                min_len = min(len(data1), len(data2))
                data1 = data1[:min_len]
                data2 = data2[:min_len]
                
                t_stat, p_value = stats.ttest_rel(data1, data2)
                
                results['variables'] = {
                    var1: {'mean': float(data1.mean()), 'std': float(data1.std())},
                    var2: {'mean': float(data2.mean()), 'std': float(data2.std())}
                }
            
            elif test_type == 'one_sample' and var1:
                # 单样本t检验
                mu = kwargs.get('mu', 0)
                data = self.data[var1].dropna()
                
                t_stat, p_value = stats.ttest_1samp(data, mu)
                
                results['sample'] = {
                    'n': len(data),
                    'mean': float(data.mean()),
                    'std': float(data.std())
                }
                results['hypothesized_mean'] = mu
            
            else:
                return {'success': False, 'error': '参数不足或test_type错误'}
            
            results['t_statistic'] = float(t_stat)
            results['p_value'] = float(p_value)
            results['significant'] = p_value < 0.05
            
            # 生成文本报告
            report = self._generate_ttest_report(results)
            results['report'] = report
            
            return results
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def anova(self, **kwargs):
        """方差分析"""
        if self.data is None:
            return {'success': False, 'error': '未加载数据'}
        
        dependent_var = kwargs.get('dependent_var')
        group_var = kwargs.get('group_var')
        
        if not dependent_var or not group_var:
            return {'success': False, 'error': '需要指定dependent_var和group_var'}
        
        try:
            # 准备数据
            groups = []
            group_names = []
            for name, group in self.data.groupby(group_var):
                data = group[dependent_var].dropna()
                if len(data) > 0:
                    groups.append(data)
                    group_names.append(str(name))
            
            if len(groups) < 2:
                return {'success': False, 'error': '至少需要2个分组'}
            
            # 执行单因素方差分析
            f_stat, p_value = stats.f_oneway(*groups)
            
            results = {
                'success': True,
                'method': '单因素方差分析(ANOVA)',
                'dependent_var': dependent_var,
                'group_var': group_var,
                'f_statistic': float(f_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'groups': {}
            }
            
            # 各组统计
            for name, data in zip(group_names, groups):
                results['groups'][name] = {
                    'n': len(data),
                    'mean': float(data.mean()),
                    'std': float(data.std())
                }
            
            # 生成报告
            report = self._generate_anova_report(results)
            results['report'] = report
            
            return results
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def chi_square_test(self, **kwargs):
        """卡方检验"""
        if self.data is None:
            return {'success': False, 'error': '未加载数据'}
        
        var1 = kwargs.get('var1')
        var2 = kwargs.get('var2')
        
        if not var1 or not var2:
            return {'success': False, 'error': '需要指定两个分类变量'}
        
        try:
            # 创建列联表
            contingency_table = pd.crosstab(self.data[var1], self.data[var2])
            
            # 执行卡方检验
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
            
            results = {
                'success': True,
                'method': '卡方检验',
                'var1': var1,
                'var2': var2,
                'chi2_statistic': float(chi2),
                'p_value': float(p_value),
                'degrees_of_freedom': int(dof),
                'significant': p_value < 0.05,
                'contingency_table': contingency_table.to_dict()
            }
            
            # 生成报告
            report = self._generate_chi_square_report(results, contingency_table)
            results['report'] = report
            
            return results
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def correlation_analysis(self, **kwargs):
        """相关分析"""
        if self.data is None:
            return {'success': False, 'error': '未加载数据'}
        
        variables = kwargs.get('variables', [])
        method = kwargs.get('method', 'pearson')  # pearson, spearman, kendall
        
        try:
            # 如果没有指定变量，使用所有数值型变量
            if not variables:
                numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
                variables = numeric_cols[:10]  # 最多10个变量
            
            if len(variables) < 2:
                return {'success': False, 'error': '至少需要2个数值型变量'}
            
            # 计算相关系数矩阵
            data_subset = self.data[variables].dropna()
            
            if method == 'pearson':
                corr_matrix = data_subset.corr(method='pearson')
            elif method == 'spearman':
                corr_matrix = data_subset.corr(method='spearman')
            elif method == 'kendall':
                corr_matrix = data_subset.corr(method='kendall')
            else:
                return {'success': False, 'error': f'不支持的方法: {method}'}
            
            results = {
                'success': True,
                'method': f'相关分析 ({method})',
                'variables': variables,
                'correlation_matrix': corr_matrix.to_dict(),
                'n_samples': len(data_subset)
            }
            
            # 找出显著相关的变量对
            significant_pairs = []
            for i, var1 in enumerate(variables):
                for var2 in variables[i+1:]:
                    corr = corr_matrix.loc[var1, var2]
                    if abs(corr) > 0.3:  # 中等以上相关
                        significant_pairs.append({
                            'var1': var1,
                            'var2': var2,
                            'correlation': float(corr),
                            'strength': self._interpret_correlation(corr)
                        })
            
            results['significant_pairs'] = significant_pairs
            
            # 生成报告
            report = self._generate_correlation_report(results)
            results['report'] = report
            
            return results
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def linear_regression(self, **kwargs):
        """线性回归分析"""
        if self.data is None:
            return {'success': False, 'error': '未加载数据'}
        
        dependent_var = kwargs.get('dependent_var')
        independent_vars = kwargs.get('independent_vars', [])
        
        if not dependent_var or not independent_vars:
            return {'success': False, 'error': '需要指定因变量和自变量'}
        
        try:
            # 准备数据
            all_vars = [dependent_var] + independent_vars
            data_clean = self.data[all_vars].dropna()
            
            y = data_clean[dependent_var]
            X = data_clean[independent_vars]
            
            # 使用scipy进行简单线性回归（单变量）
            if len(independent_vars) == 1:
                x = X.iloc[:, 0]
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                results = {
                    'success': True,
                    'method': '简单线性回归',
                    'dependent_var': dependent_var,
                    'independent_var': independent_vars[0],
                    'n_samples': len(data_clean),
                    'slope': float(slope),
                    'intercept': float(intercept),
                    'r_squared': float(r_value ** 2),
                    'r_value': float(r_value),
                    'p_value': float(p_value),
                    'std_err': float(std_err),
                    'significant': p_value < 0.05
                }
                
                # 生成回归方程
                results['equation'] = f"{dependent_var} = {intercept:.4f} + {slope:.4f} * {independent_vars[0]}"
            
            else:
                # 多元回归需要使用numpy
                X_with_const = np.column_stack([np.ones(len(X)), X.values])
                beta = np.linalg.lstsq(X_with_const, y.values, rcond=None)[0]
                
                y_pred = X_with_const @ beta
                ss_total = np.sum((y - y.mean()) ** 2)
                ss_residual = np.sum((y - y_pred) ** 2)
                r_squared = 1 - (ss_residual / ss_total)
                
                results = {
                    'success': True,
                    'method': '多元线性回归',
                    'dependent_var': dependent_var,
                    'independent_vars': independent_vars,
                    'n_samples': len(data_clean),
                    'r_squared': float(r_squared),
                    'coefficients': {
                        'Intercept': float(beta[0])
                    }
                }
                
                for i, var in enumerate(independent_vars):
                    results['coefficients'][var] = float(beta[i + 1])
                
                # 生成方程
                eq_parts = [f"{beta[0]:.4f}"]
                for i, var in enumerate(independent_vars):
                    eq_parts.append(f"{beta[i+1]:.4f} * {var}")
                results['equation'] = f"{dependent_var} = " + " + ".join(eq_parts)
            
            # 生成报告
            report = self._generate_regression_report(results)
            results['report'] = report
            
            return results
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def normality_test(self, **kwargs):
        """正态性检验"""
        if self.data is None:
            return {'success': False, 'error': '未加载数据'}
        
        variable = kwargs.get('variable')
        
        if not variable:
            return {'success': False, 'error': '需要指定变量'}
        
        try:
            data = self.data[variable].dropna()
            
            if len(data) < 3:
                return {'success': False, 'error': '数据量太少'}
            
            # Shapiro-Wilk检验
            shapiro_stat, shapiro_p = stats.shapiro(data)
            
            # Kolmogorov-Smirnov检验
            ks_stat, ks_p = stats.kstest(data, 'norm', args=(data.mean(), data.std()))
            
            results = {
                'success': True,
                'method': '正态性检验',
                'variable': variable,
                'n_samples': len(data),
                'mean': float(data.mean()),
                'std': float(data.std()),
                'skewness': float(stats.skew(data)),
                'kurtosis': float(stats.kurtosis(data)),
                'shapiro_wilk': {
                    'statistic': float(shapiro_stat),
                    'p_value': float(shapiro_p),
                    'is_normal': shapiro_p > 0.05
                },
                'kolmogorov_smirnov': {
                    'statistic': float(ks_stat),
                    'p_value': float(ks_p),
                    'is_normal': ks_p > 0.05
                }
            }
            
            # 生成报告
            report = self._generate_normality_report(results)
            results['report'] = report
            
            return results
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def nonparametric_test(self, **kwargs):
        """非参数检验"""
        if self.data is None:
            return {'success': False, 'error': '未加载数据'}
        
        test_type = kwargs.get('test_type', 'mann_whitney')
        var1 = kwargs.get('var1')
        var2 = kwargs.get('var2')
        group_var = kwargs.get('group_var')
        
        try:
            if test_type == 'mann_whitney' and var1 and group_var:
                # Mann-Whitney U 检验（独立两样本）
                groups = self.data[group_var].unique()
                if len(groups) != 2:
                    return {'success': False, 'error': '分组变量必须恰好有2个分组'}
                
                group1_data = self.data[self.data[group_var] == groups[0]][var1].dropna()
                group2_data = self.data[self.data[group_var] == groups[1]][var1].dropna()
                
                u_stat, p_value = stats.mannwhitneyu(group1_data, group2_data)
                
                results = {
                    'success': True,
                    'method': 'Mann-Whitney U检验',
                    'variable': var1,
                    'groups': {
                        str(groups[0]): {
                            'n': len(group1_data),
                            'median': float(group1_data.median())
                        },
                        str(groups[1]): {
                            'n': len(group2_data),
                            'median': float(group2_data.median())
                        }
                    },
                    'u_statistic': float(u_stat),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                }
            
            elif test_type == 'wilcoxon' and var1 and var2:
                # Wilcoxon符号秩检验（配对样本）
                data1 = self.data[var1].dropna()
                data2 = self.data[var2].dropna()
                
                min_len = min(len(data1), len(data2))
                data1 = data1[:min_len]
                data2 = data2[:min_len]
                
                w_stat, p_value = stats.wilcoxon(data1, data2)
                
                results = {
                    'success': True,
                    'method': 'Wilcoxon符号秩检验',
                    'variables': [var1, var2],
                    'n_pairs': min_len,
                    'w_statistic': float(w_stat),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                }
            
            elif test_type == 'kruskal' and var1 and group_var:
                # Kruskal-Wallis H检验（多组比较）
                groups = []
                for name, group in self.data.groupby(group_var):
                    data = group[var1].dropna()
                    if len(data) > 0:
                        groups.append(data)
                
                h_stat, p_value = stats.kruskal(*groups)
                
                results = {
                    'success': True,
                    'method': 'Kruskal-Wallis H检验',
                    'variable': var1,
                    'n_groups': len(groups),
                    'h_statistic': float(h_stat),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                }
            
            else:
                return {'success': False, 'error': '参数不足或test_type错误'}
            
            # 生成报告
            report = self._generate_nonparametric_report(results)
            results['report'] = report
            
            return results
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ========== 报告生成方法 ==========
    
    def _generate_descriptive_report(self, results):
        """生成描述性统计报告"""
        report = []
        report.append("=" * 60)
        report.append("描述性统计分析报告")
        report.append("=" * 60)
        report.append(f"\n数据维度: {results['summary']['数据维度']}")
        report.append(f"变量数量: {len(results['summary']['变量列表'])}")
        
        if 'numeric_summary' in results:
            report.append("\n数值型变量统计摘要:")
            report.append("-" * 60)
            for var, stats_dict in list(results['numeric_summary'].items())[:5]:
                report.append(f"\n{var}:")
                report.append(f"  均值: {stats_dict.get('mean', 'N/A'):.4f}")
                report.append(f"  标准差: {stats_dict.get('std', 'N/A'):.4f}")
                report.append(f"  最小值: {stats_dict.get('min', 'N/A'):.4f}")
                report.append(f"  最大值: {stats_dict.get('max', 'N/A'):.4f}")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)
    
    def _generate_ttest_report(self, results):
        """生成t检验报告"""
        report = []
        report.append("=" * 60)
        report.append(f"{results['method']}分析报告 ({results['test_type']})")
        report.append("=" * 60)
        report.append(f"\nt统计量: {results['t_statistic']:.4f}")
        report.append(f"p值: {results['p_value']:.4f}")
        report.append(f"显著性 (α=0.05): {'是' if results['significant'] else '否'}")
        
        if 'groups' in results:
            report.append("\n组间统计:")
            for group, stats in results['groups'].items():
                report.append(f"\n{group}:")
                report.append(f"  样本量: {stats['n']}")
                report.append(f"  均值: {stats['mean']:.4f}")
                report.append(f"  标准差: {stats['std']:.4f}")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)
    
    def _generate_anova_report(self, results):
        """生成方差分析报告"""
        report = []
        report.append("=" * 60)
        report.append(f"{results['method']}报告")
        report.append("=" * 60)
        report.append(f"\nF统计量: {results['f_statistic']:.4f}")
        report.append(f"p值: {results['p_value']:.4f}")
        report.append(f"显著性 (α=0.05): {'是' if results['significant'] else '否'}")
        
        report.append("\n各组统计:")
        for group, stats in results['groups'].items():
            report.append(f"\n{group}:")
            report.append(f"  样本量: {stats['n']}")
            report.append(f"  均值: {stats['mean']:.4f}")
            report.append(f"  标准差: {stats['std']:.4f}")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)
    
    def _generate_chi_square_report(self, results, contingency_table):
        """生成卡方检验报告"""
        report = []
        report.append("=" * 60)
        report.append(f"{results['method']}报告")
        report.append("=" * 60)
        report.append(f"\nχ²统计量: {results['chi2_statistic']:.4f}")
        report.append(f"自由度: {results['degrees_of_freedom']}")
        report.append(f"p值: {results['p_value']:.4f}")
        report.append(f"显著性 (α=0.05): {'是' if results['significant'] else '否'}")
        
        report.append("\n列联表:")
        report.append(str(contingency_table))
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)
    
    def _generate_correlation_report(self, results):
        """生成相关分析报告"""
        report = []
        report.append("=" * 60)
        report.append(f"{results['method']}报告")
        report.append("=" * 60)
        report.append(f"\n样本量: {results['n_samples']}")
        report.append(f"分析变量: {', '.join(results['variables'])}")
        
        if results.get('significant_pairs'):
            report.append("\n显著相关的变量对 (|r| > 0.3):")
            for pair in results['significant_pairs']:
                report.append(f"\n{pair['var1']} vs {pair['var2']}:")
                report.append(f"  相关系数: {pair['correlation']:.4f}")
                report.append(f"  强度: {pair['strength']}")
        else:
            report.append("\n未发现显著相关的变量对")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)
    
    def _generate_regression_report(self, results):
        """生成回归分析报告"""
        report = []
        report.append("=" * 60)
        report.append(f"{results['method']}报告")
        report.append("=" * 60)
        report.append(f"\n样本量: {results['n_samples']}")
        report.append(f"R²: {results['r_squared']:.4f}")
        
        if 'p_value' in results:
            report.append(f"p值: {results['p_value']:.4f}")
            report.append(f"显著性: {'是' if results['significant'] else '否'}")
        
        report.append(f"\n回归方程:")
        report.append(f"{results['equation']}")
        
        if 'coefficients' in results:
            report.append("\n回归系数:")
            for var, coef in results['coefficients'].items():
                report.append(f"  {var}: {coef:.4f}")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)
    
    def _generate_normality_report(self, results):
        """生成正态性检验报告"""
        report = []
        report.append("=" * 60)
        report.append(f"{results['method']}报告")
        report.append("=" * 60)
        report.append(f"\n变量: {results['variable']}")
        report.append(f"样本量: {results['n_samples']}")
        report.append(f"均值: {results['mean']:.4f}")
        report.append(f"标准差: {results['std']:.4f}")
        report.append(f"偏度: {results['skewness']:.4f}")
        report.append(f"峰度: {results['kurtosis']:.4f}")
        
        report.append("\nShapiro-Wilk检验:")
        report.append(f"  统计量: {results['shapiro_wilk']['statistic']:.4f}")
        report.append(f"  p值: {results['shapiro_wilk']['p_value']:.4f}")
        report.append(f"  是否正态: {'是' if results['shapiro_wilk']['is_normal'] else '否'}")
        
        report.append("\nKolmogorov-Smirnov检验:")
        report.append(f"  统计量: {results['kolmogorov_smirnov']['statistic']:.4f}")
        report.append(f"  p值: {results['kolmogorov_smirnov']['p_value']:.4f}")
        report.append(f"  是否正态: {'是' if results['kolmogorov_smirnov']['is_normal'] else '否'}")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)
    
    def _generate_nonparametric_report(self, results):
        """生成非参数检验报告"""
        report = []
        report.append("=" * 60)
        report.append(f"{results['method']}报告")
        report.append("=" * 60)
        
        stat_name = [k for k in results.keys() if 'statistic' in k][0]
        report.append(f"\n{stat_name.replace('_', ' ').title()}: {results[stat_name]:.4f}")
        report.append(f"p值: {results['p_value']:.4f}")
        report.append(f"显著性 (α=0.05): {'是' if results['significant'] else '否'}")
        
        if 'groups' in results:
            report.append("\n组间统计:")
            for group, stats in results['groups'].items():
                report.append(f"\n{group}:")
                report.append(f"  样本量: {stats['n']}")
                report.append(f"  中位数: {stats['median']:.4f}")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)
    
    def _interpret_correlation(self, r):
        """解释相关系数强度"""
        abs_r = abs(r)
        if abs_r >= 0.7:
            return "强相关"
        elif abs_r >= 0.4:
            return "中等相关"
        elif abs_r >= 0.2:
            return "弱相关"
        else:
            return "极弱相关"
    
    def analyze(self, method, file_path, **kwargs):
        """执行分析的主接口"""
        # 加载数据
        success, message = self.load_data(file_path)
        if not success:
            return {'success': False, 'error': message}
        
        # 根据方法执行相应分析
        method_map = {
            'descriptive': self.descriptive_statistics,
            'ttest': self.t_test,
            'anova': self.anova,
            'chi_square': self.chi_square_test,
            'correlation': self.correlation_analysis,
            'regression': self.linear_regression,
            'normality': self.normality_test,
            'nonparametric': self.nonparametric_test
        }
        
        if method not in method_map:
            return {'success': False, 'error': f'不支持的分析方法: {method}'}
        
        return method_map[method](**kwargs)


# 测试代码
if __name__ == '__main__':
    analyzer = BiostatsAnalyzer()
    print("Biostats统计分析引擎已加载")
    print(f"支持的分析方法: {list(BiostatsAnalyzer.METHODS.keys())}")

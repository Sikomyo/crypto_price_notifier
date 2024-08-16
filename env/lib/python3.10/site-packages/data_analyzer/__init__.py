import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
from IPython.display import display
import scipy.stats as stats
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
from statsmodels.stats.outliers_influence import variance_inflation_factor


class DataAnalyzer:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.__categorical_vars = []
        self.__numeric_vars = []
        self.__unique_val_count_threshold = 5
        self.__detect_cat_num_vars()

    def __detect_cat_num_vars(self):
        dtypes = self.data.dtypes.astype('str')
        unique_val_count = self.__get_unique_value_count()
        dtypes = pd.concat([dtypes, unique_val_count], axis=1)
        dtypes.columns = ['type', 'unique_count']

        self.__numeric_vars = self.__numeric_vars + \
                              [*dtypes[dtypes['type'].str.contains('float', regex=False)].index]
        self.__categorical_vars = self.__categorical_vars + \
                                  [*dtypes[dtypes['type'].str.contains('object|category|bool', regex=True)].index]
        self.__numeric_vars = self.__numeric_vars + \
                              [*dtypes[(dtypes['type'].str.startswith('int')) &
                                       (dtypes['unique_count'] > self.__unique_val_count_threshold)].index]
        self.__categorical_vars = self.__categorical_vars + \
                                  [*dtypes[
                                      dtypes.index.isin(self.__numeric_vars + self.__categorical_vars) == False].index]

    def get_categorical_features_summary(self):
        """
        Get summary of categorical features.
        :return: None
        """
        if len(self.__categorical_vars) == 0:
            return "No Categorical Features Found"
        unique_val_count = self.__get_unique_value_count()
        missing_value_info = self.__get_missing_values_info()
        feature_dtypes = self.__get_feature_dtypes()
        for feature in self.__categorical_vars:
            feature_length = len(self.data[feature])
            print(f'\x1B[1m\033[94m{"-" * 60}\nFeature: {feature}\n{"-" * 60}\x1B[1m\n')
            print(f'\x1b[1;31mData Type:\n\x1b[0m {feature_dtypes[feature]}\n')
            print(f'\x1b[1;31mTotal Value Count (Excluding Missing Values):\n\x1b[0m {feature_length}\n')
            print(f'\x1b[1;31mUnique Value Count (Excluding Missing Value):\n\x1b[0m {unique_val_count[feature]}\n')
            if unique_val_count[feature] <= (feature_length * 0.5):
                print(f'\x1b[1;31mUnique Values:\n\x1b[0m {self.__get_unique_values_info(feature)}\n')
            print(f'\x1b[1;31mMissing Values:\n\x1b[0m {missing_value_info.loc[feature, "count"]} '
                  f'({missing_value_info.loc[feature, "proportion"]}%)\n')
            print(f'\x1b[1;31mData Distribution:\x1b[0m\n{self.__get_categorical_feature_distribution(feature)}')
            if unique_val_count[feature] <= 15:
                self.data[feature].value_counts().plot(kind='bar', title=f'{feature} Distribution', color='black')
                plt.ylabel('Frequency')
                plt.xlabel(feature)
                plt.show()
            else:
                print('')

    def get_numeric_features_summary(self):
        """
        Get summary of numeric features.
        :return: None
        """
        if len(self.__numeric_vars) == 0:
            return "No Numeric Features Found"
        for feature in self.__numeric_vars:
            summary_statistics = self.__get_summary_statistics(feature)
            print(f'\x1B[1m\033[94m{"-" * 60}\nFeature: {feature}\n{"-" * 60}\x1B[0m\n')
            for i in summary_statistics:
                print(f'\x1b[1;31m{i: <11} \x1b[0m {summary_statistics.get(i)}')
            print(f'\x1b[1;31m\nData Distribution\x1b[0m')
            self.__plot_numerical_feature_distribution(feature)

    def get_data_structure_summary(self):
        """
        Get summary of data set like shape, top 5, bottom 5, etc.
        :return: None
        """
        print(f'\x1B[1m\033[94m{"-" * 60}\nData Shape\n{"-" * 60}\x1B[0m')
        print(f'{self.data.shape[0]} Records & {self.data.shape[1]} Features\n')
        print(f'\x1B[1m\033[94m{"-" * 60}\nDuplicate Records\n{"-" * 60}\x1B[0m')
        self.__duplicate_records_count()
        print(f'\x1B[1m\033[94m{"-" * 60}\nTop 5 Rows (Transpose)\n{"-" * 60}\x1B[0m')
        display(self.__get_head().T)
        print(f'\n\x1B[1m\033[94m{"-" * 60}\nBottom 5 Rows (Transpose)\n{"-" * 60}\x1B[0m')
        display(self.__get_tail().T)
        print(f'\n\x1B[1m\033[94m{"-" * 60}\nFeature Data Types\n{"-" * 60}\x1B[0m')
        print(self.__get_feature_dtypes())
        print(f'\n\x1B[1m\033[94m{"-" * 60}\nCategorical Features\n{"-" * 60}\x1B[0m')
        print(self.get_categorical_features())
        print(f'\n\x1B[1m\033[94m{"-" * 60}\nNumeric Features\n{"-" * 60}\x1B[0m')
        print(self.get_numeric_features())
        print(f'\n\x1B[1m\033[94m{"-" * 60}\nMissing Values Info\n{"-" * 60}\x1B[0m')
        print(self.__get_missing_values_info())

    def __get_head(self):
        return self.data.head()

    def __get_tail(self):
        return self.data.tail()

    def __duplicate_records_count(self):
        duplicate_record_count = np.sum(self.data.duplicated())
        duplicate_record_percent = np.round((duplicate_record_count / len(self.data)) * 100, 2)
        print(f'{duplicate_record_count} ({duplicate_record_percent} %)\n')

    def __get_feature_dtypes(self):
        return self.data.dtypes

    def __get_missing_values_info(self):
        missing_values_count = pd.DataFrame(self.data.isna().sum())
        missing_values_prop = pd.DataFrame(np.round(self.data.isna().mean() * 100, 2))
        missing_values_df = pd.concat([missing_values_count, missing_values_prop], axis=1)
        missing_values_df.columns = ['count', 'proportion']
        missing_values_df = missing_values_df.sort_values(by='count', ascending=False).copy()
        return missing_values_df

    def __get_unique_values_info(self, feature):
        return sorted(self.data[feature].dropna().unique())

    def __get_unique_value_count(self):
        return self.data.apply(lambda col: len(set(col.dropna())))

    def get_categorical_features(self):
        """
        Get the list of categorical features.
        :return: list
        """
        return self.__categorical_vars

    def get_numeric_features(self):
        """
        Get the list of numeric features.
        :return: list
        """
        return self.__numeric_vars

    def set_categorical_features(self, features: list):
        """
        Manually set categorical features.
        :param features: list
        :return: None
        """
        self.__categorical_vars = features

    def set_numeric_features(self, features: list):
        """
        Manually set numeric features.
        :param features: list
        :return: None
        """
        self.__numeric_vars = features

    def __get_categorical_feature_distribution(self, feature):
        category_count = self.data[feature].value_counts()
        category_proportion = np.round(self.data[feature].value_counts(normalize=True), 2) * 100
        category_distribution = pd.concat([category_count, category_proportion], axis=1)
        category_distribution.columns = ['count', 'proportion']
        return category_distribution

    def plot_chi_square_result(self):
        """
        Plots a heatmap of chi-square test results among categorical features.
        :return: None
        """
        if len(self.__categorical_vars) <= 1:
            print("Couldn't Perform Chi-square Test\nReason: Count of Categorical Features is 1")
            return
        chi_square_result_list = []
        for i in range(len(self.__categorical_vars) - 1):
            for j in range(i + 1, len(self.__categorical_vars)):
                x = self.__categorical_vars[i]
                y = self.__categorical_vars[j]
                ct = pd.crosstab(columns=self.data[x], index=self.data[y])
                stat, p, dof, expected = chi2_contingency(ct)
                chi_square_result_list.append({'x': x,
                                               'y': y,
                                               'test_statistic': np.round(stat, 4),
                                               'p_value': np.round(p, 4)})
        chi_square_result_df = pd.DataFrame(chi_square_result_list)
        chi_square_result_df_1 = chi_square_result_df[['y', 'x', 'test_statistic', 'p_value']]
        chi_square_result_df_1.columns = chi_square_result_df.columns
        chi_square_result_df = pd.concat([chi_square_result_df, chi_square_result_df_1], axis=0)
        chi_square_result_df.sort_values(by='p_value', inplace=True)
        chi_square_result_df = chi_square_result_df.pivot(index='x', columns='y', values='p_value')
        self.__plot_heatmap(chi_square_result_df, 'chi-square test p-value', 'chi')

    def __get_summary_statistics(self, feature):
        summary_statistics_dict = {}
        if feature in self.__numeric_vars:
            feature_series = self.data[feature].dropna()
            mean = np.mean(feature_series)
            median = np.median(feature_series)
            maximum = np.max(feature_series)
            minimum = np.min(feature_series)
            range_ = maximum - minimum
            stdev = np.std(feature_series)
            coeff_of_variation = stats.variation(feature_series)
            q1 = np.quantile(feature_series, 0.25)
            q3 = np.quantile(feature_series, 0.75)
            iqr = q3 - q1
            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)
            skewness = stats.skew(feature_series)
            kurtosis = stats.kurtosis(feature_series)
            summary_statistics_dict['unique'] = len(feature_series.unique())
            summary_statistics_dict['mean'] = mean
            summary_statistics_dict['median'] = median
            summary_statistics_dict['minimum'] = minimum
            summary_statistics_dict['maximum'] = maximum
            summary_statistics_dict['range'] = range_
            summary_statistics_dict['stdev'] = stdev
            summary_statistics_dict['CV'] = coeff_of_variation
            summary_statistics_dict['q1'] = q1
            summary_statistics_dict['q2'] = median
            summary_statistics_dict['q3'] = q3
            summary_statistics_dict['iqr'] = iqr
            summary_statistics_dict['lower_bound'] = lower_bound
            summary_statistics_dict['upper_bound'] = upper_bound
            summary_statistics_dict['skewness'] = skewness
            summary_statistics_dict['kurtosis'] = kurtosis
            summary_statistics_dict = {key: np.round(summary_statistics_dict[key], 4) for key in
                                       summary_statistics_dict}
            summary_statistics_dict['dtype'] = feature_series.dtype
            return summary_statistics_dict
        return 'Not a Numeric Feature'

    def __plot_numerical_feature_distribution(self, feature):
        if feature in self.__numeric_vars:
            fig, ax = plt.subplots(1, 3, figsize=(16, 5))
            self.data[feature].plot(kind='hist', ax=ax[0], color='black')
            self.data[feature].plot(kind='kde', ax=ax[1], color='black')
            self.data[feature].plot(kind='box', ax=ax[2], color='black')
            plt.show()
        else:
            return 'Not a Numeric Feature'

    def plot_correlation_matrix(self):
        """
        Plots Pearson and Spearman correlation heatmap among numeric variables.
        :return: None
        """
        pearson_correlation_matrix = self.data[self.__numeric_vars].corr(method="pearson")
        spearman_correlation_matrix = self.data[self.__numeric_vars].corr(method="spearman")
        self.__plot_heatmap(pearson_correlation_matrix, 'Pearson Correlation')
        self.__plot_heatmap(spearman_correlation_matrix, 'Spearman Correlation')

    @staticmethod
    def __plot_heatmap(matrix, title, plot_type='corr'):
        font_size = 12
        fmt = '.2f'
        size_adj = 1.5
        if plot_type != 'corr':
            font_size = 10
            fmt = '.4f'
            size_adj = 1.2
        _ = plt.figure(figsize=(len(matrix) / size_adj, len(matrix) / size_adj))
        sns.heatmap(matrix, cbar=False, annot=True, mask=np.triu(np.ones_like(matrix, dtype=bool)),
                    fmt=fmt, linecolor='black', cmap=['white'], square=True, annot_kws={"size": font_size},
                    linewidths=0.01)
        plt.title(title)
        plt.xlabel("")
        plt.ylabel("")
        plt.show()

    def plot_numeric_vs_numeric(self):
        """
        Plots scatter plots between every numeric feature.
        :return: None
        """
        if len(self.__numeric_vars) <= 1:
            print("Couldn't Plot\nReason: Count of Numeric Features is 1")
            return
        n_num_vars = len(self.__numeric_vars)
        n_plots = n_num_vars * (n_num_vars - 1)
        n_plots = n_plots if (n_plots % 2 == 0) else n_plots + 1
        fig, ax = plt.subplots(int(n_plots / 2), 2, figsize=(16, n_plots * 3), sharex="none", sharey="none")
        row = col = count = 0
        for i in range(len(self.__numeric_vars) - 1):
            for j in range(i + 1, len(self.__numeric_vars)):
                for k in range(2):
                    if k == 0:
                        x = self.data[self.__numeric_vars[i]]
                        y = self.data[self.__numeric_vars[j]]
                    else:
                        y = self.data[self.__numeric_vars[i]]
                        x = self.data[self.__numeric_vars[j]]
                    ax[row, col].scatter(x=x,
                                         y=y, color='black')
                    ax[row, col].set_xlabel(x.name)
                    ax[row, col].set_ylabel(y.name)
                    ax[row, col].set_title(f'{x.name} vs {y.name}')
                    count += 1
                    col += 1
                    if count % 2 == 0:
                        row += 1
                        col = 0
        if (count % 2) != 0:
            ax[row, 1].axis("off")
        plt.show()

    def plot_categorical_vs_categorical(self, colormap: str = 'Pastel1'):
        """
        Plots stacked bar charts between every categorical feature having <= 8 categories.
        :param colormap: colormap to apply to the plots
        :return:
        """
        if len(self.__categorical_vars) <= 1:
            print("Couldn't Plot\nReason: Count of Categorical Features is 1")
            return
        cat_unique_cnt = self.data[self.__categorical_vars].apply(lambda c: len(set(c.dropna())))
        cat_vars_plot = [*cat_unique_cnt[cat_unique_cnt <= 8].index]
        n_num_vars = len(cat_vars_plot)
        n_plots = n_num_vars * (n_num_vars - 1)
        n_plots = n_plots if (n_plots % 2 == 0) else n_plots + 1
        fig, ax = plt.subplots(int(n_plots / 2), 2, figsize=(16, n_plots * 3.5), sharex='none', sharey='none')
        row = col = count = 0
        for i in range(len(cat_vars_plot) - 1):
            for j in range(i + 1, len(cat_vars_plot)):
                for k in range(2):
                    if k == 0:
                        x = cat_vars_plot[i]
                        y = cat_vars_plot[j]
                    else:
                        y = cat_vars_plot[i]
                        x = cat_vars_plot[j]

                    cross_tab = pd.crosstab(index=self.data[x], columns=self.data[y])
                    cross_tab_prop = pd.crosstab(index=self.data[x], columns=self.data[y], normalize='index')
                    cross_tab_prop.plot(kind='barh', stacked=True, ax=ax[row, col],
                                        title=f'{x} vs {y}', colormap=colormap, edgecolor='black')
                    ax[row, col].legend(loc="upper left", fontsize="small", ncol=7, framealpha=0.9)
                    for n_, x_ in enumerate([*cross_tab.index.values]):
                        for (proportion, y_loc) in zip(cross_tab_prop.loc[x_],
                                                       cross_tab_prop.loc[x_].cumsum()):
                            if np.round(proportion * 100, 1) > 5:
                                ax[row, col].text(y=n_ - 0.1,
                                                  x=(y_loc - proportion) + (proportion / 2) - 0.03,
                                                  s=f'{np.round(proportion * 100, 1)}%',
                                                  fontsize=9)
                    count += 1
                    col += 1
                    if count % 2 == 0:
                        row += 1
                        col = 0
        if (count % 2) != 0:
            ax[row, 1].axis("off")
        plt.show()

    def plot_mutual_information(self, target: str):
        """
        Plots a bar chart of mutual information scores of all features with target.
        :param target: target variable
        :return: DataFrame
        """
        df = self.data.copy()
        df.dropna(inplace=True)
        x = df.drop(columns=[target]).copy()
        y = df[target].copy()
        is_cat = 0
        if target in self.__categorical_vars:
            is_cat = 1
            y, _ = y.factorize()
        for i in x.select_dtypes("object"):
            x[i], _ = x[i].factorize()
        discrete_features = x.dtypes == int
        if is_cat == 1:
            mutual_info = mutual_info_classif(X=x, y=y, discrete_features=discrete_features, random_state=42)
        else:
            mutual_info = mutual_info_regression(X=x, y=y, discrete_features=discrete_features, random_state=42)
        mutual_info_df = pd.DataFrame({'feature': x.columns, 'MI': mutual_info}).sort_values(by='MI', ascending=False)
        mutual_info_df.sort_values(by='MI').plot(x='feature', y='MI', kind='barh', figsize=(16, x.shape[1] / 2),
                                                 color='black', title='Mutual information')
        for n, k in enumerate(range((len(mutual_info_df) - 1), -1, -1)):
            plt.text(y=n - 0.01, x=mutual_info_df.iloc[k, 1], s=np.round(mutual_info_df.iloc[k, 1], 4))
        plt.legend().remove()
        plt.show()
        return mutual_info_df

    def get_vif(self):
        """
        Returns a data frame of VIF score of each numeric variable
        :return: DataFrame
        """
        if len(self.__numeric_vars) <= 1:
            print("Couldn't Compute VIF\nReason: Count of Numeric Features is 1")
            return
        x_vif = self.data[self.__numeric_vars].copy()
        x_vif.dropna(inplace=True)
        vif = [variance_inflation_factor(x_vif.values, i) for i in range(x_vif.shape[1])]
        vif_df = pd.DataFrame({'feature': x_vif.columns, 'vif': vif}, index=range(len(vif)))
        vif_df.sort_values(by='vif', ascending=False, inplace=True)
        vif_df = vif_df.reset_index(drop=True)
        display(vif_df)
        return vif_df

    def plot_categorical_vs_numeric(self):
        """
        Plots violin plots between every numeric and categorical feature having <= 8 categories.
        :return: None
        """
        if len(self.__numeric_vars) == 0:
            print("Couldn't Plot\nReason: No Numeric Features")
            return
        if len(self.__categorical_vars) == 0:
            print("Couldn't Plot\nReason: No Categorical Features")
            return
        cat_unique_cnt = self.data[self.__categorical_vars].apply(lambda c: len(set(c.dropna())))
        n_num_vars = len(self.__numeric_vars)
        cat_vars_plot = [*cat_unique_cnt[cat_unique_cnt <= 8].index]
        n_cat_vars = len(cat_vars_plot)
        n_plots = n_num_vars * n_cat_vars
        n_plots = n_plots if (n_plots % 2 == 0) else n_plots + 1
        fig, ax = plt.subplots(int(n_plots / 2), 2, figsize=(16, n_plots * 3.5), sharex="none", sharey="none")
        row = col = count = 0
        for x in cat_vars_plot:
            for y in self.__numeric_vars:
                sns.violinplot(x=x, y=y, data=self.data, ax=ax[row, col], palette=["gray", "lightgray"])
                ax[row, col].set_xlabel(x)
                ax[row, col].set_ylabel(y)
                ax[row, col].set_title(f'{x} vs {y}')
                count += 1
                col += 1
                if count % 2 == 0:
                    row += 1
                    col = 0
        if (count % 2) != 0:
            ax[row, 1].axis("off")
        plt.show()

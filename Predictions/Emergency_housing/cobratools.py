import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class PrinterStyle():
    """
    Contains functions to apply a custom style to pandas' print outputs
    and functions to print with a predefined style (e.g. titles)
    """
    def __init__(self, n_line_jumps=2):
        self.n_line_jumps = n_line_jumps

    def title(self, str_title):
        """
        Print title with space and a delimiter for
        a clear display of info
        """
        delimiter = "-" * len(str_title)
        line_jumps = "\n" * self.n_line_jumps
        print("{line_jumps}"
            "{title}\n"
            "{delim}"
            "{line_jumps}"
            .format(title=str_title, delim=delimiter, line_jumps=line_jumps))


class Analysis():
    """
    Apply predefined analysis methods and graphs
    """
    def __init__(self, df):
        self.df = df
        self.printer = PrinterStyle()

    def describe(self, investigation_level=2):
        """
        Overview of shape, features, header and statistics
        investigation_level: int in [1, 2]
        """
        # Display shape and list features
        self.printer.title("Properties")
        print("- Shape: {shape}\n\n"
              "- Features: {features}"
              .format(shape=self.df.shape,
              features=self.df.columns.values))
        
        # Display data header
        if investigation_level > 1:
            self.printer.title("Header")
            print(self.df.head())
        
        # Display complementary stats
        if investigation_level > 2:
            self.printer.title("Correlations")
            print(self.df.corr())
            self.printer.title("Median")
            print(self.df.median())
            self.printer.title("Skewness")
            print(self.df.skew())
            self.printer.title("Kurtosis")
            print(self.df.kurtosis())


    def export_data(self, file_name='data.csv'):
        """ Export data to csv file """
        self.df.to_csv(file_name, index=False, index_label=False)


    def get_col_uniques(self, col, dropna=True):
        """
        Returns the set of unique values for the given column
        """
        if dropna:
            return self.df[col].dropna().unique()
        else:
            return self.df[col].unique()

    
    def get_cols_type(self):
        """
        Detect features' category
        - date
        - num
        - bool
        - cat_few
        - cat_med
        - cat_many
        - (not_recognized)
        - (empty)

        input: df with columns of a single type (can still have NaNs)

        output: list containing the type for each feature
        """
        list_types = []

        for feature in self.df:
            # Retrieve unique values for the feature
            ft_set = self.get_col_uniques(feature)
            
            # Numeric types / bool
            if isinstance(ft_set[0], (np.integer, np.float)):
                if len(ft_set) == 1:
                    list_types.append('empty')
                elif len(ft_set) == 2:
                    list_types.append('bool')
                else:
                    list_types.append('num')
            else:
                try:
                    # Date type
                    isinstance(pd.to_datetime(ft_set[0]), pd.datetime)
                    list_types.append('date')
                except:
                    if isinstance(ft_set[0], str):
                        if len(ft_set) == 1:
                            list_types.append('empty')
                        elif len(ft_set) == 2:
                            list_types.append('bool')
                        elif len(ft_set) <= 10:
                            list_types.append('cat_few')
                        elif len(ft_set) <= 30:
                            list_types.append('cat_med')
                        else:
                            list_types.append('cat_many')
                    else:
                        list_types.append('not_recognized')
        
        return list_types


    def preprocess_all(self, true_val='t', false_val='f'):
        """
        Preprocess all columns

        - bools: replace string 't' 'f' by True False equivalents
        - cat_few: replace strings by one-hot encodings

        Other types are left to manual preprocessing

        Ps: Apply only if database is congruent (always the same strings
        are used for true/false)
        """
        # Preprocess booleans
        for col, col_type in zip(self.df, self.get_cols_type()):
            if col_type == 'bool':
                self.preprocess_col_bool(col=col, true_val=true_val, false_val=false_val)
            elif col_type == 'cat_few':
                self.preprocess_col_cat(col=col)


    def preprocess_col_bool(self, col, true_val='t', false_val='f'):
        """
        Replace all boolean values of a column by True and False
        
        Ps: inplace operation
        """
        self.df.replace(true_val, int(1), inplace=True)
        self.df.replace(false_val, int(0), inplace=True)


    def preprocess_col_cat(self, col):
        """
        Replace col (contains categories) by one-hot-encodings
        
        Ps: inplace operation
        """
        df_dummies = pd.get_dummies(self.df[col], prefix=col+'_cat')
        self.df = pd.concat([self.df, df_dummies], axis=1)
        self.df.drop([col], axis=1, inplace=True)


    def visualize(self, investigation_level=1, subplot_n_cols_limit=3, barplot_n_classes_limit=10):
        """
        Plot main features
        """
        # Show histograms of numeric features
        # -----------------------------------

        n_features_numeric = self.df.select_dtypes(include=['number']).shape[1]
        
        # Generate subplot grid
        fig, axes = self.generate_subplot_grid(n_features_numeric, subplot_n_cols_limit)

        # Generate subplots
        for i_feature, str_feature in enumerate(self.df.select_dtypes(include=['number'])):
            n_row = self.get_row_n(i_feature + 1, subplot_n_cols_limit)
            n_col = self.get_col_n(i_feature + 1, subplot_n_cols_limit)
            
            # Plot by referencing to a grid of either 1 or 2 dimensions
            if n_features_numeric > subplot_n_cols_limit:
                self.df[str_feature].plot.hist(ax=axes[n_row-1, n_col-1], title=str_feature)
            else:
                self.df[str_feature].plot.hist(ax=axes[n_col-1], title=str_feature)
        plt.show()

        # Show bar plots of categorical features
        # --------------------------------------  
      
        # Assess total number of features to plot, since some cant be plot
        n_features_class = 0
        for str_feature in self.df.select_dtypes(include=['object']):
            # Only plot if number of classes < plot_limit_n_classes
            if pd.get_dummies(self.df[str_feature]).shape[1] < barplot_n_classes_limit:
                n_features_class += 1

        # Generate subplot grid
        fig, axes = self.generate_subplot_grid(n_features_class, subplot_n_cols_limit)

        # Generate subplots
        n_passed = 0
        for i_feature, str_feature in enumerate(self.df.select_dtypes(include=['object'])):
            
            # Only plot if number of classes < plot_limit_n_classes
            if pd.get_dummies(self.df[str_feature]).shape[1] < barplot_n_classes_limit:
                n_row = self.get_row_n(i_feature + 1 - n_passed, subplot_n_cols_limit)
                n_col = self.get_col_n(i_feature + 1 - n_passed, subplot_n_cols_limit)
                
                # Plot by referencing to a grid of either 1 or 2 dimensions
                if n_features_class > subplot_n_cols_limit:
                    pd.get_dummies(self.df[str_feature]).sum()\
                    .plot.bar(ax=axes[n_row-1, n_col-1], title=str_feature)
                else:
                    pd.get_dummies(self.df[str_feature]).sum()\
                    .plot.bar(ax=axes[n_col-1], title=str_feature)
            else:
                # Not plotted because n_classes > plot_limit_n_classes
                n_passed += 1
        plt.show()


    @staticmethod
    def get_row_n(x, n):
        return 1 + (x - 1) // n


    @staticmethod
    def get_col_n(x, n):
        return x + (-n * ((x - 1) // n))


    def generate_subplot_grid(self, n_features, subplot_n_cols_limit):
        """
        Generate a subplot grid with:
        - number of subplots = to n_features
        - disposition depending on subplot_n_cols_limit
        - grid size proportionnal to the number of subplots
        """
        # Compute limits for subplot grid
        n_rows_total = self.get_row_n(n_features, subplot_n_cols_limit)
        if n_features > subplot_n_cols_limit:
            n_cols_total = subplot_n_cols_limit
        else:
            n_cols_total = n_features

        # Define grid size
        fig_size = (4 + (1.3 * n_cols_total), 4 + (1 * n_rows_total))
        # Generate grid
        fig, axes = plt.subplots(nrows=n_rows_total, ncols=n_cols_total, figsize=fig_size)
        # Define subplots' size
        plt.subplots_adjust(hspace=0.15*n_rows_total, wspace=0.15*n_cols_total)
        
        return fig, axes

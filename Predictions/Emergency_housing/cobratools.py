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
        self.m = df.shape[0]
        self.n = df.shape[1]

        self.target = None
        self.default_na_vals = None
        
        self.printer = PrinterStyle()


    def describe(self, investigation_level=2, header=True):
        """
        Overview of shape, features, header and statistics
        investigation_level: int in [1, 2]

        header is to display preferably for slim datasets (very few columns)
        """
        # Display shape and list features
        self.printer.title("Properties")
        print("- Shape: {shape}\n\n"
              "- Features: {features}"
              .format(shape=self.df.shape,
              features=self.df.columns.values))
        
        # Display data header
        # TODO: create a nice display
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
        self.df.to_csv(file_name)


    def get_na_counts(self):
        """
        Returns the number of NAs for each feature 
        Returns only if NA count > 0
        - by feature
        - by sample
        """
        mask_na = self.df.isna()
        na_ft = mask_na.sum(axis=0)
        na_sp = mask_na.sum(axis=1)
        #na_ft[na_ft!=0], na_sp[na_sp!=0]

        return na_ft, na_sp


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
            
            # Pure boolean
            if isinstance(ft_set[0], np.bool_):
                list_types.append('bool')

            # Numeric types / bool
            elif isinstance(ft_set[0], (np.integer, np.float)):
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


    def set_default_na_vals(self):
        """
        Define the default values to replace if no other
        imputation method was defined for the case

        TODO: implement method to define default values
        - poor: overall average based on train set average
        - slightly better: average of a similar group
        """
        self.default_na_vals = self.df.dropna().iloc[0]


    def impute_child_to_come(self, df_indiv):
        """
        Specific method to impute child_to_come NaNs
        > Impute child_to_come from pregnancy in the group of indiv of the request
        """
        # Create mask that says if pregnancy true for each REQUEST (±1min)
        ma_child_t_c = df_indiv['pregnancy'].groupby(df_indiv['request_id']).apply(lambda x: max(x=='t'))

        # Sort request_train to match with the mask
        self.df.sort_index(inplace=True)

        # Control that indexes match perfectly
        if not sum(self.df.index != ma_child_t_c.index) == 0:
            print("Issue in matching of indexes, will certainly corrupt data")

        # Set child_to_come as True if pregnancy 't', False otherwise
        self.df['child_to_come'] = ma_child_t_c

        # Check that no NaN remains
        if not self.df['child_to_come'].isna().sum() == 0:
            print("NaNs remaining")
            


    def impute_na(self):
        """
        Method built essentially for in-production "test" samples.

        If no method was implemented to impute a given feature' value,
        set a default value to prevent interuption.
        Else, try to apply the methods in order of preference

        TODO: use self.default_na_vals[feature]
        """
        raise NotImplementedError


    def transform_categories(self, true_val='true', false_val='false', target=None):
        """
        Preprocess all columns

        - bools: replace string 't' 'f' by True False equivalents
        - cat_few: replace strings by one-hot encodings

        Other types are left to manual preprocessing

        Ps: Apply only if database is congruent (always the same strings
        are used for true/false)

        Return:
        - list of columns that failed transformation*
        - (list) mapping between true/false and old cat names*
        * for convert_to_bool only

        """
        list_failed = []
        mapping_true_false_cols = []

        # Transform each categorical column
        for col, col_type in zip(self.df, self.get_cols_type()):

            # Don't modify the target variable
            if not col == target:
                
                # Convert bool values with 
                if col_type == 'bool':
                    mapping_col, failed = self.convert_to_bool(col=col,
                                                    true_val=true_val,
                                                    false_val=false_val)

                    mapping_true_false_cols.append((mapping_col))

                    if failed:
                        list_failed.append(col)
                
                # Tranform to one-hot categories
                elif col_type == 'cat_few':
                    self.convert_to_onehot_enc(col=col)
        
        return mapping_true_false_cols, list_failed



    def convert_to_bool(self, col, true_val='true', false_val='false', verbose=True):
        """
        Replace boolean values of a column by 1 and 0
        
        Ps: inplace operation

        Return:
        - mapping_true_false
        - indication if failed
        """
        recognized = False
        uniques = self.get_col_uniques(col)

        # If bool vaues not recognized, try to recognize frequent ones
        if (not true_val in uniques) or (not false_val in uniques):
        
            # Force df unique values to be lower letters
            uniques_transfo = [str(val).lower() for val in uniques]

            # Frequent bool values to test
            freq_bools = [
                ('true', 'false'),
                ('t', 'f'),
                ('1', '0'),
                ('1.0', '1.0'),
                ('male', 'female'),
                ('yes', 'no')
            ]
            # Try to recognize one of these pairs
            for bools in freq_bools:

                # If pair is recognized => assign its values to true_val/false_val
                if bools[0] in uniques_transfo and bools[1] in uniques_transfo:
                    
                    # If true is in first position
                    if bools[0] == uniques_transfo[0]:
                        true_val = uniques[0]
                        false_val = uniques[1]
                    else:
                        true_val = uniques[1]
                        false_val = uniques[0]
                    
                    if verbose:
                        print("Transform Boolean at col {}: "
                                "True/False={}".format(col, uniques))
                    recognized = True
                    break

            if not recognized:
                if verbose:
                    print("\nERROR - Transform Boolean at col {} "
                            "not recognized: {}\n".format(col, uniques))
                
                return (np.nan, np.nan), True  # True means failed

        # Replace (recognized) bool values
        bools_map = {
            true_val: int(1),
            false_val: int(0)
        }
        self.df[col] = self.df[col].map(bools_map)
        
        # Cast new type
        self.df[col] = self.df[col].astype(np.bool_)

        return (true_val, false_val), False


    def convert_to_onehot_enc(self, col):
        """
        Replace col (contains categories) by one-hot-encodings
        
        Ps: inplace operation
        """
        df_dummies = pd.get_dummies(self.df[col], prefix=col+'_cat', dtype='bool')
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

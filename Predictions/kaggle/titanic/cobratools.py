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
        self.len = df.shape[0]
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
        if investigation_level == 2:
            self.printer.title("Header")
            print(self.df.head())
        
        # Display complementary stats
        if investigation_level == 3:
            self.printer.title("Correlations")
            print(self.df.corr())
            self.printer.title("Median")
            print(self.df.median())
            self.printer.title("Skewness")
            print(self.df.skew())
            self.printer.title("Kurtosis")
            print(self.df.kurtosis())


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

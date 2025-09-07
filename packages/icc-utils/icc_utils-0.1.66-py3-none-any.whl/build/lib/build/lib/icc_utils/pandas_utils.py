import pandas as pd


class PandasUtils:

    @staticmethod
    def set_print_options(max_columns=False, max_rows=False):
        """
        Sets print options for pandas DataFrames to control their display.

        This method allows for the customization of how pandas DataFrames are printed to the console, specifically regarding the maximum number of columns and rows displayed. It also adjusts the display width to accommodate more data horizontally and allows for longer column contents without truncation.

        Args:
            max_columns (bool): If True, displays all columns of the DataFrame. Otherwise, resets to the default pandas setting.
            max_rows (bool): If True, displays all rows of the DataFrame. Otherwise, resets to the default pandas setting.

        Note:
            This method modifies global pandas display settings that affect how DataFrames are printed. These changes will persist until they are explicitly reset or overridden.
        """

        if max_columns:
            pd.set_option('display.max_columns', None)
        else:
            pd.reset_option('display.max_columns')

        if max_rows:
            pd.set_option('display.max_rows', None)
        else:
            pd.reset_option('display.max_rows')

        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

    @staticmethod
    def place_column(df, column, before, after):
        """
        Reorders columns in a DataFrame by placing a specified column between two other specified, consecutive columns.

        This method modifies the column order of a pandas DataFrame by moving a specified column to a new position, ensuring it is placed directly after the 'before' column and before the 'after' column. The method validates that the 'before' and 'after' columns are consecutive and that the specified 'column' exists within the DataFrame.

        Args:
            df (pandas.DataFrame): The DataFrame whose columns are to be reordered.
            column (str): The name of the column to move.
            before (str): The name of the column after which the specified column will be placed. This and the 'after' column must be consecutive.
            after (str): The name of the column before which the specified column will be placed. This and the 'before' column must be consecutive.

        Returns:
            pandas.DataFrame: A DataFrame with the columns reordered according to the specified arrangement.

        Raises:
            ValueError: If the 'column' does not exist in the DataFrame, or if 'before' and 'after' are not consecutive columns.
        """

        cols = df.columns.tolist()

        # Check if the column to move exists
        if column not in cols:
            raise ValueError(f"The column '{column}' does not exist in the dataframe.")

        before_idx = cols.index(before)
        after_idx = cols.index(after)

        # Check if the columns are consecutive
        if after_idx - before_idx != 1:
            raise ValueError("The specified columns are not consecutive.")

        # Remove the column to move from its current position
        cols.remove(column)

        # Place the specified column between the specified columns
        new_position = before_idx + 1
        cols = cols[:new_position] + [column] + cols[new_position:]

        return df[cols]

    @staticmethod
    def df_memory_usage(df):
        """
        Calculates and returns the total memory usage of a pandas DataFrame in megabytes.

        This method computes the memory usage of all columns in the DataFrame, including the index and any object-type columns, and returns the total in a human-readable string format.

        Args:
            df (pandas.DataFrame): The DataFrame for which memory usage is to be calculated.

        Returns:
            str: A string representing the total memory usage of the DataFrame in megabytes, formatted to two decimal places.
        """
        return f"{df.memory_usage(deep=True).sum() / 1024 ** 2 : 3.2f} MB"

    @staticmethod
    def check_for_duplicates_values(df: pd.DataFrame, columns: list) -> None:
        """
        Checks for duplicate values in specified columns of a DataFrame and raises an exception if any are found.

        This method iterates through a list of columns in the given DataFrame, checking each for duplicate values.
        If duplicates are detected in any of the specified columns, the method prints the DataFrame,
        the list of duplicate values in the affected column, and raises a ValueError indicating in which column
        the duplicates were found.

        Args:
            df (pandas.DataFrame): The DataFrame to check for duplicate values.
            columns (list): A list of column names (str) to check for duplicates.

        Raises:
            ValueError: If duplicate values are found in any of the specified columns,
                        along with the name of the affected column and the list of duplicate values.
        """
        for column in columns:
            duplicate_values = df[df[column].duplicated()][column]
            if not duplicate_values.empty:
                print(f"Duplicate values found in column '{column}':\n{duplicate_values}")
                raise ValueError(f"Duplicate values found in column '{column}'")



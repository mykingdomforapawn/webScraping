def delete_rows_with(df, columns, strings=['']):
    """Drop rows that contain certain strings.

    Parameters:
        df (pd.DataFrame): Dataframe
        columns (list): Names of columns to search in
        string (list): Strings to search for

    Returns:
        data (pd.DataFrame): Dataframe

    Raises:
        None
    """
    # search columns for strings and drop rows
    for column in columns:
        for string in strings:
            df = df[df[column].str.contains(string) == False]

    # reset index
    df.reset_index(drop=True, inplace=True)

    return df


def delete_substrings(df, string='', regex=''):
    pass


def replace_substrings():
    pass

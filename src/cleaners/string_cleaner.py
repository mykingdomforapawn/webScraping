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


def delete_blank_rows(df, columns, dropNa=True, dropEmpty=True):
    """Drop rows that are missing or empty strings.

    Parameters:
        df (pd.DataFrame): Dataframe
        columns (list): Names of columns to search in
        dropNa (bool): Indicator for missing values
        dropEmpty (bool): Indicator for empty strings

    Returns:
        data (pd.DataFrame): Dataframe

    Raises:
        None
    """
    # drop missing values
    df.dropna(subset=columns, inplace=True)

    # drop empty strings
    for column in columns:
        df = df[~(df[column] == '')]

    # reset index
    df.reset_index(drop=True, inplace=True)

    return df


def delete_substrings(df, string='', regex=''):
    pass


def replace_substrings():
    pass

import re


def delete_rows_with_substring(df, columns, strings=['']):
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
    if dropNa:
        df.dropna(subset=columns, inplace=True)

    # drop empty strings
    if dropEmpty:
        for column in columns:
            df = df[~(df[column] == '')]

    # reset index
    df.reset_index(drop=True, inplace=True)

    return df


def replace_substring(df, columns, searchStrings=[""], replaceStrings=[""]):
    """Search and replace a substring in each cell.

    Parameters:
        df (pd.DataFrame): Dataframe
        columns (list): Names of columns to search in
        searchStrings (list): Strings to search for
        dreplaceStrings (list): Strings to replace them with

    Returns:
        data (pd.DataFrame): Dataframe

    Raises:
        None
    """
    # search dataframe for strings and replace them
    for index in range(len(searchStrings)):
        df[columns] = df[columns].applymap(
            lambda x: re.sub(searchStrings[index], replaceStrings[index], str(x)))
    return df


def replace_substrings():
    pass

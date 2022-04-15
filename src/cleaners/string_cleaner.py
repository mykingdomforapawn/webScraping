
# TODO doku einfügen ins file

def delete_rows_with(df, columns, strings=['']):
    for column in columns:
        for string in strings:
            df = df[df[column].str.contains(string) == False]
    df.reset_index(drop=True, inplace=True)
    return df

    pass


def delete_substrings(df, string='', regex=''):
    pass


def replace_substrings():
    pass

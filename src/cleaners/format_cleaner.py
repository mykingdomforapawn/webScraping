import unicodedata2 as uc


def unicode_to_ascii(data):
    """Turn strings into pure ascii format.

    Parameters:
        data (pd.DataFrame): Data from the wikipedia infobox

    Returns:
        data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    data = data.applymap(lambda x: uc.normalize('NFKC', str(x)))
    return data

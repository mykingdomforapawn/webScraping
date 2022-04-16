import warnings
from locale import currency

import pandas as pd

import cleaners.string_cleaner as sc
import scrapers.static_website_scraper as sws

# TODO: Bisschen Logging Nachrichten
# TODO: bei hier weiter machen: geokoordinaten beim capital rausnehmen


def get_states_list():
    """Scrape a list of states from Wikipedia.

    Parameters:
        None

    Returns:
        data (pd.DataFrame): Dataframe 

    Raises:
        None
    """
    # scrapte table of states
    scraped_tables = sws.scrape_tables(
        url="https://en.wikipedia.org/wiki/List_of_sovereign_states",
        table_attributes={'class': 'sortable wikitable'},
        append_links=True)

    # check validity of scraped table
    if len(scraped_tables) == 0:
        raise ValueError('no table found. adjust url or table attributes.')
    elif len(scraped_tables) != 1:
        warnings.warn(
            'more than one table found. first one was selected. adjust table attributes.')
    scraped_table = scraped_tables[0]

    # set up dataframe with selected data
    df = pd.DataFrame()
    df['name'] = scraped_table.iloc[1:, 0]
    df['links'] = scraped_table.iloc[1:, 4]
    df['sovereignityDispute'] = scraped_table.iloc[1:, 2] + \
        " - " + scraped_table.iloc[1:, 3]

    # clean dataframe
    df = sc.delete_rows_with_substring(
        df, columns=['name'], strings=['↓', '↑', '→'])
    df = sc.delete_blank_rows(
        df, columns=['name'], dropNa=True, dropEmpty=True)
    df.dropna(subset=['name'], inplace=True)
    df = sc.replace_substring(df, columns=['name', 'sovereignityDispute'], searchStrings=[
        "[\[].*?[\]]", " - $"], replaceStrings=["", ""])

    # select the first link and add domain name
    for index in range(df.shape[0]):
        df['links'].iloc[index] = "https://en.wikipedia.org/" + \
            df['links'].iloc[index][0]

    return df


def get_country_data(links):

    for index in range(links.shape[0]):
        # scrapte tables of specific country
        scraped_tables = sws.scrape_tables(
            url=links.iloc[index],
            table_attributes={'class': 'infobox'},
            append_links=True)

        # check validity of scraped table
        if len(scraped_tables) == 0:
            raise ValueError('no table found. adjust url or table attributes.')
        elif len(scraped_tables) != 1:
            warnings.warn(
                'more than one table found. first one was selected. adjust table attributes.')
        scraped_table = scraped_tables[0]

        # set up dataframe with selected data
        df_country = pd.DataFrame()
        df_country['link'] = links.iloc[index]

        # hier weiter

        #df3 = scraped_table[scraped_table.iloc[:, 0].str.contains('Capital')]

        #df['links'] = scraped_table.iloc[1:, 4]
        # df['sovereignityDispute'] = scraped_table.iloc[1:, 2] + \
        #    " - " + scraped_table.iloc[1:, 3]
        # capital and largest city
        # area total
        # population total
        # religion
        # language
        # currency

        print('jamoin')
    # scrapte table of states

    # hier liste an links eingen
    # sucht dann die daten und fügt sie an
    # das geht zurück und über die links werden dann die df s gematched
    pass


def get_country_flags(links):
    pass


def main():
    df = get_states_list()
    df_2 = get_country_data(df['links'])
    df.to_csv('data/export.csv', header=False, index=False, sep=';')

    print(df.head())
    print(df.iloc[10])
    print[df['links'].iloc[10][0]]


if __name__ == '__main__':
    main()

import warnings

import pandas as pd

import cleaners.string_cleaner as sc
import scrapers.static_website_scraper as sws

# TODO doku in dieses file einfügen
# TODOsr


def get_states_list():
    # scrapte table of states
    scraped_table = sws.scrape_tables(
        url="https://en.wikipedia.org/wiki/List_of_sovereign_states",
        table_attributes={'class': 'sortable wikitable'},
        append_links=True)

    # check validity of scraped table
    if len(scraped_table) == 0:
        raise ValueError('no table found. adjust url or table attributes.')
    elif len(scraped_table) != 1:
        warnings.warn(
            'more than one table found. first one was selected. adjust table attributes.')
    scraped_table = scraped_table[0]

    # set up dataframe to collect data
    df = pd.DataFrame()
    df['name'] = scraped_table.iloc[1:, 0]
    df['links'] = scraped_table.iloc[1:, 4]
    df['sovereignityDispute'] = scraped_table.iloc[1:, 2] + \
        " - " + scraped_table.iloc[1:, 3]

    # clean dataframe
    df = sc.delete_rows_with(df, columns=['name'], strings=['↓', '↑'])

    print('hello there')

    return df


def main():
    tab = get_states_list()
    # get links in
    # get list if states mit links in spalte 1
    # links 2
    # sov dispute 3


if __name__ == '__main__':
    main()

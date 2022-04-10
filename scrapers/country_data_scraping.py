import warnings

import static_website_scraper as sws


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
            'more than one table found. first one was selected. adjust table attributes')
    scraped_table = scraped_table[0]

    # set column names
    # hier neuen df aufsetzen mit column names und richtigem row index

    # filter relevant columns
    relevant_columns = ['Common and formal names', 'Sovereignty dispute',
                        'Further information on status and recognition of sovereignty']
    # damit dann df it nur den dreien
    # dann schauen, dass das über config datei ingelesen wird

    # filter relevant rows
    # die mit dem pfeil rausfiltern

    # TODO:schauen, dass die files eine struktur bekommen

    return scraped_table


def main():
    tab = get_states_list()
    # get links in
    # get list if states mit links in spalte 1
    # links 2
    # sov dispute 3


if __name__ == '__main__':
    main()

import warnings

import pandas as pd

import cleaners.string_cleaner as sc
import scrapers.static_website_scraper as sws


def get_states_list():
    """Scrape a list of states from Wikipedia.

    Parameters:
        None

    Returns:
        data (pd.DataFrame): Dataframe 

    Raises:
        ValueError: no table found using scape_tables()
        Warning: more than one table found using scrape_tables()
    """
    # write status to console
    print("started: get_states_list()")

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

    # write status to console
    print("finished: get_states_list()")

    return df


def get_state_attributes(link, attributes):
    """Scrape a attributes of a state from Wikipedia.

    Parameters:
        link (str): url to wikipedia page of state
        attributes (list): attributes to search for

    Returns:
        state_attributes (dict): key value pairs for state attributes

    Raises:
        ValueError: no table or match found when searching
        Warning: more than one or match table found when searching 
    """
    # write status to console
    print("started: get_state_attributes() for " + link)

    # scrape table of specific state
    scraped_table = sws.scrape_tables(
        url=link,
        table_attributes={'class': 'infobox'},
        append_links=False)

    # check validity of scraped table
    if len(scraped_table) == 0:
        raise ValueError('no table found. adjust url or table attributes.')
    elif len(scraped_table) != 1:
        warnings.warn(
            'more than one table found. first one was selected. adjust table attributes.')
    scraped_table = scraped_table[0]

    # set up dict for state attributes
    state_attributes = {'link': link}

    # search for pre-defined attributes
    for attribute in attributes:

        # adjust search behaviour if nested attribute
        if '_' in attribute:

            # match the first level of the attribute
            sub_attributes = attribute.split('_')
            first_level_match = scraped_table[scraped_table.iloc[:, 0].str.contains(
                sub_attributes[0], case=False)]

            # check validity of first level match
            if first_level_match.shape[0] == 0:
                raise ValueError(
                    'no match found for the first level of the nested attribute:' + attribute)
            elif first_level_match.shape[0] != 1:
                warnings.warn(
                    'more than one match found for first level of the nested attribute:' + attribute)

            # match the second level of the attribute
            first_level_match_table = scraped_table.iloc[first_level_match.index[0]:, :]
            second_level_match = first_level_match_table[first_level_match_table.iloc[:, 0].str.contains(
                sub_attributes[1], case=False)]

            # check validity of first level match
            if second_level_match.shape[0] == 0:
                raise ValueError(
                    'no match found for the second level of the nested attribute:' + attribute)

            # select first match as the final attribute match
            attribute_match = second_level_match

        else:
            # match the attribute
            attribute_match = scraped_table[scraped_table.iloc[:, 0].str.contains(
                attribute, case=False)]

            # check validity of found values
            if attribute_match.shape[0] == 0:
                raise ValueError(
                    'no match found for the attribute:' + attribute)
            elif attribute_match.shape[0] != 1:
                warnings.warn(
                    'more than ona match found for the attribute:' + attribute)

        # add attributes and values to dict
        state_attributes[attribute] = attribute_match.iloc[0, 1]

    return state_attributes


def get_state_flag(link):
    """Scrape an url for the flag of a state from Wikipedia.

    Parameters:
        link (str): url to wikipedia page of state

    Returns:
        state_flag (dict): key value pairs for state flag

    Raises:
        ValueError: no table or match found when searching
        Warning: more than one or match table found when searching 
    """
    # write status to console
    print("started: get_state_flag() for " + link)

    # scrape links of specific state
    scraped_links = sws.scrape_links(
        url=link,
        link_attributes={'class': 'image'})

    # search for link to the flag and check validity
    flag_match = scraped_links[scraped_links.iloc[:, 0].str.contains(
        'flag', case=False)]
    if flag_match.shape[0] == 0:
        raise ValueError(
            'no match found for the flag of:' + link)
    elif flag_match.shape[0] != 1:
        warnings.warn(
            'more than ona match found for the flag of:' + link)

    # scrape follow up links of an image to get the original
    scraped_links = sws.scrape_links(
        url='https://en.wikipedia.org/' + flag_match.iloc[0, 0],
        link_attributes={'class': 'internal'})

    # check validity of results
    if scraped_links.shape[0] == 0:
        raise ValueError(
            'no match found for the original link of the flag of:' + link)
    elif scraped_links.shape[0] != 1:
        warnings.warn(
            'more than ona match found for the original link of the flag of:' + link)

    # write url to flag to dict
    state_flag = {'flag': scraped_links['href'].iloc[0]}

    return state_flag


def get_state_map(link):
    """Scrape an url for the map of a state from Wikipedia.

    Parameters:
        link (str): url to wikipedia page of state

    Returns:
        state_map (dict): key value pairs for state map

    Raises:
        ValueError: no table or match found when searching
        Warning: more than one or match table found when searching 
    """
    # write status to console
    print("started: get_state_map() for " + link)

    # scrape links of specific state
    scraped_links = sws.scrape_links(
        url=link,
        link_attributes={'class': 'image'})

    # search for link to the map and check validity
    state_name = link.rsplit('/', 1)[-1]
    state_name = state_name.replace('_', ' ')
    map_match = [f for f in scraped_links.iloc[:, 0] if all(
        c in f for c in [state_name, 'orthographic_projection'])]
    if len(map_match) == 0:
        raise ValueError(
            'no match found for the map of:' + link)
    elif len(map_match) != 1:
        warnings.warn(
            'more than ona match found for the map of:' + link)

    # scrape follow up links of an image to get the original
    scraped_links = sws.scrape_links(
        url='https://en.wikipedia.org/' + map_match[0],
        link_attributes={'class': 'internal'})

    # check validity of results
    if scraped_links.shape[0] == 0:
        raise ValueError(
            'no match found for the original link of the flag of:' + link)
    elif scraped_links.shape[0] != 1:
        warnings.warn(
            'more than ona match found for the original link of the flag of:' + link)

    # write url to map to dict
    state_map = {'map': scraped_links['href'].iloc[0]}

    return state_map


def main():
    states_list = get_states_list()
    attributes = ['capital',
                  'largest city',
                  'language',
                  'religion',
                  'area_total',
                  'population_estimate',
                  'currency']
    states_dict = {}
    for state_link in states_list['links']:
        #state_attributes = get_state_attributes(state_link, attributes)
        #state_flag = get_state_flag(state_link)
        state_map = get_state_map(state_link)
        print('hi')

        # dicts zusammenhängen
        # state name und un status hinzufügen
        # dicts unter name des states in eine großes dict

    # dict of dict to dataframe
    # clean dataframe

    df.to_csv('data/export.csv', header=False, index=False, sep=';')

    print(df.head())
    print(df.iloc[10])
    print[df['links'].iloc[10][0]]


if __name__ == '__main__':
    main()

import warnings

import pandas as pd

import cleaners.string_cleaner as sc
import scrapers.static_website_scraper as sws

# TODO: search routine testen mit test urls und dabei die phrases anpassen
# gerade bei map
# funktioniert für afghanistan so gerade nicht gut
# ggfs besser, wenn man erst nach href sucht und dann erst nach title


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

    return df


def get_attributes_list():
    attributes = ['capital',
                  'largest city',
                  'language',
                  'religion',
                  'area_total',
                  'population_estimate',
                  'currency']

    return attributes


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
        table_attributes={'class': 'infobox ib-country vcard'},
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
            attribute_match = pd.DataFrame(
                [attribute_match.iloc[0, 0], attribute_match.iloc[:, 1].str.cat(sep=' ')]).T
            # elif attribute_match.shape[0] != 1:

        # add attributes and values to dict
        state_attributes[attribute] = attribute_match.iloc[0, 1]

    return state_attributes


def search_routine(series, phrases, index_start=0, index_stop=1):

    match = [s for s in series if all(
        sp in s for sp in phrases[index_start:index_stop])]

    if len(match) == 1:
        warnings.warn(
            'no distinct match found.')
        return match
    elif index_start == len(phrases)-1 or index_stop == len(phrases):
        return []
    elif len(match) > 1:
        match = search_routine(series, phrases, index_start, index_stop+1)
    elif len(match) == 0:
        match = search_routine(series, phrases, index_start+1, index_start+2)

    return match


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
    search_phrases = ['Flag', link.rsplit('/', 1)[-1]]
    flag_match = search_routine(
        scraped_links.iloc[:, 0], search_phrases)

    # scrape follow up links of an image to get the original
    scraped_links = sws.scrape_links(
        url='https://en.wikipedia.org/' + flag_match[0],
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

    # search for link to the map by title
    search_phrases = ['Location']
    map_match = search_routine(
        scraped_links['title'].astype(str), search_phrases)

    # get href of map match
    if len(map_match) == 1:
        map_match = scraped_links['href'][scraped_links['title']
                                          == map_match[0]].to_list()

    # search for link to the map by href
    else:
        search_phrases = ['orthographic', 'Location', link.rsplit('/', 1)[-1]]
        map_match = search_routine(
            scraped_links['href'], search_phrases)
        if len(map_match) == 0:
            raise ValueError(
                'no match found for the map of:' + link)

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


def test_some_url(url):
    attributes_list = get_attributes_list()
    state_dict = {'link': url}
    # state_dict.update(get_state_attributes(
    #    state_dict['link'], attributes_list))
    # state_dict.update(get_state_flag(state_dict['link']))
    state_dict.update(get_state_map(state_dict['link']))
    pass


def main():
    test_url = 'https://en.wikipedia.org/wiki/Afghanistan'
    test_some_url(test_url)

    # init dict to collect dicts of individual states
    states_dict = {}

    # scrape list of states and attributes to scrape for each state
    states_list = get_states_list()
    attributes_list = get_attributes_list()

    # iterate over states
    for _, row in states_list.iterrows():

        # collect data about an individual state
        state_dict = {'name': row['name'], 'link': row['links'],
                      'sovereignityDispute': row['sovereignityDispute']}
        state_dict.update(get_state_attributes(
            state_dict['link'], attributes_list))
        state_dict.update(get_state_flag(state_dict['link']))
        state_dict.update(get_state_map(state_dict['link']))

        # add state dict to a dict of all states
        states_dict[row['name']] = state_dict

        print('hi')

    # dict of dict to dataframe
    # clean dataframe

    df.to_csv('data/export.csv', header=False, index=False, sep=';')

    print(df.head())
    print(df.iloc[10])
    print[df['links'].iloc[10][0]]


if __name__ == '__main__':
    main()

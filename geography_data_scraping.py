import re
import urllib.parse
from datetime import date

import lxml
import numpy as np
import pandas as pd
import requests
import unicodedata2 as uc
from bs4 import BeautifulSoup

# next todos
# hier ein script schreiben, dass die anderen Sachen implementiert
# prüfen, ob man die anderen module benutzen kann
# ggfs. cleaning modul einbauen


def clean_tables(df_list):

    # hier über die parameter den ganzen Kram steuern, sodass es auf oerster ebene transparent isr
    # if hrefs and len(parsed_row) == 4 and '↓' not in str(parsed_row) and '↑' not in str(parsed_row):
    #    parsed_href = ['https://en.wikipedia.org' + href.get('href')]

    for i in range(5):
        print("hello")

    print("world")
    return df_list


def scrape_country_data(url, feature_list):
    """Extract the country data from the soup.

    Parameters:
        url (str): Url to a page with data from a country
        feature_list (pd.DataFrame): Features to extract from the data

    Returns:
        country_data (pd.DataFrame): Data about a country

    Raises:
        None
    """
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'lxml')
    infobox = soup.find('table', attrs={'class': 'infobox'})
    image_list = infobox.find_all('a', {'class': 'image'})
    parsed_images = get_country_images(image_list)
    tablerow_list = infobox.find_all('tr')
    parsed_text = get_country_text(tablerow_list)
    country_data = parsed_images.append(parsed_text, ignore_index=True)
    country_data = enrich_data(country_data, url, soup)
    return country_data


def get_country_images(image_list):
    """Parse images from the wikipedia infobox.

    Parameters:
        image_list (bs4.BeautifulSoup): The image elemets from the wikipedia infobox in html

    Returns:
        parsed_images (pd.DataFrame): Image data from the wikipedia infobox

    Raises:
        None
    """
    country_images = pd.DataFrame(columns=['category', 'feature', 'value'])
    for image_idx, image in enumerate(image_list):
        image_page = requests.get(
            'https://en.wikipedia.org' + image.get('href')).text
        image_soup = BeautifulSoup(image_page, 'lxml')
        image_source = image_soup.find_all(
            'a', href=True, text='Original file')
        if image_source == []:
            image_source = image_soup.find_all(
                'a', href=True, text=re.compile('.png'))
        if re.search('flag', image_source[0].get('href'), re.IGNORECASE):
            feature = 'Flag'
        elif re.search('emblem', image_source[0].get('href'), re.IGNORECASE):
            feature = 'Emblem'
        elif any(re.search(line, image_source[0].get('href'), re.IGNORECASE) for line in ['orthographic', 'globe', 'location', 'EU-', 'Europe-']):
            feature = 'Location'
        else:
            feature = image.get('title')
        country_images.loc[image_idx] = [
            'Image', feature, "<img src=https:"+image_source[0].get('href')+">"]
    return country_images


def get_country_text(tablerow_list):
    """Parse text from the wikipedia infobox.

    Parameters:
        tablerow_list (bs4.BeautifulSoup): The tablerows from the wikipedia infobox in html

    Returns:
        parsed_text (pd.DataFrame): Text data from the wikipedia infobox

    Raises:
        None
    """
    country_text = pd.DataFrame(columns=['category', 'feature', 'value'])
    for tablerow_idx, tablerow in enumerate(tablerow_list):
        country_text.loc[tablerow_idx] = [
            get_category(tablerow), get_feature(tablerow), get_value(tablerow)]
    return country_text


def get_category(tablerow):
    """Extract the category of a tablerow.

    Parameters:
        tablerow (bs4.BeautifulSoup): A tablerow from the wikipedia infobox in html

    Returns:
        category (str): Category of the tablerow

    Raises:
        None
    """
    if tablerow.get('class'):
        if tablerow.get('class')[0] == 'mergedtoprow':
            category = get_feature(tablerow)
        else:
            if tablerow.previous_sibling != None:
                category = get_category(tablerow.previous_sibling)
            else:
                category = get_feature(tablerow)
    else:
        category = get_feature(tablerow)
    return category


def get_feature(tablerow):
    """Extract the feature of a tablerow.

    Parameters:
        tablerow (bs4.BeautifulSoup): A tablerow from the wikipedia infobox in html

    Returns:
        feature (str): Feature of the tablerow

    Raises:
        None
    """
    tableheader = tablerow.find('th')
    if tableheader:
        feature = tableheader.text
    else:
        feature = ''
    return feature


def get_value(tablerow):
    """Extract the value of a tablerow.

    Parameters:
        tablerow (bs4.BeautifulSoup): A tablerow from the wikipedia infobox in html

    Returns:
        value (str): Value of the tablerow

    Raises:
        None
    """
    tabledata = tablerow.find('td')
    if tabledata:
        value = tabledata.get_text(separator=" ", strip=True)
    else:
        value = ''
    return value


def enrich_data(data, url, soup):
    """Enrich data with additional information.

    Parameters:
        data (pd.DataFrame): Data from the wikipedia infobox
        url (np.ndarray): String with url source
        soup (bs4.BeautifulSoup): The wikipedia page in html

    Returns:
        enriched_data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    data = add_url(data, url)
    enriched_data = add_country_name(data, soup)
    return enriched_data


def add_url(data, url):
    """Add url source and access date to data.

    Parameters:
        data (pd.DataFrame): Data from the wikipedia infobox
        url (np.ndarray): String with url source

    Returns:
        data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    today = date.today().strftime("(%d/%m/%Y)")
    data.loc[data.shape[0]] = ['Source', 'Source', url + ' ' + today]
    return data


def add_country_name(data, soup):
    """Add country name to data.

    Parameters:
        data (pd.DataFrame): Data from the wikipedia infobox
        soup (bs4.BeautifulSoup): The wikipedia page in html

    Returns:
        data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    infobox = soup.find('table', attrs={'class': 'infobox'})
    country_name = infobox.find_all('div', {'class': 'fn org country-name'})
    data.loc[data.shape[0]] = ['Country name',
                               'Country name', country_name[0].text]
    return data


def clean_data(data):
    """Clean data for further processing.

    Parameters:
        data (pd.DataFrame): Data from the wikipedia infobox

    Returns:
        data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    data = clean_unicode(data)
    data = clean_unwanted_characters(data)
    data = clean_source_brackets(data)
    data = clean_bracket_spaces(data)
    data = clean_geographic_coordinates(data)
    data = clean_sorting_markers(data)
    data = clean_constant_rows(data)
    data = clean_sorting_rows(data)
    return data


def clean_unicode(data):
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


def clean_unwanted_characters(data):
    """Clear unwanted characters from cells.

    Parameters:
        data (pd.DataFrame): Data from the wikipedia infobox

    Returns:
        data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    data = data.replace('[^a-zA-Z0-9()[]_,.:/\%$° ]', '', regex=True)
    data = data.replace('\u2022', '', regex=True)
    data = data.replace(' a$| b$| c$', '', regex=True)
    data = data.replace(' Coordinates :', '', regex=True)
    data = data.applymap(lambda x: x.strip())
    data = data.applymap(lambda x: urllib.parse.unquote(x))
    return data


def clean_source_brackets(data):
    """Clear source brackets and their content.

    Parameters:
        data (pd.DataFrame): Data from the wikipedia infobox

    Returns:
        data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    data = data.applymap(lambda x: re.sub("[\[].*?[\]]", "", x))
    return data


def clean_bracket_spaces(data):
    """Clear spaces in round brackets.

    Parameters:
        data (pd.DataFrame): Data from the wikipedia infobox

    Returns:
        data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    for label, content in data.iteritems():
        for item_idx, item in enumerate(content):
            if re.search("(?<=\().*?(?=\))", item):
                item = re.sub("(\(\s)", "(", item)
                item = re.sub("(\s\))", ")", item)
                data[label][data[label].index[item_idx]] = item
    return data


def clean_geographic_coordinates(data):
    """Clear geographic coordinates.

    Parameters:
        data (pd.DataFrame): Data from the wikipedia infobox

    Returns:
        data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    if 'feature' in data.columns:
        for feature in ['Capital', 'Largest city']:
            feature_idx = data.index[data['feature'].str.contains(
                feature, case=False)]
            if not feature_idx.empty:
                value = data['value'].loc[feature_idx].values[0]
                if re.search(r"\d", value):
                    value = value[0:re.search(r"\d", value).start()]
                    data['value'].loc[feature_idx] = value
    return data


def clean_sorting_markers(data):
    """Clear leftover html sorting markers.

    Parameters:
        data (pd.DataFrame): Data from the wikipedia infobox

    Returns:
        data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    data = data.replace(
        regex='^A +(?=[A-Z])|^B +(?=[A-Z])|^D +(?=[A-Z])', value='')
    return data


def clean_constant_rows(data):
    """Drop rows with constant calues.

    Parameters:
        data (pd.DataFrame): Data from an html table
    Returns:
        data (pd.DataFrame): Data from an html table

    Raises:
        None
    """
    data = data.transpose()
    data = data.loc[:, (data != data.iloc[0]).any()]
    data = data.transpose().reset_index(drop=True)
    return data


def clean_sorting_rows(data):
    """Drop rows that contain sorting characters.

    Parameters:
        data (pd.DataFrame): Data from an html table
    Returns:
        data (pd.DataFrame): Data from an html table

    Raises:
        None
    """
    data = data.transpose()
    columns_with_up_arrow = [data[column].str.contains(
        '↑').any() for column in data.columns]
    columns_with_down_arrow = [data[column].str.contains(
        '↓').any() for column in data.columns]
    columns_to_drop = list(
        map(any, zip(columns_with_up_arrow, columns_with_down_arrow)))
    columns_to_keep = np.logical_not(columns_to_drop)
    data = data.loc[:, columns_to_keep]
    data = data.transpose().reset_index(drop=True)
    return data


def filter_data(data, feature_list):
    """Filter data for relevant features.

    Parameters:
        data (pd.DataFrame): Data from the wikipedia infobox
        feature_list (pd.DataFrame): Features to extract from the data

    Returns:
        filtered_data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    filtered_data = pd.DataFrame(columns=['feature', 'value'])
    for feature in feature_list.values:
        feature_split = feature[0].split('_')
        for split_idx, split in enumerate(feature_split):
            feature_split[split_idx] = split.split('/')
        category_split_searchfor = '|'.join(feature_split[0])
        if len(feature_split) > 1:
            feature_split_searchfor = '|'.join(feature_split[1])
        else:
            feature_split_searchfor = category_split_searchfor
        found_data = data[data['feature'].str.contains(
            feature_split_searchfor, case=True, regex=True) & data['category'].str.contains(category_split_searchfor, case=True, regex=True)]
        if not found_data.empty:
            filtered_data.loc[filtered_data.shape[0]] = [
                feature[0], found_data['value'].values[0]]
    return filtered_data


def combine_data(country_list, data):
    connector_row = data.loc[data.feature == 'Source', 'value']
    connector = re.sub(
        ' \((.*?)\)', '', connector_row.loc[connector_row.index[0]])
    country_list_row = country_list.loc[country_list['url'] == connector]
    data.loc[data.feature == 'Country_name',
             'value'] = country_list_row['Common and formal names'].loc[country_list_row.index[0]]
    data.loc[data.shape[0]] = ['UN membership',
                               country_list_row['Membership within the UN System'].loc[country_list_row.index[0]]]
    if country_list_row['Further information on status and recognition of sovereignty'].loc[country_list_row.index[0]] == '':
        filler = ''
    else:
        filler = ': '
    data.loc[data.shape[0]] = ['Sovereignty dispute',
                               country_list_row['Sovereignty dispute'].loc[country_list_row.index[0]] + filler
                               + country_list_row['Further information on status and recognition of sovereignty'].loc[country_list_row.index[0]]]
    return data


def join_data(data, filtered_data):
    """Filter data for relevant features.

    Parameters:
        data (pd.DataFrame): Data from the wikipedia infobox

    Returns:
        filtered_data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    restructured_data = pd.DataFrame(columns=filtered_data.feature)
    restructured_data.loc[0] = filtered_data.value.values
    if data.empty:
        data = restructured_data
    else:
        data = pd.concat([data.reset_index(drop=True),
                          restructured_data.reset_index(drop=True)], axis=0)
        data.reset_index(inplace=True, drop=True)
    return data


def process_exceptions(country_data, country_list, feature_list):
    """Process exeptions that can't be covered by the general algorithms.
       With more time and effort, the scraping algorithms could be modified
       to make this function redundant.

    Parameters:
        country_data (pd.DataFrame): Data from the wikipedia infobox
        feature_list (pd.DataFrame): Features to extract from the data

    Returns:
        country_data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    country_data = process_exception_malaysia(country_data, feature_list)
    # country_data = process_exception_usa(country_data, feature_list)
    # country_data = process_exception_turkey(country_data, feature_list)
    country_data = process_exception_netherlands(
        country_data, country_list, feature_list)
    return country_data


def process_exception_turkey(country_data, feature_list):
    """Process exeptions for turkey. The category of 'Religion' does not exist, therefore, the data has
       to be scaped somewhere else.

    Parameters:
        country_data (pd.DataFrame): Data from the wikipedia infobox
        feature_list (pd.DataFrame): Features to extract from the data

    Returns:
        country_data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """

    # soll gucken, ob turkey existiert in country_data
    #   wenn ja, auf den entsprechenden anderen link (hardcode) gehen
    #  daten da runterladen
    # das in das feld hier schreiben

    # gucken, ob die anderen exceptions nach ähnlichem Prínzip funktionieren
    return country_data


def process_exception_usa(country_data, feature_list):
    """Process exeptions for the usa. The category of 'Religion' only has a link to
       another website. The text should not be shown.

    Parameters:
        country_data (pd.DataFrame): Data from the wikipedia infobox
        feature_list (pd.DataFrame): Features to extract from the data

    Returns:
        country_data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    url = 'https://en.wikipedia.org/wiki/United_States'
    print("\n* Processing exceptions from {0}".format(url))

    if country_data[country_data['Country_name'] == 'United States – United States of America']['Official language'].str.contains('None').all():
        country_data[country_data['Country_name'] ==
                     'United States – United States of America']['Official language'] = ''
    return country_data


def process_exception_malaysia(country_data, feature_list):
    """Process exeptions for malaysia. The category of 'Oficial language' is scaped
       incorrectly and therefore it is not found while filtering.

    Parameters:
        country_data (pd.DataFrame): Data from the wikipedia infobox
        feature_list (pd.DataFrame): Features to extract from the data

    Returns:
        country_data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    url = 'https://en.wikipedia.org/wiki/Malaysia'
    print("\n* Processing exceptions from {0}".format(url))
    data = scrape_country_data(url, feature_list)
    found_data = data[data['feature'].str.contains(
        'Official language', case=True, regex=True) & data['category'].str.contains('Capital', case=True, regex=True)]
    found_data = clean_data(found_data)
    if 'Official language' not in country_data.columns:
        country_data['Official language'] = np.full(
            country_data.shape[0], np.nan)
    country_data.loc[country_data['Source'].str.contains(
        url), 'Official language'] = found_data['value'].values[0]
    return country_data


def process_exception_netherlands(country_data, country_list, feature_list):
    """Process exeptions for the netherlands. The scraped link leads to the page
       of the kingdom of netherlands which includes the overseas territories. 

    Parameters:
        country_data (pd.DataFrame): Data from the wikipedia infobox
        feature_list (pd.DataFrame): Features to extract from the data

    Returns:
        country_data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    url = 'https://en.wikipedia.org/wiki/Netherlands'
    print("\n* Processing exceptions from {0}".format(url))
    data = scrape_country_data(url, feature_list)
    data = clean_data(data)
    data = filter_data(data, feature_list)
    idx = country_data['Country_name'] == 'Netherlands – Kingdom of the Netherlands'
    for column in data['feature']:
        country_data.loc[idx, column] = data.loc[data['feature']
                                                 == column]['value'].values[0]
    return country_data


def sort_data(country_data, feature_list):
    """Sort data according to the feature_list and add the rest of the columns to the end.

    Parameters:
        country_data (pd.DataFrame): Data from the wikipedia infobox
        feature_list (pd.DataFrame): Features to extract from the data

    Returns:
        country_data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    new_columns = []
    for feature in feature_list.iloc[:, 0]:
        if feature in country_data.columns:
            new_columns.append(feature)
    new_columns = new_columns + \
        list(set(country_data.columns).difference(
            set(feature_list.iloc[:, 0])))
    country_data = country_data.reindex(new_columns, axis=1)
    return country_data


def export_data(data):
    """Export data to a csv file.

    Parameters:
        country_data (pd.DataFrame): Data from the wikipedia infobox

    Returns:
        None

    Raises:
        None
    """
    data.to_csv('data.csv', header=False, index=False, sep=';')


def main():
    country_list_url = "https://en.wikipedia.org/wiki/List_of_sovereign_states"
    print("\n* Scraping country list data from {0}".format(country_list_url))
    #country_list = scrape_country_list(country_list_url)
    #country_list = clean_data(country_list)

    #print("\n* Reading feature list")
    #feature_list = pd.read_csv('feature_list.csv', header=None)

    #country_data = pd.DataFrame()
    # for url in country_list['url']:
    #    print("\n* Scraping country data from {0}".format(url))
    #    data = scrape_country_data(url, feature_list)
    #    data = clean_data(data)
    #    data = filter_data(data, feature_list)
    #    data = combine_data(country_list, data)
    #    country_data = join_data(country_data, data)
    #country_data = process_exceptions(country_data, country_list, feature_list)
    #country_data = sort_data(country_data, feature_list)
    # export_data(country_data)


def test_single_url():
    country_list_url = "https://en.wikipedia.org/wiki/List_of_sovereign_states"
    print("\n* Scraping country list data from {0}".format(country_list_url))
    #country_list = scrape_country_list(country_list_url)
    #country_list = clean_data(country_list)

    #print("\n* Reading feature list")
    #feature_list = pd.read_csv('feature_list.csv', header=None)

    #country_data = pd.DataFrame()
    #url = 'https://en.wikipedia.org/wiki/United_States'
    #print("\n* Scraping country data from {0}".format(url))
    #data = scrape_country_data(url, feature_list)
    #data = clean_data(data)
    #data = filter_data(data, feature_list)
    #data = combine_data(country_list, data)
    #country_data = join_data(country_data, data)
    #country_data = process_exceptions(country_data, country_list, feature_list)
    #country_data = sort_data(country_data, feature_list)
    # export_data(country_data)


if __name__ == '__main__':
    main()
    # test_single_url()

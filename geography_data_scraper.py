import re
from datetime import date

import lxml
import numpy as np
import pandas as pd
import requests
import unicodedata2 as uc
from bs4 import BeautifulSoup


def parse_soup(soup):
    """Parse wikipedia page.

    Parameters:
        soup (bs4.BeautifulSoup): The wikipedia page in html

    Returns:
        parsed_data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    infobox = soup.find('table', attrs={'class': 'infobox'})
    image_list = infobox.find_all('a', {'class': 'image'})
    parsed_images = get_parsed_images(image_list)
    tablerow_list = infobox.find_all('tr')
    parsed_text = get_parsed_text(tablerow_list)
    parsed_data = parsed_images.append(parsed_text, ignore_index=True)
    return parsed_data


def get_parsed_images(image_list):
    """Parse images from the wikipedia infobox.

    Parameters:
        image_list (bs4.BeautifulSoup): The image elemets from the wikipedia infobox in html

    Returns:
        parsed_images (pd.DataFrame): Image data from the wikipedia infobox

    Raises:
        None
    """
    parsed_images = pd.DataFrame(columns=['category', 'feature', 'value'])
    for image_idx, image in enumerate(image_list):
        image_page = requests.get(
            'https://commons.wikimedia.org/' + image.get('href')).text
        image_soup = BeautifulSoup(image_page, 'lxml')
        image_source = image_soup.find_all(
            'a', href=True, text='Original file')
        parsed_images.loc[image_idx] = [
            'Image', image.get('title'), "<img src="+image_source[0].get('href')+">"]
    return parsed_images


def get_parsed_text(tablerow_list):
    """Parse text from the wikipedia infobox.

    Parameters:
        tablerow_list (bs4.BeautifulSoup): The tablerows from the wikipedia infobox in html

    Returns:
        parsed_text (pd.DataFrame): Text data from the wikipedia infobox

    Raises:
        None
    """
    parsed_text = pd.DataFrame(columns=['category', 'feature', 'value'])
    for tablerow_idx, tablerow in enumerate(tablerow_list):
        parsed_text.loc[tablerow_idx] = [
            get_category(tablerow), get_feature(tablerow), get_value(tablerow)]
    return parsed_text


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
            category = get_category(tablerow.previous_sibling)
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
    data = clean_incomplete_rows(data)
    data = clean_unwanted_characters(data)
    data = clean_source_brackets(data)
    data = clean_bracket_spaces(data)
    data = clean_geographic_coordinates(data)
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
    data = data.applymap(lambda x: uc.normalize('NFKC', x))
    return data


def clean_incomplete_rows(data):
    """Delete rows with incomplete data.

    Parameters:
        data (pd.DataFrame): Data from the wikipedia infobox

    Returns:
        data (pd.DataFrame): Data from the wikipedia infobox

    Raises:
        None
    """
    data.replace('', np.nan, inplace=True)
    data.dropna(axis=0, how='any', inplace=True)
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
    data = data.applymap(lambda x: x.strip())
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
    for feature in ['Capital', 'Largest city']:
        feature_idx = data.index[data['feature'].str.contains(
            feature, case=False)]
        if not feature_idx.empty:
            value = data['value'].loc[feature_idx].values[0]
            if re.search(r"\d", value):
                value = value[0:re.search(r"\d", value).start()]
                data['value'].loc[feature_idx] = value
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
    for feature_idx, feature in enumerate(feature_list.values):
        if '_' in feature[0]:
            [category_split, feature_split] = feature[0].split('_')
        else:
            category_split, feature_split = feature[0], feature[0]
        found_data = data[data['feature'].str.contains(
            feature_split, case=False) & data['category'].str.contains(category_split, case=False)]
        if not found_data.empty:
            filtered_data.loc[feature_idx] = [
                feature[0], found_data['value'].values[0]]
    return filtered_data


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
    data.loc[data.shape[0]+1] = ['Source', url[0] + ' ' + today]
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
    data.loc[0] = ['Country name', country_name[0].text]
    data.sort_index(inplace=True)
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


def export_data(data):
    data.to_csv('data.csv', header=False, index=False, sep=';')


def main():
    # url_list = liste runterladen
    # url_list kann dann gänflich aus dem Ordner genommen werden
    # diplomacy data von der gleichen Seite ziehen
    # hier schon als data anlegen
    # bei join data dann nach dem Namen reinfügen, obwohl das eher kompliziert klingt

    # damm checken, was da mit Finland abgeht
    # Gucken, welches Bild man nimmt, wenn es mehrere gibt

    url_list = pd.read_csv('url_list.csv', header=None)
    feature_list = pd.read_csv('feature_list.csv', header=None)
    data = pd.DataFrame()
    for url in url_list.values:
        print("\n* Parsing data from {0}".format(url))
        page = requests.get(url[0]).text
        soup = BeautifulSoup(page, 'lxml')
        parsed_data = parse_soup(soup)
        cleaned_data = clean_data(parsed_data)
        filtered_data = filter_data(cleaned_data, feature_list)
        enriched_data = enrich_data(filtered_data, url, soup)
        data = join_data(data, enriched_data)
    export_data(data)


if __name__ == '__main__':
    main()

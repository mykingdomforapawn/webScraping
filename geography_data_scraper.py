import re

import lxml
import pandas as pd
import requests
import unicodedata2 as uc
from bs4 import BeautifulSoup


def parse_soup(soup, feature_list):
    """Parse wikipedia page."""

    # get infobox, search and extract image sources
    infobox = soup.find('table', attrs={'class': 'infobox'})
    image_list = infobox.find_all('a', {'class': 'image'})
    parsed_images = pd.DataFrame(columns=['category', 'feature', 'value'])
    for image_idx, image in enumerate(image_list):
        image_page = requests.get(
            'https://commons.wikimedia.org/' + image.get('href')).text
        image_soup = BeautifulSoup(image_page, 'lxml')
        image_source = image_soup.find_all(
            'a', href=True, text='Original file')
        parsed_images.loc[image_idx] = [
            'Image', image.get('title'), image_source[0].get('href')]

    # search and extract text from table rows
    tablerow_list = infobox.find_all('tr')
    parsed_text = pd.DataFrame(columns=['category', 'feature', 'value'])
    for tablerow_idx, tablerow in enumerate(tablerow_list):
        parsed_text.loc[tablerow_idx] = [
            get_category(tablerow), get_feature(tablerow), get_value(tablerow)]

    parsed_data = parsed_images.append(parsed_text, ignore_index=True)
    return parsed_data


def get_category(tablerow):
    """..."""
    if tablerow.get('class'):
        if tablerow.get('class')[0] == 'mergedtoprow':
            category = get_feature(tablerow)
        else:
            category = get_category(tablerow.previous_sibling)
    else:
        category = get_feature(tablerow)
    return category


def get_feature(tablerow):
    """..."""
    tableheader = tablerow.find('th')
    if tableheader:
        feature = tableheader.text
    else:
        feature = 'None'
    return feature


def get_value(tablerow):
    """..."""
    tabledata = tablerow.find('td')
    if tabledata:
        value = tabledata.text
    else:
        value = 'None'
    return value


"""         try:
            feature = uc.normalize('NFKC', tablerow.th.text)
            feature = clean_str(feature)
        except AttributeError:
            continue """


def clean_str(raw_string):
    """Clean data from unnecessary stuff."""

    # TODO: make this method

    # lower case, [ bis ] wegnehmen, GEO UEI oder so, diese Punkte
    cleaned_string = re.sub('[^a-zA-Z0-9()]', '', raw_string)
    # _nicht löschen
    # [auch nicht löschen]
    # next step: immer von ( bis ) löschenauch bei []
    # lower case einführen

    """ get_feature(tablerow)
        get_value(tablerow)
        tableheader = tablerow.find('th')
        if tableheader:
            tabledata = tablerow.find('td')
            if tabledata:
                parsed_data.loc[tablerow_idx] = [
                    get_category(tablerow), tableheader.text, tabledata.text]
            else:
                parsed_data.loc[tablerow_idx] = [
                    get_category(tablerow), tableheader.text, 'None'] """
    """         if feature in feature_list.values:
            try:
                parsed_data[feature] = uc.normalize('NFKC', tablerow.td.text)
            except AttributeError:
                sibling = tablerow
                while sibling.get('class')[0] != 'mergedbottomrow':
                    sibling = sibling.next_sibling
                    parsed_data[feature + uc.normalize('NFKC', sibling.th.text)] = uc.normalize(
                        'NFKC', sibling.td.text) """

    return cleaned_string


def fetch_num(st):
    """Return first INT appeared in the string."""
    for item in st.split():
        try:
            num = int(item)
            return num
        except ValueError:
            continue


def make_dataset_row(data_dict):
    row = [data_dict.get(item) for item in headers]
    return tuple(row)


def main():
    url_list = pd.read_csv('url_list.csv', header=None)
    feature_list = pd.read_csv('feature_list.csv', header=None)
    data = []
    for url in url_list.values:
        print("\n* Parsing data from {0}".format(url))
        page = requests.get(url[0]).text
        soup = BeautifulSoup(page, 'lxml')
        parsed_data = parse_soup(soup, feature_list)

        # TODO: Hier weiter

        if parsed_data:
            parsed_data = sanitize(parsed_data)
            row = make_dataset_row(parsed_data)
            data.append(row)
        else:
            logging.warning("Parsing failed for '{0}'".format(url))
            continue
    print(data)
    # table = tablib.Dataset(*data, headers=headers)

    # time_str = datetime.now().strftime("%H-%M-%S")
    # file_name = 'f1_data_' + time_str + '.csv'

    # with open(file_name, 'w') as fp:
    #    print(table.csv, file=fp)
    # print("\n* Done. Results are exported into '{0}'".format(file_name))


if __name__ == '__main__':
    print('end')
    main()

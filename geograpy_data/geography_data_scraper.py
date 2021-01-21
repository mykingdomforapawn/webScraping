import re

import lxml
import pandas as pd
import requests
import unicodedata2 as uc
from bs4 import BeautifulSoup


def parse_soup(soup, feature_list):
    """Parse wikipedia page."""

    infobox = soup.find('table', attrs={'class': 'infobox'})
    tablerow_list = infobox.find_all('tr')
    # TODO: hier auch die Flagge rausziehen

    parsed_data = {}
    for tablerow in tablerow_list:
        try:
            feature = uc.normalize('NFKC', tablerow.th.text)
            feature = clean_str(feature)
        except AttributeError:
            continue

        if feature in feature_list.values:
            try:
                parsed_data[feature] = uc.normalize('NFKC', tablerow.td.text)
            except AttributeError:
                sibling = tablerow
                while sibling.get('class')[0] != 'mergedbottomrow':
                    sibling = sibling.next_sibling
                    parsed_data[feature + uc.normalize('NFKC', sibling.th.text)] = uc.normalize(
                        'NFKC', sibling.td.text)

    # TODO: man kann nicht die try exept methode nehmen, weil da manchmal was drinsteht
    # also doch etwas mit area_total einführen

    # TODO: eine contains Methode einführen, damit largest city und capital beide erkannst werden,
    # aufpassen weil man dann eigentlich noch mal an den anfang springen müsste

    # TODO: Bild saugen aktualisieren

    # TODO: clean str methode fertig machen
        # if 'Constructors' in attr:
        #    parsed_data['Constructor titles'] = tr.td.text.split()[0]
        #    continue

        # if 'Drivers' in attr:
        #    parsed_data['Driver titles'] = tr.td.text.split()[0]
        #    continue
    return parsed_data


def clean_str(raw_string):
    # lower case, [ bis ] wegnehmen, GEO UEI oder so, diese Punkte
    cleaned_string = re.sub('[^a-zA-Z0-9()', '', raw_string)
    # _nicht löschen
    # [auch nicht löschen]
    # next step: immer von ( bis ) löschenauch bei []
    # lower case einführen

    return cleaned_string


def sanitize(data_dict):
    """Clean data from unnecessary stuff."""
    res = data_dict.copy()

    # Remove wiki references in square brackets.
    # for k, v in res.items():
    return res


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
    feature_list = pd.read_csv('tablerow_list.csv', header=None)
    data = []
    for url in url_list.values:
        print("\n* Parsing data from {0}".format(url))
        page = requests.get(url[0]).text
        soup = BeautifulSoup(page, 'lxml')
        parsed_data = parse_soup(soup, feature_list)
        # bis hier eig auf bel. tabellen anwendbar

        # ab hier dann sehr individuell
        # vllt datatype in tablerow_list einführen, um das cleanen einfacher zu machen
        # dann in feature list umbenennen

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

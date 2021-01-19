import lxml
import pandas as pd
import requests
from bs4 import BeautifulSoup

# TODO: hier weiter:
# überlegen, wie die zuordnung von features funktionieren kann
# schauen, wie man auf die next siblings zugreifen kann, wenn es sie gibt
# daraus muss dann ein neues feature gebaut werden und dann wird zu parsed_data hinzugefügt

url_list = pd.read_csv('url_list.csv', header=None)
feature_list = pd.read_csv('tablerow_list.csv', header=None)


print(url_list.values)
print(feature_list.values)


def parse_soup(soup, feature_list):
    """Parse wikipedia page."""

    infobox = soup.find('table', attrs={'class': 'infobox'})
    tablerow_list = infobox.find_all('tr')

    parsed_data = {}
    for tablerow in tablerow_list:
        try:
            feature = tablerow.th.text
            feature = feature.strip()
        except AttributeError:
            continue

        # TODO: hier auch die Flagge rausziehen

        if feature in feature_list.values:
            parsed_data[feature] = tablerow.td.text
            continue

        # hier city und largest city trennen

        # if 'Constructors' in attr:
        #    parsed_data['Constructor titles'] = tr.td.text.split()[0]
        #    continue

        # if 'Drivers' in attr:
        #    parsed_data['Driver titles'] = tr.td.text.split()[0]
        #    continue
    return parsed_data


def sanitize(data_dict):
    """Clean data from unnecessary stuff."""
    res = data_dict.copy()

    # Remove wiki references in square brackets.
    for k, v in res.items():
        try:
            ind = v.index('[')
            logging.warning(r" Sanitizing: '{0}' : '{1}'".format(k, v))
            res[k] = v[:ind]
        except (AttributeError, ValueError):
            continue

    # Sanitize 'Races entered' field.
    #k = 'Races entered'
    #v = res[k]
    # try:
    #    v = int(v)
    # except ValueError:
    #    logging.warning(r" Sanitizing: '{0}' : '{1}'".format(k, v))
    #    res[k] = fetch_num(v)
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
    #table = tablib.Dataset(*data, headers=headers)

    #time_str = datetime.now().strftime("%H-%M-%S")
    #file_name = 'f1_data_' + time_str + '.csv'

    # with open(file_name, 'w') as fp:
    #    print(table.csv, file=fp)
    #print("\n* Done. Results are exported into '{0}'".format(file_name))


if __name__ == '__main__':
    print('end')
    main()

import lxml
import pandas as pd
import requests
from bs4 import BeautifulSoup

url_list = ['https://en.wikipedia.org/wiki/Bahrain',
            'https://en.wikipedia.org/wiki/Guatemala',
            'https://en.wikipedia.org/wiki/Finland']

urls = pd.read_csv('url_list.csv')

headers = ('Capital',
           'Capitaland largest city',
           'Largest city',
           'Area')


def parse_page(soup_instance):
    """Parse wikipedia page."""

    # hier strukturell schauen, dass infobox klar wird
    # All data of interest is under <table class="infobox vcard"> tag.
    t = soup_instance.find('table', attrs={'class': 'infobox'})
    data = t.find_all('tr')
    parsed_data = {}

    for tr in data:
        try:
            attr = tr.th.text
        except AttributeError:
            continue

        if attr in ['Capital', 'Capitaland largest city', 'Largest city', 'Official languages', 'Area']:
            parsed_data[attr] = tr.td.text
            continue

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
    for url in url_list:
        print("\n* Parsing data from {0}".format(url))
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        parsed_data = parse_page(soup)
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


# print(page)

# hier weiter
# die beiden testen
# dann auf der website weiter
# wikitable gegen infobox

#soup = BeautifulSoup(page.content, 'lxml')
#infobox = soup.find('table', {'class': 'infobox'})
# print(infobox.prettify())
#links = infobox.find_all('a')
#images = infobox.find_all('class="image"')

# print(links)
""" My_table = soup.find('table', {'class': 'wikitable sortable'})
links = My_table.findAll('a')
Countries = []
for link in links:
    Countries.append(link.get('title'))
df = pd.DataFrame()
df['Country'] = Countries """

# print(links)
# print(images)
# print(links)

#page = 'https://en.wikipedia.org/wiki/Netherlands'
# infoboxes = pd.read_html(
#    page, index_col=0, attrs={"class": "infobox"})
# print(infoboxes[0])
# print(type(infoboxes[0]))
""" contestant_name_age_town = {item.td.text:

                            [int(item.td.find_next_siblings(limit=3)[0].text),
                             item.td.find_next_siblings(limit=3)[2].a.get('href')]

                            for item in
                            soup.find(
                                "table", class_="wikitable").find_all('tr')
                            if item.td is not None} """

# print(contestant_name_age_town)

if __name__ == '__main__':
    main()

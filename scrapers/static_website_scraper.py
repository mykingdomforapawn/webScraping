import re
import urllib.parse

import pandas as pd
import requests
from bs4 import BeautifulSoup


def scrape_tables(url, table_attributes={}, display_none=False, append_links=False):
    """Scrape tables from a static website.

    Parameters:
        url (str): url of a website
        table_attributes (dict): specification to get particular tables
        display_none (bool): get data that is hidden on the website
        append_links (bool): get links from each row and append them in an extra column

    Returns:
        table_container (list): list of pd.DataFrame object containing the table data

    Raises:
        None
    """

    # set up a result container
    table_container = []

    # load page and get soup
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html5lib')

    # find and iterate over tables
    tables = soup.find_all('table', attrs=table_attributes)
    for table in tables:
        data_container = []

        # find and iterate over table rows
        table_rows = table.find_all('tr')
        for table_row in table_rows:

            # delete invisible cells before parsing the text
            if not display_none:
                table_cells_none = table_row.find_all(
                    "span", style=re.compile("none"))
                for table_cell_none in table_cells_none:
                    table_cell_none.decompose()

            # find header/body cells and parse their text
            table_cells = table_row.find_all(["td", "th"])
            table_row_parsed = [table_cell.text.strip()
                                for table_cell in table_cells]

            # find and parse all links in the row
            if append_links:
                table_row_hrefs = table_row.find_all('a', href=True)
                table_row_parsed.append([table_row_href.get(
                    'href') for table_row_href in table_row_hrefs])

            # append parsed table row to data container
            data_container.append(table_row_parsed)

        # convert nested list to dataframe and append to container
        table_container.append(pd.DataFrame(data_container))

    return table_container


def scrape_images(url, image_attributes={}):
    """Scrape images from a static website.

    Parameters:
        url (str): url to a website
        image_attributes (dict): specification to get particular images

    Returns:
        image_container (pd.DataFrame): dataframe containing the image data

    Raises:
        None
    """

    # set up a result container
    image_container = []

    # load page and get soup
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html5lib')

    # find and iterate over images
    image_tags = soup.find_all('img', attrs=image_attributes)
    for image_tag in image_tags:

        # get image attributes as dict and add it to the result container
        image_container.append(image_tag.attrs)

    # transform result container into dataframe
    image_container = pd.DataFrame(image_container)

    return image_container


def scrape_links(url, link_attributes={}, absolute_paths=False):
    """Scrape links from a static website.

    Parameters:
        url (str): url to a website
        link_attributes (dict): specification to get particular links

    Returns:
        link_container (pd.DataFrame): dataframe containing the link data

    Raises:
        None
    """

    # set up a result container
    link_container = []

    # load page and get soup
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html5lib')

    # find and iterate over images
    link_tags = soup.find_all('a', attrs=link_attributes, href=True)
    for link_tag in link_tags:

        # get image attributes as dict and add it to the result container
        link_container.append(link_tag.attrs)

    # transform result container into dataframe
    link_container = pd.DataFrame(link_container)

    # add base url to relative hrefs in links
    if absolute_paths == True and 'href' in link_container:
        link_container['href'] = link_container['href'].apply(
            lambda x: urllib.parse.urljoin(url, x))

    return link_container


def test_scrape_tables():
    url_1 = "https://en.wikipedia.org/wiki/List_of_sovereign_states"
    url_2 = "https://en.wikipedia.org/wiki/Taiwan"
    table_attributes = {'class': 'sortable wikitable'}

    # testcase: table with attributes, no display of invisible text, no parsing of links
    tables = scrape_tables(url_1, table_attributes)
    assert_data = 'The Bahamas is a Commonwealth realm.[f]'
    test_data = tables[0].loc[16, 3]
    assert test_data == assert_data, "Test expected '" + \
        assert_data + "' but got '" + test_data + "'"

    # testcase: table with attributes, with display of invisible text, no parsing of links
    tables = scrape_tables(url_1, table_attributes, display_none=True)
    assert_data = 'A AAA'
    test_data = tables[0].loc[1, 0]
    assert test_data == assert_data, "Test expected '" + \
        assert_data + "' but got '" + test_data + "'"

    # testcase: table with attributes, no display of invisible text, with parsing of links
    tables = scrape_tables(url_1, table_attributes, append_links=True)
    assert_data = '/wiki/United_Nations_System'
    test_data = tables[0].loc[0, 4][0]
    assert test_data == assert_data, "Test expected '" + \
        assert_data + "' but got '" + test_data + "'"

    # testcase: all tables from website, no display of invisible text, no parsing of links
    tables = scrape_tables(url_2)
    assert_data = '2,809,004'
    test_data = tables[3].loc[3, 3]
    assert test_data == assert_data, "Test expected '" + \
        assert_data + "' but got '" + test_data + "'"

    print("scrape_tables() was tested successfully.")


def test_scrape_images():
    url = "https://en.wikipedia.org/wiki/France"
    image_attributes = {'alt': 'Flag of France'}

    # testcase: image with attributes
    images = scrape_images(url, image_attributes)
    assert_data = 'Flag of France'
    test_data = images.loc[0][0]
    assert test_data == assert_data, "Test expected '" + \
        assert_data + "' but got '" + test_data + "'"

    # testcase: all images from website
    images = scrape_images(url)
    assert_data = 'EU-France (orthographic projection).svg'
    test_data = images.loc[3][0]
    assert test_data == assert_data, "Test expected '" + \
        assert_data + "' but got '" + test_data + "'"

    print("scrape_images() was tested successfully.")


def test_scrape_links():
    url = "https://en.wikipedia.org/wiki/Papua_New_Guinea"
    link_attributes = {'title': 'New Guinea'}

    # testcase: link with attributes, no absolute paths
    links = scrape_links(url, link_attributes)
    assert_data = '/wiki/New_Guinea'
    test_data = links.loc[0][0]
    assert test_data == assert_data, "Test expected '" + \
        assert_data + "' but got '" + test_data + "'"

    # testcase: link with attributes, with absolute paths
    links = scrape_links(url, link_attributes, absolute_paths=True)
    assert_data = 'https://en.wikipedia.org/wiki/New_Guinea'
    test_data = links.loc[0][0]
    assert test_data == assert_data, "Test expected '" + \
        assert_data + "' but got '" + test_data + "'"

    # testcase: all links from website
    links = scrape_links(url, absolute_paths=True)
    assert_data = 'Papua (disambiguation)'
    test_data = links.loc[4][2]
    assert test_data == assert_data, "Test expected '" + \
        assert_data + "' but got '" + test_data + "'"

    print("scrape_links() was tested successfully.")


def main():
    test_scrape_tables()
    test_scrape_images()
    test_scrape_links()


if __name__ == '__main__':
    main()

import os
from BeautifulSoup import BeautifulSoup
from getpass import getpass
from mechanize import Browser
from urllib import urlencode

from common import *


def get_document_urls(br, data):

    if os.path.exists(DOCUMENT_URLS_FILE):
        return DOCUMENT_URLS_FILE

    makedir(os.path.dirname(DOCUMENT_URLS_FILE))

    br.open(LOGIN_PREFIX + ADVANCED_SEARCH_URL, data)

    br.select_form(nr=0)
    br.form['py13'] = ['1948'] # date declassified (from)
    br.form['py24'] = ['2005'] # date declassified (to)
    br.form['n'] = ['100'] # number of results per page

    response = br.submit()

    url = response.geturl()

    with safe_write(DOCUMENT_URLS_FILE) as f:
        while True:

            soup = BeautifulSoup(file(download_url(br, LOGIN_PREFIX + url, SEARCH_RESULTS_DIR, data)).read())

            urls = extract_urls(soup)

            f.write('\n'.join(urls))
            f.write('\n')
            f.flush()

            url = find_next_page_url(soup)

            if url is None:
                break


def extract_urls(soup):

    urls = soup.find('form', attrs={'name': 'markedlistform'})
    urls = [l.get('href') for l in urls.findAll('a')]

    return urls


def find_next_page_url(soup):

    navigation_bar = soup.findAll('span', attrs={'class': 'stndsmall'})[-2]
    next_page_link = navigation_bar.findAll('a')[-2]

    try:
        if next_page_link.contents[0].get('alt') == 'Next Page':
            return next_page_link.get('href')
    except AttributeError:
        return


def main():

    br = Browser()
    br.set_handle_robots(False)
#    br.set_debug_responses(True)

    data = urlencode({'user': USERNAME, 'pass': getpass()})

    get_document_urls(br, data)


if __name__ == '__main__':
    main()

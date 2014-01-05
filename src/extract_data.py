import os, re, sys
from BeautifulSoup import BeautifulSoup
from collections import defaultdict
from dateutil.parser import parse
from getpass import getpass
from glob import glob
from mechanize import Browser
from urllib import urlencode

from common import *
from iterview import iterview


def extract_text(filename, contents, description):

    try:
        [text] = re.findall('<pre>([\w\W]*)(?:</pre>|<br>\s+</span>\s+<span class="stnd">)', contents)
    except ValueError:
        print >> sys.stderr, '\n', 'No text in ', filename
        text = ''

    text = ' '.join([description, text]) # prepend description, if any

    text = re.sub('<[^<]*?/?>', ' ', text) # strip HTML tags
    text = re.sub('&#?\w+;', ' ', text) # strip HTML entities

    return text


def extract_metadata(contents, classifications, sources):

    metadata = defaultdict(lambda: 'omitted')

    soup = BeautifulSoup(contents)

    text = str(soup.findAll('span', attrs={'class': 'stnd'})[0])

    text = re.sub('<span class=\"stnd\">\n\s*', '', text)
    text = re.sub('\s*\n\s*</span>', '', text)
    text = text.split('.')[0:-1]

    field = text.pop(-1).strip()

    if 'page' in field:
        metadata['pages'] = field.split(' ')[0]
        field = text.pop(-1).strip()

    if 'complete' in field:
        metadata['completeness'] = field
        field = text.pop(-1).strip()

    if 'sanitized' in field:
        metadata['sanitization'] = field
        field = text.pop(-1).strip()

    if 'date declassified' in field:
        field = re.sub('date declassified: ', '', field)
        metadata['declassified'] = parse(field).strftime('%Y-%m-%d')
        field = text.pop(-1).strip()

    if 'issue date' in field:
        field = re.sub('issue date: ', '', field)
        metadata['issued'] = parse(field).strftime('%Y-%m-%d')
        field = text.pop(-1).strip()

    if field in classifications:
        metadata['classification'] = field
        field = text.pop(-1).strip()

    if field in sources:
        metadata['source'] = field

    metadata['description'] = '.'.join(text) # includes document type

    return metadata


def extract_data(filename, classifications, sources):

    contents = file(filename).read().lower()

    [number] = re.findall('number:</b> (.*)<br>', contents)
    [page, _] = re.findall('<input [^<>]*name="?page"? [^<>]*value="(\d+)">', contents)

    description = ''

    if page == '1':

        metadata = extract_metadata(contents, classifications, sources)

        with safe_write(os.path.join(METADATA_DIR, number)) as f:
            line = [number,
                    metadata['source'],
                    metadata['classification'],
                    metadata['issued'],
                    metadata['declassified'],
                    metadata['sanitization'],
                    metadata['completeness'],
                    metadata['pages']]
            f.write('\t'.join(line))
            f.write('\n')

        description = metadata['description']

    else:
        assert number.startswith('ck')
        number = 'ck' + str(int(number[2:]) - (int(page) - 1))

    text = extract_text(filename, contents, description)

    with safe_write(os.path.join(TEXT_DIR, number + '_' + page)) as f:
        f.write(text)
        f.write('\n')


def get_metadata_options(br, key, data):

    soup = BeautifulSoup(file(download_url(br, LOGIN_PREFIX + ADVANCED_SEARCH_URL, SEARCH_FORM_DIR, data)).read())

    options = soup.find('select', attrs={'name': key})
    options = [x.get('value') for x in options.findAll('option')]
    options = [re.sub('"', '', x.lower()) for x in options if x != '']

    return options


def main():

    br = Browser()
    br.set_handle_robots(False)
#    br.set_debug_responses(True)

    data = urlencode({'user': USERNAME, 'pass': getpass()})

    classifications = get_metadata_options(br, 'ca', data)
    sources = get_metadata_options(br, 'is', data)

    makedir(METADATA_DIR)
    makedir(TEXT_DIR)

    for filename in iterview(glob(DOCUMENT_PAGES_DIR + '/*'), inc=1000):
        extract_data(filename, classifications, sources)


if __name__ == '__main__':
    main()

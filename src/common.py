import os
from contextlib import contextmanager
from hashlib import md5
from urllib2 import URLError


USERNAME = 'wallach'

CACHE = 'data/cache/'
DOCUMENT_URLS_FILE = os.path.join(CACHE, 'document_urls.txt')
HTML_DIR = os.path.join(CACHE, 'html')
SEARCH_FORM_DIR = os.path.join(HTML_DIR, 'search_form')
SEARCH_RESULTS_DIR = os.path.join(HTML_DIR, 'search_results')
DOCUMENT_PAGES_DIR = os.path.join(HTML_DIR, 'document_pages')
METADATA_DIR = os.path.join(CACHE, 'meta')
TEXT_DIR = os.path.join(CACHE, 'text')

LOGIN_PREFIX = 'https://login.silk.library.umass.edu/login?url='
ADVANCED_SEARCH_URL = 'http://galenet.galegroup.com.silk.library.umass.edu/servlet/DDRS?locID=mlin_w_umassamh&ste=2'


def makedir(path):
    if not os.path.exists(path):
        os.makedirs(path)


@contextmanager
def safe_write(filename):
    try:
        with file(filename, 'wb') as f:
            yield f
    except:
        if os.path.exists(filename):
            os.remove(filename)
            raise


def url2filename(url):
    return md5(url).hexdigest()


def _download(br, url, cache, data=None):

    makedir(cache)

    filename = os.path.join(cache, url2filename(url))

    if not os.path.exists(filename):
        with safe_write(filename) as f:
            f.write(br.open(url, data).read())

    return filename


def download(br, url, cache, data, tries=3):

    for i in xrange(tries):
        try:
            return _download(br, url, cache, data)
        except URLError as last_exception:
            pass

    raise last_exception


def download_url(br, url, cache, data, tries=3):

    for i in xrange(tries):

        filename = download(br, url, cache, data)

        try:
            contents = file(filename).read()
            assert contents, 'Empty file'
            assert '<title>Off-Campus' not in contents, 'Off-campus login page'
            return filename
        except AssertionError as last_exception:
            os.remove(filename)

    raise last_exception

import argparse
import re, sys
from BeautifulSoup import BeautifulSoup
from getpass import getpass
from mechanize import Browser
from urllib import urlencode

from common import *
from iterview import iterview


def get_document_pages(br, url, data):

    soup = BeautifulSoup(file(download_url(br, url, DOCUMENT_PAGES_DIR, data)).read())

    # extract the document length from the first page

    pages = str(soup.findAll('span', attrs={'class': 'stnd'})[0])

    pages = re.sub('<span class=\"stnd\">\n\s*', '', pages)
    pages = re.sub('\s*\n\s*</span>', '', pages)
    pages = pages.split('.')[0:-1]

    field = pages.pop(-1).strip()
    assert 'page' in field, 'Missing document length ' + url

    pages = int(field.split(' ')[0])

    # download the remaining pages (if any) -- if any of these pages
    # throws an exception, the exception will be raised and any
    # subsequent pages will not be downloaded...

    for page in xrange(2, pages + 1):
        download_url(br, url + '&page=' + str(page), DOCUMENT_PAGES_DIR, data)


def check_args(parser, args):

    if args.total_jobs is None and args.job is None:
        args.total_jobs = 1
        args.job = 1
        return

    if args.total_jobs is None or args.job is None:
        parser.error('Must specify total number of jobs and job number')

    if args.total_jobs < 1:
        parser.error('Total number of jobs cannot be less than one')

    if args.job < 1:
        parser.error('Job number cannot be less than one')

    if args.job > args.total_jobs:
        parser.error('Job number cannot be greater than total number of jobs')


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('--total-jobs', metavar='<total-jobs>', help='total number of jobs downloading documents', type=int)
    parser.add_argument('--job', metavar='<job>', help='job number between 1 and <total-jobs>', type=int)

    args = parser.parse_args()
    check_args(parser, args)

    br = Browser()
    br.set_handle_robots(False)
#    br.set_debug_responses(True)

    data = urlencode({'user': USERNAME, 'pass': getpass()})

    document_urls = [LOGIN_PREFIX + url.strip() + '&view=etext' for url in file(DOCUMENT_URLS_FILE)]

    start = args.job - 1
    step = args.total_jobs

    for url in iterview(document_urls[start::step]):
        try:
            get_document_pages(br, url, data)
        except Exception as e:
            print >> sys.stderr, '\n', (url, e)


if __name__ == '__main__':
    main()

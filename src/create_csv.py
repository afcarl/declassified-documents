import argparse
import os, re
from collections import defaultdict
from glob import glob

from common import *
from iterview import iterview


def create_stopword_list(f):

    if not f:
        return set()

    if isinstance(f, basestring):
        f = file(f)

    return set(word.strip() for word in f)


def create_csv(numbers, max_document_length, min_type_count, stopwords):

    vocab = defaultdict(int)

    data = {}

    for filename in iterview(glob(METADATA_DIR + '/*')):

        number = os.path.basename(filename)

        if numbers is not None and number not in numbers:
            continue

        with file(filename) as f:
            metadata = f.read().strip()

        fields = metadata.split('\t')

        assert len(fields) == 8
        assert fields[0] == number

        text = ''

        for page in xrange(1, int(metadata[-1]) + 1):
            with file(os.path.join(TEXT_DIR, number + '_' + str(page))) as f:
                text += f.read().strip()

        text = re.findall('[a-z]+', text)
        text = [x for x in text if x not in stopwords]

        for x in text:
            vocab[x] += 1

        data[number] = (metadata, ' '.join(text))

    for number, (metadata, text) in data.items():

        text = [x for x in text.split(' ') if vocab[x] >= min_type_count]
        text = text[:min(len(text), max_document_length)]

        print '\t'.join([metadata, ' '.join(text)])


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('--document-numbers-file', metavar='<document-numbers-file>', help='only process documents whose numbers (i.e., ckXXXXXXXXXX) are specified in <document-numbers-file>', type = argparse.FileType('r'))
    parser.add_argument('--max-document-length', metavar='<max-document-length>', help='truncate long documents to <max-document-length>', type=int)
    parser.add_argument('--min-type-count', metavar='<min-type-count>', help='remove word types that occur fewer than <min-type-count> times', type=int)
    parser.add_argument('--stopword-file', metavar='<stopword-file>', help='remove stopwords provided in <stopword-file>', type=argparse.FileType('r'))

    args = parser.parse_args()

    if args.document_numbers_file:
        numbers = [x.strip() for x in args.document_numbers_file]
    else:
        numbers = None

    create_csv(numbers, args.max_document_length, args.min_type_count, create_stopword_list(args.stopword_file))


if __name__ == '__main__':
    main()

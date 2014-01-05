import cPickle as pickle
import os
from collections import defaultdict
from itertools import islice, izip
from IPython import embed
from numpy import argsort, zeros
from pylab import plot, show, text, bar, xticks, xlim, xlabel, ylabel, legend, gca, setp
from dateutil.parser import parse
from numpy import array


DATA_DIR = 'data/'
RESULTS_DIR = 'results/lda/documents/T1000-S2000-ID1/'

def get_pairs(l):
    """
    http://stackoverflow.com/questions/5389507/iterating-over-every-two-elements-in-a-list
    """

    l = iter(l)

    return izip(l, l)


def get_topic_keys(sort=False):
    """
    Returns an array of tuples---one per topic. Each tuple consists of
    the alpha value and a list of the top words for that topic.

    Arguments:

    sort -- whether to sort the tuples by their alpha values
    """

    topics = []

    for row in open(os.path.join(RESULTS_DIR, 'topic-keys.txt.gz')):

        fields = row.split()
        assert len(topics) == int(fields[0])
        topics.append((float(fields[1]), fields[2:]))

    if sort:
        return sorted(topics)
    else:
        return topics


def get_metadata(fields=['number', 'source', 'classification', 'issued', 'declassified', 'sanitization', 'completeness', 'pages']):
    """
    Returns a generator that yields dicts---one per document. Each
    document-specific dict contains the metadata for that document,
    represented via a set of key--value pairs.

    Arguments:

    fields -- array of field names
    """

    for row in open(os.path.join(DATA_DIR, 'documents.csv')):

        row = [x.strip() for x in row.split('\t')]
        assert len(row) == 9

        yield dict(zip(fields, row[:-1]))


def get_doc_topic_dists():
    """
    Returns a dict (with document IDs as keys) containing
    document-specific distributions over topics. Each distribution is
    a dict (with topic numbers as keys and probabilities as values).
    """

    dists = {}

    for csv, row in izip(open(os.path.join(DATA_DIR, 'documents.csv')), islice(open(os.path.join(RESULTS_DIR, 'doc-topics.txt')), 1, None)):

        dist = {}

        for t, p in get_pairs([float(x) for x in row.split()[2:]]):
            if p > 0.0:
                dist[int(t)] = p

        dists[csv.split('\t')[0]] = dist

    return dists


def get_doc_topic_dists_by_year(field):
    """
    Returns a dict (with years as keys) containing year-specific
    distributions over topics, obtained by appropriately averaging
    document-specific distributions over topics. Each distribution is
    a dict (with topic numbers as keys and probabilities as values).

    Arguments:

    field -- field number (zero-indexed) from which to extract years
    """

    dists_by_year = defaultdict(lambda: defaultdict(float))
    num_by_year = defaultdict(int)

    for csv, row in izip(open(os.path.join(DATA_DIR, 'documents.csv')), islice(open(os.path.join(RESULTS_DIR, 'doc-topics.txt')), 1, None)):

        date = csv.split('\t')[field] # extract date from specified field

        if date != 'omitted': # if date is present...

            year = int(date.split('-')[0]) # ... extract year
            num_by_year[year] += 1

            for t, p in get_pairs([float(x) for x in row.split()[2:]]):
                if p > 0.0:
                    dists_by_year[year][int(t)] += p

    for year, dist in dists_by_year.items():
        if num_by_year[year] >= 10:
            for t in dist.keys():
                dist[t] /= num_by_year[year] # normalize
        else:
            for t in dist.keys():
                dist[t] = 0.0

    return dists_by_year


def plot_topic_proportion_by_year(dists_by_year_issued, dists_by_year_declassified, topic):
    """
    Generates a plot of the year-specific topic proportion for the
    specified topic by year issued and year declassified.

    Arguments:

    dists_by_year_issued -- year-specific distributions over topics
    dists_by_year_declassified -- year-specific distributions over topics
    topic -- topic number (zero-indexed) for which to generate plot
    """

    coords = [] # list of coordinates [(x1, y1), (x2, y2), ...]

    for year, dist in dists_by_year_issued.items():
        coords.append((year, dist[topic] * 100))

    coords = zip(*coords) # transpose -> [(x1, x2, ...), (y1, y2, ...)]

    plot(coords[0], coords[1], label='issued', color='black', linewidth=2)

    coords = []

    for year, dist in dists_by_year_declassified.items():
        coords.append((year, dist[topic] * 100))

    coords = zip(*coords)

    plot(coords[0], coords[1], label='declassified', color='red', linewidth=2)

    xlim(1910, 2010) # restrict x axis (years) to 1910--2010

    fontsize = 16

    for tick in gca().xaxis.get_major_ticks():
        tick.label1.set_fontsize(fontsize)

    for tick in gca().yaxis.get_major_ticks():
        tick.label1.set_fontsize(fontsize)

    legend(frameon=False)

    setp(gca().get_legend().get_texts(), fontsize=fontsize)

    show()


def plot_classification_duration_histogram():
    """
    Generates a histogram of classification durations in days.
    """

    counts = defaultdict(int)

    for row in get_metadata():
        try:
            duration = (parse(row['declassified']) - parse(row['issued'])).days
            if duration > 0:
                counts[duration] += 1
        except ValueError:
            pass

    bar(counts.keys(), counts.values(), align='center', color='gray')

    fontsize = 16

    for tick in gca().xaxis.get_major_ticks():
        tick.label1.set_fontsize(fontsize)

    for tick in gca().yaxis.get_major_ticks():
        tick.label1.set_fontsize(fontsize)

    show()


def get_doc_ids(key, value):
    """
    Returns a list of document IDs for only those documents with
    metadata that matches the specified key--value pair.

    Arguments:

    key -- metadata key to match
    value -- metadata key to match
    """

    ids = []

    for doc in get_metadata():
        if doc[key] == value:
            ids.append(doc['number'])

    return ids


def plot_relative_topic_proportions(ids, sort=False):
    """
    Generates a plot indicating which topics are over- or
    under-represented in the specified documents.

    Arguments:

    ids -- list of document IDs
    """

    dists = get_doc_topic_dists()
    topic_keys = get_topic_keys()

    num_topics = len(topic_keys)

    interesting_dist = zeros(num_topics)
    reference_dist = zeros(num_topics)

    for number, dist in dists.items():
        if number in ids:
            interesting_dist[dist.keys()] += dist.values()
        else:
            reference_dist[dist.keys()] += dist.values()

    interesting_dist /= len(ids)
    reference_dist /= (len(dists.keys()) - len(ids))

    x = array(range(num_topics))
    y = (interesting_dist - reference_dist) / reference_dist
    if sort:
        idx = argsort(y)[::-1]
        x, y = x[idx], y[idx]

    plot(x, y, marker='None', linestyle='None')

    gca().xaxis.set_visible(False)

    fontsize = 16

    for n, (a, b) in enumerate(zip(x, y)):
        text(n, b, str(a), fontsize=fontsize)

    for tick in gca().yaxis.get_major_ticks():
        tick.label1.set_fontsize(fontsize)

    show()


def get_doc_ids_with_non_zero_topic_proportions(topic):
    """
    Returns a list of tuples. Each tuple consists of a document ID and
    that document's topic proportion for the specified topic. The
    tuples are sorted in descending order by their topic proportions.

    Arguments:

    topic -- topic for which to return document IDs and proportions
    """

    tuples = {}

    for number, dist in get_doc_topic_dists().items():
        if topic in dist:
            tuples[number] = dist[topic]

    return sorted(tuples.items(), key=lambda x: x[1], reverse=True)

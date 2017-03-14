import sys, os, time, fnmatch, itertools
from datetime import datetime

import pandas as pd
import numpy as np
import igraph

import logging
logging.basicConfig(format='%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s',
        datefmt="%H:%M:%S",
        level=logging.INFO)
logger = logging.getLogger(__name__)

def get_fnames(method):
    # https://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python
    matches = []
    for root, dirname, filenames in os.walk(method):
        for filename in fnmatch.filter(filenames, "*.tree"):
            matches.append(os.path.join(root, filename))
    return matches

def parse_tree(fname):
    with open(fname, 'r') as f:
        rows = []
        for line in f:
            if line[0] == "#":
                continue

            line = line.strip().split(' ')
            pid = int(line[2].strip('"'))
            cl = line[0]

            rows.append( (pid, cl) )
    return rows


def main(args):
    fnames = get_fnames('undirdir')
    fnames = fnames[:2]  # for testing
    dfs = {}
    for fname in fnames:
        rows = parse_tree(fname)
        df = pd.DataFrame(rows, columns=['pid', 'cl'])
        dfs[fname] = df

    bottom_level = {}
    clusterings_bottom = {}
    for fname, df in dfs.iteritems():
        bottom_level[fname] = df.cl.apply(lambda x: ':'.join(x.split(':')[:-1])).astype('category')
        clusterings_bottom[fname] = igraph.Clustering(bottom_level[fname].cat.codes)
    vi = igraph.compare_communities(clusterings_bottom[fnames[0]], clusterings_bottom[fnames[1]], method='vi')
    logger.info("VI for files: {}, {}: {}".format(fnames[0], fnames[1], vi))


if __name__ == "__main__":
    total_start = time.time()
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="test compare vi (variation in information)")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    main(args)
    total_end = time.time()
    logger.info('all finished. total time: {:.2f} seconds'.format(total_end-total_start))

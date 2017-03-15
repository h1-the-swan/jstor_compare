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


def get_vi_from_clusterings(clustering_left, clustering_right):
    return igraph.compare_communities(clustering_left, clustering_right, method='vi')

def get_vi_from_df(df_left, df_right):
    clusterings = []
    for df in [df_left, df_right]:
        bottom_level = df.cl.apply(lambda x: ':'.join(x.split(':')[:-1])).astype('category')
        clusterings.append(igraph.Clustering(bottom_level.cat.codes))
    return get_vi_from_clusterings(clusterings[0], clusterings[1])

def get_vi_from_fnames(fname_left, fname_right):
    dfs = []
    for fname in [fname_left, fname_right]:
        rows = parse_tree(fname)
        df = pd.DataFrame(rows, columns=['pid', 'cl'])
        dfs.append(df)
    return get_vi_from_df(dfs[0], dfs[1])
            


def main(args):
    fname_left = args.input[0]
    fname_right = args.input[1]
    vi = get_vi_from_fnames(fname_left, fname_right)
    args.output.write("VI for files: {}, {}: {}\n".format(fname_left, fname_right, vi))


if __name__ == "__main__":
    total_start = time.time()
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="Get the Variation in Information (VI) for two clusterings of the same graph")
    parser.add_argument("input", nargs=2, help="filenames for the two tree files to compare")
    parser.add_argument("-o", "--output", type=argparse.FileType('w'), default=sys.stdout, help="output filename")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    main(args)
    total_end = time.time()
    logger.info('all finished. total time: {:.2f} seconds'.format(total_end-total_start))

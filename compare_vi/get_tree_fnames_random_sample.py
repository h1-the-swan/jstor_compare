import sys, os, time
from datetime import datetime

import pandas as pd
import numpy as np


import logging
logging.basicConfig(format='%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s',
        datefmt="%H:%M:%S",
        level=logging.INFO)
logger = logging.getLogger(__name__)


def main(args):
    full_df = pd.read_csv(args.infname, index_col=0, header=None)
    randomstate = np.random.RandomState(args.seed)
    subset = full_df.sample(n=args.number, random_state=randomstate)
    subset.reset_index(inplace=True)
    subset.index.name = 'idx'
    subset.rename(columns={0: 'orig_idx', 1: 'fname_left', 2: 'fname_right'}, inplace=True)
    subset.to_csv(args.outfname)

if __name__ == "__main__":
    total_start = time.time()
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="get random sample of tree fname combinations")
    parser.add_argument("-i", "--infname", default='all_tree_fnames_combinations.csv', help="input csv filename")
    parser.add_argument("-o", "--outfname", default='all_tree_fnames_combinations_sample.csv', help="output csv filename")
    parser.add_argument("-n", "--number", type=int, default=1000, help="number of random samples")
    parser.add_argument("--seed", default=999, help="random seed")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    main(args)
    total_end = time.time()
    logger.info('all finished. total time: {:.2f} seconds'.format(total_end-total_start))

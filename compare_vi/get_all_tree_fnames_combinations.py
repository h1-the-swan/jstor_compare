import sys, os, time, fnmatch
from datetime import datetime
import itertools


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

def output_combinations(fnames, outfname, sep=','):
    with open(outfname, 'w') as outf:
        i = 0
        for a, b in itertools.combinations(fnames, 2):
            outf.write("{}{}".format(i, sep))
            outf.write("{}{}".format(a, sep))
            outf.write("{}\n".format(b))
            i += 1

def main(args):
    methods = [
                'undirdir',
                'pagerank',
                'outdirdir',
                'pagerank_unrecorded'
            ]
    fnames = []
    for method in methods:
        fnames.extend(get_fnames(method))
    output_combinations(fnames, args.outfname)

if __name__ == "__main__":
    total_start = time.time()
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="get all tree filenames")
    parser.add_argument("-o", "--outfname", default='all_tree_fnames_combinations.csv', help="output csv filename")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    main(args)
    total_end = time.time()
    logger.info('all finished. total time: {:.2f} seconds'.format(total_end-total_start))

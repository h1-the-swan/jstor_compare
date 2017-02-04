import sys, os, time
from collections import defaultdict, Counter
from datetime import datetime

import logging
logging.basicConfig(format='%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s',
        datefmt="%H:%M:%S",
        level=logging.INFO)
logger = logging.getLogger(__name__)

def get_size_counts(fname):
    """From the tree file, get the data needed to analyze

    :fname: filename of the tree file
    :returns: counter of size: count

    """
    start = time.time()
    logger.debug("Analyzing tree file...")
    i = 0
    size_total = Counter()
    num_nodes = 0
    

    with open(fname, 'r') as f:
        for line in f:
            i += 1
            if line[0] == "#":
                continue
            line = line.strip().split(' ')

            # Get cluster
            cl = line[0]
            cl = cl.split(':')

            belongs_to = ":".join(cl[:-1])
            size_total[belongs_to] += 1

            num_nodes += 1

    size_counts = Counter()
    for count in size_total.itervalues():
        size_counts[count] += 1


    end = time.time()
    logger.debug("Done. Took {:2f} seconds.".format(end-start))
    logger.debug("Total number of nodes: {}.\n".format(num_nodes))
    return size_counts


def output_csv(d, dirname, fname, extension='csv', sep=','):
    fname = os.path.join(dirname, "{}.{}".format(fname, extension))
    logger.debug("Writing to file: {}".format(fname))
    with open(fname, 'w') as outf:
        for k, v in d.iteritems():
            outf.write("{}{}{}\n".format(k, sep, v))

def main(args):
    size_counts = get_size_counts(args.tree_fname)
    outdir = args.outdir
    label = args.label
    output_csv(size_counts, dirname=outdir, fname=label+"-size_counts")

if __name__ == "__main__":
    total_start = time.time()
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="From a .tree file, get the distribution of number of nodes per cluster")
    parser.add_argument("tree_fname", type=str, help="input filename (.tree file)")
    parser.add_argument("-o", "--outdir", type=str, help="directory for the output", default=os.path.dirname(__file__))
    parser.add_argument("--label", type=str, help="label for the output files--- e.g. 'EXAMPLE' will have output file 'EXAMPLE-size_counts.csv'")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    main(args)
    total_end = time.time()
    logger.info('all finished. total time: {:.2f} seconds'.format(total_end-total_start))


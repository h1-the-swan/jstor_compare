import sys, os, time
from collections import defaultdict, Counter
from datetime import datetime

import logging
logging.basicConfig(format='%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s',
        datefmt="%H:%M:%S",
        level=logging.INFO)
logger = logging.getLogger(__name__)

def get_pubyear(fname):
    """Get dictionary mapping paper ID to publication year

    :fname: filename for the publication years. comma separated with first column paper ID, second column year
    :returns: pubyear (dict)

    """
    start = time.time()
    logger.debug("Parsing publication year file...")
    pubyear = {}
    with open(fname, 'r') as f:
        for line in f:
            line = line.strip().split(',')
            pid = int(line[0])
            try:
                year = int(line[1])
            except ValueError:
                year = line[1]
            pubyear[pid] = year
    end = time.time()
    logger.debug("Done. Took {:2f} seconds.".format(end-start))
    logger.debug("Length of pubyear dict: {}.\n".format(len(pubyear)))
    return pubyear

def analyze_tree(fname, pubyear):
    """From the tree file, get the data needed to analyze

    :fname: filename of the tree file
    :pubyear: dictionary mapping paper id to publication year
    :returns: (
                num_nodes: Counter(year: number of nodes),
                rank_total: Counter(year: sum of rank),
                depth_counts: defaultdict(year: Counter(depth: count of nodes)),
                size_total: defaultdict(year: Counter(cluster name: number of nodes)))
                )

    """
    start = time.time()
    logger.debug("Analyzing tree file...")
    i = 0
    num_nodes = Counter()
    rank_total = Counter()
    depth_counts = defaultdict(Counter)
    size_total = defaultdict(Counter)

    with open(fname, 'r') as f:
        for line in f:
            i += 1
            if line[0] == "#":
                continue
            line = line.strip().split(' ')

            pid = int(line[2].strip('"'))
            year = pubyear.get(pid)
            if not year:
                continue

            # Get cluster
            cl = line[0]
            cl = cl.split(':')

            # Get depth
            depth = len(cl)
            depth_counts[year][depth] += 1

            # Add to running size total
            belongs_to = ":".join(cl[:-1])
            size_total[year][belongs_to] += 1

            # Add to running rank total
            rank = float(line[1])
            rank_total[year] += rank

            # Add to running total of papers per year
            num_nodes[year] += 1

    end = time.time()
    logger.debug("Done. Took {:2f} seconds.".format(end-start))
    logger.debug("Total number of nodes: {}.\n".format(sum(num_nodes.values())))
    return num_nodes, rank_total, depth_counts, size_total

def get_rank_mean(rank_total, num_nodes):
    """calculate mean rank per year

    :rank_total: Counter(year: sum of rank)
    :num_nodes: Counter(year: number of nodes)
    :returns: dict {year: mean rank}

    """
    rank_mean = {}
    for year in rank_total:
        rank_mean[year] = rank_total[year] / num_nodes[year]
    return rank_mean

def get_mean(counts_by_year):
    """get weighted mean from a (value: weight) counter by year

    :counts_by_year: dictionary of years to dictionaries mapping weight to value
    :returns: dict {year: mean}

    """
    d = {}
    for year, counts_dict in counts_by_year.iteritems():
        sum_this_year = 0
        count_this_year = 0
        for k, v in counts_dict.iteritems():
            sum_this_year += (k * v)
            count_this_year += v
        d[year] = float(sum_this_year) / count_this_year
    return d

def get_size_mean(size_total):
    """calculate mean cluster size per year

    :size_total: defaultdict(year: Counter(cluster name: number of nodes)))
    :returns: dict {year: mean cluster size}

    """
    size_counts = defaultdict(Counter)
    for year, cl_size in size_total.iteritems():
        for cl, size in cl_size.iteritems():
            size_counts[year][size] += 1
    size_mean = get_mean(size_counts)
    return size_mean

def get_depth_mean(depth_counts):
    """calculate mean cluster depth per year

    :depth_counts: defaultdict(year: Counter(depth: count of nodes)))
    :returns: dict {year: mean cluster depth}

    """
    depth_mean = get_mean(depth_counts)
    return depth_mean

def output_csv(d, dirname, fname, extension='csv', sep=','):
    fname = os.path.join(dirname, "{}.{}".format(fname, extension))
    logger.debug("Writing to file: {}".format(fname))
    with open(fname, 'w') as outf:
        for k, v in d.iteritems():
            outf.write("{}{}{}\n".format(k, sep, v))

def main(args):
    pubyear = get_pubyear(args.pubyears_fname)
    num_nodes, rank_total, depth_counts, size_total = analyze_tree(args.tree_fname, pubyear)
    outdir = args.outdir
    label = args.label
    rank_mean = get_rank_mean(rank_total, num_nodes)
    output_csv(rank_mean, dirname=os.path.join(outdir, "rank_mean"), fname=label+"-rank_mean")
    size_mean = get_size_mean(size_total)
    output_csv(size_mean, dirname=os.path.join(outdir, "size_mean"), fname=label+"-size_mean")
    depth_mean = get_depth_mean(depth_counts)
    output_csv(depth_mean, dirname=os.path.join(outdir, "depth_mean"), fname=label+"-depth_mean")

if __name__ == "__main__":
    total_start = time.time()
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="From a .tree file, get the mean rank, cluster depth, and cluster size and output into a csv file")
    parser.add_argument("tree_fname", type=str, help="input filename (.tree file)")
    parser.add_argument("pubyears_fname", type=str, help="(comma-separated) file mapping paper id to publication year")
    parser.add_argument("-o", "--outdir", type=str, help="base directory for the output. must contain directories 'rank_mean', 'size_mean', and 'depth_mean'", default=os.path.dirname(__file__))
    parser.add_argument("--label", type=str, help="label for the output files--- e.g. 'EXAMPLE' will have output files 'EXAMPLE-rank_mean.csv', 'EXAMPLE-size_mean.csv', 'EXAMPLE-depth_mean'")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    main(args)
    total_end = time.time()
    logger.info('all finished. total time: {:.2f} seconds'.format(total_end-total_start))

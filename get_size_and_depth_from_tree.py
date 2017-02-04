import sys, os, time
from collections import defaultdict, Counter
from datetime import datetime

import logging
logging.basicConfig(format='%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s',
        datefmt="%H:%M:%S",
        level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_treefile(fname):
    """From the tree file, get the data needed to analyze

    :fname: filename of the tree file
    :returns: node_size_depth: list of tuples,
                size_counts: counter of size: count,
                depth_counts: counter of depth: count

    """
    start = time.time()
    logger.debug("Analyzing tree file...")
    i = 0
    node_cluster = {}
    size_total = Counter()
    cluster_depth = {}
    num_nodes = 0
    

    with open(fname, 'r') as f:
        for line in f:
            i += 1
            if line[0] == "#":
                continue
            line = line.strip().split(' ')

            # Get paper ID
            pid = int(line[2].strip('"'))

            # Get cluster
            cl = line[0]
            cl = cl.split(':')

            # Get depth
            depth = len(cl)

            belongs_to = ":".join(cl[:-1])
            node_cluster[pid] = belongs_to
            size_total[belongs_to] += 1

            if belongs_to not in cluster_depth:
                cluster_depth[belongs_to] = depth

            num_nodes += 1

    size_counts = Counter()
    for count in size_total.itervalues():
        size_counts[count] += 1

    depth_counts = Counter()
    for cl_name, depth in cluster_depth.iteritems():
        depth_counts[depth] += 1

    node_size_depth = []
    for pid, belongs_to in node_cluster.iteritems():
        cl_size = size_total[belongs_to]
        cl_depth = cluster_depth[belongs_to]
        row = (pid, cl_size, cl_depth)
        node_size_depth.append(row)


    end = time.time()
    logger.debug("Done. Took {:2f} seconds.".format(end-start))
    logger.debug("Total number of nodes: {}.\n".format(num_nodes))
    return node_size_depth, size_counts, depth_counts


def output_csv(d, dirname, fname, extension='csv', sep=',', header=None):
    fname = os.path.join(dirname, "{}.{}".format(fname, extension))
    logger.debug("Writing to file: {}".format(fname))
    with open(fname, 'w') as outf:
        if header:
            outf.write(sep.join(header))
            outf.write("\n")

        if isinstance(d, dict):
            for k, v in d.iteritems():
                outf.write("{}{}{}\n".format(k, sep, v))
        elif isinstance(d, list):
            for row in d:
                row = [str(x) for x in row]
                row = sep.join(row)
                outf.write(row)
                outf.write("\n")

def output_node_size_depth(data, dirname, label):
    header = ['pid', 'cl_size', 'cl_depth']
    fname = label+"-node_size_depth"
    output_csv(data, dirname, fname, header=header)

def output_size_counts(data, dirname, label):
    header = ['cl_size', 'num_clusters']
    fname = label+"-size_counts"
    output_csv(data, dirname, fname, header=header)

def output_depth_counts(data, dirname, label):
    header = ['cl_depth', 'num_clusters']
    fname = label+"-depth_counts"
    output_csv(data, dirname, fname, header=header)

def main(args):
    node_size_depth, size_counts, depth_counts = analyze_treefile(args.tree_fname)
    outdir = args.outdir
    label = args.label
    output_node_size_depth(node_size_depth, outdir, label)
    output_size_counts(size_counts, outdir, label)
    output_depth_counts(depth_counts, outdir, label)

if __name__ == "__main__":
    total_start = time.time()
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="From a .tree file, get three analysis files: 1) csv of node_name, size of its cluster, depth of its cluster (this will be a rather large file); 2) csv of cluster size, number of clusters of that size; 3) csv of cluster depth, number of clusters of that depth")
    parser.add_argument("tree_fname", type=str, help="input filename (.tree file)")
    parser.add_argument("-o", "--outdir", type=str, help="directory for the output", default=os.path.dirname(__file__))
    parser.add_argument("--label", type=str, help="label for the output files--- e.g. 'EXAMPLE' will have output files 'EXAMPLE-size_and_depth_pernode.csv', 'EXAMPLE-size_counts.csv', and 'EXAMPLE-depth_counts.csv'")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    main(args)
    total_end = time.time()
    logger.info('all finished. total time: {:.2f} seconds'.format(total_end-total_start))


import sys, os, time
from datetime import datetime

from vi_compare import get_vi_from_fnames

import logging
logging.basicConfig(format='%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s',
        datefmt="%H:%M:%S",
        level=logging.INFO)
logger = logging.getLogger(__name__)

def get_vi_from_line(line, sep=','):
    line = line.strip().split(sep)
    fname_left = line[2]
    fname_right = line[3]
    logger.debug("files to compare: {} | {}".format(fname_left, fname_right))
    vi = get_vi_from_fnames(fname_left, fname_right)
    return {
            'fname_left': fname_left,
            'fname_right': fname_right,
            'vi': vi
            }

def get_vi_from_csv_rownum(csvfilename, rownum):
    rownum = str(rownum)
    vi_dict = {}
    with open(csvfilename, 'r') as f:
        i = 0
        for line in f:
            if line[:len(rownum)] == rownum:
                logger.debug('found line in csv file. line number {} in file'.format(i))
                vi_dict = get_vi_from_line(line)
                break
            i += 1
    return vi_dict
    

def main():
    vi_dict = get_vi_from_csv_rownum(args.csvfilename, args.rownum)
    if vi_dict:
        logger.debug('VI is {}. writing to {}'.format(vi_dict['vi'], args.output.name))
        output = args.sep.join( [vi_dict['fname_left'], vi_dict['fname_right'], str(vi_dict['vi'])] )
        args.output.write(output)
        args.output.write('\n')
    else:
        sys.exit(1)

if __name__ == "__main__":
    total_start = time.time()
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("csvfilename", help="filename for the csv file to read from")
    parser.add_argument("rownum", type=int, help="row number in the csv (corresponds to the idx column)")
    parser.add_argument("--output", type=argparse.FileType('w'), default=sys.stdout, help="output file")
    parser.add_argument("--sep", default=',', help="output delimiter (default: ',')")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    main()
    total_end = time.time()
    logger.info('all finished. total time: {:.2f} seconds'.format(total_end-total_start))

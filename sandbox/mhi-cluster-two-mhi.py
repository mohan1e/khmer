#! /usr/bin/env python
"compare two mhi"
from __future__ import print_function
import khmer
import screed
from cPickle import dump
import argparse
import os.path
import numpy

import sys
sys.path.append('../sourmash')
try:
    import sourmash_lib, sourmash_signature
except ImportError:
    pass

KSIZE=32
COMBINED_MH_SIZE=5000
COMBINE_THIS_MANY=10000

def load_and_tag(ct, filename):
    print('reading and tagging sequences')
    for record in screed.open(filename):
        print('.', record.name)
        ct.consume_and_tag(record.sequence)
    print('...done loading sequences!')

def filter_combined(combined, min_tagcount=100):
    return [ c for c in combined if len(c.get_tags()) >= min_tagcount ]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile1')
    parser.add_argument('infile2')
    parser.add_argument('prefix')
    args = parser.parse_args()
    
    infile1 = args.infile1
    infile2 = args.infile2
    
    print('loading nbhd minhashes 1...')
    nbhd_mh1 = khmer._minhash.load_neighborhood_minhash(infile1)
    print('...done!')
    total_tags = len(nbhd_mh1.get_all_tags())
    
    print('loading nbhd minhashes 2...')
    nbhd_mh2 = khmer._minhash.load_neighborhood_minhash(infile2)
    print('...done!')

    print('building ~chromosome level minhashes 1')
    combined1 = nbhd_mh1.build_combined_minhashes2(1000)
    combined1 = filter_combined(combined1)

    tags_in_combined1 = sum([ len(c.get_tags()) for c in combined1 ])
    print('xxx', total_tags, tags_in_combined1)

    if 1:
        seqfile='head.fa'
        print('loading sequences from', seqfile)

        ct = khmer.Countgraph(KSIZE, 1, 1)
        ct._set_tag_density(200)

    ###

        load_and_tag(ct, seqfile)

        combined2 = []
        for record in screed.open(seqfile):
            print('.2', record.name)
            x = []
            for p, tag in ct.get_tags_and_positions(record.sequence):
                x.append(tag)

            combined2.append(nbhd_mh2.combine_from_tags(COMBINED_MH_SIZE, x))
        print(combined2)
        basename = os.path.basename(seqfile)
    else:
        print('building ~chromosome level minhashes 2')
        combined2 = nbhd_mh2.build_combined_minhashes(COMBINE_THIS_MANY,
                                                      COMBINED_MH_SIZE)

    matched1 = set()
    matched2 = set()
    for i, x in enumerate(combined1):
        for j, y in enumerate(combined2):
            d = x.get_minhash().compare(y.get_minhash())
            if d > 0.05:
                matched1.add(x)
                matched2.add(y)

    print('in common: %d, %d' % (len(matched1), len(matched2)))

    compare = list(matched1)
    compare_names = ["s1.%d" % i for i in range(len(matched1)) ]
    compare += list(matched2)
    compare_names += ["s2.%d" % i for i in range(len(matched2)) ]
    
    D = numpy.zeros([len(compare), len(compare)])
    numpy.set_printoptions(precision=3, suppress=True)
    for i, x in enumerate(compare):
        for j, y in enumerate(compare):
            d = x.get_minhash().compare(y.get_minhash())
            if d > 0.05:
                matched1.add(x)
                matched2.add(y)
                D[i, j] = d

    print(D)
    fp = open(args.prefix, 'wb')
    numpy.save(fp, D)
    fp.close()

    fp = open('%s.labels.txt' % args.prefix, 'w')
    fp.write("\n".join(compare_names))
    fp.close()
    

if __name__ == '__main__':
    main()
    #nbhd_mh, combined = main()

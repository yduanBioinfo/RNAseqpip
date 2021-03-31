#!/usr/bin/env python3
'''
_version = 0.2.3
wrapper for RNAseqpip programs
'''
from __future__ import print_function
import sys, re, os, copy
from threading import Thread
import subprocess
import logging
import argparse

import hisat, cufflinks, NOISeq, htseq
import funcAnnot.b2gprog.GOannot as GOannot
import funcAnnot.kegg.KOannot as KOannot
from funcAnnot.kegg.annot2go_stat import annot2go_stat
from funcAnnot.annot_from_db import annot
from funcAnnot.kegg.koenrich.keggenrich import enrich as koenrich
from progsuit import Configuration, Group_data, getAbsPath, matchpath, log
from get_gene_length import len_for_Rsp
from get_geneids import get_geneids
    
logging.basicConfig()
FILEPATH=os.path.realpath(__file__)
FILEDIR=os.path.dirname(FILEPATH)
BASE_CONF=FILEDIR+"/confs/base.conf"

def add_arguments(parser):
    parser.add_argument('-c','--conf',help='configuration file',nargs='?',\
    default=None)
    parser.add_argument('-g','--group_data',help='group_data file. conflict with -1 -2',nargs='?')
    parser.add_argument('-v','--verbose',help='Out put all running information. Typically used in debug.',default=False,action='store_true')
    parser.add_argument('-q','--quite',help='Running quitely.',default=False,action='store_true')
    parser.add_argument('-o','--outpath',help='outpath',nargs='?')

def main(argv):
    parser = argparse.ArgumentParser(description='RNA-seq analyse pipeline')
    parser.add_argument('program',help='all for whole pip/ali for alignment/ass for assembly/\
    cptDE for compute different expression',choices=['all','cptDE','seq2exp','func','verse'])
    args=parser.parse_args(argv[1:2])

    if args.program == 'cptDE':
        from cptDE import main as sub_main
        sub_main(argv[1:])

    if args.program == 'seq2exp':
        from seq2exp import main as sub_main
        # should avoid position parser.
        sub_main(argv[1:])
        
    if args.program == 'func':
        from func import main as sub_main
        sub_main(argv[1:])

    if args.program == 'verse':
        from verse import main as sub_main
        sub_main(argv[1:])
        
if __name__ == '__main__':
    import sys
    main(sys.argv)

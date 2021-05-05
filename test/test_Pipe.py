# Test RNASeqpipe class

import sys, os
import subprocess
import filecmp
import glob
from ..run_RNAseqpipe import main as run_main

gp_root="./test/RNAseqpip_data/data/gps"
# template file
tp=gp_root + "/small_group_data_template.txt"
# small group file
sg=gp_root + "/small_group_data.txt"
# Configurations
cf_root="./confs"

# Requeired data
genome = "./test/RNAseqpip_data/data/test_genome.fa"
gff = "./test/RNAseqpip_data/data/test.dlmrna.gc.final.gff"

# Reference results
refroot = "./test/RNAseqpip_data/refout"

def _check_exist(targets):
    """ Make sure targets files exist and not empty 
    (bigger than 100)."""
    for t in targets:
        assert os.path.exists(t) and os.path.getsize(t) > 100

def test_hvc(tmpdir):
    """Hisat2 + stringtie + verse + salmon

    ## Check if the t is identical with reference file.
    ## But the results are not allways the same,
    ## so, this procedure will not be performed.
    ## way1
    #assert open(refdir+"/"+t).read() == open(tmpdir.join(t)).read()
    ## way2
    #assert filecmp.cmp(refdir+"/"+t,tmpdir.join(t))
    """
    #refdir = refroot+"/hvc_count_out"
    order = "./run_RNAseqpipe.py seq2exp -c {0}/dUTP.conf,{0}/gc_no_gff.conf,{0}/hisat_stringtie_verse.conf -g {1} -o {2} ".format(cf_root,sg,tmpdir).split()
    subprocess.call(order)
    
    targets = ["all_flagstat.txt","merged_asm/merged.fa","merged_asm/merged.gtf","salmon/quant_merge.elen","salmon/quant_merge.numreads","salmon/quant_merge.len","salmon/quant_merge.tpm"]
    targets = map(tmpdir.join, targets)
    _check_exist(targets)
    _check_exist(glob.glob(str(tmpdir.join("merged*.count"))))

def test_hcv(tmpdir):
    """Hisat2 + cufflinks + verse"""
    #refdir = refroot+"/hcv_out"
    order = "./run_RNAseqpipe.py seq2exp -c {0}/gc_no_gff.conf,{0}/hisat_cuff_verse.conf -g {1} -o {2} ".format(cf_root,sg,tmpdir).split()
    subprocess.call(order)
    
    targets = ["all_flagstat.txt","merged_asm/merged.fa","merged_asm/merged.gtf","salmon/quant_merge.elen","salmon/quant_merge.numreads","salmon/quant_merge.len","salmon/quant_merge.tpm"]
    targets = map(tmpdir.join, targets)
    _check_exist(targets)
    _check_exist(glob.glob(str(tmpdir.join("merged*.count"))))

def test_hv(tmpdir):
    """Hisat2 + verse"""
    #refdir = refroot+"/hcv_out"
    order = "./run_RNAseqpipe.py seq2exp -c {0}/gc.conf,{0}/hisat_verse_count.conf -g {1} -o {2}".format(cf_root,sg,tmpdir).split()
    subprocess.call(order)
    
    targets = ["all_flagstat.txt"]
    targets = map(tmpdir.join, targets)
    _check_exist(targets)
    _check_exist(glob.glob(str(tmpdir.join("merged*.count"))))

def test_salmon(tmpdir):
    """salmon"""
    #refdir = refroot+"/hcv_out"
    order = "./run_RNAseqpipe.py salmon --gtf {0} -g {1} -o {2} --genome {3}".format(gff,sg,tmpdir,genome).split()
    subprocess.call(order)
    
    targets = ["quant_merge.elen","quant_merge.numreads","quant_merge.len","quant_merge.tpm"]
    targets = map(tmpdir.join, targets)
    _check_exist(targets)

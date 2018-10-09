#!/usr/bin/env sh

# INIT of group_data
# Directory for group data files.
gp_root="data/gps"
# template file
tp="${gp_root}/small_group_data_template.txt"
# small group file
sg="${gp_root}/small_group_data.txt"
./init_test_data.sh ${tp} > ${sg}

# Configuration files
cf_root="../../confs"

mkdir testout
# set2exp count mode
# quite mode
#../../RNAseqpip.py seq2exp -c ${cf_root}/hisat_stringtie_verse.conf -g ${sg} -o testout/hvc_count_out -q && echo "hsv seq2exp done!" || echo "hsv seq2exp faild!"
# verbose mode
../../RNAseqpip.py seq2exp -c ${cf_root}/hisat_stringtie_verse.conf -g ${sg} -o testout/hvc_count_out --verbose && echo "hsv seq2exp done!" || echo "hsv seq2exp faild!"
echo "../../RNAseqpip.py seq2exp -c ${cf_root}/hisat_stringtie_verse.conf -g ${sg} -o testout/hvc_count_out --verbose" 

# hisat cufflinks verse
# quite mode
#../../RNAseqpip.py seq2exp -c ${cf_root}/hisat_cuff_verse.conf -g ${sg} -o testout/hsv_out -q && echo "hcv seq2exp done!" || echo "hcv seq2exp faild!"
# verbose mode
../../RNAseqpip.py seq2exp -c ${cf_root}/hisat_cuff_verse.conf -g ${sg} -o testout/hsv_out --verbose && echo "hcv seq2exp done!" || echo "hcv seq2exp faild!"

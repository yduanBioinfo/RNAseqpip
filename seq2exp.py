#!/usr/bin/env python

from __future__ import print_function
import sys
import hisat, cufflinks, htseq

from progsuit import Configuration, Group_data, getAbsPath, matchpath

def seq2exp(myconf,myfq1,myfq2,fqnames,ali_path,ali_name,mygroup_data,run_cdiff=True):
	#from fastq to assembly gff
	#run_cdiff: if cuffdiff step should be performed

	ali_ress,sort_ress = hisat.pip_hisats(myconf,myfq1,myfq2,fqnames,ali_path,ali_name)
	#alignment results,samtools sorted results

	cufflinks_ress = cufflinks.cufflinks(myconf,sort_ress)#cufflinks results

	#write path/assembly.txt
		
	assembly = ali_path+"/assembly.txt"
	cu_ress_f = open(assembly,'w')
	cu_ress_f.write("\n".join(cufflinks_ress))
	cu_ress_f.close()
		
	merged = cufflinks.cuffmerge(myconf,assembly,ali_path+"/merged_asm")
	quants = cufflinks.cuffquants(myconf,sort_ress,merged)
	norm = cufflinks.cuffnorm(myconf,quants,merged,ali_path)
	gene_fpkm = norm+"/genes.fpkm_table"#cufflinks fpkm
	samples_table = norm+"/samples.table"
	#run cuffdiff
	treat_group = mygroup_data.get_g_cdgp()
	#{group1:[dataname1,dataname2,...],group2:[],...}
	try:
		gpnames1,gpnames2=treat_group.values()
	except:
		print(treat_group.values(),file=sys.stderr)
		run_cdiff = False
		sys.stderr.write("Warning:only two group data can run cuffdiff!\n")
		sys.stderr.write("cuffdiff step skipped\n")
	
	if run_cdiff:
		quants1,quants2 = matchpath(gpnames1,gpnames2,quants)
		cu_diff = ali_path+"/diffout"
		cufflinks.cuffdiff(myconf,merged,quants1,quants2,cu_diff)
	
	#cuffdiff end
	htcount = htseq.htseqpip(myconf,sort_ress,ali_path,merged,plotqa=False)
	#return expressionf	
	return gene_fpkm, htcount, quants, merged
	
def main(argv):
	
	import argparse, sys
	
	parser = argparse.ArgumentParser(description='RNA-seq seq2exp program')
	parser.add_argument('-c','--conf',help='configuration file',nargs='?',\
	type=argparse.FileType('r'),default='configuration.txt')
	parser.add_argument('-1','--fq1',help='fq_1',nargs='*')
	parser.add_argument('-2','--fq2',help='fq_2',nargs='*')
	parser.add_argument('-g','--group_data',help='group_data file. conflict with -1 -2'\
	,nargs='?',type=argparse.FileType('r'))
	parser.add_argument('-o','--outpath',help='outpath',nargs='?')
	args = parser.parse_args(argv[1:])

	if len(argv) == 1:
		parser.print_usage()
		sys.exit(1)

	myconf = Configuration(args.conf)
	ali_path = getAbsPath(args.outpath)#home path for alignment results
	ali_name = 'mapped.sam'#alignment result name
	
	if args.group_data and args.fq1:
		raise StandardError("You can't specify both -g and -1 the same time")
	#input data processing
	#convert group_data 2 paired data
	#check if fq1 contains as many files as fq2 is when dealing with paired data
	if args.group_data:
		mygroup_data = Group_data(args.group_data)
		fqnames, myfq1, myfq2 = mygroup_data.get2pip()
	else:
		myfq1 = args.fq1
		myfq2 = args.fq2
		fqnames = ["" for i in range(len(myfq1))]
		
	if args.fq2 and len(args.fq1) != len(args.fq2):
		raise StandardError("-2 should be as long as -1\n")

	seq2exp(myconf,myfq1,myfq2,fqnames,ali_path,ali_name,mygroup_data,run_cdiff=False)
		
if __name__ == '__main__':

	import sys
	main(sys.argv)
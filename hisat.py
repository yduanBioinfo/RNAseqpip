#!/usr/bin/env python

import sys, os, copy
from progsuit import Configuration, Prog_Rsp
from collections import OrderedDict as Ordic

'''
[usage] : ./hisat.py build/align/balign [hisat style order]
build : build hisat2 index [hisat-2_build]
align : align using hisat2 build
balign : align using hisat2 build and if index is not exist, build it.
'''

CLIP_CONVERTER=os.path.join(os.path.dirname(__file__),"conv_clipping.sh")

def check_index(index):

	for i in range(1,9):
		if os.path.isfile(index+'.'+str(i)+'.ht2'):
			continue
		return False
	return True
		
def build_index(fasta,index):

	file = os.popen("hisat2-build %s %s"%(fasta,index))
	sys.stderr.write(file.read())
	error_handle(file.close())#return exit status
	
def pip_hisat(myconf,fq1,fq2,subpath,ali_path,ali_name,conv_clip=True,silence=False):
	#myconf : Configuration obj
	#ali_path : alignment out path
	#outfile=/ali_path/subpath/ali_name
	rm_sam = True#only store sorted bamfile to save room
	sm = "4G"#memory using in sort
	
	#build index if needed
	if not check_index(myconf['hisat2']['-x']):
		build_index(myconf['all']['genome'],myconf['hisat2']['-x'])
	
	#hisat2
	if not subpath:
		subpath = os.path.basename(fq1).split(".")[0]
	ali_path = getAbsPath(ali_path+"/"+subpath)
	#add filename in path [hisat2 out path]
	hst_out = ali_path+"/"+ali_name
	#hisat2 out : /abs/path/to/name.sam
	
	#run hisat2
	order1 = {'-1':fq1,'-S':hst_out}
	if fq2:
		order1['-2'] = fq2
	order2 = {}
	hisat2 = Prog_Rsp(myconf,"hisat2",order1,order2,silence)
	hisat2.run()
	#clipping convert
	#convert soft-clipping that stringtie needed to hard-clipping which is supported by cufflinks.
	if conv_clip:
		n_conv = hst_out.rstrip(".sam")+"_conv.sam"
		os.system(CLIP_CONVERTER+" %s %s"%(hst_out,n_conv))
		os.system("rm %s"%hst_out)#remove samfile1
		hst_out = n_conv
	
	#sort
	bamname = "sort.bam"
	sort_out = ali_path+"/"+bamname
	#sort out : /abs/path/to/sort.bam
	
	#run sort
	process = 8
	samtools = getOrder("samtools",myconf['prog_path']) 
	os.system("%s sort -o %s -@ %s -m %s %s"%\
	(samtools,sort_out,process,sm,hst_out))
	
	if rm_sam:
		os.system("rm %s"%hst_out)
	
	return hst_out, sort_out #alignment result name
	
def pip_hisats(conf,fq1,fq2,subpath,ali_path,ali_name):
	#conf : Configuration obj
	
	result = []#hisat result
	result_s = []#sorted results
	for i in range(len(fq1)):
		myfq1 = fq1[i]
		try:
			myfq2 = fq2[i]
		except:
			myfq2 = None
		tmp = pip_hisat(conf,myfq1,myfq2,subpath[i],ali_path,ali_name)
		result.append(tmp[0])
		result_s.append(tmp[1])
		
	return result,result_s
	
def getAbsPath(inpath,default='./tmp'):

	if not inpath:
		inpath = default
	if not os.path.isdir(inpath):
		os.makedirs(inpath)
	return os.path.abspath(inpath)
	
def getOrder(order,myPconf):

	if order in myPconf:
		return myPconf[order]
	return order

def error_handle(code,name="unknown"):

	if code:
		sys.stderr.write("Error\n")
		sys.exit(99)
		
if __name__ == '__main__':

	import sys
	
	if sys.argv[1] == 'build':
		status = build_index(sys.argv[2],sys.argv[3])
	
	elif sys.argv[1] == 'align':
		status = alignment(sys.argv[2:-1],sys.argv[-1])
		
	elif sys.argv[1] == 'balign':
		pass
	else:
		sys.exit(1)
		
	print(status)

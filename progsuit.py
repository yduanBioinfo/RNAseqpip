#!/usr/bin/env python

import os, re, sys, copy
from collections import OrderedDict as Ordic

class Pconf(object):

	'''
	parameters for a certain program or general(all).
	data={parameter1:value,parameter2:value}
	'''

	def __init__(self,conf,name='all'):

		self.name = name
		self._pr_pattern = re.compile(r"([^=#]+)=([^=#]+)")#parameter pattern
		self.data = self.parse_file(conf)#record name and path
		
	def __getitem__(self,key):
	
		return self.data.get(key)
		
	def __contains__(self,value):
	
		return self.data.has_key(value)
		
	def __setitem__(self,key,value):
	
		self.data[key] = value

	def get(self,key):
	
		return self.__getitem__(key)
		
	def items(self):
	
		return self.data.items()
		
	def values(self):
	
		return self.data.values()
	
	def keys(self):
	
		return self.data.keys()
		
	def parse_file(self,conf):

		mydic = Ordic()#save file name and path
		for eachline in conf:
			tmp = self._pr_pattern.match(eachline)
			if not tmp:
				continue
			if tmp.group(1).strip() in mydic.keys():
				print("Warning:repeat names : %s"%tmp.group(1))
			mydic[tmp.group(1).strip()] = tmp.group(2).strip()
		return mydic
		
class Configuration(Pconf):

	'''
	handle configuration.txt of RNAseqpip
	data = {program1:Pconf1,program2:Pconf2}
	'''
	
	def __init__(self,conf):
		
		self._st_pattern = re.compile(r"\<(\S+)\>")
		self._ed_pattern = re.compile(r"\<[/](\S+)\>")
		self.data = {} 
		self.parse_file(conf)
		
	def parse_file(self,conf):
	
		paras = [] #parameters
		name = ''
		
		for eachline in conf:
			#print(eachline)
			st = self._st_pattern.search(eachline)
			ed = self._ed_pattern.search(eachline)
			if name and ed:
				#end of a program
				if name != ed.group(1):
					sys.stderr.write("\
					configuration format error!\n")
					sys.exit(1)
				self.data[name] = Pconf(paras)
				paras = []
				name = ''
			elif name and name not in self.data:
				#parameters of program and unique
				paras.append(eachline)
			elif not name and st:
				#start of a program
				name = st.group(1)
			else:
				pass

class Dataset(Pconf):
	'''
	dataset in group_data
	'''
	
	def __init__(self,conf):
	
		self._seqData = {}
		super(Dataset,self).__init__(conf)
		self.filetype = self.data.get('filetype')
		self.library = self.data.get('library')
		
	def parse_file(self,conf):

		mydic = Ordic()#save file name and path
		for eachline in conf:
			tmp = self._pr_pattern.match(eachline)
			if not tmp:#maybe seq data information
				self._append_seq(eachline)
				continue
			if tmp.group(1).strip() in mydic.keys():
				print("Warning:repeat names : %s"%tmp.group(1))
			mydic[tmp.group(1).strip()] = tmp.group(2).strip()
		return mydic
		
	def _append_seq(self,line,sep="\t"):
	
		line = line.rstrip("\n")
		if not line:
			return
		lst = line.split(sep)
		self._seqData[lst[0]] = tuple(lst[1:])
		
	def values(self):
	
		return self._seqData.values()
		
	def items(self):
	
		return self._seqData.items()
			
class Group(object):
	'''
	group in group_data
	'''

	def __init__(self,conf):
	
		self._data = Ordic()
		self._header = []
		self.parse_file(conf)
		
	def parse_file(self,lst,sep="\t"):
		
		assert isinstance(lst,list)
		self._header = lst[0].rstrip("\n").split(sep)[1:]
		for each in lst[1:]:
			tmp = each.rstrip("\n").split(sep)
			self._data[tmp[0]] = tuple(tmp[1:])
			
	def get_sample(self,key):
	
		return self._data.get(key)
		
	def get_header(self):
	
		return self._header
		
	def get_group(self,key):
	
		if key not in self._header:
			return
		outlst = []
		indx = self._header.index(key)
		for key, value in self._data.items():
			outlst.append((key,value[indx]))
		return outlst
		
	def get_groups(self):
	
		outlst = []
		for key,value in self._data.items():
			tmp = [key]
			tmp.extend(value)
			outlst.append(tuple(tmp))
		return outlst
	
	def get_cdgp(self,indx=0):
		#group for cuffdiff
		#{treat1:[treat1_1,treat1_2,...],treat2:[treat2_1,treat2_2,...]}
		#indx: which column should be as covariate
		
		outdata = {}
		for key,value in self._data.items():
			outdata.setdefault(value[indx],[]).append(key)
		return outdata
			
class Group_data(Configuration):
	'''
	parse group file in RNAseqpip
	'''
	
	def __init__(self,conf):
		
		self.group = ''#Group object
		super(Group_data,self).__init__(conf)
		
	def parse_file(self,conf):
	
		paras = [] #parameters
		name = ''
		
		for eachline in conf:
			#print(eachline)
			st = self._st_pattern.search(eachline)
			ed = self._ed_pattern.search(eachline)
			if name and ed:
				#end of a program
				if name != ed.group(1):
					sys.stderr.write("\
					configuration format error!\n")
					sys.exit(1)
				if name == 'GROUP':
					self.group = Group(paras)
					paras = []
					name = ''
					continue
				self.data[name] = Dataset(paras)
				paras = []
				name = ''
			elif name and name not in self.data:
				#parameters of program and unique
				paras.append(eachline)
			elif not name and st:
				#start of a program
				name = st.group(1)
			else:
				pass
	
	def _items(self):
		
		for each_set in self.values():
			for name, file in each_set.items():
				yield name, file
				
	def get_seqf(self):#get sequencing file
	#PE only!!!!!
		outlst = [[],[]]
		for each_set in self.values():
			for a, b in each_set.values():
				outlst[0].append(a)
				outlst[1].append(b)
		return outlst
	
	def get_g_group(self,key):
	
		return self.group.get_group(key)
		
	def get_g_groups(self):
		
		return self.group.get_groups()
		
	def get_g_header(self):
	
		return self.group.get_header()
	
	def get_g_cdgp(self):
		#group for cuffdiff
		#[(treat1_1,treat1_2,...),(treat2_1,treat2_2,...)]
		
		return self.group.get_cdgp()
		
	def get_items(self):
		
		outlst = []
		for each in self._items():
			outlst.append(each)
		return outlst
			
	def get2pip(self):

		names = []
		fq1 = []
		fq2 = []
		for name, values in self._items():
			names.append(name)
			fq1.append(values[0])
			try:
				fq2.append(values[1])
			except:
				fq2.append('')
		return names,fq1,fq2
			
class Prog(object):
		
	def run_order(self,order,name="unknown",silence=False):
	
		file=os.popen(order)
		if not silence:
			print(file.read())
		self.error_handle(file.close(),name)
		
	def error_handle(self,code,name="unknown"):
	
		if code:
			sys.stderr.write("Error in %s step.\n" % name)
			sys.exit(99)
			

class Prog_Rsp(Pconf,Prog):

	'''Prog class for RNAseqpip
	'''
	
	def __init__(self,Conf,progname,order1={},order2={},silence=False):
		#Conf is a Configuration object.
		#progname should be same with which in configuration.txt
		#order1 and order2 be as {a:valuea,b:valueb,c:"",d:"aaa bbb",...}
		#order1 has high priority, order2 has low priority
		#self.data = {parameter1:value1,parameter}
		
		self.Conf = Conf
		self.progname = progname
		self.myPconf = self.Conf[progname] if self.Conf[progname] else {}#16/7/26
		self.order1, self.order2 = order1, order2
		self.silence = silence
		#changed in 16/7/2
		#self.data = order1
		self.data = Ordic()
		self.data.update(order1)
		#changed in 16/7/2
		self.data.update(self.diff_orders(self.myPconf,order1))
		self.data.update(self.diff_orders(order2,self.myPconf,order1))
		
	def run(self):
		#for outside use
	
		order = self.gen_order(self.progname,self.data)
		sys.stderr.write(order+"\n")
		return self.run_order(order,self.progname,self.silence)
		
	def get_prog_path(self,prog,myConf):
		#myConf is a Configuration object.(should be self.Conf)
		#return prog path if in myConf

		return self.getOrder(prog,myConf["prog_path"])
		
	def getOrder(self,order,myPconf):
		#if order in myPconf,return value else return order
		
		if order in myPconf:
			return myPconf[order]
		return order
		
	def gen_order(self,program,orders):
		#generate order for run 
		#orders is a dict
		
		tmporder = ""
		for key, value in orders.items():
			if key == "locp":#location parameter
				if isinstance(value,list):
					#more than one parameters
					tmporder += " "+" ".join(value)
					continue
				assert isinstance(value,str)
				#only one parameter
				tmporder += " "+value
				continue
			tmporder += " "+str(key)+" "+str(value)
		outorder=self.get_prog_path(program,self.Conf) + tmporder
		return outorder
		
	def diff_orders(self,order1,order2={},order3={}):
		#get orders in order1 but not in order2 and order3
		#order2 has higher priority than order3
		
		outorder = Ordic()
		if not order1:
			return outorder
		for key,value in order1.items():
			if key in order2 or key in order3:
				continue
			outorder[key] = value
		return outorder

def getAbsPath(inpath,default='./tmp'):

	if not inpath:
		inpath = default
	if not os.path.isdir(inpath):
		os.makedirs(inpath)
	return os.path.abspath(inpath)
	
if __name__ == '__main__':

	#myconf = Configuration(open("../conf2.txt"))
	#bam = "/home/yduan/data/growth/ruibo/pip/tmp/2014-11-BB2/sort.bam"
	#cufflinks = Prog_Rsp(myconf,"cufflinks",{"-o":"xxxx","-p":"8",bam:""})
	#cufflinks.run()
	import sys
	mygroup_data = Group_data(open(sys.argv[1]))
	#print(mygroup_data.group)
	#print(mygroup_data.get2pip())
	print(mygroup_data.group.get_header())
	print(mygroup_data.get_g_header())
	print(mygroup_data.group.get_groups())
	print(mygroup_data.get_g_groups())
	print(mygroup_data.get_g_cdgp())
	x = mygroup_data.get_g_cdgp()
	z,y = x.values()
	print(z)
	print(y)
import datetime
import json
import logging
# import sys
# fdsdfasf
# import collections
import re
# import xlrd
import subprocess
import types
#from datetime import datetime
import datetime
from logging import handlers

from neolib.core_util import *
from neolib.file_util import *


# import  shutil
# import time
#
# import pymysql
# import  json
#
# import xlrd

#from neolib.general_import import *




def executeAsync( cmd):
	fd = subprocess.Popen(cmd, shell=True,
						  stdin=subprocess.PIPE,
						  stdout=subprocess.PIPE,
						  stderr=subprocess.PIPE)
	return fd.stdout, fd.stderr

def listarg2Map(list):
	maparg = {}
	i = 0
	while i < len(list):
		value = list[i]


		if value.startswith("-"):
			value = re.sub("-","",value)
			print(value)
			nextvalue = list[i + 1] if i +1 < len(list) else ""
			nextvalue = "" if  nextvalue.startswith("-") else nextvalue

			maparg[value] = nextvalue


		i=i+1
	return maparg



def deffilter(root,file):
	return  True

def listAllFile(basedir,filter=deffilter):
	listaa = []
	for root, dirs, files in os.walk(basedir):
		root = root.replace("\\","/")
		for file in files:
			if not filter(root,file): continue
			listaa.append((root,file))

	return listaa

def getExtNameFromPath(path):
	return os.path.splitext(path)[1]


def removeEmptyFolder(basedir):
	listaa = []
	while True:
		for root, dirs, files in os.walk(basedir):
			# print(root,len(files),len(dirs))
			sublen = len(files) + len(dirs)
			if sublen == 0: listaa.append(root)

		if len(listaa) == 0: return

		for tmp in listaa:
			# shutil.rmtree(tmp)
			print(tmp)
			os.rmdir(tmp)

			def removeEmptyFolder(basedir):
				listaa = []
				while True:
					for root, dirs, files in os.walk(basedir):
						# print(root,len(files),len(dirs))
						sublen = len(files) + len(dirs)
						if sublen == 0: listaa.append(root)

					if len(listaa) == 0: return

					for tmp in listaa:
						# shutil.rmtree(tmp)
						print(tmp)
						os.rmdir(tmp)

def def_process(*args) :
	n, iter, idx, size = args
	return n[idx:idx + size]

def do_while_template(main_param, total_size, unit_size, process=def_process,
                      process_init=lambda *args: None,
                      process_end=lambda *args: None,
                      prcess_filter=lambda struct_local:(struct_local.main_param, struct_local.iter, struct_local.buff_index, struct_local.real_size)):
	"""
	enable struct_local method are  flows for prcess_filter
	['total_size',  'iter', 'remain_size', 'length', 'unit_size', 'buff_index', 'process_end', 'main_param']

	"""
	remain_size = total_size

	buff_index = 0
	list_ret = []
	iter =0
	#print(locals().keys())
	real_size =0
	args = prcess_filter(Struct(**locals()))
	ret_process = process_init(*args)

	if ret_process != None:
		list_ret.append(ret_process)

	while remain_size>0:
		real_size = min(remain_size, unit_size)
		args = prcess_filter(Struct(**locals()))
		ret_process = process(*args)
		try:
			if ret_process == None:
				break
			list_ret.append(ret_process)
		finally:
			remain_size -= unit_size
			buff_index += unit_size
			iter +=1
	args = prcess_filter(Struct(**locals()))
	ret_process = process_end(*args)
	if ret_process != None:
		list_ret.append(ret_process)

	return 	list_ret



def sample_while():
	sample_buff = "0123456789"*10
	print(sample_buff)
	prcess_filter = lambda struct_local: (
	struct_local.main_param, struct_local.iter, struct_local.buff_index, struct_local.real_size)
	prcess = lambda n, iter,idx, size: n[idx:idx + size]
	list_ret = do_while_template(sample_buff,len(sample_buff),10,prcess,prcess_filter=prcess_filter)

	#list_ret = SampleWhileTemplate(sample_buff,len(sample_buff),10).get_result()
	print(list_ret)

def get_safe_mapvalue(maparg,key,defvalue=''):
	if key in maparg:
		return maparg[key]
	return defvalue

def _linux_set_time(time_tuple):
	import ctypes.util
	import time

	# /usr/include/linux/time.h:
	#
	# define CLOCK_REALTIME                     0
	CLOCK_REALTIME = 0

	# /usr/include/time.h
	#
	# struct timespec
	#  {
	#    __time_t tv_sec;            /* Seconds.  */
	#    long int tv_nsec;           /* Nanoseconds.  */
	#  };
	class timespec(ctypes.Structure):
		_fields_ = [("tv_sec", ctypes.c_long),
					("tv_nsec", ctypes.c_long)]

	librt = ctypes.CDLL(ctypes.util.find_library("rt"))

	ts = timespec()
	ts.tv_sec = int( time.mktime( datetime.datetime( *time_tuple[:6]).timetuple() ) )
	ts.tv_nsec = time_tuple[6] * 1000000 # Millisecond to nanosecond

	# http://linux.die.net/man/3/clock_settime
	librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))

class NeoLogger(logging.Logger):
	def debug_f(self, msg: str, *args, **kwargs):
		self.debug(msg.format(*args, **kwargs))

	def info_f(self, msg: str, *args, **kwargs):
		self.info(msg.format(*args, **kwargs))

	def warning_f(self, msg: str, *args, **kwargs):
		self.warning(msg.format(*args, **kwargs))

	def error_f(self, msg: str, *args, **kwargs):
		self.error(msg.format(*args, **kwargs))

	def critical_f(self, msg: str, *args, **kwargs):
		self.critical(msg.format(*args, **kwargs))


def create_logger(loggename,formatter = '%(threadName)s %(asctime)s - %(name)s - %(levelname)s - %(message)s',
				logger_class = None,
                  handler=None
                  ):
	'''
	formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	'''
	if handler == None:
		handler = handlers.TimedRotatingFileHandler(filename="log.txt", when='D')

	#handler = handlers.TimedRotatingFileHandler(filename=loggename + ".txt", when='D')
	#loggename = loggename
	# create logger
	if logger_class == None:
		logger = logging.getLogger(loggename)
	else:
		logger = logger_class(loggename)

	logger.setLevel(logging.DEBUG)

	# create console handler and set level to debug
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)

	# create formatter
	formatter = logging.Formatter(formatter)

	# add formatter to ch
	ch.setFormatter(formatter)
	handler.setFormatter(formatter)

	logger.handlers.clear()

	# # add ch to logger
	# logger.removeHandler(ch)
	# logger.removeHandler(handler)

	logger.addHandler(ch)
	logger.addHandler(handler)

	return logger

def json_pretty(json_obj,sort_keys=False,is_datetime_to_str=False,default=None):
	def myconverter(o):
			if isinstance(o, datetime.datetime):
				return o.__str__()


	if is_datetime_to_str:
		default = myconverter
	return json.dumps(json_obj, sort_keys=sort_keys, indent=4, separators=(',', ': '),ensure_ascii=False,default=default)

def get_data_from_file(filename):
	str = StrFromFile(filename)
	return json.loads(str)
def note_with_unit(bytes, unit='B'):
	KB = 1024
	tmpByte = float(bytes)
	prevByte = float(tmpByte)
	tuple_bunit = ("", "K", "M", "G", "T")
	count = 0
	while True:
		tmpByte /= KB
		if tmpByte < 1:
			break
		prevByte = tmpByte
		count += 1

	bunit = tuple_bunit[count]


	ret = "%.2f"%prevByte


	return ret + bunit+unit

def devide_by_unitsize(orgsize,unitsize):
	list_inputsize_per_loop = [unitsize for _ in range(int(orgsize / unitsize))]
	remain = orgsize % unitsize
	if remain > 0:
		list_inputsize_per_loop.append(remain)
	return list_inputsize_per_loop



def seperate_filter(hex_str_filter,org_hex_str_buff):
	return [ org_hex_str_buff[match.start(0):match.end(0)] for match in re.finditer(r'FF+',hex_str_filter)]


def imports():
	for name, val in globals().items():
		if isinstance(val, types.ModuleType):
			yield val.__name__

def get_ext_name_from_path(path):
	root,ext = os.path.splitext(path)
	return ext

def get_datetime_str(fmt= "%Y-%m-%d %H:%M:%S"):
	return datetime.datetime.now().strftime(fmt)

def split_by_list(obj_like_list,list_sep)->list:
	obj  = Struct()
	obj.st_idx = 0
	def process(obj,buf,idx):
		ret_val = buf[obj.st_idx:obj.st_idx + idx]
		obj.st_idx += idx
		#print(ret_val)
		return ret_val
	return [ process(obj,obj_like_list,val_idx) for idx,val_idx in enumerate(list_sep)]
def split_size_by_unit(obj_like_list_size,unit):
	loop = obj_like_list_size // unit
	remain = obj_like_list_size % unit
	list_sep = [unit]*loop
	if remain>0:
		list_sep.append(remain)
	return list_sep
	#return split_by_list(obj_like_list,list_sep)

def split_by_unit(obj_like_list,unit):
	list_sep = split_size_by_unit(len(obj_like_list) ,unit)
	return split_by_list(obj_like_list,list_sep)

	#return [obj_like_list[unit * idx:unit * idx + unit] for idx in range(len(obj_like_list) // unit)]

def simple_view_list(obj_like_list,tab_idex=0):

	for tmp in obj_like_list:
		if type(tmp) == Struct:
			print("neo Struct:" * tab_idex, tmp.get_dict())
			continue
		print("\t"*tab_idex,tmp)
		if type(tmp) == list:
			simple_view_list(tmp,tab_idex+1)



def replace_contents_by_tag( sttag, edtag,contents, org_contents):

	patt = r"({0})(.+)({1})".format(sttag, edtag)
	comp = re.compile(patt, re.DOTALL)
	match = comp.search(org_contents)
	if match == None:
		raise Exception("SEARCH FAIL")
	new_contents = comp.sub(r"\1\n" + contents + r"\3", org_contents)


	return new_contents

def get_base_dir(cur_file):
	return os.path.dirname(os.path.dirname(os.path.abspath(cur_file)))
if __name__ == '__main__':
	ret = split_by_unit(b'0123456789012345678901234567890',10)
	print(ret)
	ret = split_size_by_unit(24,10)
	exit(ret)
	sample_while()
	exit()
	ext= get_ext_name_from_path("C:/app/PYTOOL/pythonshell.py")
	print(ext)
	exit()
	print(list(find_files("D:/PROJECT/GIANT/RELEASE/tcp_client_sample/giant_auth")))
	exit()
	print(devide_by_unitsize(1024+1,1024))
	print(note_with_unit(4400000000+4693331968))
	print(note_with_unit(1025))
	print(note_with_unit(0))

def input_multi_lines(title = "input msg for history(X is break):\n",exit_str="X"):
	msg = ""
	while True:
		sub = input(title)
		if sub == exit_str:
			break
		msg += "\n" + sub

		# print(msg)
		title = ""
	return msg
						# if __name__ != '__main__':
# 	exit()
#
# print(ConvStringForm(intype="und",outtype='cam').ConvertString("TEST_ABCCC_DDDD"))
# print(ConvStringForm(intype="spc",outtype='cam').ConvertString("TEST ABCCC DDDD"))
# print(ConvStringForm(intype="cam",outtype='und').ConvertString("TestAbhAaaAcc"))
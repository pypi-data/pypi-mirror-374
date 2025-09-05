import os, sys
import re
import shutil

from pprint import pprint

from neolib.file_util import find_files_simple
from neolib.neo_class import NeoRunnableClass
print("start")
print(sys.argv)


def safe_copy(org_path, dst_file):
	org_path = os.path.abspath(org_path)
	dst_file = os.path.abspath(dst_file)
	dst_dir = os.path.dirname(dst_file)
	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)

	shutil.copy2(org_path, dst_file)
	print("copied", org_path, "\n\t-->", dst_file)

def make_normal_abs(path_name):
	return  os.path.abspath(path_name).replace("\\","/")

class ReleaseClass(NeoRunnableClass):
	def init(self):
		print(self.map_args)
		self.cmd = self.map_args.get("cmd")
		self.header_path = self.map_args.get("input_dir")
		self.base_pub_dir = self.map_args.get("out_dir")
		self.not_recursive = self.map_args.get("not_recursive",False)
		self.ext_name = self.map_args.get("ext_name")
		self.reg_exp = self.map_args.get("reg")
		self.str_forbidden = self.map_args.get("forbidden")
		self.platform = self.map_args.get("platform")
		
		
		
		self.list_ext = [f".{tmp}" for tmp in self.ext_name.split('|')]
		
		
		pass
	
	def _ft_copy(self):
		header_path = make_normal_abs(self.header_path)
		base_pub_dir = make_normal_abs(self.base_pub_dir)
		
		for root, subFolder, files in os.walk(header_path):
			
			print("root:", root)
			print("header_path:", header_path)
			if self.not_recursive and root != header_path:
				continue
				
				
			for item in files:
				fileNamePath = os.path.join(root, item)
				#print(header_path)
				#print(root)
				subpath = root.replace(header_path, "").replace("\\", "/").strip("/")
				#print(subpath)
				# print(subpath.strip("/"))
	
				dst_file = os.path.abspath(os.path.join(base_pub_dir, subpath, item))
				yield fileNamePath, dst_file
	
	def copy_ext(self):
		ft = self._ft_copy()
	
		for fileNamePath, dst_file in ft:
			_, ext = os.path.splitext(fileNamePath)
			if ext.lower() in self.list_ext:
				safe_copy(fileNamePath, dst_file)
	
	def copy_reg(self):
		
		print("copy_files_by_reg", self.reg_exp,self.str_forbidden)
		ft = self._ft_copy()
		listStr_forbidden = [tmp.strip() for tmp in self.str_forbidden.split("|") if tmp.strip() !=""]
		for fileNamePath, dst_file in ft:
			is_forbidden = False
			for str_forbidden in listStr_forbidden:
				if str_forbidden!="" and str_forbidden in fileNamePath:
					print(fileNamePath,"is forbidden",file=sys.stderr)
					is_forbidden = True
					break
			if is_forbidden: continue
			mat = re.search(self.reg_exp,fileNamePath )
			if mat:
				print("match info", mat)
				safe_copy(fileNamePath, dst_file)
	
	def header(self):
		self.list_ext = [".h", ".hpp"]
		self.copy_ext()
	
	
	def source(self):
		self.list_ext = [".c", ".cpp"]
		self.copy_ext()
	
	
	def target(self,lib_org_path, platform, base_pub_dir):
		dst_dir, file_name = os.path.split(lib_org_path)
		base_pub_dir = os.path.join(base_pub_dir, platform, file_name)
	
		safe_copy(lib_org_path, base_pub_dir)
		# dst_dir = os.path.dirname(base_pub_dir)
		# if not os.path.exists(dst_dir):
		#	os.makedirs(dst_dir)
		# shutil.copy(lib_org_path,base_pub_dir)
	
		print(lib_org_path)
		print(base_pub_dir)
		pass
	
	
	def check_files(self,base_dir):
		for tmp in find_files_simple(base_dir):
			print(tmp)
		
		pass
		
		

	def do_run(self):
		procees = getattr(self, self.cmd)
		procees()
		pass

import os
import shutil

from neolib import neoutil
from neolib.neoutil import input_multi_lines


class UpdateInitAndCommit():
	form_contents = '''# -*- coding: utf-8 -*- 	
{version_name} = "{__version__}"
"""
#[ver].[majer].[miner]
#ver: 전체 프레임의 격변이 있을때
#majer:큰 기능 추가가 되었을때
#miner:버그 수정및 작은 기능 추가.
"""
{history_name} = """{__history__}"""
	'''
	version_name = "__version__"
	history_name = "__history__"

	def __init__(self,init_file="../__init__.py",force_version=None):
		self.init_file = init_file
		#self.force_version = force_version


		pass
	def get_next_verseion(self,version):
		ver, majer, miner = version.split(".")

		miner = str(int(miner) + 1)
		never = ".".join([ver, majer, miner])
		print(version,"->",never)
		return never

	def get_version_histrory(self,contents):
		mapt_return = {}
		exec(contents, globals(), mapt_return)
		return mapt_return

	def add_history(self,version,histrory ,msg):
		new_histrory = "\n* {version}{msg}".format(version=version, msg=msg)
		return new_histrory+histrory

	def change_init(self,msg,force_version=None):
		#org_file = "../__init__.py"

		shutil.copy(self.init_file,self.init_file+".tmp")
		contents = neoutil.StrFromFile(self.init_file)
		mapt_return = self.get_version_histrory(contents)
		version = mapt_return["__version__"]
		history = mapt_return["__history__"]
		
		version = self.get_next_verseion(version) if not force_version else force_version
		history =self.add_history(version,history,msg)

		mapt_return["__version__"] = version
		mapt_return["__history__"] = history

		mapt_return["version_name"] = self.version_name
		mapt_return["history_name"] = self.history_name
		#mapt_return["__version__"] = get_next_verseion(mapt_return["__version__"])
		contents = self.form_contents.format(**mapt_return)

		neoutil.StrToFile(contents,self.init_file)
		return version
	def commmit(self,version,msg):
		msg = msg.replace("\r","")
		lines  =msg.split("\n")
		msg = " ".join(["-am \"{}\"".format(tmp) for  tmp in lines if tmp !=""])

		cmd = "git commit -am \"ver *{} \" {}".format(version,msg)

		print(cmd)
		os.system(cmd)

	def push_all(self):
		#os.system("git push origin master")
		os.system("git push origin vr_shrink")

	def run(self,msg =None,force_version=None):
		title = "input msg for history(X is break):\n"
		if msg == None:
			msg = input_multi_lines(title)

		# msg = ""
		# while True:
		# 	sub = input(title)
		# 	if sub == "X":
		# 		break
		# 	msg += "\n"+sub
		#
		# 	#print(msg)
		# 	title = ""

		self.version =version = self.change_init(msg,force_version)
		self.commmit(version,msg)
		self.push_all()
		pass

if __name__ == '__main__':
	msg = """
attribtedict ->  Box 로 변경
	"""
	#commmit("1.2.3",msg)
	force_version = "2.1.0"
	#force_version = None
	UpdateInitAndCommit().run(msg,force_version=force_version)
	#main(msg)
	# version = change_init(msg)
	# commmit(version)
	# push_all()

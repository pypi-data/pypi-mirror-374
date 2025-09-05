import argparse
import os
import subprocess


def main(args:argparse.Namespace):
	print(args)


	pass

def touch(infile):



	#print(os.path.abspath(fname))

	#print(os.path.curdir)
	#print(os.getcwd())
	fname = os.path.abspath(infile)
	print('filename',fname)

	if os.path.exists(fname):
		os.utime(fname, None)
	else:
		open(fname, 'a').close()


def run_with_log(cmd_sentence:str,log_file):

	f = subprocess.Popen(cmd_sentence, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	#p = select..poll()
	#p.register(f.stdout)
	list_encode =['utf-8','euc-kr']
	with open(log_file,"wb") as fo:
		while True:
		#	if p.poll(1):
			line = f.stdout.readline()
			if not line:
				break
			fo.write(line)
			is_decoded = False
			for encode in list_encode:
				try:
					print(line.decode(encode).strip())
					is_decoded = True
					break
				except:
					continue
			if not  is_decoded:
				print("encoding prob",line)

			fo.flush()
			#time.sleep(0.1)




	pass
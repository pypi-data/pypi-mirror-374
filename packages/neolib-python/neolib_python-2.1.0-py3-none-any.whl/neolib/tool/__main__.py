import argparse

from neolib.tool.cmd import run_with_log, touch

if __name__ == '__main__':
	
	exam_vc = '''
python release.py target -t $(TargetPath) -p $(Platform) -o ..\publish\lib
python release.py header -id . -o ..\publish
python release.py source -id . -o ..\publish
	'''
	#	print("###os.environ  aa", os.environ['PUBLISH_DIR'])
	parser = argparse.ArgumentParser(description=f'fota_core_module cmd')
	parser.add_argument('cmd', action='store', help='command ')
	
	parser.add_argument('-b', dest='base_file', action='store',
	                    help='base file for delta or undelta')
	
	parser.add_argument('-i', dest='in_file', action='store', help='in file')
	parser.add_argument('-e', dest='exe_file', action='store', help='in file')
	parser.add_argument('-o', dest='out_file', action='store', help='out file')
	
	# print(globals())
	args = parser.parse_args()
	
	
	
	print(args)
	
	# exit()
	# lib_org_path = sys.argv[1]
	# platform = sys.argv[2]
	# target_dir = sys.argv[3]
	
	if args.cmd == 'run_with_log':
		run_with_log(args.exe_file,args.out_file)
	elif args.cmd == 'touch':
		touch(args.in_file)
		pass

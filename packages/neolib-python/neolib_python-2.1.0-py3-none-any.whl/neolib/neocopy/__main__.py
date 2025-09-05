import argparse

from neolib.neocopy.release import *

if __name__ == '__main__':
	

	#	print("###os.environ  aa", os.environ['PUBLISH_DIR'])
	argparse.ArgumentParser
	parser = argparse.ArgumentParser(description=f'release cmd  use')
	parser.add_argument('cmd', action='store',
	                    default=r'..\publish',
	                    help='header or target')
	
	parser.add_argument('-o', dest='out_dir', action='store',
	                    default=r'..\publish',
	                    help='out directory')
	
	parser.add_argument('-p', dest='platform', action='store',
	                    default=r'..\publish',
	                    help='platform name like x86 or x64')
	
	parser.add_argument('-t', dest='target_path', action='store',
	                    help='target path like c:/dst/aaa.exe or c:/dst/aaa.lib or dll')
	
	parser.add_argument('-id', dest='input_dir', action='store',
	                    default='.',
	                    help='input dir')
	
	parser.add_argument('-r', dest='reg', action='store',
	                    default='.*',
	                    help='input dir')
	
	parser.add_argument('-f', dest='forbidden', action='store',
	                    default='.*',
	                    help='input dir')
	parser.add_argument('-xlsx', dest='input_xlsx', action='store',
	                    default='.*',
	                    help='input dir')
	parser.add_argument('-ext', dest='ext_name', action='store', default='lib', help='input dir')
	
	parser.add_argument('--not-recursive', dest='not_recursive', action='store_const',
	                    default=False,
	                    const=True,
	                    help='not recursive')
	
	args = parser.parse_args()
	
	print(args)
	
	
	ReleaseClass(**vars(args)).run()
	
	# if args.cmd == 'header':
	# 	copy_header(args.input_dir, args.out_dir,args.not_recursive)
	# elif args.cmd == 'source':
	# 	copy_source(args.input_dir, args.out_dir,args.not_recursive)
	# elif args.cmd == 'copy_ext':
	# 	copy_files_by_ext(args.input_dir, args.out_dir, [f".{tmp}" for tmp in args.ext_name.split('|')],args.not_recursive)
	# elif args.cmd == 'copy_reg':
	# 	copy_files_by_reg(args.input_dir, args.out_dir, args.reg, args.forbidden,args.not_recursive)
	# elif args.cmd == 'target':
	# 	copy_target(args.target_path, args.platform, args.out_dir,args.not_recursive)
	# elif args.cmd == 'check_files':
	# 	check_file_datetime(args.target_path, args.platform, args.out_dir,args.not_recursive)
	#
	#
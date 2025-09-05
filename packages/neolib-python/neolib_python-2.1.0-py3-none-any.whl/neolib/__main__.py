import argparse

import neolib
from neolib.tool import cmd
from neolib.tool.cmd import run_with_log


def main():
	print("neolib module tool",neolib.__version__)
	# parser = argparse.ArgumentParser()
	# parser.add_argument("-c", "-config", action="store", dest="config", help="sample device address",
	#                     default="config.yml")

	parser = argparse.ArgumentParser(description=f'fota_core_module cmd')
	parser.add_argument('cmd', action='store' ,help='command ')

	parser.add_argument('-b', dest='base_file', action='store',
	                    help='base file for delta or undelta')

	parser.add_argument('-i', dest='in_file', action='store',help='in file')
	parser.add_argument('-e', dest='exe_file', action='store', help='in file')
	parser.add_argument('-o', dest='out_file', action='store',help='out file')

	#print(globals())
	args = parser.parse_args()
	print(type(args))
	#print(args)
	#print(args.cmd)

	pargs =()



	if args.cmd in ['delta','undelta']:
		pargs =(args.base_file,args.in_file,args.out_file )

		pass
	elif args.cmd in ['comp','uncomp']:
		pargs = ( args.in_file, args.out_file)
		pass
	elif args.cmd in ['run_with_log']:

		run_with_log(args.exe_file,args.out_file)
		return

	else:
		assert 'NO CMD'
	getattr(cmd,args.cmd)(args)

	#module =globals()[args.cmd]
	#print(module)
	#module.main(args)

if __name__ == "__main__":
	# execute only if run as a script
    main()
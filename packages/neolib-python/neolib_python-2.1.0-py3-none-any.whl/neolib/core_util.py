

class Struct:
	def __init__(self, **entries):
		self.__dict__.update(entries)

	def get_dict(self):
		return dict(self.__dict__)

	def from_dict(self,dict):
		self.__dict__.update(dict)

	def __repr__(self):
		return str(self.__dict__)
	
def get_maps_from_args(argv):
	length = len(argv)
	#print(argv)

	maps = {tmp[1:]: '' for tmp in argv if tmp.startswith('-')}

	for key, val in maps.items():
		idx = argv.index('-' + key)
	#	print(idx)
		if idx + 1 >= length: continue
		if argv[idx + 1].startswith('-'): continue

		maps[key] = argv[idx + 1]
	return maps

def getMapsFromArgs(argv):
	return get_maps_from_args(argv)

def get_struct_from_args(argv):
	return Struct(**get_maps_from_args(argv))
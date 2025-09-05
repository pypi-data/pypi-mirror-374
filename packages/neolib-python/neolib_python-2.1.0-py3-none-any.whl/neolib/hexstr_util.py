

def HexString2ByteArray(hexstr) :
	return bytes.fromhex(hexstr)

def ByteArray2HexString(bytes,sep="") :
	return sep.join('{:02X}'.format(x) for x in bytes)
	#return sep.join('{:02X}'.format(ord(x)) for x in bytes)

def HexString2Text(hexstr,enc="utf-8") :
	return HexString2ByteArray(hexstr).decode(enc)

def Text2HexString(str,enc="utf-8",sep="") :
	return ByteArray2HexString(str.encode(enc),sep)


def tobytes(in_data):
	if type(in_data) == str:
		return HexString2ByteArray(in_data)
	if type(in_data) == bytes:
		return in_data
	if type(in_data) == NeoByteBuff:
		return in_data.buff

	if type(in_data) == list:
		return bytes(in_data)
	if type(in_data) == bytearray:
		return bytes(in_data)

def tohexstr(in_data,sep=""):
	if type(in_data) == str:
		return in_data.replace(' ','')
	if type(in_data) == bytes or type(in_data) == list or type(in_data) == bytearray:
		return ByteArray2HexString(in_data,sep)


class NeoByteBuff():
	def __init__(self,buff,sep="",encoding='utf-8'):
		# if type(buff) == NeoByteBuff:
		# 	buff = buff.tobytes()

		self.buff = tobytes(buff)
		self.sep = sep
		self.encoding = encoding
		pass

	def __str__(self):
		return f"HEX  (len:{self.length}) {self.tohexstr()}"

	@property
	def length(self):
		return len(self.buff)

	def tohexstr(self):
		return tohexstr(self.buff,sep=self.sep)

	def tobytes(self):
		return tobytes(self.buff)

	def tostring(self):
		return tobytes(self.buff).decode(encoding=self.encoding)

	def __add__(self, other):
		if isinstance(other, NeoByteBuff):
			return NeoByteBuff(self.buff + other.buff)

		elif isinstance(other, bytes):
			return NeoByteBuff(self.buff + other)

		elif isinstance(other, str):
			return NeoByteBuff(self.buff + tobytes(other))

if __name__ == "__main__":
	#print(tobytes('hh'))

	bio = NeoByteBuff(NeoByteBuff(b'aa'))
	print(bio)
	print(ByteArray2HexString(b'\x03\x04'))


	bio += NeoByteBuff(b'bb')
	print(bio)

	bio += b'cc'
	print(bio)

	bio += 'hh'
	print(bio)
	#print(tohexstr([3,5]))
	pass
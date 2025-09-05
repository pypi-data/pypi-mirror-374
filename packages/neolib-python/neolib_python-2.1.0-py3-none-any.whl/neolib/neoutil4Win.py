import datetime

import win32api
import win32clipboard
import win32process

from neolib import neo_class


def GetClipBoard():
	try:
		win32clipboard.OpenClipboard()
		strret = win32clipboard.GetClipboardData( win32clipboard.CF_UNICODETEXT)  # set clipboard data
		win32clipboard.CloseClipboard()

	except TypeError:
		pass

	return strret

def SetClipBoard(str):
	try:
		win32clipboard.OpenClipboard()
		win32clipboard.EmptyClipboard()
		win32clipboard.SetClipboardData( win32clipboard.CF_UNICODETEXT,str)  # set clipboard data
		win32clipboard.CloseClipboard()
	except TypeError:
		pass

def	ProcIDFromWnd(hwnd):
	thdID,prdID = win32process.GetWindowThreadProcessId(hwnd)
	return prdID

def KillProcess( uID):

	hProcess = win32api.OpenProcess(0x1fffff, False, uID);
	if hProcess != None:
		ret = win32api.TerminateProcess(hProcess, 0)
		win32process.GetExitCodeProcess(hProcess)
		win32api.CloseHandle(hProcess);

def KillProcessFromHandle( hwnd):
	pid = ProcIDFromWnd(hwnd)
	KillProcess(pid)


def get_utc_time(curlocal,native):
	import pytz
	local = pytz.timezone(curlocal)
	local_dt = local.localize(native, is_dst=None)
	utc_dt = local_dt.astimezone(pytz.utc)
	return utc_dt

def _win_set_time(time_tuple):



	naive = datetime.datetime(*time_tuple[0:6])
	utc_dt = get_utc_time("Asia/Seoul",naive)
	time_tuple = utc_dt.timetuple()





	print(time_tuple)
	inputform = time_tuple[:2] + (time_tuple.tm_wday,) + time_tuple[2:6] + (0,)
	print(inputform)



	win32api.SetSystemTime(*inputform[0:])

class NeoAnalyzeClasss(neo_class.NeoAnalyzeClasss):
	def SetClopBoard(self):
		SetClipBoard(self.strlines)
		None


if  __name__ == "__main__":
	time_tuple = (2012,  # Year
				  9,  # Month
				  6,  # Day
				  0,  # Hour
				  38,  # Minute
				  0,  # Second
				  0,  # Millisecond
				  )

	_win_set_time(time_tuple)
	None



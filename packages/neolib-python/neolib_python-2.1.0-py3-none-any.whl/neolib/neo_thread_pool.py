import concurrent.futures
import time


def def_done_method(future, args):
	try:
		data = future.result()
	except Exception as exc:
		print('%r generated an exception: %s' % (args, exc))
	else:
		print('%r page is %d bytes' % (args, len(data)))



def do_thread_pool(max_workers,load_method,list_args,done_method = def_done_method):
	with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:

		future_to_url = {executor.submit(load_method, *args): args for args in list_args}
		for future in concurrent.futures.as_completed(future_to_url):
			args = future_to_url[future]
			done_method(future,args)




if __name__ =='__main__':
	URLS = ['http://www.foxnews.com/',
			'http://www.cnn.com/',
			'http://europe.wsj.com/',
			'http://www.bbc.co.uk/',
			'http://some-made-up-domain.com/']


	# Retrieve a single page and report the URL and contents
	def load_url(url, timeout):
		print('start')
		time.sleep(2)
		print('aaa')
		return 'aaaaa'


	# with urllib.request.urlopen(url, timeout=timeout) as conn:
	#     return conn.read()

	# We can use a with statement to ensure threads are cleaned up promptly


	do_thread_pool(5, load_url, [('http://www.foxnews.com/', 4)])
# -*- coding: utf-8 -*- 	
__version__ = "2.1.0"
"""
#[ver].[majer].[miner]
#ver: 전체 프레임의 격변이 있을때
#majer:큰 기능 추가가 되었을때
#miner:버그 수정및 작은 기능 추가.
"""
__history__ = """
* 2.1.0
attribtedict ->  Box 로 변경
	
* 2.0.8
attribtedict ->  Box 로 변경
	
* 2.0.7
attribtedict ->  Box 로 변경
	
* 2.0.6
find_files_ext 함수 추가.
	
* 2.0.5

	
* 2.0.4
UpdateInitAndCommit 에 강제 버젼 변경 기능 추가.
	
* 2.0.3
UpdateInitAndCommit 에 강제 버젼 변경 기능 추가.
	
* 2.0.2
UpdateInitAndCommit 에 강제 버젼 변경 기능 추가.
	
* 2.0.1
UpdateInitAndCommit 에 강제 버젼 변경 기능 추가.
	
* 2.0.0
UpdateInitAndCommit 에 강제 버젼 변경 기능 추가.
	
* 2.0.0
UpdateInitAndCommit 에 강제 버젼 변경 기능 추가.
	
* 1.9.0
UpdateInitAndCommit 에 강제 버젼 변경 기능 추가.
	
* 1.9.0
NeoAltByte => NAB SHORTEN WORD
and enable update NeoAltByte
	
* 1.8.2
NeoAltByte => NAB SHORTEN WORD
and enable update NeoAltByte
	
* 1.8.1
NeoAltByte => NAB SHORTEN WORD
and enable update NeoAltByte
	
* 1.8.0
NeoAltByte => NAB SHORTEN WORD
and enable update NeoAltByte
	
* 1.7.24
NeoAltByte => NAB SHORTEN WORD
and enable update NeoAltByte
	
* 1.7.23
change db
	
* 1.7.22
change db
	
* 1.7.21
change db
	
* 1.7.20
change db
	
* 1.7.19
change db
	
* 1.7.18
change db
	
* 1.7.17
change db
	
* 1.7.16
change db
	
* 1.7.15
change db
	
* 1.7.14
change db
	
* 1.7.13
change db
	
* 1.7.12
change db
	
* 1.7.11
run_wit_log main change
	
* 1.7.10
run_wit_log main change
	
* 1.7.9
run_wit_log main change
	
* 1.7.8
run_wit_log main change
	
* 1.7.7
run_wit_log main change
	
* 1.7.6
crypto -> cryptodome
	
* 1.7.5
crypto -> cryptodome
	
* 1.7.4
crypto -> cryptodome
	
* 1.7.3
crypto -> cryptodome
	
* 1.7.2
일부 문제 수정
	
* 1.7.1
cmd touch 추가 .
	
* 1.6.2
cmd touch 추가 .
	
* 1.7.0
cmd touch 추가 .
	
* 1.6.6
cmd 추가.
	
* 1.6.5
json pretty 수정
	
* 1.6.4
json pretty 수정
	
* 1.6.3
MqttHandler 추가.
	
* 1.6.2
NeoAltBytes 수정.
	
* 1.6.1
NeoAltBytes 수정.
	
* 1.6.0
NeoAltBytes 추가.
	
* 1.5.35
data ->neo_data 
	
* 1.5.34
data ->neo_data 
	
* 1.5.33
data ->neo_data 
	
* 1.5.32
data ->neo_data 
	
* 1.5.31
data ->neo_data 
	
* 1.5.30
data ->neo_data 
	
* 1.5.29
data ->neo_data 
	
* 1.5.28
add data.py pandas   빈칸 윗쪽에서 가져오는 함수 추가. 
	
* 1.5.27
add operator oveloading in  NeoByteBuff 
	
* 1.5.26
move NeoByteBuff on neo_class to hexstr_util 
	
* 1.5.25
add NeoByteBuff 
	
* 1.5.24
add NeoByteBuff 
	
* 1.5.23
add NeoByteBuff 
	
* 1.5.22
update cmd kill
	
* 1.5.21
update cmd submodule
	
* 1.5.20
change json_preytty
	
* 1.5.19
change json_preytty
	
* 1.5.18
add NeoByteIO 
	
* 1.5.17
remove sm4
	
* 1.5.16
remove sm4
	
* 1.5.15
remove sm4
	
* 1.5.14
change crypto ->block cipher->input of enc or dec
src -> src = tobytes(src) 

	
* 1.5.13
add find_files_simple

	
* 1.5.12
	remove print on NeoRunnableClass 

	
	
* 1.5.11
	remove print on NeoRunnableClass 

* 1.5.10
	change neoutil create_logger for default handler 
	log.txt 가 생성 되는 퍼미션 에러가 발생할수 있다.

	
* 1.5.10
	remove print on NeoRunnableClass 

	
* 1.5.9
	change neoutil create_logger for default handler 
	log.txt 가 생성 되는 퍼미션 에러가 발생할수 있다.
	
* 1.5.8add module update_history_and_git	
* 1.5.7add module update_history_and_git	
*1.5.5
	hexstr_util 수정
*1.5.4
	update xlrd list sturct and map with title_filter
	
*1.5.2
	update seed
	
	
*1.5.1
update db
- generate call insert with charset
	
	
*1.3.3
	replace_contents_by_tag 추가
	split_by_unit
	split_size_by_unit
	split_by_list 추가
	
*1.3.4
	xlr util 멀티 시트 구현 

*1.3.5
	gen_make.py 추가
	
*1.3.6
	xls line to Struct 

*1.3.7
	add ctype loaad handler 

*1.3.8
	reneal crete_logger in neoutil
	using NeoLogger with info_f,debug_f....
	these function use  like string format 

*1.3.9
	at neo tcp server, add init param for specify host address
	
*1.4.0

*1.4.2
	add eno_decorator
*1.5.0
	add async tcp server			
	
	
"""
	
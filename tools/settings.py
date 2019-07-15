
from os.path import abspath, dirname, join as path_join

BASE_PATH = dirname(abspath(__file__))

"""
	数据库配置
"""
database_config = {
	'dialect' : 'sqlite',
	'dbname' : path_join(dirname(BASE_PATH), path_join('db','taptap.db')),
	'echo' : False,
	'encoding' : 'utf-8',
	'connect_args' : {'check_same_thread': False},
	'open_transaction' : False
}

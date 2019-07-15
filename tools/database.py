# -*- coding:utf-8 -*-

from .settings import database_config
from jinjasql import JinjaSql

from sqlalchemy import create_engine, MetaData, Table, Column

jinja_sql_engine = JinjaSql()

__all__ = ['pooled_db_connector']

def parse_sql(sql, param=None):

	sql, param = jinja_sql_engine.prepare_query(sql, param)

	return sql%tuple(param)

class PooledDbConnector:

	def __init__(self):
		self._engine = self._create_engine()
		self._metadata = MetaData(bind=self._engine)
		self._tables = {}

	def __del__(self):
		pass

	def regist_table(self, table_name, cols):
		"""
			添加表格到MetaData中。
			:param
				table_name:字符串，表示表格名字
				cols:字典数组，字典的键值对将作为Column函数的参数传入
		"""

		if table_name in self._tables:
			return

		cols_ = []
		for col in cols:
			cols_.append(Column(**col))

		self._tables[table_name] = Table(table_name,self._metadata,*cols_)
		self._metadata.create_all(self._engine)

		return self._tables[table_name]

	def get_table(self, table_name):
		"""
			获取表格
		"""

		return self._tables.get(table_name)

	def get_connection(self):

		return self._engine.connect()

	def _create_url(self):

		url = """
			{{-dialect-}}
			{%- if dialect == 'sqlite' -%}
				:///{{dbname}}
			{%- else -%}
				{{driver}}://{{user}}{{password}}@{{host}}/{{dbname}}
			{%- endif -%}
		"""

		url = parse_sql(url, database_config)
		return url

	def _create_engine(self):

		param = {
			'echo' : database_config.get('echo'),
			'encoding' : database_config.get('encoding'),
			'connect_args' : database_config.get('connect_args'),
		}

		engine = create_engine(self._create_url(), **param)

		return engine


pooled_db_connector = PooledDbConnector()
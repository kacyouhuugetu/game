# -*- coding:utf-8 -*-

from .settings import database_config
from .database import pooled_db_connector
from .exception import *

import uuid
import math
import re
import sqlalchemy

__all__ = ['CommomModel']


def create_uuid():
	return uuid.uuid4().hex.upper()


class CommonModelMetaClass(type):

	def __init__(self, *args, **kwargs):
		super(CommonModelMetaClass, self).__init__(*args, **kwargs)
		self.__create_model__()

class ModelTable:
	def __init__(self, table_name):
		self._table_name = table_name

class ModelFiled:
	def __init__(self, **param):
		self._param = param

class CommonModel(metaclass=CommonModelMetaClass):


	"""
		_table_name = 'test'
		_table_fields = [{
			'name' : 'field1',
			'type_' : Integer,
			'primary_key' : True
		}]

	"""


	@classmethod
	def __create_model__(cls):
		if cls.__base__ == object:
			return

		

		if not hasattr(cls, '_table_name'):
			raise ValueError('缺失属性_table_name，表示对应的数据库表格名称')
		if not hasattr(cls, '_table_fields'):
			raise ValueError('缺失属性_table_fields，表示对应的数据库字段配置')

		table_fields = []
		for field_ in cls._table_fields:

			if not 'name' in field_:
				raise ValueError('存在某一字段配置缺少name，表示数据库字段的名称')

			field = field_.copy()
			# 字段默认类型为字符串
			field_type = field.setdefault('type_', 'String()')

			if type(field_type) == str:
				try:
					field_type = eval('sqlalchemy.'+field_type)
				except:
					raise ValueError('无法识别的类型：%s'%field_type)

				field['type_'] = field_type


			# 设置uuid
			if type(field.get('type_')) == sqlalchemy.String and ( field.get('default') == 'uuid' or (field.get('primary_key', False) and field.get('default') is None) ):

				field['default'] = create_uuid

			table_fields.append(field)


		cls._table = pooled_db_connector.regist_table(cls._table_name, table_fields)

	@classmethod
	def get(cls, **param):

		wheres = []
		pattern = "{field} = {value}"

		for key in param:
			value = param[key]

			column = getattr(cls._table.c, key)
			if type(column.type) in (sqlalchemy.String, sqlalchemy.Text):
				value = "'" + value + "'"

			wheres.append(pattern.format(
				field = key,
				value = value
			))

		return cls.select(where=wheres, one=True)


	@classmethod
	def count(cls, where=None, distinct=False):

		if not hasattr(cls, '_table'):
			raise UnimplementedError()

		conn = pooled_db_connector.get_connection()

		count = None

		try:
			select = cls._prepare_select_sql(where=where, distinct=distinct)
			select = select.count()

			result = conn.execute(select)

			row = result.fetchone()
			count = list(row.values())[0]

		except:
			pass

		finally:
			conn.close()

		return count


	@classmethod
	def select(cls, fields=None, where=None, order=None, distinct=False, page=None, limit=None, to_dict=True, one=False):

		if not hasattr(cls, '_table'):
			raise UnimplementedError()

		conn = pooled_db_connector.get_connection()
		data = None

		cls.count(where=where, distinct=distinct)

		try:
			select = cls._prepare_select_sql(fields, where, order, distinct, page, limit)
			
			result = conn.execute(select)

			rows = result.fetchall()

			if to_dict:
				data = []
				for row in rows:
					data.append(dict(row.items()))	
			else:
				data = rows



		finally:
			conn.close()


		if one:
			if data is None or len(data)==0:
				raise NoExistError()
			elif len(data)>1:
				raise MoreThanOneError()
			else:
				data = data[0]

		return data


	@classmethod
	def select_batch(cls, fields=None, where=None, order=None, distinct=False, limit=100, to_dict=True):

		if not hasattr(cls, '_table'):
			raise UnimplementedError()

		count = cls.count(where=where, distinct=distinct)
		n_page = math.ceil(count/limit)

		# 表格不存在
		if count is None:
			raise StopIteration()

		for page in range(1, n_page+1):

			yield from cls.select(fields=fields, where=where, order=order, distinct=distinct, page=page, limit=limit, to_dict=to_dict)



	@classmethod
	def insert(cls, **param):

		if not hasattr(cls, '_table'):
			raise UnimplementedError()

		conn = pooled_db_connector.get_connection()
		if database_config.get('open_transaction'):
			trans = conn.begin()

		is_commit = False
		try:
			ins = cls._table.insert()
			conn.execute(ins, **param)

			if database_config.get('open_transaction'):
				trans.commit()
			else:
				# conn.commit()
				pass

		except Exception as e:
			trans.rollback()
			raise e

		else:
			is_commit = True

		finally:
			conn.close()

		return is_commit

	@classmethod
	def insert_batch(cls, data, every_commit=False):

		if not hasattr(cls, '_table'):
			raise UnimplementedError()


		# 对每次插入都执行commit
		if every_commit:

			n_commit = 0
			for item in data:
				is_commit = cls.insert(**item)
				if not is_commit:
					break
				else:
					n_commit += 1

		else:

			conn = pooled_db_connector.get_connection()
			if database_config.get('open_transaction'):
				trans = conn.begin()

			is_commit = False
			try:
				ins = cls._table.insert()
				for item in data:
					conn.execute(ins, **item)

				if database_config.get('open_transaction'):
					trans.commit()
				else:
					# conn.commit()
					pass

			except Exception as e:
				if database_config.get('open_transaction'):
					trans.rollback()
				raise e

			else:
				is_commit = True

			finally:
				conn.close()

			n_commit = len(data) if is_commit else 0

		return n_commit

	@classmethod
	def update(cls, **param):

		if not hasattr(cls, '_table'):
			raise UnimplementedError()

		table = cls._table

		conn = pooled_db_connector.get_connection()
		if database_config.get('open_transaction'):
			trans = conn.begin()

		is_commit = False
		try:

			where = None

			if 'where' in param:
				where = param.pop('where')
			# 若不存在where，但param中含有主键，则以该主键作为where条件
			else:
				primary_field, is_string = None, False
				for key in param:
					column = getattr(table.c, key)
					if column.primary_key:
						primary_field = column.name
						is_string = type(column.type) in ( sqlalchemy.String, sqlalchemy.Text )

				if primary_field:

					value = param.pop(primary_field)
					if is_string:
						value = "'" + value + "'"

					where = '%s = %s'%(primary_field, value)

			update = table.update().where(cls._get_where_statement(where))

			update = update.values(**param)
			conn.execute(update)

			if database_config.get('open_transaction'):
				trans.commit()
			else:
				# conn.commit()
				pass

		except Exception as e:
			if database_config.get('open_transaction'):
				trans.rollback()
			raise e

		else:
			is_commit = True

		finally:
			conn.close()

		return is_commit

	@classmethod
	def delete(cls, where=None):

		if not hasattr(cls, '_table'):
			raise UnimplementedError()

		table = cls._table

		conn = pooled_db_connector.get_connection()
		if database_config.get('open_transaction'):
			trans = conn.begin()

		is_commit = False
		try:

			delete = table.delete().where(cls._get_where_statement(where))
			conn.execute(delete)

			if database_config.get('open_transaction'):
				trans.commit()
			else:
				# conn.commit()
				pass

		except:
			if database_config.get('open_transaction'):
				trans.rollback()

		else:
			is_commit = True

		finally:
			conn.close()

		return is_commit

	@classmethod
	def _get_where_statement(cls, where=None):

		and_conditions = []
		table = cls._table

		if where:
			if type(where) == str:
				where = re.split(r'&&', where)
			elif type(where) == sqlalchemy.sql.expression.BinaryExpression:
				where = [[where]]

			for index, conditions in enumerate(where):
				if type(conditions) in (str, sqlalchemy.sql.expression.BinaryExpression):
					where[index] = [conditions]

			# 组间为与关系，组内为或关系
			for conditions in where:

				or_conditions = []
				for condition in conditions:

					if type(condition) == str:
						field, op, value = [ele.strip() for ele in re.split(r'\s+', condition, maxsplit=2)]

						field = getattr(table.c, field)
						if value.startswith(':'):
							value = getattr(table.c, value[1:])
						else:
							value = eval(value)

						if op == '=':
							op = '=='

						if op in ('=', '==', '>', '>=', '<', '<=', '!='):
							condition = eval('field' + op + 'value')
						else:
							condition = eval('field' + '.' + op + '(value)')


					or_conditions.append(condition)

				or_conditions = sqlalchemy.or_(*or_conditions)

				and_conditions.append(or_conditions)
		and_conditions = sqlalchemy.and_(*and_conditions)

		return and_conditions

	@classmethod
	def _get_order_statment(cls, order=None):

		order_clauses = []
		table = cls._table

		if order:
			if type(order) == str:
				order = re.split(r'\s+', order)

			for order_ in order:
				if type(order_) == str:
					order_ = order_.strip()
					field, is_desc = (order_[1:], True) if order_.startswith('-') else (order_, False)
					
					field = getattr(table.c, field)
					order_ = field.desc() if is_desc else field.asc()

				order_clauses.append(order_)

		return order_clauses

	@classmethod
	def _prepare_select_sql(cls, fields=None, where=None, order=None, distinct=False, page=None, limit=None, to_dict=True, one=False):

		if not hasattr(cls, '_table'):
			raise ValueError('非法模型')

		table = cls._table

		if fields:
			fields = [getattr(table.c, field) if type(field) == str else field for field in fields]
		else:
			fields = [table]

		select = sqlalchemy.select(fields).where(cls._get_where_statement(where))
		select = select.order_by(*cls._get_order_statment(order))

		if distinct:
			select = select.distinct()

		if page and limit:
			page, limit = int(page), int(limit)
			select = select.offset((page-1)*limit).limit(limit)

		return select

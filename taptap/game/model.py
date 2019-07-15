# -*- coding:utf-8 -*-

from tools.common_model import CommonModel

from datetime import date

class Game(CommonModel):

	_table_name = 'T_GAME'
	_table_fields = [{
		'name' : 'id',
		'type_' : 'String(32)',
		'primary_key' : True,
		'comment' : '主键ID'
	},{
		'name' : 'taptap_id',
		'type_' : 'String(32)',
		'primary_key' : True,
		'comment' : 'TAPTAP ID'
	},{
		'name' : 'name',
		'type_' : 'String(1000)',
		'nullable' : False,
		'comment' : '手游名称'
	},{
		'name' : 'img',
		'type_' : 'String(1000)',
		'comment' : '手游图片'
	},{
		'name' : 'tags',
		'type_' : 'String(1000)',
		'comment' : '手游标签'
	},{
		'name' : 'rating_score',
		'type_' : 'Float',
		'comment' : '手游评分'
	},{
		'name' : 'publisher',
		'type_' : 'String(1000)',
		'comment' : '手游厂商'
	},{
		'name' : 'follow',
		'type_' : 'Integer',
		'comment' : '关注人数'
	},{
		'name' : 'review',
		'type_' : 'Integer',
		'comment' : '评论人数',
	},{
		'name' : 'last_update',
		'type_' : 'Date',
		'comment' : '最后一次更新时间',
	}]


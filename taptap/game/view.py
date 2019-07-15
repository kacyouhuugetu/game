import json

from flask import Blueprint, render_template, request, jsonify

from taptap.game.model import Game

game = Blueprint('game', __name__)

@game.route('/list', methods=['GET', 'POST'])
def list():

	

	return render_template('game/list.html')

@game.route('/get_game_list', methods=['GET', 'POST'])
def get_game_list():

	count, data = 0, None

	try:
		form = request.form

		page = int(form.get('page', 1))
		# 最多一次获取100条记录
		limit = min(int(form.get('limit', 20)), 100)

		where = []
		order = form.get('order')

		if form.get('publisher'):
			where.append("publisher like '%%%s%%'"%form.get('publisher'))

		if form.get('rating_score'):
			where.append("rating_score >= %s"%form.get('rating_score'))

		if form.get('review'):
			where.append("review >= %s"%form.get('review'))

		# 获取记录条数
		count = Game.count(where=where)
		# 获取分页
		data = Game.select(where=where, order=order, page=page, limit=limit)


	except Exception as e:
		pass
		raise e


	return jsonify({
		'count': count,
		'data' : data,
	})
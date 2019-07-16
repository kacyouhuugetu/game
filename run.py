from flask import Flask, render_template

import random

app = Flask(__name__)


from taptap.game.view import game

app.register_blueprint(game,url_prefix='/game')

# 为模板添加版本号
@app.context_processor 
def add_version():
	return {'version':random.random()}

#设置json编码
app.config['JSON_AS_ASCII'] = False

if __name__ == '__main__':
	app.run(host='localhost', port=8888, debug=True)
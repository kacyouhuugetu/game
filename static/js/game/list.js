
var game_list_vue_args = {

	el : '#game-container',
	data : {

		// 手游厂商
		publisher : null,
		// 最低评分
		rating_score : null,
		// 最低评价人数
		review : null,
		// 最低关注人数
		follow : null,
		// 排序方法
		order : null,

		// 页码
		page : 1,
		// 分页大小
		limit : 20,
		// 可供选择的分页大小
		limits : [10, 20, 50, 100],
		game_list : [],
		game_count : 0,

	},
	computed : {
		cur_page : {
			get : function(){
				return this.page;
			},
			// 设置当前页码
			set : function(newValue){

				this.page = newValue;

				// 获取数据
				this.get_list_data();
			}
		}
	},
	methods : {
		nvl : function(value, default_){
			return _.isNil(value) || (_.isString(value) && _.isEmpty(value) ) || !_.isFinite(value) ?default_:value;
		},
		empty_or_number_verify : function(field, value, item){
			var ok = _.isEmpty(value)?true:_.isFinite(Number(value));
			if(!ok){
				return field + '必须为数字';
			}
		},
		// 获取当前分页数据
		get_list_data : function(){

			$.ajax({
				async : false,
				url : '/game/get_game_list',
				type : 'POST',
				data : {
					page : this.page,
					limit : this.limit,
					publisher : this.publisher,
					rating_score : this.rating_score,
					review : this.review,
					order : this.order,
				},
				context : {
					vue : this,
				},
				dataType : 'json',
				success : function(data){
					var vue = this.vue;
					vue.game_list = data.data;
					vue.count = data.count;
				}
			});

		},
		// 刷新分页
		refresh : function(){
			// 显示第一页
			this.cur_page = 1;

			var vue = this;
			this.$nextTick(function(){

				// 初始化分页组件
				layui.use('laypage', function(){

					var laypage = layui.laypage;

					//执行一个laypage实例
					laypage.render({
						elem : 'game-paginator', // 分页器id号
						count : vue.count, // 数据总数，从服务端得到
						limit : vue.limit, // 分页大小
						limits : vue.limits, // 可供选择的分页大小
						// 分页回调
						jump : function(obj, first){
							if(!first){
								// 设置当前页码
								vue.cur_page = obj.curr;
							}

							// 滚至顶部
							vue.$nextTick(function(){
								
								if(!first){
									window.location.href = '#game-list';
								}
							});
						},
					});
				});
			});
		}
	},
	mounted : function(){
		// 刷新分页
		this.refresh();

		var vue = this;
		layui.use('form', function(){

			var form = layui.form;

			// 表单验证
			form.verify({

				rating_score : _.bind(vue.empty_or_number_verify, null, '最低评分'),
				review : _.bind(vue.empty_or_number_verify, null, '最低评分人数'),
			});

			form.on('submit(filter)', function(data){

				vue.publisher = data.field.publisher;
				vue.rating_score = data.field.rating_score;
				vue.review = data.field.review;
				vue.follow = data.field.follow;
				vue.order = data.field.order;

				vue.refresh();

			});

			form.render();

		});
	},

};

var game_list_vue;

$(function(){

	game_list_vue = new Vue(game_list_vue_args);

});
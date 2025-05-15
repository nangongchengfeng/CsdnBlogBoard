from datetime import datetime

from flask import Flask, render_template

from api.csdn import cs, GetArticle
from models import db, Info, Categorize, Article

# Initialize Flask app
app = Flask(__name__)
# 配置缓存
# cache.init_app(app, config={
#     'CACHE_TYPE': 'filesystem',
#     'CACHE_DIR': 'cache-directory'
# })
# Configure database settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:xxxx@43.xxxx.xxxx.5:3306/csdn'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'charset': 'utf8mb4'}}
db.init_app(app)

#  创建表，如果表已经存在，则不会创建
# with app.app_context():
#     db.create_all()
DEFAULT_BLUEPRINT = [
    (cs, '/'),  # 应用管理
]
url_path_prefix = "/api"


def config_blueprint(app):
    for blueprint, url_prefix in DEFAULT_BLUEPRINT:
        url_prefix = url_path_prefix + url_prefix  # 添加 /api 前缀
        app.register_blueprint(blueprint, url_prefix=url_prefix)


@app.route('/')
def index():
    # 从数据库中获取所有年份数据
    all_dates = GetArticle()  # 获取所有日期字段
    # 从数据库中获取所有年份数据
    years = sorted({item["year"] for item in all_dates}, reverse=True)  # 提取年份并去重排序
    latest_year = max(years) if len(years) > 0 else datetime.now().year

    # 获取用户信息（假设从数据库查询）
    # 获取用户信息
    info_data = Info.query.first()

    if info_data:
        result = {
            'id': info_data.id,  # 自增主键 ID
            'date': info_data.date,  # 抓取时间，格式如 "YYYY-MM-DD HH:MM:SS"
            'head_img': info_data.head_img,  # 用户头像链接 URL
            'author_name': info_data.author_name,  # 作者用户名
            'article_num': info_data.article_num,  # 原创文章数量（整数）
            'fans_num': info_data.fans_num,  # 粉丝数量（整数）
            'like_num': info_data.like_num,  # 点赞总数（整数）
            'comment_num': info_data.comment_num,  # 评论总数（整数）
            'collect_num': info_data.collect_num,  # 收藏总数（整数）
            'share_num': info_data.share_num,  # 分享总数（整数）
            'visit_num': info_data.visit_num,  # 累计访问量（整数）
            'rank': info_data.rank,  # 排名（整数）
            'level': info_data.level,  # 等级（文本，如 "Lv.3"）
            'score': info_data.score,  # 积分/得分（整数）
            'code_age' : info_data.code_age,  # 编程龄（文本，如 "1 年"）

        }
        return render_template('index.html', info=result, years=years,
                               latest_year=latest_year)
    else:
        return render_template('index.html', info=None)


config_blueprint(app)

if __name__ == '__main__':
    # Run the application
    app.run(debug=True)

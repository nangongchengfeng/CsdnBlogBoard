# -*- coding: utf-8 -*-
# @Time    : 2024/12/15 15:28
# @Author  : 南宫乘风
# @Email   : 1794748404@qq.com
# @File    : csdn.py
# @Software: PyCharm
from datetime import datetime

from flask import Blueprint, jsonify, request
from common.result.result import Result
from models import Categorize, Article

cs = Blueprint('cs', __name__)


def get_quarter(month):
    """根据月份返回季度"""
    if 1 <= month <= 3:
        return "第一季度"
    elif 4 <= month <= 6:
        return "第二季度"
    elif 7 <= month <= 9:
        return "第三季度"
    elif 10 <= month <= 12:
        return "第四季度"


@cs.route('/data')
def GetArticle():
    try:
        articles = Article.query.filter().all()

        result = []
        for article in articles:
            article_date = datetime.strptime(article.date, '%Y-%m-%d %H:%M:%S')
            article_dict = {
                'id': article.id,
                'url': article.url,
                'title': article.title,
                'date': article.date,
                'read_num': article.read_num,
                'comment_num': article.comment_num,
                'type': article.type,
                'date_day': article_date.date(),
                'date_month': article_date.strftime('%Y年%m月'),
                'weekday': article_date.weekday(),
                'year': article_date.year,
                'month': article_date.month,
                'quarter': get_quarter(article_date.month),
                'week': article_date.isocalendar()[1],  # 提取 isocalendar 中的 week 值
            }
            result.append(article_dict)

        return result
    except Exception as e:
        print(f"Error in get_articles: {str(e)}")
        return []


from collections import defaultdict


@cs.route('/quarter')
def GetQuarter():
    """
    获取 每年 每 季度 博客 数量
    """
    """统计每年每季度的博客数量"""
    year_quarter_count = defaultdict(lambda: defaultdict(int))
    data = GetArticle()
    for article in data:
        year = article["year"]
        quarter = article["quarter"]
        year_quarter_count[year][quarter] += 1
    # 转换为指定格式
    result = []
    for year, quarters in year_quarter_count.items():
        year_data = {"product": str(year)}
        for quarter in ["第一季度", "第二季度", "第三季度", "第四季度"]:
            year_data[quarter] = quarters.get(quarter, 0)
        result.append(year_data)

    return Result.success(result)


@cs.route('/categorize')
def Pie():
    # 查询数据库获取分类信息
    categorize_data = Categorize.query.all()

    # 将数据库数据转化为 ECharts 饼图数据格式
    if categorize_data:
        pie_data = [
            {"value": item.article_num, "name": item.categorize}
            for item in categorize_data
        ]
    else:
        pie_data = []  # 如果没有数据，返回空列表

    # 返回 JSON 数据
    return Result.success(pie_data)


@cs.route('/read')
def GetRead():
    """统计各个类型文件的名称对应的阅读量和文章数量"""
    data = GetArticle()
    type_stats = defaultdict(lambda: {'count': 0, 'reads': 0})
    for article in data:
        article_type = article["type"]
        type_stats[article_type]['count'] += 1
        type_stats[article_type]['reads'] += article["read_num"]
    # 转换为指定格式
    result = {
        'labels': [],
        'reads': [],
        'counts': []
    }
    for type_name, stats in type_stats.items():
        result['labels'].append(type_name)
        result['reads'].append(stats['reads'])
        result['counts'].append(stats['count'])

    return Result.success(result)


@cs.route('/heatmap/<int:year>')
def GetHeatmap(year):
    """
    获取指定年份的文章发布热力图数据
    :param year: 指定的年份
    :return: 热力图数据
    """
    data = GetArticle()
    # 筛选指定年份的数据
    # 筛选指定年份的数据
    data_filtered = [article for article in data if article['year'] == year]

    # 创建一个字典来统计每周每天的文章数
    heatmap_dict = defaultdict(int)
    for article in data_filtered:
        week = article['week']
        weekday = article['weekday']
        key = (week, weekday)
        heatmap_dict[key] += 1

    # 准备返回的数据
    heatmap_data = []
    for (week, weekday), count in heatmap_dict.items():
        heatmap_data.append([week - 1, weekday, count])  # ECharts 的 x 轴从 0 开始

    # 获取所有的周和星期几
    weeks = sorted(set(week for week, _ in heatmap_dict.keys()))
    weekdays = sorted(set(weekday for _, weekday in heatmap_dict.keys()))

    # 确保生成的数据是完整的（包含所有周和星期几的组合）
    complete_heatmap_data = []
    for week in range(1, max(weeks) + 1):
        for weekday in range(7):  # 星期一到星期日
            count = heatmap_dict.get((week, weekday), 0)
            complete_heatmap_data.append([week - 1, weekday, count])

    result = {
        'data': complete_heatmap_data,
        'xAxis': [f'第{i}周' for i in range(1, max(weeks) + 1)],
        'yAxis': ["星期{}".format(i + 1) if i != 6 else "星期日" for i in range(7)]
    }
    return Result.success(result)


@cs.route('/articles')
def GetArticles():
    """获取文章列表"""
    articles= GetArticle()
    # 获取可能的筛选参数
    filter_type = request.args.get('type', None)
    filter_quarter = request.args.get('quarter', None)
    filter_year = request.args.get('year', None)
    filter_week = request.args.get('week', None)
    filter_day = request.args.get('day', None)

    # 根据类型筛选
    if filter_type:
        articles = [article for article in articles if article['type'] == filter_type]

    # 根据月份筛选
    if filter_quarter:
        articles = [article for article in articles if article['quarter'] == filter_quarter]

    # 根据年份筛选
    if filter_year:
        articles = [article for article in articles if article['year'] == int(filter_year)]

    # 根据周数筛选
    if filter_week:
        articles = [article for article in articles if article['week'] == int(filter_week)]

    # 根据星期筛选
    if filter_day:
        articles = [article for article in articles if article['weekday'] == int(filter_day) - 1]

    # 去重，保留第一个出现的文章
    seen_urls = set()
    unique_articles = []
    for article in articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)

    # 按日期降序排序
    unique_articles.sort(key=lambda x: x['date'], reverse=True)

    # 返回前 100 篇文章
    result = []
    for article in unique_articles[:100]:
        result.append({
            'title': article['title'],
            'url': article['url'],
            'date': article['date'],
            'type': article['type']
        })

    return Result.success(result)
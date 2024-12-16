# 用于CSDN数据博客的爬虫抓取

import datetime as dt
import random
import re
import time

import requests
from bs4 import BeautifulSoup

from app import app
from models import db, Info, Categorize

headers = {
    'User-Agent': 'Mozilla/5.0 (MSIE 10.0; Windows NT 6.1; Trident/5.0)',
    'referer': 'https: // passport.csdn.net / login',
}


def get_info():
    """获取大屏第一列信息数据并存储到数据库"""

    # 我的博客地址
    url = 'https://blog.csdn.net/heian_99/article/details/105689982'
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()  # 检查响应状态
            now = dt.datetime.now().strftime("%Y-%m-%d %X")

            soup = BeautifulSoup(resp.text, 'lxml')

            # 获取用户信息
            user_info = soup.find('div', class_='user-info d-flex flex-column profile-intro-name-box')
            if not user_info:
                raise ValueError("Cannot find user info section")
            author_name = user_info.find('a').get_text(strip=True)

            # 获取头像
            avatar_box = soup.find('div', class_='avatar-box d-flex justify-content-center flex-column')
            if not avatar_box:
                raise ValueError("Cannot find avatar section")
            head_img = avatar_box.find('a').find('img')['src']

            # 获取统计数据
            data_info = soup.find_all('div', class_='data-info d-flex item-tiling')
            if len(data_info) < 2:
                raise ValueError("Cannot find data info section")

            row1_nums = data_info[0].find_all('span', class_='count')
            row2_nums = data_info[1].find_all('span', class_='count')

            if len(row1_nums) < 4 or len(row2_nums) < 4:
                raise ValueError("Incomplete data info")

            level_mes = data_info[0].find_all('dl')[-1]['title'].split(',')[0]

            info = {
                'date': now,  # 时间
                'head_img': head_img,  # 头像
                'author_name': author_name,  # 用户名
                'article_num': str(row1_nums[0].get_text()),  # 文章数
                'fans_num': str(row2_nums[1].get_text()),  # 粉丝数
                'like_num': str(row2_nums[2].get_text()),  # 喜欢数
                'comment_num': str(row2_nums[3].get_text()),  # 评论数
                'level': level_mes,  # 等级
                'visit_num': str(row1_nums[3].get_text()),  # 访问数
                'score': str(row2_nums[0].get_text()),  # 积分
                'rank': str(row1_nums[2].get_text()),  # 排名
            }

            # 激活应用上下文
            with app.app_context():
                existing_info = Info.query.filter_by(author_name=author_name).first()
                if existing_info:
                    existing_info.date = info['date']
                    existing_info.head_img = info['head_img']
                    existing_info.article_num = info['article_num']
                    existing_info.fans_num = info['fans_num']
                    existing_info.like_num = info['like_num']
                    existing_info.comment_num = info['comment_num']
                    existing_info.level = info['level']
                    existing_info.visit_num = info['visit_num']
                    existing_info.score = info['score']
                    existing_info.rank = info['rank']
                    print("更新用户信息到数据库")
                else:
                    new_info = Info(**info)
                    db.session.add(new_info)
                    print("添加新用户信息到数据库")

                db.session.commit()
                print("成功保存数据到数据库")
                return True

        except Exception as e:
            retry_count += 1
            print(f"Error in get_info (attempt {retry_count}/{max_retries}): {str(e)}")
            if retry_count < max_retries:
                import time
                time.sleep(5)
            else:
                print("Max retries reached, failed to save data")
                return False


# 爬取分类信息
def get_categorize():
    try:
        id = "heian_99"
        base_url = f'https://blog.csdn.net/{id}'
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()

        # 使用 BeautifulSoup 解析页面
        soup = BeautifulSoup(response.content, "lxml")
        spans = soup.find_all('a', attrs={'class': 'special-column-name'})
        if not spans:
            print("No categories found.")
            return

        for span in spans:
            try:
                href = span.get('href')
                if not href:
                    print("Warning: Missing href for a span.")
                    continue

                # 获取专栏名
                blog_column = span.text.strip()

                # 从链接中提取博客id
                blog_id = href.split("_")[-1].split(".")[0]

                # 获取文章数量
                num_span = span.find('span', class_='special-column-num')
                if num_span:
                    blogs_column_num = int(re.findall(r'\d+', num_span.text)[0])
                else:
                    blogs_column_num = 0

                # 获取专栏详细信息
                try:
                    detail_response = requests.get(href, headers=headers, timeout=10)
                    detail_response.raise_for_status()

                    detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                    column_operating_div = detail_soup.find('div', {'class': 'column_operating'})

                    if column_operating_div:
                        subscribe_num = int(re.findall(r'\d+', column_operating_div.find('span', {
                            'class': 'column-subscribe-num'}).text)[0]) if column_operating_div.find('span', {
                            'class': 'column-subscribe-num'}) else 0
                        mumber_spans = column_operating_div.find_all('span', {'class': 'mumber-color'})

                        article_num = int(mumber_spans[1].text) if len(mumber_spans) > 1 else 0
                        read_num = int(mumber_spans[2].text) if len(mumber_spans) > 2 else 0
                        collect_num = int(mumber_spans[3].text) if len(mumber_spans) > 3 else 0
                    else:
                        subscribe_num = article_num = read_num = collect_num = 0
                except Exception as e:
                    print(f"Error retrieving details for {href}: {e}")
                    subscribe_num = article_num = read_num = collect_num = 0

                # 保存到数据库
                with app.app_context():
                    existing_categorize = Categorize.query.filter_by(href=href).first()
                    if existing_categorize:
                        # 更新已有记录
                        existing_categorize.categorize = blog_column
                        existing_categorize.categorize_id = blog_id
                        existing_categorize.column_num = blogs_column_num
                        existing_categorize.num_span = subscribe_num
                        existing_categorize.article_num = article_num
                        existing_categorize.read_num = read_num
                        existing_categorize.collect_num = collect_num
                        print(f"更新分类信息: {blog_column}")
                    else:
                        # 新增记录
                        new_categorize = Categorize(
                            href=href,
                            categorize=blog_column,
                            categorize_id=blog_id,
                            column_num=blogs_column_num,
                            num_span=subscribe_num,
                            article_num=article_num,
                            read_num=read_num,
                            collect_num=collect_num
                        )
                        db.session.add(new_categorize)
                        print(f"添加新的分类信息: {blog_column}")

                    db.session.commit()

                # 延迟，避免爬取过快
                time.sleep(random.uniform(1, 2))

            except Exception as inner_e:
                print(f"Error processing category {span}: {inner_e}")
                continue

        print("所有的分类信息已经保存到数据库")
    except Exception as e:
        print(f"错误日志: get_categorize: {e}")


def get_blog_columns():
    """
    从 Categorize 表获取博客专栏信息
    """
    with app.app_context():
        from models import db, Categorize

        # 查询 Categorize 表中的专栏信息
        blog_columns = db.session.query(
            Categorize.href,
            Categorize.categorize,
            Categorize.categorize_id,
            Categorize.article_num
        ).all()

        # 转换为列表格式
        return [
            [column.href, column.categorize, str(column.categorize_id), str(column.article_num)]
            for column in blog_columns
        ]


def append_blog_info(blog_column_url, blog_column_name, blogs):
    # 发送get请求，获取响应
    reply = requests.get(url=blog_column_url, headers=headers)
    # 使用BeautifulSoup解析响应
    blog_span = BeautifulSoup(reply.content, "lxml")
    # 获取所有的class="column_article_list"的<ul>标签
    blogs_list = blog_span.find_all('ul', attrs={'class': 'column_article_list'})
    # 遍历所有的<ul>标签
    for arch_blog_info in blogs_list:
        # 获取<ul>标签内所有的<li>标签
        blogs_list = arch_blog_info.find_all('li')
        # 遍历所有的<li>标签
        for blog_info in blogs_list:
            # 获取<li>标���内的文章链接和标题
            blog_url = blog_info.find('a', attrs={'target': '_blank'})['href']
            blog_title = blog_info.find('h2', attrs={'class': "title"}).get_text().strip().replace(" ", "_").replace(
                '/', '_')
            statuses = blog_info.find_all("span", class_="status")
            three_status = []
            for index, status in enumerate(statuses):
                if index == 0:
                    time_str = status.text.split('·')[0]
                    time_str = time_str.strip()
                    three_status.append(time_str)
                else:
                    time_str = status.text.split('·')[0]
                    num = int(re.findall(r'\d+', time_str)[0])
                    three_status.append(num)

            # 将文章信息存储在字典中
            blog_dict = {'url': blog_url, 'title': blog_title, 'date': three_status[0], 'read_num': three_status[1],
                         'comment_num': three_status[2], 'type': blog_column_name}
            # 将字典追加到文章列表中
            blogs.append(blog_dict)
    # 返回所有文章的信息
    return blogs


def get_blog():
    """
    主函数：抓取并保存博客数据到数据库
    """
    from models import db, Article

    # 获取专栏信息
    blog_columns = get_blog_columns()

    # 存储所有博客信息
    blogs = []

    # 遍历专栏博客信息
    for blog_column in blog_columns:
        blog_column_url = blog_column[0]
        blog_column_name = blog_column[1]
        blog_column_id = blog_column[2]
        blog_column_num = int(blog_column[3])
        print(f"正在处理专栏: {blog_column_name} , 文章数量: {blog_column_num}", "url:", blog_column_url, "id:",
              blog_column_id)
        # 处理多页专栏
        if blog_column_num > 40:
            # 计算翻页数量
            page_num = round(blog_column_num / 40)

            # 倒序循环翻页链接
            for i in range(page_num, 0, -1):
                # 拼接翻页链接
                blog_column_url = blog_column[0]
                url_str = blog_column_url.split('.html')[0]
                blog_column_url = url_str + '_' + str(i) + '.html'

                # 抓取并追加博客信息
                append_blog_info(blog_column_url, blog_column_name, blogs)

            # 获取第一页的文章列表信息
            blog_column_url = blog_column[0]
            blogs = append_blog_info(blog_column_url, blog_column_name, blogs)
        else:
            # 获取专栏第一页的文章列表信息
            blogs = append_blog_info(blog_column_url, blog_column_name, blogs)
    print("--------------------------------------------------------------------------")
    print(f"已抓取 {len(blogs)} 篇文章")
    try:
        with app.app_context():
            for blog in blogs:
                # Check if an article with the same URL exists
                existing_article = Article.query.filter_by(url=blog['url']).first()

                if existing_article:
                    # Update existing article data
                    existing_article.title = blog['title']
                    existing_article.date = blog['date']
                    existing_article.read_num = blog['read_num']
                    existing_article.comment_num = blog['comment_num']
                    existing_article.type = blog['type']
                else:
                    # Insert a new article
                    new_article = Article(
                        url=blog['url'],
                        title=blog['title'],
                        date=blog['date'],
                        read_num=blog['read_num'],
                        comment_num=blog['comment_num'],
                        type=blog['type']
                    )
                    db.session.add(new_article)

            # Commit changes to the database
            db.session.commit()
            print("数据已保存到数据库")
    except Exception as e:
        print(f"错误信息: {e}")


if __name__ == '__main__':
    # main()
    get_info()
    get_categorize()
    get_blog()

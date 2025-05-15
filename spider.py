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


def to_int(s):
    try:
        return int(s.replace(',', '').strip())
    except:
        return 0


def get_info():
    """获取大屏第一列信息数据并存储到数据库"""

    # 我的博客地址
    url = 'https://blog.csdn.net/heian_99'
    max_retries = 3
    retry_count = 0

    # 循环用于重试
    while retry_count < max_retries:
        try:
            print(f"尝试抓取数据 (第 {retry_count + 1}/{max_retries} 次)...")
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()  # 检查响应状态，如果不是 2xx 会抛出异常
            now = dt.datetime.now().strftime("%Y-%m-%d %X")  # 这个 now 变量似乎没有被使用

            soup = BeautifulSoup(resp.text, 'lxml')
            # 获取用户信息的数据源
            user_info_container = soup.find('div', class_='user-profile-head-info-r-c')

            if not user_info_container:
                # 如果找不到容器，直接抛出错误，进入 except 块进行重试或结束
                raise ValueError("没有找到用户信息数据源，请检查CSDN的HTML页面结构。")

            extracted_statistics = {}

            # 1. 从 user_info_container 中找到所有的 <li> 元素
            list_items = user_info_container.find_all('li')

            # 2. & 3. 遍历每个 <li> 并提取信息
            for item in list_items:
                name_div = item.find('div', class_='user-profile-statistics-name')
                num_div = item.find('div', class_='user-profile-statistics-num')

                if name_div and num_div:
                    label = name_div.get_text(strip=True)
                    value = num_div.get_text(strip=True)
                    # 4. 存储信息
                    extracted_statistics[label] = value

            print("用户统计数据:", extracted_statistics)  # 添加标签说明打印的是什么数据

            # 获取统计数据 (成就数据)
            data_info_list = soup.find_all('ul', class_='aside-common-box-achievement')

            if not data_info_list:
                # 如果找不到容器，直接抛出错误
                raise ValueError("没有找到data_info数据源，请检查CSDN的HTML页面结构。")

            target_keywords = {
                "点赞": "点赞",
                "评论": "评论",
                "收藏": "收藏",
                "分享": "分享"
            }
            extracted_achievements = {}
            # 2. 遍历找到的 <ul> 元素
            for ul_element in data_info_list:
                # 3. 在每个 <ul> 内部，找到所有的 <li> 元素
                list_items = ul_element.find_all('li')

                # 4. 遍历每个 <li>
                for li_item in list_items:
                    # 4a. 找到包含描述文本的 <div>
                    text_container_div = li_item.find('div')
                    if not text_container_div:
                        continue

                    # 4b. 在 <div> 内找到包含数字的 <span>
                    num_span = text_container_div.find('span')

                    if num_span:
                        # 4c. 获取数字文本
                        value_str = num_span.get_text(strip=True)

                        # 4d. 获取 <div> 的完整文本内容 (包括其子元素如 <em>) 来匹配关键词
                        full_text_content = text_container_div.get_text(strip=True)

                        for keyword, label_name in target_keywords.items():
                            if keyword in full_text_content:
                                # 5. 存储提取到的信息
                                extracted_achievements[label_name] = value_str
                                # 假设每个li只对应一个目标成就，找到后可以跳出内层循环
                                break

            print("成就统计数据:", extracted_achievements)  # 添加标签说明打印的是什么数据
            code_age_div = soup.find('div', class_='person-code-age')

            code_age_text = None  # 初始化变量

            if code_age_div:
                # 在找到的 div 中查找 span 标签
                span_tag = code_age_div.find('span')
                if span_tag:
                    # 提取 span 标签的文本内容，并去除首尾空白
                    code_age_text = span_tag.get_text(strip=True)
                    print(f"方法1抓取到的码龄：{code_age_text}")
            else:
                print("方法1未找到码龄所在的 div 元素。")

            author_name = soup.find('div', class_='user-profile-head-name').find('div').get_text(strip=True)
            print("作者姓名:", author_name)

            img_tag_css = soup.select_one('div.user-profile-avatar img')

            if img_tag_css:
                # 获取 img 标签的 src 属性值
                image_url_css = img_tag_css.get('src')
                print(f"方法2抓取到的图像链接：{image_url_css}")
            else:
                print("方法2未找到用户头像所在的 img 元素。")
            print("数据抓取成功！")

            info = {
                'date': now,
                'head_img': image_url_css,
                'author_name': author_name,
                'code_age': code_age_text or '',
                # 统计字段
                'article_num': to_int(extracted_statistics.get('原创', '0')),
                'fans_num': to_int(extracted_statistics.get('粉丝', '0')),
                'visit_num': to_int(extracted_statistics.get('总访问量', '0')),
                # 成就字段
                'like_num': to_int(extracted_achievements.get('点赞', '0')),
                'comment_num': to_int(extracted_achievements.get('评论', '0')),
                'collect_num': to_int(extracted_achievements.get('收藏', '0')),
                'share_num': to_int(extracted_achievements.get('分享', '0')),
                # 如有额外字段，可按需添加
                'rank': to_int(extracted_statistics.get('排名', '0')),
                'level': extracted_statistics.get('等级', ''),
                'score': to_int(extracted_statistics.get('积分', '0')),
            }
            print("数据:", info)
            save_info(info)
            # === 关键修改：成功后跳出循环 ===
            break

        except Exception as e:
            retry_count += 1  # 只在发生异常时增加重试计数
            print(f"抓取过程中发生错误 (尝试 {retry_count}/{max_retries} 次): {str(e)}")
            if retry_count < max_retries:
                print("等待 5 秒后重试...")
                time.sleep(5)
            else:
                print("达到最大重试次数，抓取失败。")
                # 达到最大次数后，循环条件不再满足，自动退出循环
                # 如果你希望函数明确返回失败状态，可以在这里 return False
                return False  # 添加返回 False 表示失败

    # 如果循环是通过 break 退出的，说明抓取成功
    # 如果是通过达到 max_retries 且最后一个 except 执行后循环条件不满足而退出的，说明失败 (上面已经 return False)
    # 所以这里可以添加一个成功时的返回，或者直接让函数结束
    if retry_count < max_retries:  # 只有在成功时 retry_count 才小于 max_retries
        return True  # 添加返回 True 表示成功


def save_info(info: dict):
    """在 Flask 应用上下文中，将 info 写入或更新到数据库"""
    with app.app_context():
        existing = Info.query.filter_by(author_name=info['author_name']).first()
        if existing:
            # 更新已有记录
            existing.date = info['date']
            existing.head_img = info['head_img']
            existing.code_age = info['code_age']
            existing.article_num = info['article_num']
            existing.fans_num = info['fans_num']
            existing.visit_num = info['visit_num']
            existing.like_num = info['like_num']
            existing.comment_num = info['comment_num']
            existing.collect_num = info['collect_num']
            existing.share_num = info['share_num']
            existing.rank = info['rank']
            existing.level = info['level']
            existing.score = info['score']
            print("更新用户信息到数据库")
        else:
            # 插入新记录
            new_info = Info(**info)
            db.session.add(new_info)
            print("添加新用户信息到数据库")

        db.session.commit()
        print("成功保存数据到数据库")
        return True


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
    # get_info()
    # get_categorize()
    get_blog()

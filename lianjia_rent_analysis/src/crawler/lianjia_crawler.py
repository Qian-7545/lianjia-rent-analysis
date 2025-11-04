import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import re
import os


class LianJiaCrawler:
    def __init__(self):
        # 使用你从浏览器获取的真实请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        # 使用你获取的URL作为基础
        self.base_url = "https://bj.lianjia.com/zufang/"

    def crawl_rental_list(self, page=1):
        """爬取租房列表页"""
        # 构建分页URL
        if page == 1:
            url = self.base_url
        else:
            url = f"https://bj.lianjia.com/zufang/pg{page}/"

        print(f"🔄 正在爬取第 {page} 页: {url}")

        try:
            # 添加随机延时，模仿人类行为
            time.sleep(random.uniform(2, 4))

            # 发送请求
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'  # 设置编码

            # 检查响应状态
            if response.status_code != 200:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return None

            return response.text

        except Exception as e:
            print(f"❌ 爬取失败: {e}")
            return None

    def parse_rental_page(self, html_content, page=1):
        """解析租房页面，提取房源信息"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # 找到房源列表容器
        content_list = soup.select_one('.content__list')
        if not content_list:
            print("❌ 未找到房源列表容器")
            return []

        # 查找所有房源项目
        rental_items = content_list.select('.content__list--item')
        print(f"📊 第{page}页找到 {len(rental_items)} 个房源")

        houses = []
        for i, item in enumerate(rental_items):
            try:
                house_info = self.parse_single_house(item)
                if house_info:
                    houses.append(house_info)
                    print(f"   ✅ 解析成功: {house_info['title'][:20]}... - {house_info['price']}元/月")
            except Exception as e:
                print(f"   ❌ 解析第{i + 1}个房源失败: {e}")

        return houses

    def parse_single_house(self, item):
        """解析单个房源信息"""
        house_info = {}

        # 提取标题
        title_elem = item.select_one('.content__list--item--title a')
        if title_elem:
            house_info['title'] = title_elem.text.strip()
            house_info['link'] = "https://bj.lianjia.com" + title_elem.get('href', '')

        # 提取价格
        price_elem = item.select_one('.content__list--item-price em')
        if price_elem:
            price_text = price_elem.text.strip()
            # 处理价格范围（如"2900-3250"）
            if '-' in price_text:
                # 取价格范围的平均值
                price_parts = price_text.split('-')
                try:
                    price1 = int(price_parts[0])
                    price2 = int(price_parts[1])
                    house_info['price'] = (price1 + price2) // 2  # 取平均值
                    house_info['price_range'] = price_text  # 保存原始价格范围
                except:
                    house_info['price'] = 0
                    house_info['price_range'] = price_text
            else:
                try:
                    house_info['price'] = int(price_text)
                except:
                    house_info['price'] = 0

        # 提取描述信息（包含面积、户型、楼层等）
        desc_elem = item.select_one('.content__list--item--des')
        if desc_elem:
            desc_text = desc_elem.get_text(separator='|', strip=True)
            house_info['full_description'] = desc_text

            # 从描述中提取具体信息
            desc_parts = desc_text.split('|')
            for part in desc_parts:
                part = part.strip()
                # 提取面积
                if '㎡' in part:
                    house_info['area'] = part
                # 提取户型
                elif '室' in part and '厅' in part:
                    house_info['layout'] = part
                # 提取楼层
                elif '层' in part:
                    house_info['floor'] = part
                # 提取朝向
                elif '东' in part or '南' in part or '西' in part or '北' in part:
                    house_info['orientation'] = part
                # 提取位置（通常是第一个部分）
                elif not any(key in part for key in ['㎡', '室', '厅', '层', '东', '南', '西', '北']):
                    if 'location' not in house_info:
                        house_info['location'] = part
                    else:
                        house_info['location'] += "|" + part

        # 提取小区/区域
        region_elem = item.select_one('.content__list--item--brand')
        if region_elem:
            house_info['region'] = region_elem.text.strip()

        # 提取标签（如：近地铁、精装等）
        tags_elems = item.select('.content__list--item--bottom oneline')
        if tags_elems:
            house_info['tags'] = [tag.text.strip() for tag in tags_elems]

        return house_info

    def crawl_multiple_pages(self, start_page=1, end_page=3):
        """爬取多页数据"""
        all_houses = []

        for page in range(start_page, end_page + 1):
            print(f"\n{'=' * 50}")
            print(f"处理第 {page} 页")
            print(f"{'=' * 50}")

            html_content = self.crawl_rental_list(page)
            if not html_content:
                print(f"❌ 第{page}页爬取失败，跳过")
                continue

            houses = self.parse_rental_page(html_content, page)
            all_houses.extend(houses)

            print(f"✅ 第{page}页完成，获取 {len(houses)} 个房源")

        print(f"\n🎉 所有页面完成！共获取 {len(all_houses)} 个房源")
        return all_houses

    def save_to_csv(self, houses, filename="lianjia_rentals.csv"):
        """保存房源信息到CSV文件"""
        if not houses:
            print("❌ 没有数据可保存")
            return

        # 确保输出目录存在 - 修正路径
        os.makedirs('../../output', exist_ok=True)

        df = pd.DataFrame(houses)
        filepath = f'../../output/{filename}'  # 修正路径
        df.to_csv(filepath, index=False, encoding='utf_8_sig')
        print(f"💾 数据已保存到: {filepath}")

        # 显示数据统计
        print(f"\n📊 数据统计:")
        print(f"   房源数量: {len(houses)}")
        if 'price' in df.columns:
            print(f"   平均价格: {df['price'].mean():.0f}元/月")
            print(f"   价格范围: {df['price'].min()} - {df['price'].max()}元/月")
        if 'area' in df.columns:
            print(f"   面积范围: {df['area'].unique()[:5]}...")  # 显示前5个不同的面积


# 测试代码
if __name__ == "__main__":
    crawler = LianJiaCrawler()

    print("=" * 60)
    print("           链家租房爬虫 - 完整数据提取")
    print("=" * 60)

    # 爬取多页数据
    houses = crawler.crawl_multiple_pages(1, 3)

    if houses:
        # 保存数据
        crawler.save_to_csv(houses)

        # 显示前3个房源详情
        print(f"\n🏠 前3个房源详情:")
        for i, house in enumerate(houses[:3]):
            print(f"\n房源 {i + 1}:")
            for key, value in house.items():
                print(f"  {key}: {value}")
    else:
        print("❌ 没有获取到任何房源数据")
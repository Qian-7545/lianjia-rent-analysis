from src.crawler.lianjia_crawler import LianJiaCrawler
from src.analysis.data_analysis import RentDataAnalyzer
import os


def ensure_directories():
    """确保必要的目录存在"""
    directories = ['data/raw', 'data/processed', 'output']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✓ 目录结构检查完成")


def main():
    print("=" * 60)
    print("           链家租房信息分析系统")
    print("=" * 60)

    # 确保目录存在
    ensure_directories()

    # 创建爬虫实例并运行
    crawler = LianJiaCrawler()

    print("\n🚀 开始爬取链家租房数据...")
    houses = crawler.crawl_multiple_pages(1, 3)

    if houses:
        # 保存数据
        crawler.save_to_csv(houses)

        print(f"\n🎉 爬取完成！成功获取 {len(houses)} 条租房数据")

        # 数据分析
        print("\n" + "=" * 50)
        print("           开始数据分析")
        print("=" * 50)

        data_file = "output/lianjia_rentals.csv"
        analyzer = RentDataAnalyzer(data_file)
        analyzer.generate_full_report()

        print("\n📁 项目完成！生成的文件：")
        print("   - output/lianjia_rentals.csv (房源数据)")
        print("   - output/price_analysis.html (高价房源图表)")
        print("   - output/price_distribution.html (价格分布图表)")
        print("   - data/raw/ (原始数据目录)")
        print("   - data/processed/ (处理后的数据目录)")
    else:
        print("❌ 数据获取失败")


if __name__ == "__main__":
    main()
import pandas as pd
import numpy as np
from pyecharts.charts import Bar, Pie, Scatter
from pyecharts import options as opts
import os


class RentDataAnalyzer:
    def __init__(self, data_file):
        """初始化数据分析器"""
        self.df = pd.read_csv(data_file, encoding='utf_8_sig')
        print(f"数据加载成功！共 {len(self.df)} 条记录")

        # 基础数据清洗
        self.clean_data()

    def clean_data(self):
        """数据清洗"""
        # 移除价格为0的记录
        self.df = self.df[self.df['price'] > 0]
        print(f"清洗后数据量: {len(self.df)} 条")

    def basic_analysis(self):
        """基础统计分析"""
        print("\n=== 基础统计分析 ===")
        print(f"房源数量: {len(self.df)}")
        print(f"平均价格: {self.df['price'].mean():.0f} 元/月")
        print(f"价格中位数: {self.df['price'].median()} 元/月")
        print(f"最高价格: {self.df['price'].max()} 元/月")
        print(f"最低价格: {self.df['price'].min()} 元/月")

        # 价格分布
        price_ranges = [
            (0, 2000, "2000元以下"),
            (2000, 4000, "2000-4000元"),
            (4000, 6000, "4000-6000元"),
            (6000, 8000, "6000-8000元"),
            (8000, 10000, "8000-10000元"),
            (10000, float('inf'), "10000元以上")
        ]

        range_counts = {}
        for low, high, label in price_ranges:
            count = len(self.df[(self.df['price'] >= low) & (self.df['price'] < high)])
            range_counts[label] = count

        print("\n价格分布:")
        for range_name, count in range_counts.items():
            if count > 0:
                percentage = (count / len(self.df)) * 100
                print(f"  {range_name}: {count}套 ({percentage:.1f}%)")

    def create_price_chart(self, output_file="price_analysis.html"):
        """创建价格分析图表"""
        # 按价格排序的前20个房源
        top_20 = self.df.nlargest(20, 'price')[['title', 'price']]

        bar = (
            Bar()
            .add_xaxis(top_20['title'].str[:15].tolist())  # 截取标题前15个字符
            .add_yaxis("月租金(元)", top_20['price'].tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="高价房源TOP20"),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
                yaxis_opts=opts.AxisOpts(name="月租金(元)")
            )
        )

        # 确保输出目录存在
        os.makedirs('../../output', exist_ok=True)
        bar.render(f"../../output/{output_file}")
        print(f"📊 价格分析图表已生成: output/{output_file}")

    def create_price_distribution_chart(self, output_file="price_distribution.html"):
        """创建价格分布饼图"""
        price_ranges = [
            (0, 2000, "2000元以下"),
            (2000, 4000, "2000-4000元"),
            (4000, 6000, "4000-6000元"),
            (6000, 8000, "6000-8000元"),
            (8000, 10000, "8000-10000元"),
            (10000, float('inf'), "10000元以上")
        ]

        data = []
        for low, high, label in price_ranges:
            count = len(self.df[(self.df['price'] >= low) & (self.df['price'] < high)])
            if count > 0:
                data.append((label, count))

        pie = (
            Pie()
            .add("", data)
            .set_global_opts(title_opts=opts.TitleOpts(title="租金价格分布"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"))
        )

        pie.render(f"../../output/{output_file}")
        print(f"📊 价格分布图表已生成: output/{output_file}")

    def analyze_by_region(self):
        """按区域分析 - 改进版本"""
        if 'location' in self.df.columns:
            print("\n=== 区域分析 ===")

            # 改进的区域提取逻辑
            def extract_district(location_str):
                if pd.isna(location_str):
                    return '未知'
                # 常见的北京行政区
                beijing_districts = [
                    '东城', '西城', '朝阳', '海淀', '丰台', '石景山',
                    '通州', '昌平', '大兴', '顺义', '房山', '门头沟',
                    '平谷', '怀柔', '密云', '延庆'
                ]

                # 从location中查找行政区
                for district in beijing_districts:
                    if district in location_str:
                        return district
                return '其他'

            self.df['district'] = self.df['location'].apply(extract_district)

            district_stats = self.df.groupby('district').agg({
                'price': ['count', 'mean', 'min', 'max']
            }).round(0)

            # 重命名列
            district_stats.columns = ['房源数量', '平均价格', '最低价格', '最高价格']
            district_stats = district_stats.sort_values('房源数量', ascending=False)

            print("\n各区域房源统计:")
            for district, row in district_stats.iterrows():
                if row['房源数量'] > 0:  # 只显示有房源的区域
                    print(f"  {district}: {int(row['房源数量'])}套, 均价{int(row['平均价格'])}元")
    def generate_full_report(self):
        """生成完整分析报告"""
        print("\n" + "=" * 50)
        print("           租房数据分析报告")
        print("=" * 50)

        self.basic_analysis()
        self.analyze_by_region()
        self.create_price_chart()
        self.create_price_distribution_chart()

        print(f"\n🎉 分析完成！共分析 {len(self.df)} 条有效数据")


# 测试代码
if __name__ == "__main__":
    analyzer = RentDataAnalyzer("../../output/lianjia_rentals.csv")
    analyzer.generate_full_report()
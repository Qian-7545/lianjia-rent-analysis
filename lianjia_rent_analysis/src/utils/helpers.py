import re


def clean_price(price_text):
    """清理价格文本"""
    if not price_text:
        return 0

    # 移除非数字字符（保留数字和小数点）
    cleaned = re.sub(r'[^\d.]', '', str(price_text))
    try:
        return float(cleaned)
    except:
        return 0


def extract_area(text):
    """从文本中提取面积"""
    if not text:
        return None
    match = re.search(r'(\d+\.?\d*)\s*㎡', str(text))
    return match.group(1) if match else None


def format_price(price):
    """格式化价格显示"""
    if price >= 10000:
        return f"{price / 10000:.1f}万元/月"
    else:
        return f"{price:.0f}元/月"


def get_price_range_label(price):
    """获取价格区间标签"""
    if price < 2000:
        return "2000元以下"
    elif price < 4000:
        return "2000-4000元"
    elif price < 6000:
        return "4000-6000元"
    elif price < 8000:
        return "6000-8000元"
    elif price < 10000:
        return "8000-10000元"
    else:
        return "10000元以上"
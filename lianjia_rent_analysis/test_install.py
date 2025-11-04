try:
    import requests
    import pandas as pd
    from bs4 import BeautifulSoup
    from pyecharts.charts import Bar
    print("✅ 所有库安装成功！")
except ImportError as e:
    print(f"❌ 安装失败: {e}")
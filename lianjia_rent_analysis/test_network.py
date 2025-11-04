import requests

def test_connection():
    """测试网络连接"""
    try:
        # 测试基本网络连接
        response = requests.get("https://www.baidu.com", timeout=10)
        if response.status_code == 200:
            print("✅ 网络连接正常")
            return True
        else:
            print("❌ 网络连接异常")
            return False
    except Exception as e:
        print(f"❌ 网络连接失败: {e}")
        return False

if __name__ == "__main__":
    test_connection()
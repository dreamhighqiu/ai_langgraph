

import requests
import re
import time

# fmt: off  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y0hSclpnPT06OWNkNmRiZDM=

class HuiceBBS:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Origin': 'http://bbs.huice.com',
            'Referer': 'http://bbs.huice.com/'
        })
        self.base_url = 'http://bbs.huice.com'

    def login(self, username, password):
        """登录论坛"""
        login_url = f"{self.base_url}/member.php"
        params = {
            'mod': 'logging',
            'action': 'login',
            'loginsubmit': 'yes',
            'infloat': 'yes',
            'lssubmit': 'yes',
            'inajax': '1'
        }

        data = {
            'fastloginfield': 'username',
            'username': username,
            'password': password,
            'quickforward': 'yes',
            'handlekey': 'ls'
        }

        try:
            response = self.session.post(login_url, params=params, data=data)

            if response.status_code == 200:
                # 检查登录是否成功
                if '欢迎您回来' in response.text or '登录成功' in response.text:
                    print("✓ 登录成功")
                    return True
                else:
                    print("✗ 登录失败，请检查用户名和密码")
                    return False
            else:
                print(f"✗ 登录请求失败，状态码: {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ 登录过程中出现错误: {e}")
            return False

    def get_formhash(self):
        """获取formhash值"""
        try:
            response = self.session.get(f"{self.base_url}/")
# pragma: no cover  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y0hSclpnPT06OWNkNmRiZDM=

            if response.status_code == 200:
                # 从HTML中提取formhash
                pattern = r'formhash=([a-f0-9]{8})'
                match = re.search(pattern, response.text)

                if match:
                    formhash = match.group(1)
                    print(f"✓ 获取到formhash: {formhash}")
                    return formhash
                else:
                    print("✗ 未找到formhash")
                    return None
            else:
                print(f"✗ 获取首页失败，状态码: {response.status_code}")
                return None

        except Exception as e:
            print(f"✗ 获取formhash过程中出现错误: {e}")
            return None

    def create_post(self, fid, formhash, subject, message):
        """发布新帖子

        Args:
            fid: 版块ID (forum id)
            formhash: 表单哈希值
            subject: 帖子标题
            message: 帖子内容
        """
        # 发帖URL和参数 (基于你提供的接口信息)
        post_url = f"{self.base_url}/forum.php"
        params = {
            'mod': 'post',
            'action': 'newthread',
            'fid': fid,
            'extra': '',
            'topicsubmit': 'yes'
        }

        # 发帖表单数据 (基于你提供的接口信息)
        data = {
            'formhash': formhash,
            'posttime': int(time.time()),  # 当前时间戳
            'wysiwyg': '1',
            'subject': subject,
            'message': message,
            'allownoticeauthor': '1',
            'usesig': '1',
            'save': '',
            'file': '',
            # 注意：这里有重复的file参数，按原样保留
            'file': ''  # 第二个file参数，根据抓包数据保留
        }

        try:
            print(f"正在发布帖子到版块 {fid}...")
            response = self.session.post(post_url, params=params, data=data)

            print(f"状态码: {response.status_code}")
            print(f"响应内容长度: {len(response.text)} 字符")

            # 根据Discuz常见响应判断发帖是否成功
            if response.status_code == 200:
                # 尝试从响应中提取信息判断是否成功
                if '发帖成功' in response.text or '主题已发布' in response.text:
                    print("✓ 发帖成功！")
                    return True
                elif '抱歉' in response.text or '错误' in response.text:
                    print("✗ 发帖失败，可能的原因：")
                    print("  - formhash已过期")
                    print("  - 权限不足")
                    print("  - 内容不符合规则")
                    # 可以打印部分错误信息
                    error_match = re.search(r'<div class="alert_error">(.*?)</div>', response.text, re.DOTALL)
                    if error_match:
                        error_msg = re.sub('<[^<]+?>', '', error_match.group(1)).strip()
                        print(f"  错误信息: {error_msg[:100]}...")
                    return False
                else:
                    # 如果没有明确的成功/失败标识，检查重定向或跳转
                    print("⚠ 发帖结果不确定，请手动检查")
                    # 可以保存响应内容供调试
                    with open('post_response.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print("  响应内容已保存到 post_response.html")
                    return None
            else:
                print(f"✗ 发帖请求失败，状态码: {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ 发帖过程中出现错误: {e}")
            return False
# pylint: disable  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y0hSclpnPT06OWNkNmRiZDM=

    def post_new_thread(self, username, password, fid, subject, message):
        """完整的发帖流程：登录 -> 获取formhash -> 发帖"""
        print("=" * 50)
        print("开始发帖流程")
        print("=" * 50)

        # 1. 登录
        if not self.login(username, password):
            return False

        # 2. 获取formhash
        formhash = self.get_formhash()
        if not formhash:
            print("✗ 无法获取formhash，发帖终止")
            return False

        # 3. 发帖
        result = self.create_post(fid, formhash, subject, message)

        return result


# 使用示例
if __name__ == "__main__":
    # 配置信息
    USERNAME = "huice0011"
    PASSWORD = "huice0011"

    # 发帖信息
    FID = 40  # 版块ID (根据你的需求修改，40对应Loadrunner版块)
    POST_SUBJECT = "测试帖子标题 - Python自动发布"
    POST_MESSAGE = """这是一个通过Python requests自动发布的测试帖子。

帖子内容可以包含多行文本，支持基本的Discuz! BB代码格式。

测试时间：""" + time.strftime("%Y-%m-%d %H:%M:%S")
# pylint: disable  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y0hSclpnPT06OWNkNmRiZDM=

    # 创建实例并执行发帖
    bbs = HuiceBBS()
    success = bbs.post_new_thread(USERNAME, PASSWORD, FID, POST_SUBJECT, POST_MESSAGE)

    if success:
        print("\n✓ 发帖流程完成！")
    else:
        print("\n✗ 发帖流程失败")
from win11toast import toast
import os

# 获取当前脚本的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 构建相对路径
ICON_PATH = os.path.join(script_dir, "LOGO.ico")

def notice(text):
    print(ICON_PATH)
    toast(text, icon=ICON_PATH)


if __name__ == "__main__":
    notice("123")

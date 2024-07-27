from win11toast import toast

ICON_PATH = r"C:\Users\Havoc\PycharmProjects\Creeper-CFT\LOGO.ico"

def notice(text):
    toast(text, icon=ICON_PATH)


if __name__ == "__main__":
    notice("123")

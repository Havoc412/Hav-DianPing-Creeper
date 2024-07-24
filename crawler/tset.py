import re

def get_num(text):
    match = re.search(r'\d+', text)
    if match:
        number = match.group()
        return number
    else:
        print(f"没有找到数字部分， origin:{text}")
        return 0


if __name__ == '__main__':
    print(get_num("nihi123nii"))
    print(get_num("人均：20!!!"))
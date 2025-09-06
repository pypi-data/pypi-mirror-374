'''
Author: 凌逆战 | Never
Date: 2025-08-22 23:41:13
Description: pip install 'markitdown[all]
'''
from neverlib.utils import get_path_list

html_path_list = get_path_list("./LXP-Never", end="*.html")

for html_path in html_path_list:
    print(html_path)
    break



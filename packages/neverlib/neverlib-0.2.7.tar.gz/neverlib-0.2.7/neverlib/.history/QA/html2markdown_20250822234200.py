'''
Author: 凌逆战 | Never
Date: 2025-08-22 23:41:13
Description: 
'''
from neverlib.utils import get_path_list

path_list = get_path_list(
    "/Users/never/Desktop/test",
    "*.html",
    recursive=True,
)

for path in path_list:
    print(path)



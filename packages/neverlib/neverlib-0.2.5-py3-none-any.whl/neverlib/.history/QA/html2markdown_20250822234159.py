from neverlib.utils import get_path_list

path_list = get_path_list(
    "/Users/never/Desktop/test",
    "*.html",
    recursive=True,
)

for path in path_list:
    print(path)



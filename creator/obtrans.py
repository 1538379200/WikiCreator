from pathlib import Path
from functools import lru_cache
import os


obfile_list = []

@lru_cache()
def get_file(filepath):
    sub_dir = []
    if len([x for x in filepath]) == 0:
        return
    else:
        for path_ in filepath:
            if Path(path_).is_dir():
                for sub_path in Path(path_).iterdir():
                    if sub_path.is_dir():
                        sub_dir.append(sub_path)
                    else:
                        if sub_path.suffix in (".md", ".png"):
                            obfile_list.append(sub_path)
            else:
                if path_.suffix in (".md", ".png"):
                    obfile_list.append(path_)
        return get_file(tuple(sub_dir))

def obsidian_trans(filepath):
    md_list = []
    png_list = []
    get_file(filepath)
    for file in obfile_list:
        if file.suffix == '.md':
            md_list.append(os.fspath(file))
        elif file.suffix == '.png':
            png_list.append(os.fspath(file))
    return md_list, png_list


import os
import zipfile
import sys

# 确保有足够的命令行参数传入
if len(sys.argv) < 3:
    print("Usage: python tqu.py <directory_to_search> <text_to_search>")
    sys.exit(1)

# 第一个命令行参数是要搜索的目录
directory_to_search = sys.argv[1]
# 第二个命令行参数是要搜索的文本
text_to_search = sys.argv[2]

# 遍历目录
for foldername, subfolders, filenames in os.walk(directory_to_search):
    for filename in filenames:
        if filename.endswith('.jar'):
            # 构造完整的文件路径
            full_path = os.path.join(foldername, filename)
            try:
                # 打开JAR文件
                with zipfile.ZipFile(full_path, 'r') as jarfile:
                    # 遍历JAR文件内的每个文件
                    for name in jarfile.namelist():
                        # 打开JAR文件内的文件
                        with jarfile.open(name) as file:
                            if text_to_search.encode() in file.read():
                                print(f"Found '{text_to_search}' in {full_path}")
                                break  # 找到文本后跳出循环
            except zipfile.BadZipFile:
                print(f"Bad zip file: {full_path}")
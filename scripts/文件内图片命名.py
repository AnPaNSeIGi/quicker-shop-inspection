# -*- coding: utf-8 -*-
"""
文件内图片命名工具
===================
将指定文件夹内的图片文件按「修改时间先后」重命名为 1,2,3...
用于整理自动巡检脚本（Quicker 动作）在 RMS记录 / 邮件记录 目录下
生成的巡检截图，方便按时间顺序归档查看。

用法：
    python 文件内图片命名.py [文件夹1] [文件夹2] ...

示例：
    python 文件内图片命名.py "D:\记录\RMS记录" "D:\记录\邮件记录"
    不带参数时，默认处理当前目录下的 RMS记录 与 邮件记录 两个文件夹。

说明：
    原脚本中的路径为开发机绝对路径（D:\\Users\\Administrator\\Desktop\\...），
    上传到 GitHub 时已改为命令行参数方式，避免在其他环境运行时因路径不存在而报错。
"""
import os
import shutil
import sys
import uuid

# 支持的图片格式
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}


def process_folder(folder_path):
    """处理单个文件夹：将图片按修改时间先后重命名为 1,2,3..."""
    if not os.path.isdir(folder_path):
        print(f"错误：文件夹不存在 - {folder_path}")
        return

    # 创建唯一临时目录
    temp_dir_name = f".temp_rename_{uuid.uuid4().hex}"
    temp_dir = os.path.join(folder_path, temp_dir_name)
    os.makedirs(temp_dir, exist_ok=False)

    try:
        # 步骤1：将所有图片移动到临时目录
        moved_count = 0
        for file in os.listdir(folder_path):
            full_path = os.path.join(folder_path, file)
            if not os.path.isfile(full_path):
                continue
            ext = os.path.splitext(file)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                dest = os.path.join(temp_dir, file)
                shutil.move(full_path, dest)
                moved_count += 1

        if moved_count == 0:
            print(f"文件夹 {folder_path} 中没有图片文件。")
            return

        # 步骤2：获取临时目录中所有文件，按修改时间排序
        file_list = []
        for file in os.listdir(temp_dir):
            full_path = os.path.join(temp_dir, file)
            if os.path.isfile(full_path):
                mtime = os.path.getmtime(full_path)          # 修改时间
                file_list.append((mtime, file, full_path))
        file_list.sort(key=lambda x: (x[0], x[1]))           # 时间相同则按文件名稳定排序

        # 步骤3：按顺序重命名并移回原文件夹
        print(f"开始处理文件夹：{folder_path}")
        for index, (_, old_name, temp_path) in enumerate(file_list, start=1):
            ext = os.path.splitext(old_name)[1]
            new_name = f"{index}{ext}"
            dest_path = os.path.join(folder_path, new_name)
            os.rename(temp_path, dest_path)                  # 移动并重命名
            print(f"重命名：{old_name} -> {new_name}")

        print(f"文件夹 {folder_path} 处理完成，共处理 {moved_count} 个文件。\n")
    finally:
        # 清理临时目录
        try:
            os.rmdir(temp_dir)
        except OSError:
            print(f"警告：临时目录 {temp_dir} 未完全清空，请手动检查。")
        else:
            print(f"临时目录 {temp_dir} 已删除。")


if __name__ == "__main__":
    # 优先使用命令行参数；未提供时使用默认相对路径（脚本所在目录下的 RMS记录 / 邮件记录）
    args = sys.argv[1:]
    if args:
        folders = args
    else:
        # 默认相对路径：脚本所在目录下的 RMS记录 与 邮件记录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        folders = [
            os.path.join(script_dir, "RMS记录"),
            os.path.join(script_dir, "邮件记录"),
        ]

    for folder in folders:
        process_folder(folder)
    print("所有操作完成。")

# -*- coding: utf-8 -*-
"""
新导入资料解析工具
===================
从「无人店铺操作表格.xlsx」的"待加工数据"工作表中，批量提取每家店铺的
R-Login ID / 登录密码 / 用户ID / 邮箱 等字段，输出为结构化的"提取结果"表格，
供后续 Quicker 自动巡检动作批量调用。

用法：
    python 新导入资料.py [输入xlsx路径] [输出xlsx路径(可选)]

示例：
    python 新导入资料.py "D:\店铺数据\无人店铺操作表格.xlsx"
    python 新导入资料.py "data\无人店铺操作表格_示例.xlsx" "output\提取结果.xlsx"

说明：
    原脚本中的路径为开发机绝对路径（D:\Users\Administrator\Desktop\...），
    上传到 GitHub 时已改为命令行参数方式，避免在其他环境运行时因路径不存在而报错。
    依赖：pandas, openpyxl
"""
import os
import re
import sys

try:
    import pandas as pd
except ImportError:
    print("缺少依赖：请先安装 pandas 和 openpyxl（pip install pandas openpyxl）")
    exit(1)


def parse_a_column(text):
    """
    从A列文本中提取：
    R-Login ID, ログインパスワード, ユーザID, パスワード（记为A_パスワード）
    """
    if pd.isna(text):
        return {}
    # 使用正则一次性提取四个字段（支持中文或英文冒号，忽略中间换行）
    pattern = r'R-Login ID[：:]s*(S+).*?ログインパスワード[：:]s*(S+).*?ユーザID[：:]s*(S+).*?パスワード[：:]s*(S+)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return {
            'R-Login ID': match.group(1),
            'ログインパスワード': match.group(2),
            'ユーザID': match.group(3),
            'A_パスワード': match.group(4)
        }
    else:
        # 如果格式不匹配，返回空字典（可根据需要添加日志）
        return {}


def parse_b_column(text):
    """
    从B列文本中提取：
    重要メールアドレス, メール, パスワード（记为B_パスワード）
    """
    if pd.isna(text):
        return {}
    pattern = r'重要メールアドレス[：:]s*(S+).*?メール[：:]s*(S+).*?パスワード[：:]s*(S+)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return {
            '重要メールアドレス': match.group(1),
            'メール': match.group(2),
            'B_パスワード': match.group(3)
        }
    else:
        return {}


def main():
    args = sys.argv[1:]
    if args:
        input_path = args[0]
    else:
        # 默认相对路径：脚本所在目录上一级 data 目录下的示例表格
        script_dir = os.path.dirname(os.path.abspath(__file__))
        input_path = os.path.join(script_dir, "..", "data", "无人店铺操作表格_示例.xlsx")
        print(f"未提供输入文件，使用默认示例：{input_path}")

    # 输出文件：默认在原目录下生成新文件，避免覆盖原文件
    if len(args) >= 2:
        output_path = args[1]
    else:
        dir_name = os.path.dirname(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(dir_name, f"{base_name}_提取结果.xlsx")

    # 读取"待加工数据"工作表（无表头，所有列作为字符串读入）
    try:
        df = pd.read_excel(input_path, sheet_name='待加工数据', header=None, dtype=str)
    except Exception as e:
        print(f"读取文件失败：{e}")
        exit(1)

    # 存储所有提取结果
    results = []

    for idx, row in df.iterrows():
        a_text = row[0]   # A列
        b_text = row[1]   # B列

        a_data = parse_a_column(a_text)
        b_data = parse_b_column(b_text)

        # 合并同一行的数据，并添加原始行号（Excel行号 = 索引+1，因为无表头）
        combined = {
            '原始行号': idx + 1,
            **a_data,
            **b_data
        }
        results.append(combined)

    # 转换为DataFrame，并确保列顺序统一
    result_df = pd.DataFrame(results)
    desired_columns = [
        '原始行号',
        'R-Login ID',
        'ログインパスワード',
        'ユーザID',
        'A_パスワード',
        '重要メールアドレス',
        'メール',
        'B_パスワード'
    ]
    # 如果某行缺少某个字段，会自动填充NaN
    result_df = result_df.reindex(columns=desired_columns)

    # 将结果写入新Excel文件（只包含此工作表）
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            result_df.to_excel(writer, sheet_name='提取结果', index=False)
        print(f"处理完成！结果已保存至：{output_path}")
    except Exception as e:
        print(f"保存文件失败：{e}")


if __name__ == "__main__":
    main()

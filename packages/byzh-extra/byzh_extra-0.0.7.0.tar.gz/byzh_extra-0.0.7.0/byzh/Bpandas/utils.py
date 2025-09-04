import pandas as pd

def b_strip(df: pd.DataFrame):
    """
    去除dataframe中的空格
    :param df:
    :return:
    """
    # 处理columns
    df.columns = pd.Series(df.columns).map(lambda x: x.strip() if isinstance(x, str) else x)
    # 处理index
    df.index = df.index.map(lambda x: x.strip() if isinstance(x, str) else x)
    # 处理values
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    return df

def b_df2dict(df:pd.DataFrame, key:str, value:str):
    """
    dataframe转字典
    :param df:
    :param key:
    :param value:
    :return:
    """
    my_dict = df.set_index(key)[value].to_dict()
    return my_dict

def b_set_display(all_row=True, all_col=True):
    # 行
    if all_row:
        pd.set_option('display.max_rows', None)  # 显示所有行
    # 列
    if all_col:
        pd.set_option('display.max_columns', None)  # 显示所有列
        pd.set_option('display.width', None)  # 设置显示宽度为无限制
        pd.set_option('display.max_colwidth', None)  # 设置列宽为无限制
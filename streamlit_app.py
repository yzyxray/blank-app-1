import pandas as pd
import re
import requests
import streamlit as st

# 提取主域名
def extract_root_domain(url):
    try:
        return re.search(r"https?://([^/]+)", url).group(1)
    except AttributeError:
        return ""

# 获取最终的Landing Page
def get_final_url(url):
    try:
        response = requests.get(url, timeout=10)
        return response.url
    except Exception as e:
        return ""

# 提取参数值
def extract_param(url, param):
    try:
        match = re.search(rf"{param}=([^&]+)", url)
        return match.group(1) if match else ""
    except Exception as e:
        return ""

# Streamlit 应用界面
st.title("Excel 文件处理工具")
st.write("上传一个包含URL的Excel文件，我会帮你提取主域名和相关参数！")

# 上传文件
uploaded_file = st.file_uploader("上传Excel文件", type=["xlsx"])

if uploaded_file:
    try:
        # 尝试读取 Excel 文件
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        
        # 打印列名以调试
        st.write("Excel 文件中的列名：", df.columns.tolist())

        # 检查是否存在 'TargetUrl' 列
        if 'TargetUrl' not in df.columns:
            st.error("上传的 Excel 文件中没有找到 'TargetUrl' 列，请检查文件格式！")
        else:
            # 处理数据
            df['Response URL'] = df['TargetUrl'].apply(get_final_url)
            st.write("处理完成！预览结果：")
            st.dataframe(df)

    except ImportError as e:
        st.error("缺少 'openpyxl' 库，请确保它已正确安装！")
    except Exception as e:
        st.error(f"无法读取 Excel 文件：{e}")

    # 处理数据
    df['Root Domain'] = df['Source url'].apply(extract_root_domain)
    df['Response URL'] = df['TargetUrl'].apply(get_final_url)
    df['Affid'] = df['Response URL'].apply(lambda x: extract_param(x, "Affid"))
    df['s4'] = df['Response URL'].apply(lambda x: extract_param(x, "s4"))
    df['sub4'] = df['Response URL'].apply(lambda x: extract_param(x, "sub4"))
    df['affid'] = df['Response URL'].apply(lambda x: extract_param(x, "affid"))

    # 显示处理后的数据
    st.write("处理完成！预览结果：")
    st.dataframe(df)

    # 提供下载链接
    output_file = "processed_data.xlsx"
    df.to_excel(output_file, index=False)

    with open(output_file, "rb") as file:
        st.download_button(
            label="下载处理后的文件",
            data=file,
            file_name="processed_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

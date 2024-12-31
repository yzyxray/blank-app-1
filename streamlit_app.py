import streamlit as st
import pandas as pd
import numpy as np
import pandas as pd
import aiohttp
import time
import asyncio
st.title('广告链接信息解析')

DATE_COLUMN = 'date/time'
# 这里配置需要匹配的key
matched_keys = ["Affid", "s4", "affid", "sub4", "subid", "subid3"]


@st.cache_resource
async def extract_url_async(target_urls, results=[], results_url_map={}):
    async with aiohttp.ClientSession() as session:
        percent_complete = 0
        for index, url in enumerate(target_urls):
            percent_complete = int((index + 1) / len(target_urls) * 100)
            my_bar.progress(percent_complete, text=f'解析进度：{percent_complete}%')
            result = {}
            if url in results_url_map:
                results.append(results_url_map[url])
            else:
                try:
                    print("current url", url)
                    async with session.get(url, timeout=60) as response:
                        result["reponse url"] = str(response.url)
                        query = response.url.query
                        for m_key in matched_keys:
                            if m_key in query:
                                result[m_key] = query[m_key]

                        results_url_map[url] = result
                except Exception as e:
                    print(e)
                    results_url_map[url] = "error"
                finally:
                    results.append(result)


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


data_path = st.file_uploader("上传excel文件")
if data_path:
    google_sheet_df = pd.read_excel(data_path)
    edited_df = st.data_editor(google_sheet_df.head(50))
    progress_text = "Operation in progress. Please wait."

    # 这里不用管，主要逻辑在里面，一路运行就可以了；
    clicked = st.button('start generate')
    # st.write(edited_df)
    if clicked:
        my_bar = st.progress(0, text=progress_text)
        # 这里运行下会开始慢慢跑，下面有进度条
        target_urls = google_sheet_df["Target url"].iloc[1:].to_list()
        loops = asyncio.new_event_loop()
        results = []
        results_url_map = {}
        loops.run_until_complete(extract_url_async(
            target_urls, results, results_url_map))
        valid_results = [{"target_url": k} | v for k,
                         v in results_url_map.items() if type(v) is dict]
        results_df = pd.DataFrame(valid_results)
        # 这里是最后的输出，把输出的路径改一下，不然就会在同一个文件夹下
        merged_df = google_sheet_df.merge(
            results_df, left_on="Target url", right_on="target_url", how="left")
        st.write(merged_df)
        st.download_button(
            label="Download data as CSV",
            data=convert_df(merged_df),
            file_name='large_df.csv',
            mime='text/csv',
        )

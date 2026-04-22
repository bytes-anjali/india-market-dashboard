import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import data_fetcher
import config

st.set_page_config(
    page_title="India Market Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 India Stock Market Dashboard")

col_time, col_btn = st.columns([4, 1])
with col_time:
    st.caption(f"Last updated: {data_fetcher.get_last_updated()}")
with col_btn:
    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()

st.divider()

st.subheader("🏦 Market Indices")
with st.spinner("Loading indices..."):
    indices_df = data_fetcher.get_indices()

if not indices_df.empty:
    cols = st.columns(len(indices_df))
    for i, row in indices_df.iterrows():
        with cols[i]:
            change = row["Change %"]
            st.metric(
                label=row["Index"],
                value=f"{row['Value']:,}" if row['Value'] != 'N/A' else 'N/A',
                delta=f"{change}%"
            )

st.divider()

st.subheader("🏢 Top 10 Stocks")
with st.spinner("Loading stocks..."):
    stocks_df = data_fetcher.get_top_stocks()

if not stocks_df.empty:
    def color_change(val):
        return "color: green" if val >= 0 else "color: red"
    styled = stocks_df.style.applymap(color_change, subset=["Change %"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

st.divider()

st.subheader("📰 Latest Market News")
with st.spinner("Loading news..."):
    news = data_fetcher.get_news()

if news:
    for article in news:
        st.markdown(f"**[{article['Title']}]({article['Link']})**")
        st.caption(f"🗞 {article['Source']}  •  {article['Published']}")
        st.divider()
else:
    st.info("No news available at the moment.")

st.subheader("🗓 IPO Calendar")
with st.spinner("Loading IPO data..."):
    ipo_df = data_fetcher.get_ipo_data()

if not ipo_df.empty:
    st.dataframe(ipo_df, use_container_width=True, hide_index=True)
else:
    st.info("No IPO data available.")

st.divider()
st.caption("⏱ Click 'Refresh Now' to update data manually.")

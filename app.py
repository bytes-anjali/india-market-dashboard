import news_engine
import streamlit as st
import pandas as pd
import data_fetcher
import config

st.set_page_config(page_title="India Market Dashboard", page_icon="📈", layout="wide")
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
            st.metric(
                label=row["Index"],
                value=f"{row['Value']:,}" if row['Value'] != 'N/A' else 'N/A',
                delta=f"{row['Change %']}%"
            )

st.divider()
st.subheader("🏢 Top 10 Stocks")
with st.spinner("Loading stocks..."):
    stocks_df = data_fetcher.get_top_stocks()

if not stocks_df.empty:
    st.dataframe(stocks_df, use_container_width=True, hide_index=True)

st.divider()
import news_engine  # add this at top if not already

st.subheader("📰 Market News (Clustered)")

with st.spinner("Loading news..."):
    news = news_engine.get_clustered_news()

if news:
    for story in news:
        st.markdown(f"### {story['headline']}")

        for src in story["sources"]:
            st.markdown(f"- [{src['source']}]({src['link']})")
            if src["published"]:
                st.caption(f"{src['published']}")

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

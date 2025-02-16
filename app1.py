import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Page Configurations
st.set_page_config(page_title="Startup Funding Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    if not os.path.exists('NoteBook/startup_funding_cleaned.csv'):
        st.error("Dataset not found! Please check the file path.")
        return None
    df = pd.read_csv('NoteBook/startup_funding_cleaned.csv')
    df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    return df

df = load_data()

if df is not None:
    st.sidebar.title("Startup Funding Analysis")
    option = st.sidebar.radio("Select an option:", ["Overall Analysis", "Startup", "Investor"])

    if option == "Overall Analysis":
        st.title("📊 Overall Startup Funding Analysis")
        selected_year = st.sidebar.selectbox("Select Year", sorted(df['year'].dropna().unique(), reverse=True))
        df_filtered = df[df['year'] == selected_year]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Investment", f"₹{df_filtered['amount'].sum():,.0f} Cr")
        col2.metric("Max Funding", f"₹{df_filtered.groupby('startup')['amount'].sum().max():,.0f} Cr")
        col3.metric("Avg Funding", f"₹{df_filtered.groupby('startup')['amount'].sum().mean():,.0f} Cr")
        col4.metric("Total Startups Funded", df_filtered['startup'].nunique())

        # Monthly Trends
        st.subheader("📈 Monthly Funding Trend")
        trend_option = st.radio("Select Trend Type", ["Total Investment", "Number of Investments"], horizontal=True)
        trend_data = df_filtered.groupby('month')['amount'].sum().reset_index() if trend_option == "Total Investment" else df_filtered.groupby('month')['amount'].count().reset_index()
        fig = px.line(trend_data, x='month', y='amount', markers=True, title=f"{trend_option} ({selected_year})", labels={'month': 'Month', 'amount': trend_option})
        st.plotly_chart(fig, use_container_width=True)

        # Sector-wise Investment
        st.subheader("🏢 Top 5 Sectors by Investment")
        sector_data = df_filtered.groupby('vertical')['amount'].sum().nlargest(5)
        fig_sector = px.pie(sector_data, names=sector_data.index, values=sector_data.values, hole=0.4)
        st.plotly_chart(fig_sector, use_container_width=True)

        # City-wise Investment
        st.subheader("🌍 Top 5 Cities by Investment")
        city_data = df_filtered.groupby('city')['amount'].sum().nlargest(5)
        fig_city = px.bar(city_data, x=city_data.index, y=city_data.values, text_auto=True)
        st.plotly_chart(fig_city, use_container_width=True)

    elif option == "Startup":
        startup_list = sorted(df['startup'].dropna().unique())
        selected_startup = st.sidebar.selectbox("🔍 Select a Startup", startup_list)
        btn1 = st.sidebar.button("Show Funding Details")

        if btn1:
            st.title(f"🏢 Funding Details for {selected_startup}")
            startup_data = df[df['startup'] == selected_startup][['date', 'investors', 'round', 'amount']]
            st.dataframe(startup_data, height=300)

    elif option == "Investor":
        investor_list = sorted(set([i.strip() for sublist in df['investors'].dropna().str.split(',') for i in sublist]))
        selected_investor = st.sidebar.selectbox("🔍 Select an Investor", investor_list)
        btn2 = st.sidebar.button("Find Investment Details")

        if btn2:
            st.title(f"💰 Investment Details for {selected_investor}")
            investor_data = df[df['investors'].str.contains(selected_investor, na=False, regex=False)][['date', 'startup', 'amount']]
            st.dataframe(investor_data, height=300)

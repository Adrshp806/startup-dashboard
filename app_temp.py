import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import plotly.express as px
from PIL import Image

# Page Configurations
st.set_page_config(page_title="Startup Funding Analysis", layout="wide", page_icon="💼")

# Load the dataset with a file existence check
DATA_PATH = 'NoteBook/startup_funding_cleaned.csv'
if not os.path.exists(DATA_PATH):
    st.error("Dataset not found! Please check the file path.")
    st.stop()

df = pd.read_csv(DATA_PATH)

# Ensure 'date' column is in datetime format
df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce')
df['year'] = df['date'].dt.year  # Ensure year is an integer
df['month'] = df['date'].dt.month
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')  # Ensure 'amount' is numeric


def overall_analysis():
    st.title("📊 Overall Startup Funding Analysis")
    
    # Year selection filter
    selected_year = st.selectbox('Select Year', sorted(df['year'].dropna().unique(), reverse=True))
    df_filtered = df[df['year'] == selected_year]
    
    # Key metrics
    total_investment = df_filtered['amount'].sum()
    max_funding = df_filtered.groupby('startup')['amount'].sum().max()
    avg_funding = df_filtered.groupby('startup')['amount'].sum().mean()
    num_startup = df_filtered['startup'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Max Funding', f"₹{round(max_funding)} Cr")
    col2.metric('Total Investment', f"₹{round(total_investment)} Cr")
    col3.metric('Average Funding', f"₹{round(avg_funding)} Cr")
    col4.metric('Total Startups Funded', str(num_startup))
    
    # Month-over-Month Graph
    st.subheader("📊 Month-over-Month Investment")
    select_option = st.radio('Select Type', ['Total Investment', 'Count of Investments'], horizontal=True)
    
    temp_df = df_filtered.groupby('month')['amount'].sum().reset_index() if select_option == 'Total Investment' \
        else df_filtered.groupby('month')['amount'].count().reset_index()
    temp_df['Month'] = temp_df['month'].astype(str)
    
    fig = px.line(temp_df, x='Month', y='amount', markers=True,
                  title=f'Month-over-Month {select_option} ({selected_year})',
                  labels={'Month': 'Month', 'amount': select_option},
                  line_shape='spline')
    st.plotly_chart(fig, use_container_width=True)
    
    # Investment Distribution by Sector
    st.subheader("📊 Top 5 Sectors by Investment")
    sector_sum = df_filtered.groupby('vertical')['amount'].sum().nlargest(5)
    fig_sector = px.pie(sector_sum, names=sector_sum.index, values=sector_sum.values,
                         title='Investment by Sector', hole=0.4)
    st.plotly_chart(fig_sector, use_container_width=True)
    
    # Investment Distribution by City
    st.subheader("📈 Top 5 Cities by Investment")
    city_sum = df_filtered.groupby('city')['amount'].sum().nlargest(5)
    fig_city = px.bar(city_sum, x=city_sum.index, y=city_sum.values, text_auto=True,
                       title='Investment by City', labels={'x': 'City', 'y': 'Total Investment'})
    st.plotly_chart(fig_city, use_container_width=True)
    
    # Top Investors
    st.subheader("💰 Top 10 Investors")
    top_investors = df_filtered.groupby('investors')['amount'].sum().nlargest(10).reset_index()
    fig_investors = px.bar(top_investors, x='investors', y='amount', text_auto=True,
                            title='Top Investors', labels={'investors': 'Investors', 'amount': 'Total Investment'})
    st.plotly_chart(fig_investors, use_container_width=True)

def load_investor_details(investor):
    st.title(f"💰 Investment Details for {investor}")

    investor_df = df[df['investors'].str.contains(investor, na=False, regex=False)]
    
    st.subheader("📌 Most Recent Investments")
    st.dataframe(investor_df[['date', 'startup', 'vertical', 'city', 'round', 'amount']].head(), height=200)
    
    st.subheader("💰 Top 5 Biggest Investments")
    biggest_investment = investor_df.groupby('startup')['amount'].sum().nlargest(5)
    fig_big = px.bar(biggest_investment, x=biggest_investment.index, y=biggest_investment.values,
                      title='Top Investments', text_auto=True)
    st.plotly_chart(fig_big, use_container_width=True)
    
    st.subheader("📊 Investment Distribution by Sector")
    sector_distribution = investor_df.groupby('vertical')['amount'].sum().nlargest(5)
    fig_sector = px.pie(sector_distribution, names=sector_distribution.index, values=sector_distribution.values,
                         title='Investment by Sector')
    st.plotly_chart(fig_sector, use_container_width=True)
    
    st.subheader("📈 Year-over-Year Investments")
    yearly_trend = investor_df.groupby('year')['amount'].sum()
    fig_trend = px.line(yearly_trend, x=yearly_trend.index, y=yearly_trend.values,
                         markers=True, title=f'Yearly Investments by {investor}')
    st.plotly_chart(fig_trend, use_container_width=True)

# Sidebar
st.sidebar.title("Startup Funding Analysis")
option = st.sidebar.radio('Select an option:', ['Overall Analysis', 'Startup', 'Investor'])

if option == 'Overall Analysis':
    overall_analysis()
elif option == 'Startup':
    #st.image(startup_image, use_column_width=True)  # Display startup image
    startup_list = sorted(df['startup'].dropna().unique().tolist())
    selected_startup = st.sidebar.selectbox('🔍 Select a Startup', startup_list)
    if st.sidebar.button('Show Funding Details'):
        st.title(f"🏢 Funding Details for {selected_startup}")
        startup_details = df[df['startup'] == selected_startup][['date', 'investors', 'round', 'amount']]
        st.dataframe(startup_details, height=200)
else:
    investor_list = sorted(set([inv.strip() for sublist in df['investors'].dropna().str.split(',') for inv in sublist]))
    investor = st.sidebar.selectbox('🔍 Select an Investor', investor_list)
    if st.sidebar.button('Find Investment Details'):
        load_investor_details(investor)
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import plotly.express as px
# Page Configurations
st.set_page_config(page_title="Startup Funding Analysis")

# Load the dataset with a file existence check
if not os.path.exists('NoteBook/startup_funding_cleaned.csv'):
    st.error("Dataset not found! Please check the file path.")
else:
    df = pd.read_csv('NoteBook/startup_funding_cleaned.csv')

# Ensure 'date' column is in datetime format
#date column need to convert to datetime format
df['date'] = pd.to_datetime(df['date'],format='mixed', errors='coerce')
df['year'] = df['date'].dt.year  # Ensure year is an integer
df['month'] = df['date'].dt.month


df['amount'] = pd.to_numeric(df['amount'], errors='coerce')  # Ensure 'amount' is numeric


# Function for overall analysis
def overall_analysis():
    st.markdown("""
        <style>
            .metric-box {
                background-color: #f4f4f8;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            }
            .main-title {
                font-size: 24px;
                font-weight: bold;
                color: #2E86C1;
                text-align: center;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="main-title">📊 Overall Analysis</p>', unsafe_allow_html=True)
    
    # Year selection filter (applies to all graphs)
    selected_year = st.selectbox('Select Year', sorted(df['year'].unique(), reverse=True))
    df_filtered = df[df['year'] == selected_year]
    
    # Key metrics
    total_investment = round(df_filtered['amount'].sum())
    max_funding = df_filtered.groupby('startup')['amount'].sum().max()
    avg_funding = df_filtered.groupby('startup')['amount'].sum().mean()
    num_startup = df_filtered['startup'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric('Max Funding', f"₹{round(max_funding)} Cr")
    with col2:
        st.metric('Total Investment', f"₹{round(total_investment)} Cr")
    with col3:
        st.metric('Average Funding', f"₹{round(avg_funding)} Cr")
    with col4:
        st.metric('Total Startups Funded', str(num_startup))
    
    # Month-over-Month Graph
    st.markdown('<p class="main-title">📊 MoM Graph</p>', unsafe_allow_html=True)
    select_option = st.radio('Select Type', ['Total Investment', 'Count of Investments'], horizontal=True)
    
    if select_option == 'Total Investment':
        temp_df = df_filtered.groupby('month')['amount'].sum().reset_index()
    else:
        temp_df = df_filtered.groupby('month')['amount'].count().reset_index()
    
    temp_df['Month'] = temp_df['month'].astype(str)
    
    fig = px.line(
        temp_df, x='Month', y='amount', markers=True,
        title=f'Month-over-Month {select_option} ({selected_year})',
        labels={'Month': 'Month', 'amount': select_option},
        line_shape='spline'
    )
    fig.update_layout(xaxis_tickangle=-45, hovermode='x')
    st.plotly_chart(fig, use_container_width=True)
    
    # Investment Distribution by Sector
    st.markdown('<p class="main-title">📊 Investment by Sector</p>', unsafe_allow_html=True)
    sector_sum = df_filtered.groupby('vertical')['amount'].sum().nlargest(5)
    fig_sector = px.pie(
        sector_sum, names=sector_sum.index, values=sector_sum.values, title='Top 5 Sectors by Investment',
        hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_sector, use_container_width=True)
    
    # Investment Distribution by City
    st.markdown('<p class="main-title">📈 Investment by City</p>', unsafe_allow_html=True)
    city_sum = df_filtered.groupby('city')['amount'].sum().nlargest(5)
    fig_city = px.bar(
        city_sum, x=city_sum.index, y=city_sum.values, text_auto=True,
        title='Top 5 Cities by Investment', labels={'x': 'City', 'y': 'Total Investment'},
        color=city_sum.values, color_continuous_scale='blues'
    )
    st.plotly_chart(fig_city, use_container_width=True)
    
    # Funding Heatmap
    st.markdown('<p class="main-title">🔥 Funding Heatmap</p>', unsafe_allow_html=True)
    pivot_df = df_filtered.pivot_table(index='city', columns='month', values='amount', aggfunc='sum', fill_value=0)
    pivot_df = pivot_df.reset_index().melt(id_vars='city', var_name='Month', value_name='Funding Amount')
    
    fig_heatmap = px.density_heatmap(
        pivot_df, x='Month', y='city', z='Funding Amount',
        color_continuous_scale='YlGnBu', title='Investment Heatmap', height=600
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Top Investors
    st.markdown('<p class="main-title">💰 Top Investors</p>', unsafe_allow_html=True)
    top_investors = df_filtered.groupby('investors')['amount'].sum().nlargest(10).reset_index()
    fig_investors = px.bar(
        top_investors, x='investors', y='amount', text_auto=True,
        title='Top 10 Investors', labels={'investors': 'Investors', 'amount': 'Total Investment'},
        color='amount', color_continuous_scale='viridis'
    )
    st.plotly_chart(fig_investors, use_container_width=True)



# Fuction to display investor details
def load_investor_details(investor):
    st.markdown(f'<p class="main-title">Investment Details for {investor}</p>', unsafe_allow_html=True)

    last5_df = df[df['investors'].str.contains(investor, na=False, regex=False)].head()[['date', 'startup', 'vertical', 'city', 'round', 'amount']]
    st.markdown('<p class="section-title">📌 Most Recent Investments</p>', unsafe_allow_html=True)
    st.dataframe(last5_df, height=200, hide_index=True)

    col1, col2 = st.columns(2)

    with col1:
        biggest_investment = df[df['investors'].str.contains(investor, na=False, regex=False)].groupby('startup')['amount'].sum().sort_values(ascending=False).head()
        st.markdown('<p class="section-title">💰 Top 5 Biggest Investments</p>', unsafe_allow_html=True)
        
        fig, ax = plt.subplots(figsize=(6,6))
        sns.barplot(x=biggest_investment.index, y=biggest_investment.values, palette="magma", ax=ax)
        ax.set_xticklabels(biggest_investment.index, rotation=45, ha='right', fontsize=10)
        ax.set_xlabel('Startup', fontsize=12, fontweight='bold', color='#154360')
        ax.set_ylabel('Investment Amount', fontsize=12, fontweight='bold', color='#154360')
        ax.set_title('Top 5 Biggest Investments', fontsize=14, fontweight='bold', color='#154360')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)
    
    with col2:
        vertical_series = df[df['investors'].str.contains(investor, na=False, regex=False)].groupby('vertical')['amount'].sum().sort_values(ascending=False).head()
        st.markdown('<p class="section-title">📊 Investment Distribution by Sector</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(6,6))
        ax.pie(vertical_series, labels=vertical_series.index, autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor': 'black'})
        ax.set_title('Investment by Sector', fontsize=14, fontweight='bold', color='#154360')
        st.pyplot(fig)

    col1, col2 = st.columns(2)
    with col1:
        raised_in_round = df[df['investors'].str.contains(investor)].groupby('round')['amount'].sum().sort_values(ascending=False).head()
        st.markdown('<p class="section-title">📈Total Amount Distribution by Stage</p>', unsafe_allow_html=True)

        fig2, ax = plt.subplots(figsize=(6,6))
        colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F1C40F', '#9B59B6']
        ax.pie(raised_in_round, labels=raised_in_round.index, autopct='%1.1f%%', startangle=140, 
               colors=colors, wedgeprops={'edgecolor': 'black'})

        ax.set_title('Investment by Stages', fontsize=14, fontweight='bold', color='#154360')

        st.pyplot(fig2)
    with col2:
         by_city = df[df['investors'].str.contains(investor)].groupby('city')['amount'].sum().sort_values(ascending=False).head()
         st.markdown('<p class="section-title">📈Total Amount Distribution by city</p>', unsafe_allow_html=True)
         fig3, ax = plt.subplots(figsize=(6,6))
         colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F1C40F', '#9B59B6']
         ax.pie(by_city, labels=by_city.index, autopct='%1.1f%%', startangle=140, 
                colors=colors, wedgeprops={'edgecolor': 'black'})

         ax.set_title('Investment by City', fontsize=14, fontweight='bold', color='#154360')

         st.pyplot(fig3)
    
    
    year_series = df[df['investors'].str.contains(investor, na=False, regex=False)].groupby('year')['amount'].sum()
    st.markdown('<p class="section-title">📈 Year-over-Year Investments</p>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(6,6))
    ax.plot(year_series.index, year_series.values, marker='o', linestyle='-', color='#3498DB')
    ax.set_xlabel('Year')
    ax.set_ylabel('Total Investment Amount')
    ax.set_title(f'Yearly Investments by {investor}')
    ax.grid(True)
    st.pyplot(fig)





#g
# Sidebar
st.sidebar.markdown('<h1 style="color:black;">Startup Funding Analysis</h1>', unsafe_allow_html=True)
option = st.sidebar.radio('Select an option:', ['Overall Analysis', 'StartUp', 'Investor'])

if option == 'Overall Analysis':
   overall_analysis()
elif option == 'StartUp':
    startup_list = sorted(df['startup'].dropna().unique().tolist())
    selected_startup = st.sidebar.selectbox('🔍 Select a StartUp', startup_list)
    btn1 = st.sidebar.button('Show Funding Details')
    
    if btn1:
        st.markdown(f'<p class="main-title">🏢 Funding Details for {selected_startup}</p>', unsafe_allow_html=True)
        startup_details = df[df['startup'] == selected_startup][['date', 'investors', 'round', 'amount']]
        st.dataframe(startup_details, height=200, hide_index=True)
else:
    investor_list = sorted(set([inv.strip() for sublist in df['investors'].dropna().str.split(',') for inv in sublist]))
    investor = st.sidebar.selectbox('🔍 Select an Investor', investor_list)
    btn2 = st.sidebar.button('Find Investment Details')
    
    if btn2:
        load_investor_details(investor)
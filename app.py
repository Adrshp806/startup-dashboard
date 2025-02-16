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


# Function to overall analyiss

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
    
    Total = round(df['amount'].sum())
    max_funding = df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(1).values[0]
    avg_funding = df.groupby('startup')['amount'].sum().mean()
    num_startup = df['startup'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric('Max Funding', f"₹{round(max_funding)} Cr")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric('Total Investment', f"₹{round(Total)}Cr")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric('Average Funding', f"₹{round(avg_funding)} Cr")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric('Total Startups Funded', str(num_startup))
        st.markdown('</div>', unsafe_allow_html=True)


    # Title
    st.markdown('<p class="main-title">📊 MoM Graph</p>', unsafe_allow_html=True)

    # Year selection dropdown
    selected_year = st.selectbox('Select Year', sorted(df['year'].unique(), reverse=True))

    # Type selection dropdown (Total vs. Count)
    select_option = st.selectbox('Select Type', ['Total', 'Count'])

    # Filter data by selected year
    df_filtered = df[df['year'] == selected_year]

    # Group data based on user selection
    if select_option == 'Total':
        temp_df = df_filtered.groupby(['month', 'year'])['amount'].sum().reset_index()
    else:
        temp_df = df_filtered.groupby(['month', 'year'])['amount'].count().reset_index()

    # Create 'x_axis' column (Month-Year format)
    temp_df['x_axis'] = temp_df['month'].astype(str) + '-' + temp_df['year'].astype(str)

    # Plot with Plotly
    fig = px.line(
        temp_df, 
        x='x_axis', 
        y='amount', 
        markers=True, 
        title=f'Month-over-Month Investment ({selected_year})',
        labels={'x_axis': 'Month-Year', 'amount': 'Total Investment'},
        line_shape='spline'
    )

    # Improve layout
    fig.update_layout(
        xaxis_tickangle=-45,
        xaxis_title='Month-Year',
        yaxis_title='Total Investment',
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x'
    )

    # Show plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    
    
    sector_sum = df.groupby('vertical')['amount'].sum().sort_values(ascending=False).head(5)
    st.markdown('<p class="section-title">📊 Investment Distribution by Sector</p>', unsafe_allow_html=True)
    fig7, ax7 = plt.subplots(figsize=(6,6))
    ax7.pie(sector_sum, labels=sector_sum.index, autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor': 'black'})
    ax7.set_title('Investment by Sector', fontsize=14, fontweight='bold', color='#154360')
    st.pyplot(fig7)

    by_city = df.groupby('city')['amount'].sum().sort_values(ascending=False).head()
    st.markdown('<p class="section-title">📈Total Amount Distribution by city</p>', unsafe_allow_html=True)
    fig8, ax8 = plt.subplots(figsize=(6,6))
    colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F1C40F', '#9B59B6']
    ax8.pie(by_city, labels=by_city.index, autopct='%1.1f%%', startangle=140, 
            colors=colors, wedgeprops={'edgecolor': 'black'})

    ax8.set_title('Investment by City', fontsize=14, fontweight='bold', color='#154360')

    st.pyplot(fig8)

    # Title
    st.markdown('<p class="section-title">🔥 Funding Heatmap</p>', unsafe_allow_html=True)

    # Year selection slider (optional, assuming you have a 'year' column)
    selected_year = st.slider('Select Year', min_value=df['year'].min(), max_value=df['year'].max(), value=df['year'].max())

    # Filter data by selected year
    filtered_df = df[df['year'] == selected_year]

    # Create pivot table
    pivot_df = filtered_df.pivot_table(index='city', columns='month', values='amount', aggfunc='sum', fill_value=0)

    # Reset index for Plotly
    pivot_df = pivot_df.reset_index().melt(id_vars='city', var_name='Month', value_name='Funding Amount')

    # Plot interactive heatmap
    fig = px.density_heatmap(
        pivot_df, x='Month', y='city', z='Funding Amount', 
        color_continuous_scale='YlGnBu', 
        title=f'Funding Heatmap ({selected_year})', 
        labels={'city': 'City', 'Month': 'Month', 'Funding Amount': 'Total Investment'},
        height=600
    )

    # Improve layout
    fig.update_layout(
        xaxis_tickangle=-45,
        margin=dict(l=50, r=50, t=50, b=50)
    )

    # Display plot
    st.plotly_chart(fig, use_container_width=True)

        # 📈 Top Investors Bar Chart
    st.markdown('<p class="section-title">�� Top Investors</p>', unsafe_allow_html=True)
    # Year selection slider (optional, assuming you have a 'year' column)
    selected_years = st.slider('Select Years', min_value=df['year'].min(), max_value=df['year'].max(), value=df['year'].max())

    # Filter data by selected year
    filtered_df = df[df['year'] == selected_years]
    top_investors = filtered_df.groupby('investors')['amount'].sum().sort_values(ascending=False).head(10).reset_index()

    fig_investors = px.bar(
        top_investors,
        x='investors',
        y='amount',
        title=f'Top Investors in {selected_years}',
        labels={'investors': 'Investors', 'amount': 'Total Investment'},
        color='amount',
        text_auto=True
    )

    fig_investors.update_layout(
        xaxis_tickangle=-45,
        xaxis_title='Investor',
        yaxis_title='Total Investment',
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x'
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
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Page Configurations
st.set_page_config(page_title="Startup Funding Analysis")

# Load the dataset
df = pd.read_csv('NoteBook/startup_funding_cleaned.csv')

# Custom Styling
st.markdown("""
    <style>
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #2E4053;
            padding: 20px;
        }
        [data-testid="stSidebar"] h1 {
            color: white;
        }
        /* Page Title */
        .main-title {
            font-size: 32px;
            font-weight: bold;
            color: #1A5276;
            text-align: center;
        }
        /* Section Headers */
        .section-title {
            font-size: 22px;
            font-weight: bold;
            color: #2471A3;
            margin-top: 20px;
        }
        /* Border around sections */
        .styled-container {
            border: 2px solid #3498DB;
            padding: 20px;
            border-radius: 10px;
            background-color: #F8F9F9;
            box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Function to display investor details
def load_investor_details(investor):
    st.markdown(f'<p class="main-title">Investment Details for {investor}</p>', unsafe_allow_html=True)

    # Recent Investments
    last5_df = df[df['investors'].str.contains(investor)].head()[['date', 'startup', 'vertical', 'city', 'round', 'amount']]
    st.markdown('<p class="section-title">📌 Most Recent Investments</p>', unsafe_allow_html=True)
    st.dataframe(last5_df, height=200, hide_index=True)

    col1, col2 = st.columns(2)

    with col1:
        biggest_investment = df[df['investors'].str.contains(investor)].groupby('startup')['amount'].sum().sort_values(ascending=False).head()

        st.markdown('<p class="section-title">💰 Top 5 Biggest Investments</p>', unsafe_allow_html=True)

        # Create figure for bar chart
        fig, ax = plt.subplots(figsize=(6,6))
        sns.barplot(x=biggest_investment.index, y=biggest_investment.values, palette="magma", ax=ax)

        ax.set_xlabel('Startup', fontsize=12, fontweight='bold', color='#154360')
        ax.set_ylabel('Investment Amount', fontsize=12, fontweight='bold', color='#154360')
        ax.set_title('Top 5 Biggest Investments', fontsize=14, fontweight='bold', color='#154360')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        st.pyplot(fig)

    with col2:
        vertical_series = df[df['investors'].str.contains(investor)].groupby('vertical')['amount'].sum().sort_values(ascending=False).head()

        st.markdown('<p class="section-title">📊 Investment Distribution by Sector</p>', unsafe_allow_html=True)

        fig, ax = plt.subplots(figsize=(6,6))
        colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F1C40F', '#9B59B6']
        ax.pie(vertical_series, labels=vertical_series.index, autopct='%1.1f%%', startangle=140, 
               colors=colors, wedgeprops={'edgecolor': 'black'})

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
    
    # Ensure 'date' column is in datetime format
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['year'] = df['date'].dt.year

# Ensure 'amount' column is numeric
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

# Filter investments by the selected investor
filtered_df = df[df['investors'].str.contains(selected_investor, na=False)]

if not filtered_df.empty:
    year_series = filtered_df.groupby('year')['amount'].sum()
    
    st.markdown('<p class="section-title">📈 Year-over-Year Investments</p>', unsafe_allow_html=True)
    
    fig4, ax2 = plt.subplots(figsize=(6,6))
    ax2.plot(year_series.index, year_series.values, marker='o', linestyle='-', color='#3498DB')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Total Investment Amount')
    ax2.set_title(f'Yearly Investments by {selected_investor}')
    ax2.grid(True)

    st.pyplot(fig4)
else:
    st.warning(f"No investment data available for {selected_investor}.")





# Sidebar
st.sidebar.markdown('<h1 style="color:white;">Startup Funding Analysis</h1>', unsafe_allow_html=True)

option = st.sidebar.radio('Select an option:', ['Overall Analysis', 'StartUp', 'Investor'])

if option == 'Overall Analysis':
    st.markdown('<p class="main-title">📊 Overall Analysis</p>', unsafe_allow_html=True)

elif option == 'StartUp':
    startup_list = sorted(df['startup'].unique().tolist())
    selected_startup = st.sidebar.selectbox('🔍 Select a StartUp', startup_list)
    btn1 = st.sidebar.button('Show Funding Details')

    if btn1:
        st.markdown(f'<p class="main-title">🏢 Funding Details for {selected_startup}</p>', unsafe_allow_html=True)
        startup_details = df[df['startup'] == selected_startup][['date', 'investors', 'round', 'amount']]
        st.dataframe(startup_details, height=200, hide_index=True)

else:
    investor_list = sorted(set([inv.strip() for sublist in df['investors'].dropna().str.split(',') for inv in sublist]))
    selected_investor = st.sidebar.selectbox('🔍 Select an Investor', investor_list)
    btn2 = st.sidebar.button('Find Investment Details')

    if btn2:
        load_investor_details(selected_investor)

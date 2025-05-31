import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import pymysql
from datetime import datetime
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

# Page config
st.set_page_config(
    page_title="Walmart Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title('📊 Walmart Sales Analytics Dashboard')
st.markdown("""
    This dashboard provides comprehensive analysis of Walmart sales data, including:
    - Sales trends and patterns
    - Product performance metrics
    - Customer behavior insights
    - Interactive visualizations
""")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Data Overview", "Sales Analysis", "Product Analysis", "Customer Insights"])

# File uploader in sidebar
st.sidebar.title("Data Upload")
uploaded_file = st.sidebar.file_uploader('Upload Walmart Sales CSV', type=['csv'])

# Data loading and cleaning function
@st.cache_data
def load_and_clean_data(file):
    """Load and clean the uploaded data."""
    try:
        # Read CSV first without date parsing
        df = pd.read_csv(file)
        
        # Convert column names to lowercase
        df.columns = df.columns.str.lower()
        
        # Now parse dates if date column exists
        if 'date' in df.columns:
            # Try to infer the date format first
            try:
                df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y')
            except ValueError:
                # If the format is different, let pandas try to parse it
                df['date'] = pd.to_datetime(df['date'])
        
        # Drop duplicates
        df.drop_duplicates(inplace=True)
        
        # Drop missing values
        df.dropna(inplace=True)
        
        # Convert numeric columns and ensure they are float64
        numeric_columns = ['unit_price', 'quantity', 'total', 'cogs', 'gross_margin_percentage', 'gross_income', 'rating']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('float64')
        
        # Calculate total if not present
        if 'total' not in df.columns and 'unit_price' in df.columns and 'quantity' in df.columns:
            df['total'] = (df['unit_price'] * df['quantity']).astype('float64')
        
        # Ensure time column is string
        if 'time' in df.columns:
            df['time'] = df['time'].astype(str)
        
        # Convert to Arrow table for better serialization
        # First ensure all object columns are strings
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str)
            
        # Convert to Arrow table
        table = pa.Table.from_pandas(df)
        return table.to_pandas()
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None

# Load data if file is uploaded
if uploaded_file:
    st.session_state.df = load_and_clean_data(uploaded_file)
    df = st.session_state.df

    if df is not None:
        # Show available columns
        with st.expander('Show available columns in uploaded data'):
            st.write(list(df.columns))

        if page == "Data Overview":
            st.header("📈 Data Overview")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Sales", f"${df['total'].sum():,.2f}" if 'total' in df.columns else 'N/A')
            with col2:
                st.metric("Total Transactions", f"{len(df):,}")
            with col3:
                st.metric("Average Order Value", f"${df['total'].mean():,.2f}" if 'total' in df.columns else 'N/A')
            with col4:
                if 'product_line' in df.columns:
                    st.metric("Unique Products", f"{df['product_line'].nunique():,}")
                else:
                    st.warning("'product_line' column not found.")

            # Data preview
            st.subheader("Data Preview")
            st.dataframe(df.head(), use_container_width=True)

            # Data quality metrics
            st.subheader("Data Quality Metrics")
            col1, col2 = st.columns(2)
            with col1:
                st.write("Missing Values:")
                st.write(df.isnull().sum())
            with col2:
                st.write("Data Types:")
                st.write(df.dtypes)

        elif page == "Sales Analysis":
            st.header("💰 Sales Analysis")
            
            # Date range selector if date column exists
            if 'date' in df.columns:
                min_date = df['date'].min()
                max_date = df['date'].max()
                date_range = st.date_input("Select Date Range", [min_date, max_date])
                
                # Filter data based on date range
                mask = (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])
                df_filtered = df[mask]
            else:
                st.warning("No date column found in data.")
                df_filtered = df

            # Sales over time
            if 'date' in df.columns and 'total' in df.columns:
                st.subheader("Sales Trend Over Time")
                daily_sales = df_filtered.groupby('date')['total'].sum().reset_index()
                fig = px.line(daily_sales, x='date', y='total', 
                             title='Daily Sales Trend',
                             labels={'total': 'Total Sales ($)', 'date': 'Date'})
                st.plotly_chart(fig, use_container_width=True)

            # Sales by category
            if 'product_line' in df.columns and 'total' in df.columns:
                st.subheader("Sales by Product Category")
                category_sales = df_filtered.groupby('product_line')['total'].sum().sort_values(ascending=False)
                fig = px.bar(category_sales, 
                            title='Total Sales by Product Category',
                            labels={'total': 'Total Sales ($)', 'product_line': 'Product Category'})
                st.plotly_chart(fig, use_container_width=True)
            elif 'product_line' not in df.columns:
                st.info("'product_line' column not found. Upload a file with this column for category analysis.")

        elif page == "Product Analysis":
            st.header("📦 Product Analysis")
            
            # Product performance metrics
            if all(col in df.columns for col in ['product_line', 'total', 'quantity', 'unit_price']):
                st.subheader("Product Performance Metrics")
                
                # Top selling products
                top_products = df.groupby('product_line').agg({
                    'total': 'sum',
                    'quantity': 'sum',
                    'unit_price': 'mean'
                }).sort_values('total', ascending=False)
                
                fig = px.scatter(top_products, 
                               x='quantity', 
                               y='total',
                               size='unit_price',
                               hover_data=['unit_price'],
                               title='Product Performance: Quantity vs Total Sales',
                               labels={'quantity': 'Total Quantity Sold', 
                                     'total': 'Total Sales ($)',
                                     'unit_price': 'Average Unit Price'})
                st.plotly_chart(fig, use_container_width=True)

                # Product category analysis
                st.subheader("Product Category Analysis")
                category_metrics = df.groupby('product_line').agg({
                    'total': ['sum', 'mean', 'count'],
                    'quantity': ['sum', 'mean'],
                    'unit_price': ['mean', 'std']
                }).round(2)
                st.dataframe(category_metrics, use_container_width=True)
            else:
                st.info("Required columns for product analysis not found. Please upload a file with 'product_line', 'total', 'quantity', and 'unit_price'.")

        elif page == "Customer Insights":
            st.header("👥 Customer Insights")
            
            if all(col in df.columns for col in ['customer_type', 'total', 'quantity']):
                # Customer type analysis
                st.subheader("Customer Type Analysis")
                customer_metrics = df.groupby('customer_type').agg({
                    'total': ['sum', 'mean', 'count'],
                    'quantity': ['sum', 'mean']
                }).round(2)
                st.dataframe(customer_metrics, use_container_width=True)

                # Customer type visualization
                fig = px.pie(df, 
                            names='customer_type', 
                            values='total',
                            title='Sales Distribution by Customer Type')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("'customer_type', 'total', or 'quantity' column not found. Please upload a file with these columns.")

            # Payment method analysis if available
            if 'payment' in df.columns and 'total' in df.columns:
                st.subheader("Payment Method Analysis")
                payment_metrics = df.groupby('payment').agg({
                    'total': ['sum', 'mean', 'count']
                }).round(2)
                st.dataframe(payment_metrics, use_container_width=True)
            elif 'payment' not in df.columns:
                st.info("'payment' column not found. Please upload a file with this column for payment analysis.")

            # Save data option
            if st.sidebar.button('Save Cleaned Data'):
                try:
                    df.to_csv('Walmart_clean_data.csv', index=False)
                    st.sidebar.success('Cleaned data saved as Walmart_clean_data.csv')
                except Exception as e:
                    st.sidebar.error(f'Error saving data: {str(e)}')

            # Database upload option
            st.sidebar.title("Database Upload")
            if st.sidebar.checkbox('Upload to Database'):
                with st.sidebar.form("database_upload"):
                    user = st.text_input('MySQL User', 'root')
                    password = st.text_input('MySQL Password', '', type='password')
                    host = st.text_input('MySQL Host', 'localhost')
                    port = st.text_input('MySQL Port', '3306')
                    db = st.text_input('Database Name', 'walmart_db')
                    submit = st.form_submit_button('Upload to Database')
                    
                    if submit:
                        try:
                            engine_str = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
                            df.to_sql(name='walmart_sales', con=create_engine(engine_str), if_exists='replace', index=False)
                            st.sidebar.success('Data uploaded to database successfully!')
                        except Exception as e:
                            st.sidebar.error(f'Error: {str(e)}')

else:
    st.info('👆 Please upload a CSV file to begin analysis') 
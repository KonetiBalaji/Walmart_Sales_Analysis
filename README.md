
🛒 Walmart Sales Analysis Project




🔧 1. Environment Setup
Tools Used: Visual Studio Code (VS Code), Python 3.8+, MySQL, PostgreSQL
Goal: Establish a clean and structured project workspace in VS Code for efficient development, data processing, and version control.



🔐 2. Kaggle API Integration

Downloaded kaggle.json API key from Kaggle profile settings.
Configured local environment by placing the key in the .kaggle/ directory.
Used:
bash
Copy
Edit
kaggle datasets download -d <dataset-path>
to download Walmart sales data.



📥 3. Dataset Acquisition

Source: Walmart Sales Dataset from Kaggle.
Storage: Saved to a dedicated data/ folder within the project.
📦 4. Install Libraries & Load Data
Installed required Python libraries using:
bash
Copy
Edit
pip install pandas numpy sqlalchemy mysql-connector-python psycopg2
Loaded data into Pandas DataFrame for processing.


🔍 5. Exploratory Data Analysis

Used .info(), .head(), and .describe() to understand structure and content.
Identified column types, null values, and data ranges.


🧹 6. Data Cleaning

Removed duplicate entries.
Handled missing values and fixed inconsistent data types.
Cleaned and formatted currency fields.
Ensured data integrity for further analysis.

✨ 7. Feature Engineering

Created a new column: total_amount = unit_price * quantity
Enhanced dataset usability for SQL queries and reporting.

🗃️ 8. Data Loading into SQL Databases

SQLAlchemy used to connect and load data into both:
MySQL
PostgreSQL
Created tables and inserted cleaned data.
Verified data load via test queries.

🧠 9. Business Analysis via SQL

Performed analytical queries to solve business questions, including:

Revenue trends across branches and product categories.
Best-selling products and top-performing cities.
Payment method preferences and seasonal trends.
Profit margin breakdowns by branch.


📊 10. Dashboard & Visualizations
Created dashboards to visualize SQL query results using various chart types:

Revenue Breakdown by Branch → Bar Chart
Sales Over Time → Line Graph
Top Product Categories → Horizontal Bar Chart
Payment Method Popularity → Pie Chart
Monthly Profit Margins → Area Chart
✅ The dashboard was designed to deliver quick business insights and can be extended into tools like Power BI, Tableau, or even web dashboards.

📁 Project Structure
graphql
Copy
Edit

```
walmart-sales-project/
│
├── data/                # Raw and cleaned datasets
├── sql_queries/         # SQL scripts for analysis
├── notebooks/           # Jupyter notebooks for Python-based analysis
├── dashboards/          # Visualizations based on SQL outputs
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies
└── main.py              # Script for loading, cleaning, and processing

```





✅ Results & Insights

Top Branch: Branch C consistently outperformed in revenue.
Preferred Payment: Most customers chose Electronic Wallets.
Category Leader: Food and beverages topped the sales chart.
Customer Behavior: Ratings were higher for evening shoppers, and weekends saw the most activity.



🔮 Future Enhancements

Real-time data ingestion and visualization via dashboards.
Integration with Power BI or Tableau.
Merge with other retail datasets to build a more complete retail analytics platform.

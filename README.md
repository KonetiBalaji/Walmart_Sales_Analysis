# 📊 Walmart Sales Analytics Dashboard

A comprehensive data analytics dashboard for Walmart sales data, built with Streamlit. This project provides interactive visualizations, business insights, and data analysis capabilities for Walmart sales data.

## 🌟 Features

- **Interactive Dashboard**: User-friendly interface with multiple analysis pages
- **Data Analysis**:
  - Sales trends and patterns
  - Product performance metrics
  - Customer behavior insights
  - Payment method analysis
- **Visualizations**:
  - Interactive charts and graphs
  - Customizable date ranges
  - Product category analysis
  - Customer segmentation
- **Data Management**:
  - CSV file upload
  - Data cleaning and preprocessing
  - Database integration (MySQL)
  - Export capabilities

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/walmart-sales-analytics.git
   cd walmart-sales-analytics
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:8501
   ```

## 📋 Project Structure

```
walmart-sales-analytics/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
├── Walmart.csv        # Sample data file
└── Walmart_clean_data.csv  # Processed data file
```

## 🛠️ Technologies Used

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **SQLAlchemy**: Database integration
- **PyMySQL**: MySQL database connector

## 📊 Dashboard Pages

1. **Data Overview**
   - Key metrics
   - Data preview
   - Data quality metrics

2. **Sales Analysis**
   - Sales trends over time
   - Category-wise sales
   - Date range selection

3. **Product Analysis**
   - Product performance metrics
   - Category analysis
   - Price-quantity relationships

4. **Customer Insights**
   - Customer type analysis
   - Payment method analysis
   - Customer segmentation

## 💾 Data Management

### Data Upload
- Upload CSV files through the web interface
- Automatic data cleaning and preprocessing
- Data validation and error handling

### Database Integration
- Optional MySQL database connection
- Secure credential management
- Data export capabilities

## 🔒 Security

- Secure database connections
- Password protection for database access
- Data validation and sanitization

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Walmart for the sample dataset
- Streamlit team for the amazing framework
- Open source community for various libraries and tools

## 📞 Support

For support, email your.email@example.com or open an issue in the repository.

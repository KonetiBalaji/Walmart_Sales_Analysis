# Walmart Sales Analytics Dashboard

A comprehensive, industry-grade analytics dashboard for Walmart sales data analysis, built with Streamlit and modern Python practices.

## 🚀 Features

- **Interactive Dashboard**: Real-time data visualization and analysis
- **Data Processing**: Automated data cleaning, validation, and transformation
- **Advanced Analytics**: Sales trends, product performance, and customer insights
- **Database Integration**: Secure MySQL database integration
- **Export Capabilities**: Export reports in multiple formats (CSV, Excel, PDF)
- **Security**: Secure authentication and data handling
- **Monitoring**: Built-in logging and performance monitoring
- **Scalability**: Designed for handling large datasets efficiently

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Database**: MySQL, SQLAlchemy
- **Validation**: Pydantic, Great Expectations
- **Security**: Python-Jose, bcrypt
- **Monitoring**: Loguru, Prometheus
- **Testing**: Pytest
- **Code Quality**: Black, Flake8, MyPy

## 📋 Prerequisites

- Python 3.9+
- MySQL Server
- Redis (for caching)
- Git

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/walmart-sales-analytics.git
   cd walmart-sales-analytics
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   # For development
   pip install -r requirements/dev.txt

   # For production
   pip install -r requirements/prod.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```bash
   python scripts/init_db.py
   ```

## 🏃‍♂️ Running the Application

### Development
   ```bash
   streamlit run app/main.py
   ```

### Production
   ```bash
   gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000
   ```

## 📊 Dashboard Pages

1. **Data Overview**
   - Key metrics and KPIs
   - Data quality metrics
   - Data preview

2. **Sales Analysis**
   - Sales trends over time
   - Category-wise sales
   - Regional analysis

3. **Product Analysis**
   - Product performance metrics
   - Category analysis
   - Price analysis

4. **Customer Insights**
   - Customer type analysis
   - Payment method analysis
   - Customer behavior patterns

## 🧪 Testing

Run tests with pytest:
   ```bash
   pytest tests/
   ```

Run with coverage:
   ```bash
   pytest --cov=app tests/
   ```

## 📝 Code Quality

- Format code:
   ```bash
   black .
   isort .
   ```

- Lint code:
   ```bash
   flake8
   mypy .
   ```

## 📚 Documentation

Generate documentation:
   ```bash
   mkdocs serve
   ```

## 🔒 Security

- All database credentials are stored in environment variables
- Input validation using Pydantic
- Secure password hashing with bcrypt
- JWT-based authentication
- Rate limiting on API endpoints

## 📈 Monitoring

- Application logs in `logs/`
- Prometheus metrics available at `/metrics`
- Sentry integration for error tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



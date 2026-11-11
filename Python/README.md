# E-Commerce Order Management & Database Analytics System

## Project Overview
A database-driven E-Commerce Analytics project built using Microsoft SQL Server, Python and Flask.

The project manages e-commerce data and generates business insights through SQL queries, Python reports and an interactive web dashboard.

## Technologies Used
- Microsoft SQL Server
- Python
- Flask
- pyodbc
- Pandas
- HTML and CSS
- JavaScript
- Chart.js
- Excel

## Database Features
- 11 relational database tables
- Primary keys and foreign key relationships
- Sample data generation using Python and Faker
- Stored procedures for business reports
- Triggers for audit logging
- Indexing and query performance analysis

## Analytics Features
- Monthly revenue analysis
- Top-selling products
- Top customers by revenue
- Category-wise revenue
- Low-stock analysis
- Returns analysis
- Monthly sales visualization

## Web Dashboard Features
- Total revenue
- Total orders
- Total customers
- Total products
- Monthly revenue chart
- Category-wise revenue chart
- Top 10 best-selling products
- Recent orders
- Date-range filtering
- Reset date filter
- Excel export containing order details

## Project Structure

```text
eCommerce-Database-main/
│
├── Database/
│   ├── database.sql
│   ├── 04_Revenue_Analysis.sql
│   ├── 05_Stored_Procedures.sql
│   ├── 06_Triggers_Audit.sql
│   └── Performance_Tuning.sql
│
├── Python/
│   ├── templates/
│   │   └── dashboard.html
│   ├── static/
│   ├── analytics_dashboard.py
│   ├── business_analysis.py
│   ├── generate_data.py
│   ├── generate_orders.py
│   └── sqlserver_connect.py
│
└── README.md
```

## How to Run

1. Install Python.
2. Install Microsoft SQL Server and configure the database.
3. Install the required Python packages:

```bash
python -m pip install flask pyodbc pandas openpyxl
```

4. Update the SQL Server connection settings in the Python files.
5. Run the Flask dashboard:

```bash
cd Python
python analytics_dashboard.py
```

6. Open this address in your browser:

```text
http://127.0.0.1:5000
```

## Project Objective

To demonstrate practical skills in relational database design, SQL querying, Python database integration, business analytics, data visualization and web application development.

## Data Note
The project uses generated sample e-commerce data for demonstration and learning purposes.

from flask import Flask, render_template, request, send_file
import pyodbc
import pandas as pd
from io import BytesIO

app = Flask(__name__)


# =====================================
# DATABASE CONNECTION
# =====================================

def get_connection():
    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=EcommerceDB;"
        "Trusted_Connection=yes;"
        "Connection Timeout=30;"
    )
    return pyodbc.connect(connection_string, timeout=30)


# =====================================
# DASHBOARD
# =====================================

@app.route("/")
def dashboard():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Build a parameterized date filter.
    # The selected end date is inclusive.
    date_filter = ""
    date_params = []

    if start_date:
        date_filter += " AND o.OrderDate >= ?"
        date_params.append(start_date)

    if end_date:
        date_filter += " AND o.OrderDate < DATEADD(day, 1, ?)"
        date_params.append(end_date)

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # 1. TOTAL REVENUE
        cursor.execute(
            """
            SELECT COALESCE(SUM(oi.Quantity * oi.UnitPrice), 0)
            FROM dbo.Orders o
            JOIN dbo.OrderItems oi
                ON o.OrderID = oi.OrderID
            WHERE EXISTS (
                SELECT 1
                FROM dbo.Payments p
                WHERE p.OrderID = o.OrderID
                  AND p.PaymentStatus = 'Successful'
            )
            """ + date_filter,
            date_params
        )
        total_revenue = float(cursor.fetchone()[0])

        # 2. TOTAL ORDERS
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.Orders o
            WHERE 1 = 1
            """ + date_filter,
            date_params
        )
        total_orders = cursor.fetchone()[0]

        # 3. TOTAL CUSTOMERS (overall count)
        cursor.execute("SELECT COUNT(*) FROM dbo.Customers")
        total_customers = cursor.fetchone()[0]

        # 4. TOTAL PRODUCTS (overall count)
        cursor.execute("SELECT COUNT(*) FROM dbo.Products")
        total_products = cursor.fetchone()[0]

        # 5. TOP 10 BEST-SELLING PRODUCTS
        cursor.execute(
            """
            SELECT TOP 10
                p.ProductName,
                SUM(oi.Quantity) AS TotalQuantity
            FROM dbo.Products p
            JOIN dbo.OrderItems oi
                ON p.ProductID = oi.ProductID
            JOIN dbo.Orders o
                ON oi.OrderID = o.OrderID
            WHERE 1 = 1
            """ + date_filter + """
            GROUP BY p.ProductName
            ORDER BY TotalQuantity DESC
            """,
            date_params
        )
        top_products = cursor.fetchall()

        product_names = [row[0] for row in top_products]
        product_quantities = [int(row[1]) for row in top_products]

        # 6. MONTHLY REVENUE
        cursor.execute(
            """
            SELECT
                YEAR(o.OrderDate),
                MONTH(o.OrderDate),
                SUM(oi.Quantity * oi.UnitPrice)
            FROM dbo.Orders o
            JOIN dbo.OrderItems oi
                ON o.OrderID = oi.OrderID
            WHERE EXISTS (
                SELECT 1
                FROM dbo.Payments p
                WHERE p.OrderID = o.OrderID
                  AND p.PaymentStatus = 'Successful'
            )
            """ + date_filter + """
            GROUP BY YEAR(o.OrderDate), MONTH(o.OrderDate)
            ORDER BY YEAR(o.OrderDate), MONTH(o.OrderDate)
            """,
            date_params
        )
        monthly_data = cursor.fetchall()

        months = [
            f"{row[0]}-{row[1]:02d}"
            for row in monthly_data
        ]
        monthly_revenue = [float(row[2]) for row in monthly_data]

        # 7. CATEGORY-WISE REVENUE
        cursor.execute(
            """
            SELECT
                c.CategoryName,
                SUM(oi.Quantity * oi.UnitPrice)
            FROM dbo.Categories c
            JOIN dbo.Products p
                ON c.CategoryID = p.CategoryID
            JOIN dbo.OrderItems oi
                ON p.ProductID = oi.ProductID
            JOIN dbo.Orders o
                ON oi.OrderID = o.OrderID
            WHERE EXISTS (
                SELECT 1
                FROM dbo.Payments pay
                WHERE pay.OrderID = o.OrderID
                  AND pay.PaymentStatus = 'Successful'
            )
            """ + date_filter + """
            GROUP BY c.CategoryName
            ORDER BY SUM(oi.Quantity * oi.UnitPrice) DESC
            """,
            date_params
        )
        category_data = cursor.fetchall()

        category_names = [row[0] for row in category_data]
        category_revenue = [float(row[1]) for row in category_data]

        # 8. RECENT ORDERS
        recent_orders_query = """
            SELECT TOP 10
                o.OrderID,
                c.FirstName + ' ' + c.LastName AS CustomerName,
                o.OrderDate,
                o.OrderStatus
            FROM dbo.Orders o
            JOIN dbo.Customers c
                ON o.CustomerID = c.CustomerID
            WHERE 1 = 1
        """ + date_filter + """
            ORDER BY o.OrderDate DESC
        """

        cursor.execute(recent_orders_query, date_params)
        recent_orders = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        "dashboard.html",
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_customers=total_customers,
        total_products=total_products,
        product_names=product_names,
        product_quantities=product_quantities,
        months=months,
        monthly_revenue=monthly_revenue,
        category_names=category_names,
        category_revenue=category_revenue,
        recent_orders=recent_orders
    )


# ==========================================
# EXCEL REPORT DOWNLOAD
# ==========================================

@app.route("/export_excel")
def export_excel():

    connection = get_connection()

    query = """
    SELECT
        o.OrderID,
        c.FirstName + ' ' + c.LastName AS CustomerName,
        o.OrderDate,
        o.OrderStatus
    FROM dbo.Orders o
    JOIN dbo.Customers c
        ON o.CustomerID = c.CustomerID
    ORDER BY o.OrderDate DESC;
    """

    df = pd.read_sql(query, connection)

    connection.close()

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Orders")

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Ecommerce_Orders_Report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# =====================================
# START APPLICATION
# =====================================

if __name__ == "__main__":
    app.run(debug=True)


import pyodbc
import pandas as pd

# Connect to SQL Server
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=EcommerceDB;"
    "Trusted_Connection=yes;"
)

connection = pyodbc.connect(connection_string)
reports = {}

print("Database connected successfully!")

# Retrieve monthly revenue
query = """
SELECT
    YEAR(o.OrderDate) AS OrderYear,
    MONTH(o.OrderDate) AS OrderMonth,
    SUM(oi.Quantity * oi.UnitPrice) AS TotalRevenue
FROM Orders o
INNER JOIN OrderItems oi
    ON o.OrderID = oi.OrderID
WHERE EXISTS (
    SELECT 1
    FROM Payments p
    WHERE p.OrderID = o.OrderID
      AND p.PaymentStatus = 'Successful'
)
GROUP BY YEAR(o.OrderDate), MONTH(o.OrderDate)
ORDER BY OrderYear, OrderMonth;
"""

df = pd.read_sql(query, connection)
reports["Monthly Revenue"] = df.copy()
print("\nMonthly Revenue Report:")
print(df)
# Top 10 Best-Selling Products

query = """
SELECT TOP 10
    p.ProductID,
    p.ProductName,
    SUM(oi.Quantity) AS TotalQuantitySold,
    SUM(oi.Quantity * oi.UnitPrice) AS TotalSales
FROM dbo.OrderItems oi
JOIN dbo.Products p
    ON oi.ProductID = p.ProductID
JOIN dbo.Orders o
    ON oi.OrderID = o.OrderID
WHERE o.OrderStatus <> 'Cancelled'
GROUP BY p.ProductID, p.ProductName
ORDER BY TotalQuantitySold DESC;
"""

df = pd.read_sql(query, connection)
reports["Best Products"] = df.copy()
print("\nTop 10 Best-Selling Products:")
print(df.to_string(index=False))
# Top 10 Customers by Revenue

query = """
SELECT TOP 10
    c.CustomerID,
    c.FirstName + ' ' + c.LastName AS CustomerName,
    SUM(oi.Quantity * oi.UnitPrice) AS TotalRevenue
FROM dbo.Customers c
JOIN dbo.Orders o
    ON c.CustomerID = o.CustomerID
JOIN dbo.OrderItems oi
    ON o.OrderID = oi.OrderID
WHERE o.OrderStatus <> 'Cancelled'
AND EXISTS (
    SELECT 1
    FROM dbo.Payments p
    WHERE p.OrderID = o.OrderID
    AND p.PaymentStatus = 'Successful'
)
GROUP BY c.CustomerID, c.FirstName, c.LastName
ORDER BY TotalRevenue DESC;
"""

df = pd.read_sql(query, connection)
reports["Top Customers"] = df.copy()
print("\nTop 10 Customers by Revenue:")
print(df.to_string(index=False))
# REPORT 4: CATEGORY-WISE SALES ANALYSIS

query = """
SELECT
    c.CategoryName,
    SUM(oi.Quantity) AS TotalQuantitySold,
    SUM(oi.Quantity * oi.UnitPrice) AS TotalRevenue
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
GROUP BY c.CategoryName
ORDER BY TotalRevenue DESC;
"""

df = pd.read_sql(query, connection)
reports["Category Sales"] = df.copy()
print("\nREPORT 4: CATEGORY-WISE SALES")
print(df.to_string(index=False))

# ==========================================
# REPORT 5: LOW STOCK ANALYSIS
# ==========================================

query = """
SELECT
    p.ProductID,
    p.ProductName,
    i.OnHandQty,
    i.ReservedQty,
    i.OnHandQty - i.ReservedQty AS AvailableQty
FROM dbo.Products p
JOIN dbo.Inventory i
    ON p.ProductID = i.ProductID
WHERE i.OnHandQty - i.ReservedQty <= 10
ORDER BY AvailableQty ASC;
"""

df = pd.read_sql(query, connection)
reports["Low Stock"] = df.copy()
print("\nREPORT 5: LOW STOCK PRODUCTS")
print(df.to_string(index=False))


# ==========================================
# REPORT 6: RETURNS ANALYSIS
# ==========================================

query = """
SELECT
    r.ReturnStatus,
    COUNT(DISTINCT r.ReturnID) AS TotalReturns,
    SUM(ri.ReturnQuantity) AS TotalReturnedQuantity
FROM dbo.Returns r
LEFT JOIN dbo.ReturnItems ri
    ON r.ReturnID = ri.ReturnID
GROUP BY r.ReturnStatus
ORDER BY TotalReturns DESC;
"""

df = pd.read_sql(query, connection)
reports["Returns"] = df.copy()
print("\nREPORT 6: RETURNS ANALYSIS")
print(df.to_string(index=False))
import matplotlib.pyplot as plt

print("Starting Report 7...")

query = """
SELECT
    YEAR(o.OrderDate) AS OrderYear,
    MONTH(o.OrderDate) AS OrderMonth,
    SUM(oi.Quantity * oi.UnitPrice) AS TotalRevenue
FROM dbo.Orders o
JOIN dbo.OrderItems oi
    ON o.OrderID = oi.OrderID
WHERE EXISTS (
    SELECT 1
    FROM dbo.Payments p
    WHERE p.OrderID = o.OrderID
      AND p.PaymentStatus = 'Successful'
)
GROUP BY YEAR(o.OrderDate), MONTH(o.OrderDate)
ORDER BY OrderYear, OrderMonth;
"""

df = pd.read_sql(query, connection)
reports["Monthly Chart Data"] = df.copy()
print(df)

df["Month"] = (
    df["OrderYear"].astype(str)
    + "-"
    + df["OrderMonth"].astype(str).str.zfill(2)
)

plt.figure(figsize=(10, 5))
plt.plot(df["Month"], df["TotalRevenue"], marker="o")
plt.title("Monthly E-Commerce Revenue")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()

print("Report 7 completed!")
# EXPORT REPORT TO EXCEL


# EXPORT ALL 7 REPORTS TO EXCEL

with pd.ExcelWriter("Business_Report.xlsx", engine="openpyxl") as writer:

    for sheet_name, report_df in reports.items():
        report_df.to_excel(
            writer,
            sheet_name=sheet_name,
            index=False
        )

print("All 7 reports exported to Excel successfully!")




connection.close()

print("\nAll 7 business reports completed successfully!")


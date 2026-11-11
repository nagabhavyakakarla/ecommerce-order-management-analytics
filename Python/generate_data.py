

import pyodbc
import random
from faker import Faker
from decimal import Decimal

# Generate Indian sample data
fake = Faker("en_IN")

# Connect to SQL Server
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=EcommerceDB;"
    "Trusted_Connection=yes;"
)

conn = None
cursor = None

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    print("Connected to SQL Server!")

    # Check whether tables are empty
    cursor.execute("""
        SELECT
            (SELECT COUNT(*) FROM dbo.Categories),
            (SELECT COUNT(*) FROM dbo.Customers),
            (SELECT COUNT(*) FROM dbo.Products),
            (SELECT COUNT(*) FROM dbo.Inventory)
    """)

    counts = cursor.fetchone()

    if any(count > 0 for count in counts):
        raise Exception(
            "Data already exists. Insertion stopped to avoid duplicates."
        )

    # 1. Insert Categories
    categories = [
        ("Electronics", "Electronic devices and accessories"),
        ("Clothing", "Men and women clothing"),
        ("Footwear", "Shoes and sandals"),
        ("Home Appliances", "Appliances for home"),
        ("Books", "Educational and general books"),
        ("Furniture", "Home and office furniture"),
        ("Sports", "Sports equipment"),
        ("Beauty", "Beauty and personal care"),
        ("Toys", "Children toys and games"),
        ("Groceries", "Daily household groceries")
    ]

    cursor.fast_executemany = True

    cursor.executemany("""
        INSERT INTO dbo.Categories
        (CategoryName, Description)
        VALUES (?, ?)
    """, categories)

    print("10 Categories inserted!")

    # Get actual Category IDs
    cursor.execute("SELECT CategoryID FROM dbo.Categories")
    category_ids = [row[0] for row in cursor.fetchall()]

    # 2. Generate Customers
    customers = []

    states = [
        "Andhra Pradesh", "Telangana", "Tamil Nadu",
        "Karnataka", "Kerala", "Maharashtra"
    ]

    cities = [
        "Tirupati", "Hyderabad", "Chennai",
        "Bengaluru", "Vijayawada", "Visakhapatnam",
        "Pune", "Kochi", "Mumbai"
    ]

    for i in range(500):
        customers.append((
            fake.first_name(),
            fake.last_name(),
            f"customer{i+1}@example.com",
            "+91" + str(random.randint(6000000000, 9999999999)),
            random.choice(cities),
            random.choice(states)
        ))

    cursor.executemany("""
        INSERT INTO dbo.Customers
        (FirstName, LastName, Email, Phone, City, State)
        VALUES (?, ?, ?, ?, ?, ?)
    """, customers)

    print("500 Customers inserted!")

    # 3. Generate Products
    product_types = [
        "Laptop", "Smartphone", "Headphones",
        "Keyboard", "Mouse", "Monitor",
        "Smart Watch", "Tablet", "Camera",
        "Speaker", "Office Chair", "Desk",
        "Running Shoes", "T-Shirt", "Backpack",
        "Cookware Set", "Air Conditioner",
        "Refrigerator", "Football", "Textbook"
    ]

    products = []

    for i in range(1, 101):
        products.append((
            f"{random.choice(product_types)} Model {i:03d}",
            random.choice(category_ids),
            f"SKU-{i:04d}",
            Decimal(str(round(random.uniform(299, 150000), 2))),
            1
        ))

    cursor.executemany("""
        INSERT INTO dbo.Products
        (ProductName, CategoryID, SKU, Price, IsActive)
        VALUES (?, ?, ?, ?, ?)
    """, products)

    print("100 Products inserted!")

    # Get actual Product IDs
    cursor.execute("SELECT ProductID FROM dbo.Products")
    product_ids = [row[0] for row in cursor.fetchall()]

    # 4. Generate Inventory
    inventory = []

    for product_id in product_ids:
        on_hand = random.randint(10, 500)
        reserved = random.randint(0, on_hand)

        inventory.append((
            product_id,
            on_hand,
            reserved
        ))

    cursor.executemany("""
        INSERT INTO dbo.Inventory
        (ProductID, OnHandQty, ReservedQty)
        VALUES (?, ?, ?)
    """, inventory)

    print("100 Inventory records inserted!")

    # Save all changes
    conn.commit()

    print("\nAll data inserted successfully!")
    print("Transaction committed.")

except Exception as error:

    if conn:
        conn.rollback()

    print("Error occurred:", error)
    print("Transaction rolled back.")

finally:

    if cursor:
        cursor.close()

    if conn:
        conn.close()

    print("Database connection closed.")


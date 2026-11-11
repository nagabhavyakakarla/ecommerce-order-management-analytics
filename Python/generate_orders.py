

import pyodbc
import random
from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker
import uuid

fake = Faker("en_IN")

# Connect to SQL Server
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=EcommerceDB;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()

try:
    # Get existing customers and products
    cursor.execute("SELECT CustomerID FROM Customers")
    customers = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT ProductID, Price FROM Products")
    products = [(row[0], Decimal(str(row[1])))
                for row in cursor.fetchall()]

    if not customers or not products:
        raise Exception("Customers or Products table is empty")

    # Generate 1000 orders
    for i in range(1000):

        customer_id = random.choice(customers)

        order_date = fake.date_time_between(
            start_date=datetime(2025, 1, 1),
            end_date=datetime.now()
        )

        order_status = random.choice([
            "Pending", "Confirmed", "Shipped",
            "Delivered", "Cancelled"
        ])

        # Insert Order
        cursor.execute("""
            INSERT INTO Orders
            (CustomerID, OrderDate, OrderStatus)
            OUTPUT INSERTED.OrderID
            VALUES (?, ?, ?)
        """, customer_id, order_date, order_status)

        order_id = cursor.fetchone()[0]

        # Insert Order Items
        selected_products = random.sample(
            products, min(random.randint(1, 4), len(products))
        )

        order_items = []
        total_amount = Decimal("0.00")

        for product_id, price in selected_products:

            quantity = random.randint(1, 5)
            total_amount += price * quantity

            cursor.execute("""
                INSERT INTO OrderItems
                (OrderID, ProductID, Quantity, UnitPrice)
                OUTPUT INSERTED.OrderItemID
                VALUES (?, ?, ?, ?)
            """, order_id, product_id, quantity, price)

            order_item_id = cursor.fetchone()[0]

            order_items.append(
                (order_item_id, product_id, quantity)
            )

            # Record inventory sale
            cursor.execute("""
                INSERT INTO InventoryTransactions
                (ProductID, TransactionType, QuantityChange,
                 TransactionDate, ReferenceID, Remarks)
                VALUES (?, 'Sale', ?, ?, ?, ?)
            """, product_id, -quantity, order_date,
                 order_id, "Sale from order")

        # Insert Payment
        payment_status = random.choice([
            "Pending", "Successful", "Failed", "Refunded"
        ])

        payment_date = order_date + timedelta(
            days=random.randint(0, 5)
        )

        cursor.execute("""
            INSERT INTO Payments
            (OrderID, PaymentDate, Amount,
             PaymentMethod, PaymentStatus)
            VALUES (?, ?, ?, ?, ?)
        """, order_id, payment_date, total_amount,
             random.choice([
                 "UPI", "Credit Card", "Debit Card",
                 "Cash", "Net Banking"
             ]), payment_status)

        # Insert Shipment
        shipment_status = random.choice([
            "Processing", "Shipped", "In Transit",
            "Delivered", "Failed"
        ])

        shipped_at = None
        delivered_at = None

        if shipment_status != "Processing":
            shipped_at = order_date + timedelta(days=1)

        if shipment_status == "Delivered":
            delivered_at = shipped_at + timedelta(days=3)

        cursor.execute("""
            INSERT INTO Shipments
            (OrderID, TrackingNumber, CourierName,
             ShipmentStatus, ShippedAt, DeliveredAt)
            VALUES (?, ?, ?, ?, ?, ?)
        """, order_id, uuid.uuid4().hex[:20],
             random.choice(["BlueDart", "DTDC", "Delhivery"]),
             shipment_status, shipped_at, delivered_at)

        # Generate returns for some orders
        if random.random() < 0.10:

            return_date = order_date + timedelta(
                days=random.randint(2, 20)
            )

            return_status = random.choice([
                "Requested", "Approved", "Rejected",
                "Received", "Refunded"
            ])

            cursor.execute("""
                INSERT INTO Returns
                (OrderID, ReturnDate, ReturnStatus, Reason)
                OUTPUT INSERTED.ReturnID
                VALUES (?, ?, ?, ?)
            """, order_id, return_date, return_status,
                 random.choice([
                     "Damaged product",
                     "Wrong item",
                     "Product not as expected",
                     "Size issue"
                 ]))

            return_id = cursor.fetchone()[0]

            # Insert ReturnItems
            returned_items = random.sample(
                order_items,
                random.randint(1, len(order_items))
            )

            for item_id, product_id, quantity in returned_items:

                return_quantity = random.randint(1, quantity)

                cursor.execute("""
                    INSERT INTO ReturnItems
                    (ReturnID, OrderItemID, ReturnQuantity)
                    VALUES (?, ?, ?)
                """, return_id, item_id, return_quantity)

                # Record returned stock
                cursor.execute("""
                    INSERT INTO InventoryTransactions
                    (ProductID, TransactionType, QuantityChange,
                     TransactionDate, ReferenceID, Remarks)
                    VALUES (?, 'Return', ?, ?, ?, ?)
                """, product_id, return_quantity, return_date,
                     return_id, "Customer product return")

    conn.commit()

    print("Orders generated successfully!")
    print("Total orders: 1000")

except Exception as e:
    conn.rollback()
    print("Error:", e)

finally:
    cursor.close()
    conn.close()

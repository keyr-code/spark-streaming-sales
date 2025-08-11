"""
Create and stream sales data for The Goods department store in real-time
"""

import os
import argparse
import json
import random
import time
from datetime import datetime
import pandas as pd
import numpy as np
from faker import Faker
from config import data_config
from utils.utils import weighted_choice
from utils.logger.logger import setup_logger

# Initialize logger
logger = setup_logger("streaming_data_generator")
logger.info("Streaming Data Generator logger initialized.")

# Get the base directory
# For Docker container, use the mounted path
output_dir = "/app/data/raw"


class SalesDataStreamGenerator:
    def __init__(self):
        self.fake = Faker()

        # Load required data
        try:
            self.products_df = pd.read_csv(os.path.join(output_dir, "products.csv"))
            self.customers_df = pd.read_csv(os.path.join(output_dir, "customers.csv"))
            self.employees_df = pd.read_csv(os.path.join(output_dir, "employees.csv"))

            # Filter active employees
            self.sales_employees = self.employees_df[
                (self.employees_df["is_manager"] == False)
                & (self.employees_df["dept_id"].notna())
                & (
                    self.employees_df["termination_date"].isna()
                    | (self.employees_df["termination_date"].isna())
                )
            ]

            # Group products by department
            self.products_by_dept = {}
            for dept_id in data_config.DEPT_POPULARITY.keys():
                self.products_by_dept[dept_id] = self.products_df[
                    self.products_df["dept_id"] == dept_id
                ]

        except FileNotFoundError as e:
            print(f"Error: {e}")
            raise

    def generate_sale(self):
        """Generate a single sales transaction"""
        # Current timestamp for real-time data
        current_time = datetime.now()

        # Select department based on popularity
        dept_id = weighted_choice(
            list(data_config.DEPT_POPULARITY.keys()),
            list(data_config.DEPT_POPULARITY.values()),
        )

        # Select random customer
        customer = self.customers_df.sample(1).iloc[0]
        customer_id = customer["customer_id"]

        # Select employee from the department if possible
        dept_employees = self.sales_employees[
            self.sales_employees["dept_id"] == dept_id
        ]
        if not dept_employees.empty:
            employee = dept_employees.sample(1).iloc[0]
        else:
            employee = self.sales_employees.sample(1).iloc[0]
        employee_id = employee["employee_id"]

        # Get products for this department
        dept_products = self.products_by_dept.get(dept_id)
        if dept_products.empty:
            dept_products = self.products_df.sample(min(10, len(self.products_df)))

        # Determine number of items in this sale
        num_items = min(np.random.geometric(p=0.5), len(dept_products), 10)
        num_items = max(1, num_items)

        # Select random products
        sale_products = dept_products.sample(num_items)

        # Generate unique sale ID
        sale_id = f"SALE0{random.randint(500001, 1000000)}"

        # Calculate totals
        subtotal = 0
        sale_items = []

        # Create sale items
        for _, product in sale_products.iterrows():
            quantity = min(np.random.geometric(p=0.7), 5)
            unit_price = product["price"]
            discount_percent = None
            if random.random() < 0.2:
                discount_percent = random.choice([0.1, 0.15, 0.2, 0.25, 0.3, 0.5])
                unit_price = round(unit_price * (1 - discount_percent), 2)

            item_total = round(unit_price * quantity, 2)
            subtotal += item_total

            sale_items.append(
                {
                    "product_id": product["product_id"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount_percent": discount_percent,
                    "item_total": item_total,
                }
            )

        # Calculate tax and total
        tax = round(subtotal * 0.0825, 2)
        total = subtotal + tax

        # Create sale record
        sale = {
            "sale_id": sale_id,
            "customer_id": customer_id,
            "employee_id": employee_id,
            "sale_time": current_time.isoformat(),
            "dept_id": dept_id,
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "payment_method": random.choices(
                ["Credit Card", "Debit Card", "Cash", "Mobile Payment", "Gift Card"],
                weights=[0.4, 0.3, 0.2, 0.08, 0.02],
            )[0],
            "store_id": f"STORE{random.randint(1, 10):02d}",
            "register_id": f"REG{random.randint(1, 20):02d}",
            "items_count": num_items,
            "items": sale_items,
        }

        return sale

    def stream_to_stdout(self, interval=1.0):
        """Stream sales data to stdout continuously"""
        try:
            record_count = 0
            logger.info("Starting sales data stream...")
            while True:
                record = self.generate_sale()
                record_count += 1
                print(json.dumps(record))
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info(f"\nStreaming stopped. Total records generated: {record_count}")

    def stream_to_kafka(self, producer, topic, interval=1.0):
        """Stream sales data to Kafka topic"""
        try:
            record_count = 0
            print(f"Starting sales data stream to Kafka topic '{topic}'...")
            while True:
                record = self.generate_sale()
                record_count += 1
                producer.send(topic, value=record)
                if record_count % 10 == 0:
                    print(f"Generated {record_count} records")
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info(f"\nStreaming stopped. Total records generated: {record_count}")


def main():
    parser = argparse.ArgumentParser(description="Stream sales data continuously")
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=1.0,
        help="Time interval between records in seconds",
    )

    args = parser.parse_args()
    generator = SalesDataStreamGenerator()
    generator.stream_to_stdout(interval=args.interval)


if __name__ == "__main__":
    main()

"""
Utility functions for SimzGoodz department store data generation
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
from config import data_config

# Initialize Faker with seed for reproducibility
fake = Faker()
Faker.seed(data_config.SEED)
random.seed(data_config.SEED)
np.random.seed(data_config.SEED)


def ensure_output_dir():
    """Create output directory if it doesn't exist"""
    if not os.path.exists(data_config.OUTPUT_DIR):
        os.makedirs(data_config.OUTPUT_DIR)


def save_to_csv(df, filename):
    """Save DataFrame to CSV in the output directory"""
    ensure_output_dir()
    filepath = os.path.join(data_config.OUTPUT_DIR, filename)
    df.to_csv(filepath, index=False)
    print(f"Saved {len(df)} records to {filepath}")
    return filepath


def generate_date_between(
    start_date=data_config.START_DATE, end_date=data_config.END_DATE
):
    """Generate a random date between start_date and end_date"""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)


def weighted_choice(choices, weights):
    """Make a weighted random choice from a list"""
    return random.choices(choices, weights=weights, k=1)[0]


def generate_product_id(dept_id, product_num):
    """Generate a product ID based on department and sequence number"""
    dept_prefix = {
        1001: "ELEC",
        1002: "CLTH",
        1003: "HOME",
        1004: "GROC",
        1005: "BEAU",
        1006: "SPRT",
        1007: "TOYS",
        1008: "AUTO",
        1009: "BOOK",
        1010: "JEWL",
        1011: "FURN",
        1012: "GRDN",
    }.get(dept_id, "MISC")

    return f"{dept_prefix}-{product_num:06d}"


def get_job_level(job_title):
    """Determine job level from job title for salary calculation"""
    job_title = job_title.lower()
    if "manager" in job_title or "director" in job_title:
        return "manager"
    elif "lead" in job_title:
        return "lead"
    elif (
        "specialist" in job_title or "expert" in job_title or "consultant" in job_title
    ):
        return "specialist"
    elif "senior" in job_title:
        return "specialist"
    else:
        return "associate"

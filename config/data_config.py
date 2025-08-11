"""
Configuration settings for SimzGoodz department store data generation
"""

# Basic configuration
COMPANY_NAME = "SimzGoodz"
SEED = 42  # For reproducibility
OUTPUT_DIR = "output"

# Scale factors for data generation
NUM_DEPARTMENTS = 12
NUM_PRODUCTS_PER_DEPT_MIN = 100
NUM_PRODUCTS_PER_DEPT_MAX = 500
NUM_EMPLOYEES_PER_DEPT_MIN = 15
NUM_EMPLOYEES_PER_DEPT_MAX = 50
NUM_CUSTOMERS = 50000
NUM_SALES = 500000
NUM_SUPPLIERS = 200
NUM_WAREHOUSES = 8

# Date ranges
START_DATE = "2020-01-01"
END_DATE = "2023-12-31"

# Department definitions with realistic details
DEPARTMENTS = [
    {"dept_id": 1001, "name": "Electronics", "annual_revenue": 12450000, "floor": 2},
    {"dept_id": 1002, "name": "Clothing", "annual_revenue": 9850000, "floor": 1},
    {"dept_id": 1003, "name": "Home Goods", "annual_revenue": 7650000, "floor": 3},
    {"dept_id": 1004, "name": "Grocery", "annual_revenue": 18250000, "floor": 1},
    {"dept_id": 1005, "name": "Beauty & Personal Care", "annual_revenue": 6350000, "floor": 1},
    {"dept_id": 1006, "name": "Sports & Outdoors", "annual_revenue": 5150000, "floor": 2},
    {"dept_id": 1007, "name": "Toys & Games", "annual_revenue": 4950000, "floor": 2},
    {"dept_id": 1008, "name": "Automotive", "annual_revenue": 3050000, "floor": 3},
    {"dept_id": 1009, "name": "Books & Media", "annual_revenue": 2850000, "floor": 2},
    {"dept_id": 1010, "name": "Jewelry", "annual_revenue": 7250000, "floor": 1},
    {"dept_id": 1011, "name": "Furniture", "annual_revenue": 8450000, "floor": 3},
    {"dept_id": 1012, "name": "Garden & Outdoor", "annual_revenue": 4150000, "floor": 3}
]

# Department popularity weights (for sales distribution)
DEPT_POPULARITY = {
    1001: 0.15,  # Electronics
    1002: 0.18,  # Clothing
    1003: 0.08,  # Home Goods
    1004: 0.25,  # Grocery
    1005: 0.10,  # Beauty
    1006: 0.05,  # Sports
    1007: 0.07,  # Toys
    1008: 0.03,  # Automotive
    1009: 0.04,  # Books
    1010: 0.02,  # Jewelry
    1011: 0.02,  # Furniture
    1012: 0.01   # Garden
}

# Job titles by department
JOB_TITLES = {
    1001: ["Electronics Sales Associate", "TV Specialist", "Computer Technician", "Mobile Phone Specialist", 
           "Audio Equipment Expert", "Electronics Department Lead", "Customer Service Technician"],
    1002: ["Clothing Sales Associate", "Fitting Room Attendant", "Fashion Consultant", "Clothing Department Lead",
           "Visual Merchandiser", "Inventory Specialist", "Men's Department Associate", "Women's Department Associate"],
    1003: ["Home Goods Associate", "Interior Design Consultant", "Furniture Specialist", "Home Department Lead",
           "Kitchenware Specialist", "Bedding Expert", "Home Decor Consultant"],
    1004: ["Grocery Clerk", "Produce Specialist", "Bakery Associate", "Grocery Department Lead",
           "Deli Counter Associate", "Cashier", "Stock Clerk", "Inventory Manager"],
    1005: ["Beauty Consultant", "Cosmetics Specialist", "Skincare Advisor", "Beauty Department Lead",
           "Fragrance Expert", "Makeup Artist", "Personal Care Specialist"],
    1006: ["Sports Equipment Specialist", "Fitness Consultant", "Outdoor Gear Expert", "Sports Department Lead",
           "Footwear Specialist", "Team Sports Consultant", "Camping Equipment Expert"],
    1007: ["Toy Demonstrator", "Game Specialist", "Children's Entertainment Advisor", "Toy Department Lead",
           "Educational Toy Consultant", "Video Game Specialist", "Collectibles Expert"],
    1008: ["Automotive Specialist", "Car Parts Expert", "Tool Advisor", "Automotive Department Lead",
           "Car Accessories Specialist", "DIY Project Consultant"],
    1009: ["Bookseller", "Media Specialist", "Literary Expert", "Books Department Lead",
           "Magazine Specialist", "Music Department Associate", "Educational Materials Consultant"],
    1010: ["Jewelry Consultant", "Watch Specialist", "Fine Jewelry Expert", "Jewelry Department Lead",
           "Gemstone Specialist", "Jewelry Repair Technician", "Custom Design Consultant"],
    1011: ["Furniture Sales Associate", "Interior Designer", "Furniture Department Lead",
           "Mattress Specialist", "Office Furniture Consultant", "Upholstery Expert"],
    1012: ["Garden Center Associate", "Plant Specialist", "Outdoor Living Expert", "Garden Department Lead",
           "Landscaping Consultant", "Seasonal Department Associate", "Patio Furniture Specialist"]
}

# Salary ranges by job level
SALARY_RANGES = {
    "entry": (30000, 40000),
    "associate": (38000, 50000),
    "specialist": (45000, 60000),
    "lead": (55000, 70000),
    "manager": (65000, 95000),
    "director": (90000, 130000),
    "executive": (120000, 200000)
}
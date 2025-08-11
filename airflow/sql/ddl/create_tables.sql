-- Create schema
CREATE SCHEMA IF NOT EXISTS simzgoodz;

-- Set search path
SET search_path TO simzgoodz;

-- Departments table
CREATE TABLE IF NOT EXISTS departments (
    dept_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    annual_revenue NUMERIC(12, 2),
    floor INTEGER,
    annual_budget NUMERIC(12, 2),
    marketing_budget NUMERIC(12, 2),
    area_sqft INTEGER,
    num_sections INTEGER,
    profit_margin NUMERIC(4, 2),
    customer_satisfaction NUMERIC(3, 1),
    inventory_turnover NUMERIC(4, 1)
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    dept_id INTEGER,
    category VARCHAR(100),
    brand VARCHAR(100),
    price NUMERIC(10, 2) NOT NULL,
    cost NUMERIC(10, 2),
    stock INTEGER,
    reorder_level INTEGER,
    supplier_id VARCHAR(20),
    weight_kg NUMERIC(10, 2),
    dimensions VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    date_added DATE,
    warehouse_id VARCHAR(20)
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(200),
    phone VARCHAR(50),
    address VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    join_date DATE,
    birth_date DATE,
    gender VARCHAR(10),
    loyalty_points INTEGER,
    segment VARCHAR(50),
    preferred_payment VARCHAR(50),
    marketing_opt_in BOOLEAN,
    last_purchase_date DATE,
    card_type VARCHAR(20),
    card_last_four VARCHAR(4),
    card_expiry VARCHAR(10)
);

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(200),
    phone VARCHAR(50),
    dept_id INTEGER,
    job_title VARCHAR(100),
    salary NUMERIC(10, 2),
    hire_date DATE,
    birth_date DATE,
    address VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    is_manager BOOLEAN DEFAULT FALSE,
    reports_to VARCHAR(20),
    emergency_contact VARCHAR(100),
    emergency_phone VARCHAR(50),
    termination_date DATE,
    termination_reason VARCHAR(200)
);

-- Sales fact table
CREATE TABLE IF NOT EXISTS sales_fact (
    sale_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20),
    employee_id VARCHAR(20),
    sale_date DATE NOT NULL,
    sale_time TIME NOT NULL,
    dept_id INTEGER,
    subtotal NUMERIC(10, 2) NOT NULL,
    tax NUMERIC(10, 2) NOT NULL,
    total NUMERIC(10, 2) NOT NULL,
    payment_method VARCHAR(50),
    store_id VARCHAR(20),
    register_id VARCHAR(20),
    items_count INTEGER
);

-- Sales items table
CREATE TABLE IF NOT EXISTS sales_items (
    sale_item_id SERIAL PRIMARY KEY,
    sale_id VARCHAR(20),
    product_id VARCHAR(20),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    discount_percent NUMERIC(5, 2),
    item_total NUMERIC(10, 2) NOT NULL
);

-- Metrics tables for analytics
CREATE TABLE IF NOT EXISTS metrics_department (
    dept_id INTEGER,
    name VARCHAR(100),
    transaction_count INTEGER,
    total_sales NUMERIC(14, 2),
    avg_transaction_value NUMERIC(10, 2),
    unique_customers INTEGER,
    market_share NUMERIC(5, 4),
    report_date DATE,
    PRIMARY KEY (dept_id, report_date)
);

CREATE TABLE IF NOT EXISTS metrics_daily (
    day_date DATE PRIMARY KEY,
    transaction_count INTEGER,
    total_sales NUMERIC(14, 2),
    avg_transaction_value NUMERIC(10, 2),
    unique_customers INTEGER
);

CREATE TABLE IF NOT EXISTS metrics_product (
    product_id VARCHAR(20),
    name VARCHAR(200),
    category VARCHAR(100),
    dept_id INTEGER,
    units_sold INTEGER,
    total_sales NUMERIC(14, 2),
    avg_price NUMERIC(10, 2),
    transaction_count INTEGER,
    revenue_per_unit NUMERIC(10, 2),
    report_date DATE,
    PRIMARY KEY (product_id, report_date)
);

CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    address VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    capacity_sqft INTEGER,
    manager_id VARCHAR(20),
    phone VARCHAR(50)
);

-- Suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_name VARCHAR(100),
    contact_title VARCHAR(100),
    email VARCHAR(200),
    phone VARCHAR(50),
    address VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    country VARCHAR(50),
    website VARCHAR(100),
    industry VARCHAR(100),
    primary_dept_id INTEGER,
    payment_terms VARCHAR(50),
    rating INTEGER,
    active_since DATE
);

-- Inventory transactions table
CREATE TABLE IF NOT EXISTS inventory_transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    product_id VARCHAR(20),
    transaction_date DATE NOT NULL,
    transaction_time TIME NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    from_warehouse VARCHAR(20),
    to_warehouse VARCHAR(20),
    unit_cost NUMERIC(10, 2),
    total_value NUMERIC(10, 2),
    reference_id VARCHAR(20),
    employee_id VARCHAR(20)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sales_fact_date ON sales_fact(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_fact_customer ON sales_fact(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_fact_dept ON sales_fact(dept_id);
CREATE INDEX IF NOT EXISTS idx_sales_items_sale ON sales_items(sale_id);
CREATE INDEX IF NOT EXISTS idx_sales_items_product ON sales_items(product_id);
CREATE INDEX IF NOT EXISTS idx_products_dept ON products(dept_id);
CREATE INDEX IF NOT EXISTS idx_employees_dept ON employees(dept_id);
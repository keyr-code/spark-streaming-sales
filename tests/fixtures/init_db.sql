-- Initialize test database with required tables
-- This script will be used by PostgreSQL to initialize the test database

-- Create schema
CREATE SCHEMA IF NOT EXISTS simzgoodz;

-- Set search path
SET search_path TO simzgoodz;

-- Products table (matches the expected table name in tests)
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    stock INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    date_added DATE DEFAULT CURRENT_DATE
);

-- Orders table (matches the expected table name in tests)
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20),
    order_date DATE DEFAULT CURRENT_DATE,
    total_amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    payment_method VARCHAR(50)
);

-- Insert sample data for testing
INSERT INTO products (product_id, name, description, price, stock) VALUES
('P001', 'Test Product 1', 'Sample product for testing', 19.99, 100),
('P002', 'Test Product 2', 'Another sample product', 29.99, 50);

INSERT INTO orders (order_id, customer_id, total_amount, status) VALUES
('O001', 'CUST001', 49.98, 'completed'),
('O002', 'CUST002', 29.99, 'pending');

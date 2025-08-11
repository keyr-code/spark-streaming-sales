-- Set search path
SET search_path TO simzgoodz;

-- Add foreign keys for products table
ALTER TABLE products 
ADD CONSTRAINT fk_products_dept 
FOREIGN KEY (dept_id) REFERENCES departments(dept_id);

ALTER TABLE products 
ADD CONSTRAINT fk_products_warehouses 
FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id);

ALTER TABLE products 
ADD CONSTRAINT fk_products_suppliers 
FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id);

-- Add foreign keys for employees table
ALTER TABLE employees 
ADD CONSTRAINT fk_employees_dept 
FOREIGN KEY (dept_id) REFERENCES departments(dept_id);

ALTER TABLE employees 
ADD CONSTRAINT fk_employees_reports_to 
FOREIGN KEY (reports_to) REFERENCES employees(employee_id) 
NOT VALID;

-- Add foreign keys for sales_fact table
ALTER TABLE sales_fact 
ADD CONSTRAINT fk_sales_fact_customer 
FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

ALTER TABLE sales_fact 
ADD CONSTRAINT fk_sales_fact_employee 
FOREIGN KEY (employee_id) REFERENCES employees(employee_id);

ALTER TABLE sales_fact 
ADD CONSTRAINT fk_sales_fact_dept 
FOREIGN KEY (dept_id) REFERENCES departments(dept_id);

-- Add foreign keys for sales_items table

ALTER TABLE sales_items 
ADD CONSTRAINT fk_sales_items_product 
FOREIGN KEY (product_id) REFERENCES products(product_id);

-- Add foreign keys for metrics tables
ALTER TABLE metrics_department 
ADD CONSTRAINT fk_metrics_department_dept 
FOREIGN KEY (dept_id) REFERENCES departments(dept_id);

ALTER TABLE metrics_product 
ADD CONSTRAINT fk_metrics_product_product 
FOREIGN KEY (product_id) REFERENCES products(product_id);

ALTER TABLE metrics_product 
ADD CONSTRAINT fk_metrics_product_dept 
FOREIGN KEY (dept_id) REFERENCES departments(dept_id);

-- Add foreign keys for warehouses table
ALTER TABLE warehouses 
ADD CONSTRAINT fk_warehouses_employees 
FOREIGN KEY (manager_id) REFERENCES employees(employee_id) DEFERRABLE INITIALLY DEFERRED;

-- Add foreign keys for inventory_transactions table
ALTER TABLE inventory_transactions 
ADD CONSTRAINT fk_inventory_product 
FOREIGN KEY (product_id) REFERENCES products(product_id);

ALTER TABLE inventory_transactions 
ADD CONSTRAINT fk_inventory_from_warehouse 
FOREIGN KEY (from_warehouse) REFERENCES warehouses(warehouse_id);

ALTER TABLE inventory_transactions 
ADD CONSTRAINT fk_inventory_to_warehouse 
FOREIGN KEY (to_warehouse) REFERENCES warehouses(warehouse_id);

ALTER TABLE inventory_transactions 
ADD CONSTRAINT fk_inventory_employee 
FOREIGN KEY (employee_id) REFERENCES employees(employee_id);
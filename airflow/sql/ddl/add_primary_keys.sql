-- Set search path
SET search_path TO simzgoodz;

-- Make sure tables have their primary keys (optional)
ALTER TABLE departments DROP CONSTRAINT IF EXISTS departments_pkey;
ALTER TABLE departments ADD CONSTRAINT departments_pkey PRIMARY KEY (dept_id);

ALTER TABLE products DROP CONSTRAINT IF EXISTS products_pkey;
ALTER TABLE products ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);

ALTER TABLE customers DROP CONSTRAINT IF EXISTS customers_pkey;
ALTER TABLE customers ADD CONSTRAINT customers_pkey PRIMARY KEY (customer_id);

ALTER TABLE employees DROP CONSTRAINT IF EXISTS employees_pkey;
ALTER TABLE employees ADD CONSTRAINT employees_pkey PRIMARY KEY (employee_id);

ALTER TABLE suppliers DROP CONSTRAINT IF EXISTS suppliers_pkey;
ALTER TABLE suppliers ADD CONSTRAINT suppliers_pkey PRIMARY KEY (supplier_id);

ALTER TABLE warehouses DROP CONSTRAINT IF EXISTS warehouses_pkey;
ALTER TABLE warehouses ADD CONSTRAINT warehouses_pkey PRIMARY KEY (warehouse_id);

ALTER TABLE inventory_transactions DROP CONSTRAINT IF EXISTS inventory_transactions_pkey;
ALTER TABLE inventory_transactions ADD CONSTRAINT inventory_transactions_pkey PRIMARY KEY (transaction_id);

ALTER TABLE sales_items DROP CONSTRAINT IF EXISTS sales_items_pkey;
ALTER TABLE sales_items ADD CONSTRAINT sales_items_pkey PRIMARY KEY (sale_id, product_id);
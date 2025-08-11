-- Set search path
SET search_path TO simzgoodz;

-- Drop all tables in reverse order of dependencies
DROP TABLE IF EXISTS data_quality_results CASCADE;
DROP TABLE IF EXISTS metrics_product CASCADE;
DROP TABLE IF EXISTS metrics_daily CASCADE;
DROP TABLE IF EXISTS metrics_department CASCADE;
DROP TABLE IF EXISTS inventory_transactions CASCADE;
DROP TABLE IF EXISTS sales_items CASCADE;
DROP TABLE IF EXISTS sales_fact CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS warehouses CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

-- Confirm tables are dropped
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'simzgoodz';
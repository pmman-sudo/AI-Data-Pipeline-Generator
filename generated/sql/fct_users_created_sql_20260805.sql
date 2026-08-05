WITH 
-- Remove duplicate orders and filter cancelled orders
filtered_orders AS (
  SELECT DISTINCT 
    customer_id,
    order_id,
    order_date,
    order_total,
    status
  FROM 
    raw.customer_orders
  WHERE 
    status != 'cancelled'
),

-- Standardize timestamps to UTC
ordered_orders AS (
  SELECT 
    customer_id,
    order_id,
    order_date AT TIME ZONE 'UTC' AS order_date_utc,
    order_total
  FROM 
    filtered_orders
),

-- Calculate total sales and order count
aggregated_orders AS (
  SELECT 
    customer_id,
    SUM(order_total) AS total_sales,
    COUNT(order_id) AS order_count
  FROM 
    ordered_orders
  GROUP BY 
    customer_id
),

-- Calculate average order value
average_order_value AS (
  SELECT 
    customer_id,
    total_sales,
    order_count,
    total_sales / order_count AS average_order_value
  FROM 
    aggregated_orders
)

-- Create a final analytics-ready table
INSERT INTO fct_users_created (
  user_id,
  created_at,
  email
)
SELECT 
  customer_id AS user_id,
  MIN(order_date_utc) AS created_at,
  NULL AS email  -- email is not provided in the raw.customer_orders table
FROM 
  average_order_value
GROUP BY 
  customer_id;
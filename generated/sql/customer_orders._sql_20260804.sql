WITH orders_without_duplicates AS (
  SELECT DISTINCT user_id, created_at, email
  FROM raw.customer_orders
),
filtered_orders AS (
  SELECT user_id, created_at, email
  FROM orders_without_duplicates
  WHERE email NOT LIKE '%@cancelled%'
),
orders_with_utc_timestamps AS (
  SELECT 
    user_id,
    email,
    created_at AT TIME ZONE 'UTC' AS created_at_utc
  FROM filtered_orders
),
customer_orders_with_sales AS (
  SELECT 
    c.user_id,
    c.email,
    SUM(1) AS order_count,
    SUM(1) * 1.0 AS total_sales
  FROM orders_with_utc_timestamps c
  GROUP BY c.user_id, c.email
),
final_customer_orders AS (
  SELECT 
    user_id,
    email,
    order_count,
    total_sales,
    total_sales / order_count AS average_order_value
  FROM customer_orders_with_sales
)
SELECT * 
INTO analytics.customer_orders
FROM final_customer_orders;
{{
  config(
    materialized = 'table',
    alias = 'orders'
  )
}}

WITH raw_orders AS (
  SELECT 
    user_id,
    created_at,
    email
  FROM 
    {{ ref('raw_orders') }}
),
raw_customers AS (
  SELECT 
    user_id
  FROM 
    {{ ref('raw_customers') }}
)
SELECT 
  raw_orders.user_id::BIGINT AS user_id,
  raw_orders.created_at::TIMESTAMP AS created_at,
  raw_orders.email::STRING AS email
FROM 
  raw_orders
  LEFT JOIN raw_customers 
  ON raw_orders.user_id = raw_customers.user_id
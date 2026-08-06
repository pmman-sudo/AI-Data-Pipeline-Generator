{{
  config(
    materialized = 'table',
    alias = 'sales_orders'
  )
}}

WITH 
raw_orders AS (
  SELECT 
    user_id,
    created_at,
    email
  FROM 
    {{ ref('raw_orders') }}
),

raw_customers AS (
  SELECT 
    user_id,
    email
  FROM 
    {{ ref('raw_customers') }}
)

SELECT 
  ro.user_id::BIGINT AS user_id,
  ro.created_at::TIMESTAMP AS created_at,
  ro.email::STRING AS email
FROM 
  raw_orders ro
  LEFT JOIN raw_customers rc ON ro.user_id = rc.user_id
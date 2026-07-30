sql
{{
  config(
    materialized = 'table',
    alias = 'fct_users_created'
  )
}}

WITH 
logging_events AS (
  SELECT * FROM {{ ref('logging_events') }}
)

SELECT 
  CAST(logging_events.user_id AS VARCHAR(100)) AS user_id,
  CAST(logging_events.user_name AS BOOLEAN) AS user_name
FROM 
  logging_events
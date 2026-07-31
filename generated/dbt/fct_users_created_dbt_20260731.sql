{{
  config(
    materialized = 'table',
    alias = 'fct_users_created'
  )
}}

WITH users_created AS (
  SELECT 
    user_id,
    user_name
  FROM 
    {{ ref('logging_events') }}
)

SELECT 
  user_id::varchar(100) AS user_id,
  user_name::boolean AS user_name
FROM 
  users_created
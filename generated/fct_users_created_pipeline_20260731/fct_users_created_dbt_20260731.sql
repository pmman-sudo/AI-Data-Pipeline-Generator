{{
  config(
    materialized = 'table',
    alias = 'fct_users_created'
  )
}}


WITH 
-- Extract the table name from the upstream lineage URN
logging_events AS (
  SELECT * FROM {{ ref('logging_events') }}
),

-- Filter and transform the data
users_created AS (
  SELECT 
    -- Cast the user_id column to varchar(100)
    CAST(user_id AS VARCHAR(100)) AS user_id,
    -- Cast the user_name column to boolean
    CAST(user_name AS BOOLEAN) AS user_name
  FROM 
    logging_events
)

-- Select the transformed data
SELECT 
  user_id,
  user_name
FROM 
  users_created
sql
{{
  config(
    materialized = 'table',
    alias = 'fct_users_created'
  )
}}

WITH 
  -- Extract the table name from the lineage array:
  -- "urn:li:dataset:(urn:li:dataPlatform:hive,logging_events,PROD)"
  -- Table name is "logging_events"
  upstream_data AS (
    SELECT 
      user_id,
      user_name
    FROM 
      {{ ref('logging_events') }}
  )

SELECT 
  -- Cast the columns to the appropriate data types
  user_id::varchar(100) AS user_id,
  -- The user_name column is defined as boolean, which is likely incorrect.
  -- Assuming it's supposed to be a string, we'll cast it as such.
  user_name::varchar(100) AS user_name
FROM 
  upstream_data
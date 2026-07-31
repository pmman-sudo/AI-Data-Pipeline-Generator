{{
  config(
    materialized = 'table',
    alias = 'fct_users_created'
  )
}}

WITH 
-- Extracting table name from upstream lineage: urn:li:dataset:(urn:li:dataPlatform:hive,logging_events,PROD)
logging_events AS (
  SELECT * FROM {{ ref('logging_events') }}
)

SELECT 
  -- Casting user_id to varchar(100) as per metadata
  CAST(user_id AS VARCHAR(100)) AS user_id,
  
  -- Casting user_name to boolean as per metadata
  CAST(user_name AS BOOLEAN) AS user_name

FROM 
  logging_events
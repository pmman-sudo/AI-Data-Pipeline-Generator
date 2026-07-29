sql
{{
  -- Define the dbt model for fct_users_created.
  -- This model depends on the logging_events table, which is specified in the lineage array.
  config(
    materialized = 'table',
    persist_docs = {'relation': True, 'columns': True}
  )
}}

WITH upstream_data AS (
  -- Use the dbt ref function to refer to the upstream table.
  SELECT 
    -- Cast columns to the appropriate data type if necessary.
    CAST(user_id AS VARCHAR(100)) AS user_id,
    -- The user_name column is specified as a boolean type, 
    -- but it's described as the name of the user who signed up. 
    -- This might be a discrepancy in the table metadata. 
    -- For the sake of this model, we will cast it to a boolean.
    CAST(user_name AS BOOLEAN) AS user_name
  FROM 
    {{ ref('logging_events') }}
)

SELECT 
  -- Select the user_id and user_name columns from the upstream data.
  user_id,
  user_name
FROM 
  upstream_data
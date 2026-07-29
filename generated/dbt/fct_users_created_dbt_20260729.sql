sql
{{
  -- Description: This dbt model creates the fct_users_created fact table.
  -- Depends on the logging_events table.
}}

WITH users_created AS (
  -- Extract user_id and user_name from the lineage table
  SELECT 
    user_id,
    user_name
  FROM 
    {{ ref('logging_events') }} 
  WHERE 
    -- Assuming that there is a column that indicates a new user creation
    -- This filter might need to be adjusted based on the actual column names in logging_events
    event_type = 'new_user_created'
)

SELECT 
  -- Cast columns to appropriate data types if necessary
  user_id::varchar(100) AS user_id,
  -- Since the user_name column is of boolean type, it's likely an error.
  -- Assuming it's actually a string and needs to be cast accordingly
  NULLIF(user_name::varchar(100), '') AS user_name
INTO 
  {{ this }}

FROM 
  users_created;
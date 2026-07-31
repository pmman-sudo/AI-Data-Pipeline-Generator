{#
  This dbt model generates the fct_users_created table.
  It depends on the logging_events table, which is the upstream dependency.
#}

{{ config(
  materialized = 'table',
  alias = 'fct_users_created'
) }}

WITH 
logging_events AS (
  {{ ref('logging_events') }}
),

-- Filter and transform the data to create the fct_users_created table
fct_users_created AS (
  SELECT 
    -- Cast user_id to varchar(100) if necessary
    CAST(user_id AS VARCHAR(100)) AS user_id,
    -- Cast user_name to boolean if necessary
    CAST(user_name AS BOOLEAN) AS user_name
  FROM 
    logging_events
)

SELECT 
  user_id,
  user_name
FROM 
  fct_users_created
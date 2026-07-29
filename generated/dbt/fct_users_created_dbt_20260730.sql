sql
{{
    config(
        materialized='table',
        alias='fct_users_created'
    )
}}

WITH 
-- Extract relevant user data from upstream dependency
users AS (
    SELECT 
        user_id,
        user_name
    FROM 
        {{ ref('logging_events') }}
    WHERE 
        -- Additional filter conditions can be added here if necessary
        TRUE
),

-- Prepare the data for fact table creation
prepared_data AS (
    SELECT 
        user_id,
        user_name
    FROM 
        users
)

-- Create the fact table
SELECT 
    CAST(user_id AS VARCHAR(100)) AS user_id,
    CAST(user_name AS BOOLEAN) AS user_name
FROM 
    prepared_data
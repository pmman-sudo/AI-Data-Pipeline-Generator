{# 
    dbt Model for fct_users_created
#}

{{
    config(
        materialized='table',
        alias='fct_users_created'
    )
}}


SELECT 
    -- Cast user_id to varchar(100) to ensure data type consistency
    CAST(user_id AS VARCHAR(100)) AS user_id,

    -- Cast user_name to boolean to ensure data type consistency
    CAST(user_name AS BOOLEAN) AS user_name

FROM 
    -- Using dbt's ref() function to reference the upstream dependency
    {{ ref('logging_events') }}
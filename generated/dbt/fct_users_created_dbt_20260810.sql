{{
  config(
    alias = 'fct_users_created',
    materialized = 'table',
    owner = 'Demo',
    tags = ['Demo']
  )
}}

SELECT 
    user_id,
    created_at,
    email
FROM 
    source(fct_users_created)
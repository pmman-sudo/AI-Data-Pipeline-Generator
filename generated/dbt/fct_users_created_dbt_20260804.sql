{{
  config(
    materialized = 'incremental',
    unique_key = 'user_id',
    on_schema_change = 'sync_all_columns',
    aliases = ['raw_users: raw_users']
  )
}}


with users as (
  select 
    user_id,
    created_at,
    email
  from 
    {{ ref('raw_users') }}
  where 
    user_id is not null 
    and email is not null
)

, active_users as (
  select 
    user_id,
    created_at,
    lower(email) as email
  from 
    users
  where 
    user_id in (select distinct user_id from users)
)

, parsed_users as (
  select 
    user_id,
    created_at,
    email,
    cast(created_at as date) as signup_date,
    extract(month from created_at) as created_month
  from 
    active_users
)

select 
  row_number() over (order by user_id) as user_sk,
  user_id,
  created_at,
  email,
  signup_date,
  created_month
from 
  parsed_users
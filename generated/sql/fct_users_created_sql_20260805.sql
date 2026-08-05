SELECT 
    uc.user_id,
    uc.created_at,
    uc.email
FROM 
    fct_users_created uc;
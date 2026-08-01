SELECT 
    DATE(created_at) AS creation_date,
    COUNT(user_id) AS new_users
FROM 
    fct_users_created
GROUP BY 
    DATE(created_at)
ORDER BY 
    creation_date;
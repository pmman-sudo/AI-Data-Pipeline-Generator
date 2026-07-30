SELECT 
    DATE_TRUNC('day', created_at) AS registration_day,
    COUNT(DISTINCT user_id) AS num_users_registered
FROM 
    fct_users_created
GROUP BY 
    DATE_TRUNC('day', created_at)
ORDER BY 
    registration_day ASC;
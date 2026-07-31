SELECT 
    ue.user_id,
    CASE 
        WHEN ue.user_name IS NOT NULL THEN TRUE 
        ELSE FALSE 
    END AS user_name
FROM 
    logging_events ue
WHERE 
    ue.user_id IS NOT NULL
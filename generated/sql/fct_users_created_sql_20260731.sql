SELECT 
    user_id,
    user_name
FROM 
    logging_events
WHERE 
    user_id IS NOT NULL
    AND user_name IS NOT NULL;
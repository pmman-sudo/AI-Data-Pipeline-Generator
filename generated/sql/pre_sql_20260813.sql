SELECT 
    user_id, 
    created_at, 
    email
FROM 
    pre
WHERE 
    created_at IS NOT NULL
AND 
    email IS NOT NULL
ORDER BY 
    created_at DESC; 

CREATE INDEX idx_created_at ON pre (created_at);
CREATE INDEX idx_email ON pre (email);

INSERT INTO pre (user_id, created_at, email)
SELECT 
    user_id, 
    created_at, 
    email
FROM 
    pre
WHERE 
    created_at IS NOT NULL
AND 
    email IS NOT NULL;

COMMIT; 

GRANT SELECT ON pre TO 'Demo'; 

ALTER TABLE pre OWNER TO 'Demo';
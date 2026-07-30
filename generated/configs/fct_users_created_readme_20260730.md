README documentation for fct_users_created dataset

Purpose
The fct_users_created dataset is designed to store information about newly created users, providing a centralized location for tracking user creation events.

Columns
The fct_users_created dataset contains the following columns: 
user_id: a unique identifier for each user, stored as a varchar(100)
user_name: a boolean value indicating whether a user name is associated with the user

Owners
The owners of the fct_users_created dataset are urn:li:corpuser:jdoe and urn:li:corpuser:datahub

Tags
There are no tags associated with the fct_users_created dataset

Lineage
The fct_users_created dataset has upstream lineage from urn:li:dataset:(urn:li:dataPlatform:hive,logging_events,PROD)

Example usage
To query the fct_users_created dataset and retrieve a list of user IDs and corresponding user names, you can use the following SQL query: 
SELECT user_id, user_name FROM fct_users_created WHERE user_name = TRUE
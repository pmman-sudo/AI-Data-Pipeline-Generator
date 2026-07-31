# fct_users_created README Documentation
## Purpose
The `fct_users_created` table is designed to store information about user creation events. It provides a centralized location for tracking user ID and user name data.

## Columns
The following columns are included in the `fct_users_created` table:
* `user_id` (varchar(100)): A unique identifier for each user.
* `user_name` (boolean): A boolean value indicating whether a user name is present.

## Owners
The owners of the `fct_users_created` table are:
* `urn:li:corpuser:jdoe`
* `urn:li:corpuser:datahub`

## Tags
There are no tags associated with the `fct_users_created` table.

## Lineage
The `fct_users.created` table has upstream lineage from the following dataset:
* `urn:li:dataset:(urn:li:dataPlatform:hive,logging_events,PROD)`

## Example Usage
To query the `fct_users_created` table and retrieve a list of all user IDs with their corresponding user name status, you can use the following SQL query:
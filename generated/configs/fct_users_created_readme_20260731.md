# fct_users_created README Documentation
## Purpose
The `fct_users_created` table is designed to store information about created users. This dataset is used to track user creation events.

## Columns
The following columns are included in the `fct_users_created` table:
* `user_id` (varchar(100)): Unique identifier for each user
* `user_name` (boolean): Indicates whether a user name is available

## Owners
The `fct_users_created` dataset is owned by:
* urn:li:corpuser:jdoe
* urn:li:corpuser:datahub

## Tags
There are no tags associated with this dataset.

## Lineage
The `fct_users_created` dataset has the following upstream lineage:
* urn:li:dataset:(urn:li:dataPlatform:hive,logging_events,PROD)

## Example Usage
To query the `fct_users_created` table and retrieve the count of users created, you can use the following SQL query:
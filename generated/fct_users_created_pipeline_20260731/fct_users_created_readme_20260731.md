# README: fct_users_created Dataset
=====================================

## Purpose
The `fct_users_created` dataset is designed to store information about users created in the system. It provides a centralized location for tracking user creation events.

## Columns
The dataset contains the following columns:

* `user_id` (varchar(100)): Unique identifier for the user
* `user_name` (boolean): Flag indicating whether the user has a name or not

## Owners
The owners of this dataset are:
* `urn:li:corpuser:jdoe`
* `urn:li:corpuser:datahub`

## Tags
There are no tags associated with this dataset.

## Lineage
This dataset is generated from the `logging_events` dataset in the `hive` data platform, which is located in the `PROD` environment. The upstream lineage is:
* `urn:li:dataset:(urn:li:dataPlatform:hive,logging_events,PROD)`

## Example Usage
To access this dataset, you can use the following query:
# customer_orders Dataset
## Purpose
The customer_orders dataset is designed to store information about customer orders, including the user who made the order, the timestamp of when the order was created, and the email address associated with the user.

## Columns
The following columns are available in the customer_orders dataset:
* **user_id** (BIGINT): Primary key
* **created_at** (TIMESTAMP): Record creation timestamp
* **email** (STRING): User email address

## Owners
The owners of the customer_orders dataset are:
* Demo

## Tags
The customer_orders dataset is associated with the following tags:
* Demo

## Lineage
The lineage of the customer_orders dataset is currently empty.

## Example Usage
The customer_orders dataset can be used to analyze customer ordering behavior, such as identifying the most frequent customers or analyzing the distribution of orders over time. For example, you could use the following query to retrieve the number of orders made by each user:
```sql
SELECT user_id, COUNT(*) as order_count
FROM customer_orders
GROUP BY user_id
ORDER BY order_count DESC;
```
This query would return a list of users and the number of orders they have made, sorted in descending order by the number of orders.
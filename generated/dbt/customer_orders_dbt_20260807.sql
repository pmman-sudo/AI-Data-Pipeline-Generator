{
  {
    config(
      materialized = 'table',
      alias = 'customer_orders',
      owner = 'Demo',
      tags = ['Demo']
    )
  }

  SELECT 
    user_id,
    created_at,
    email
  FROM 
    source(customer_orders)
}
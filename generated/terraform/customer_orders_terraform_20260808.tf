terraform
variable "database_username" {
  type        = string
  sensitive   = true
}

variable "database_password" {
  type        = string
  sensitive   = true
}

variable "database_name" {
  type        = string
}

variable "database_host" {
  type        = string
}

variable "database_port" {
  type        = number
  default     = 5432
}

provider "postgresql" {
  host     = var.database_host
  port     = var.database_port
  username = var.database_username
  password = var.database_password
}

resource "postgresql_database" "customer_orders_db" {
  name  = var.database_name
  owner = "Demo"
}

resource "postgresql_schema" "customer_orders_schema" {
  name  = "public"
  database = postgresql_database.customer_orders_db.name
}

resource "postgresql_table" "customer_orders_table" {
  database = postgresql_database.customer_orders_db.name
  schema   = postgresql_schema.customer_orders_schema.name
  name     = "customer_orders"

  column {
    name = "user_id"
    type = "BIGINT"
  }

  column {
    name = "created_at"
    type = "TIMESTAMP"
  }

  column {
    name = "email"
    type = "VARCHAR"
  }

  constraint {
    type = "PRIMARY KEY"
    columns = ["user_id"]
  }
}

resource "postgresql_grant" "customer_orders_grant" {
  database    = postgresql_database.customer_orders_db.name
  schema      = postgresql_schema.customer_orders_schema.name
  table       = postgresql_table.customer_orders_table.name
  role        = "Demo"
  privileges = ["SELECT", "INSERT", "UPDATE", "DELETE"]
}
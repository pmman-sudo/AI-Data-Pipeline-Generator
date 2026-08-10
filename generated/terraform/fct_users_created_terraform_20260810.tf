terraform
variable "database_name" {
  type = string
}

variable "database_username" {
  type = string
}

variable "database_password" {
  type      = string
  sensitive = true
}

variable "database_host" {
  type = string
}

variable "database_port" {
  type = number
}

variable "environment" {
  type = string
}

provider "postgresql" {
  host     = var.database_host
  port     = var.database_port
  username = var.database_username
  password = var.database_password
  database = var.database_name
}

resource "postgresql_role" "fct_users_created_owner" {
  name     = "Demo"
  login    = true
  password = var.database_password
}

resource "postgresql_schema" "fct_users_created_schema" {
  name  = "Demo"
  owner = postgresql_role.fct_users_created_owner.name
}

resource "postgresql_table" "fct_users_created_table" {
  name       = "fct_users_created"
  schema    = postgresql_schema.fct_users_created_schema.name
  owner     = postgresql_role.fct_users_created_owner.name
  tablespace = "main"

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
    type = "STRING"
  }

  constraint {
    type = "PRIMARY KEY"
    columns = ["user_id"]
  }
}

resource "postgresql_grant" "fct_users_created_grant" {
  database    = var.database_name
  schema      = postgresql_schema.fct_users_created_schema.name
  table       = postgresql_table.fct_users_created_table.name
  role        = postgresql_role.fct_users_created_owner.name
  privileges = ["SELECT", "INSERT", "UPDATE", "DELETE"]
}
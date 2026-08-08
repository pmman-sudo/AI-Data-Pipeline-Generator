terraform
variable "database_name" {
  type        = string
  description = "Name of the database"
}

variable "database_username" {
  type        = string
  description = "Username for database connection"
}

variable "database_password" {
  type        = string
  sensitive   = true
  description = "Password for database connection"
}

variable "database_host" {
  type        = string
  description = "Host for database connection"
}

variable "database_port" {
  type        = number
  description = "Port for database connection"
}

variable "owners" {
  type        = list(string)
  default     = ["Paul"]
  description = "List of owners for the table"
}

variable "tags" {
  type        = list(string)
  default     = []
  description = "List of tags for the table"
}

provider "postgres" {
  host     = var.database_host
  port     = var.database_port
  username = var.database_username
  password = var.database_password
  database = var.database_name
}

resource "postgres_schema" "public" {
  name  = "public"
  owner = var.database_username
}

resource "postgres_table" "fct_users_created" {
  name        = "fct_users_created"
  schema     = postgres_schema.public.name
  owner      = var.database_username
  depends_on = [postgres_schema.public]
}

resource "postgres_column" "id" {
  table = postgres_table.fct_users_created.name
  schema = postgres_schema.public.name
  name   = "id"
  type   = "integer"
}

output "table_name" {
  value = postgres_table.fct_users_created.name
}

output "table_schema" {
  value = postgres_schema.public.name
}

output "table_owner" {
  value = var.owners
}
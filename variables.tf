variable "rotate_key_after_days" {
  description = "Number of days after the creation."
  type = string
  default = "490"
}

variable "deactivate_key_after_days" {
  description = "Number of days to deactivate a key. This number must be bigger than rotate_key_after_days."
  type = string
  # default = "491"
}

variable "delete_inactive_key_after_days" {
  description = "Number of days to delete a key. This number must be bigger than deactivate_key_after_days."
  type = string
  default = "555"
}

variable "source_email" {
  description = "This e-mail will be used to send the e-mails."
  type = string
  default = "Henrique Cezar - HACKATHON <henrique.cezar@csgi.com>"
}

variable "scheduler_interval" {
  description = "Interval expression for the scheduler. It is possible to user rate(X minutes), rate(X hours), rate(X days) or cron(0 20 * * ? *)"
  type = string
  default = "rate(3 minutes)" # Using rate
  #default = "cron(0 1 * * ? *)" # Using cron - Remember that we work with UTC time. This example means Every day at 1:00 AM (UTC)
}

variable "cloudwatch_retaition_days" {
  description = "Number of days for CloudWatch logs."
  type = number
  default = 14
}
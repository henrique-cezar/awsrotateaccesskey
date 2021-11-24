resource "aws_ses_email_identity" "source_email" {
  email = var.source_email
}
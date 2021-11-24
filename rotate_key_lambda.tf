data "archive_file" "csg_hackathon_lambda_code" {
    type = "zip"
    source_file = "csg_iam_rotate_old_key_lambda.py"
    output_path = "csg_iam_rotate_old_key_lambda.zip"
}

resource "aws_lambda_function" "csg_hackathon_rote_iam_key" {
    filename = data.archive_file.csg_hackathon_lambda_code.output_path
    function_name = "csg_iam_rotate_old_key_lambda"
    role = aws_iam_role.csg_hackathon_role.arn
    handler = "csg_iam_rotate_old_key_lambda.lambda_handler"

    # The code below guarantee that Terraform will deploy the lambda again, only if any change was made.
    source_code_hash = filebase64sha256(data.archive_file.csg_hackathon_lambda_code.output_path)
  
    runtime = "python3.8"
    environment {
      variables = {
          SOURCE_EMAIL  = var.source_email,
          ROTATE_KEY = var.rotate_key_after_days,
          DEACTIVATE_KEY = var.deactivate_key_after_days,
          DELETE_KEY = var.delete_inactive_key_after_days
      }
    }

    depends_on = [
      data.archive_file.csg_hackathon_lambda_code,
      aws_iam_role.csg_hackathon_role,
      aws_cloudwatch_log_group.csg_hackathon_lambda_log
    ]
}

# Schedule Lambda Function

resource "aws_cloudwatch_event_rule" "csg_hackathon_scheduler" {
    name                = "csg_hackathon_scheduler"
    description         = "Rotate Old IAM Access Keys."
    schedule_expression = var.scheduler_interval 
}

resource "aws_cloudwatch_event_target" "csg_hackathon_target" {
    rule        = aws_cloudwatch_event_rule.csg_hackathon_scheduler.name
    target_id   = "IAMRotateKeys"
    arn         = aws_lambda_function.csg_hackathon_rote_iam_key.arn
}

# Allow cloudwatch to invoke lambda function

resource "aws_lambda_permission" "allow_cloudwatch" {
    statement_id    = "AllowExecutionFromCloudWatch"
    action          = "lambda:InvokeFunction"
    function_name   = aws_lambda_function.csg_hackathon_rote_iam_key.function_name
    principal       = "events.amazonaws.com" 
    source_arn      = aws_cloudwatch_event_rule.csg_hackathon_scheduler.arn  
}

# Define log retaintion
resource "aws_cloudwatch_log_group" "csg_hackathon_lambda_log" {
  name              = "/aws/lambda/csg_iam_rotate_old_key_lambda"
  retention_in_days = var.cloudwatch_retaition_days
}
# Policy for Lambda
resource "aws_iam_policy" "csg_hackathon_policy" {
    name        = "csg_hackathon_policy_rotate_iam_access_key"
    path        = "/"
    description = "Policy for CSG Hackathon 2021."
    
    policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Action": "logs:*",
            "Effect": "Allow",
            "Resource": "*"
        },
        {
            "Sid": "",
            "Action": [
                "ses:SendEmail"
            ],
            "Effect": "Allow",
            "Resource": "*"
        },
        {
            "Sid": "",
            "Action": [
                "iam:ListUsers",
                "iam:*AccessKey*",
                "iam:ListUserTags"
            ],
            "Effect": "Allow",
            "Resource": "*"                
        }
    ]
}
EOF
}

# IAM Role for Lambda
resource "aws_iam_role" "csg_hackathon_role" {
    name = "csg_hackathon_role_rotate_iam_access_key"

    assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {                
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
EOF  
}

# Attach role and policy
resource "aws_iam_role_policy_attachment" "csg_hackathon_attach" {
    role = aws_iam_role.csg_hackathon_role.name
    policy_arn = aws_iam_policy.csg_hackathon_policy.arn

    depends_on = [
      aws_iam_policy.csg_hackathon_policy,
      aws_iam_role.csg_hackathon_role
    ]
}
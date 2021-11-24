#CSG Hackathon - 2021
====

##Project
This project solve the issue related to AWS IAM User's Access Key Rotation.
Based on CSG Policies we need to rotate these Access Keys in certain period and the aim is to automate the process.

##Solution
Using a group of tools to deploy, schedule and execute the rotation:
 1. Terraform - As this solution is based on AWS account, terraform will help us to deploy many times the same solution to any AWS account
 2. Event Bridge - Based on Event Bridge from AWS we can schedule base a rate or a cron expression to trigger a lambda function to execute the task.
 3. Lambda Function - The Lambda will be responsible for:
    * List the Users' Access Keys
    * Check the Age of the Keys
    * Check the Tags to validate if we can rotate the key
    * If the Key match with the requirements we can: Create a New Key, Inactivate an Old Key or even delete an inactive Key.
    * If a new Key is generated, an emails is sent to the email or list of, into the User's tag.

##Requirements
To deploy: 
1. We need an AWS CLI installed and configured.
2. We need to update the file "aws_provider.tf" with that data that reflects the account where you want to deploy
3. We can predefine values into "variables.tf" file where we have definitions for the solutions, like, Source e-mail, Retention for the Logs (in days)
4. We need guarantee that the account where the solution will be deployed have SES in Production mode, not SANDBOX.
5. To rotate the Access Key, the users needs to have 2 TAGS: (autorotate and contact-email):
    * autorotate: Can be populated with true or false. true means that this user wants to autorotate your keys.
    * contact-email: This is an email or list of emails where we will be sending an email with the new key and access key. To provide more than one email we need to separate them by "space".

After the Deploy:
The configuration about time to rotate or Source email ( email used to send the notifications ), we can change it directly on the Lambda Function, but I suggest to execute it using terraform.

##Preparing you environment to Deploy.
1. Copy the bundle
2. Update the file aws_provider.tf
3. Initialize the Terraform (from the source folder: terraform init)
4. Execute the plan for validate your configuration (from the source folder: terraform plan)
5. Deploy the solution (from the source folder: terraform apply --auto-approve)

##Removing the solution from on environment.
If you want to remove the deploy you only need to run a terraform command from the source folder.
This implementation are considering local terraform lock, therefore, the state of you deploy will be stored into you PC.

To remove everything run: terraform destroy --auto-approve

=======
by Henrique do Prado Cezar ( henrique.cezar@csgi.com )
=======
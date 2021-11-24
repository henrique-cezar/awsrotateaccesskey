import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone
import os

lst_aws_users = boto3.client("iam")
sesClient = boto3.client('ses')

# Get the list of users
paginator = lst_aws_users.get_paginator('list_users')


# Time to rotate, deactivate the old one and delete are set in Lambda Function in Environment Variable. 
age_rotate_key      = int(os.environ['ROTATE_KEY'])
age_deactivate_key  = int(os.environ['DEACTIVATE_KEY'])
age_delete_key      = int(os.environ['DELETE_KEY'])
SOURCE_EMAIL        = os.environ['SOURCE_EMAIL']

LIST_USERS=[]

def get_key_age(key_creation_date):
    current_date = datetime.now(timezone.utc)
    age = (current_date - key_creation_date).days
    return age

def send_email(new_access_key, destination_email):
    # In order to send emails to anyone else without to verify the email, you must move your account out of sandbox mode by contacting AWS support and requesting it: https://docs.aws.amazon.com/console/ses/sandbox
    try:

        print(new_access_key)
        username        = str(new_access_key.get('AccessKey').get('UserName'))
        accesskeyid     = str(new_access_key.get('AccessKey').get('AccessKeyId'))
        secretaccesskey = str(new_access_key.get('AccessKey').get('SecretAccessKey'))

        
        body_html = """
        <html>
        <head></head>
        <body>
        <h1>CSG Hackathon - 2021</h1>
        <p>This email was sent to warning you that a new Access Key was generate for: """ + username + """
            <ul>
              <li>AccessKeyId: """ + accesskeyid + """ </li>
              <li>SecretAccessKey: """ + secretaccesskey + """</li>
            </ul>
        <p> ** Your previous Access Key will be inactivated after """ + str(age_deactivate_key) + """ days and will be deleted after """ + str(age_delete_key) + """ days of the creation. Please check your applications.
    
        </body>
        </html>
        """
        body_text = ("CSG Hackathon - 2021\r\n"
                "This email was sent to warning you that a new Access Key was generate for: " + username +
                "* AccessKeyId:"+ accesskeyid +
                "\r\n* SecretAccessKey:" + secretaccesskey + "\r\n"
                "** Your previous Access Key will be inactivated after " + str(age_deactivate_key) + " days and will be deleted after " + str(age_delete_key) + " days of the creation. Please check your applications.")

        # send email using ses
        print("Sending email")
        response=sesClient.send_email(
            Source = SOURCE_EMAIL,
            Destination={ 'ToAddresses': [ destination_email ] },
            Message={
                'Subject': {
                    'Data': 'CSG - AWS User Access Key Rotation.',
                    'Charset': 'utf-8',
                },
                'Body': {
                    'Html': {
                        'Charset': 'utf-8',
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': 'utf-8',
                        'Data': body_text,
                    }
                }
            }
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
    return 0

def check_action(list_users):

    try:
        # We need to check each user 
        for aws_user in list_users:       
            #Check if the Tag autorotate exists and is true
            if aws_user.get('Tags').get('autorotate') == 'true':
                print('Working on: ',aws_user.get('UserName'))
                # As we can have more than one key we need to interate on it.
                for accesskey in aws_user.get('AccessKeys'):
                    print("AccessKeys:",aws_user.get('AccessKeys'))
                    # IF Status Inactive and Age bigger or equal to ${age_delete_key}
                    print("Status=",accesskey.get('Status'), " Age=",accesskey.get('Age'), " Quant=", len(aws_user.get('AccessKeys')))
                    
                    if (accesskey.get('Age') >= age_delete_key and accesskey.get('Status') == 'Inactive' ):
                        print("Deleting Key for the following user: " + aws_user.get('UserName'))
                        del_access_key = lst_aws_users.delete_access_key(UserName=aws_user.get('UserName'), AccessKeyId=aws_user.get('AccessKeyId'))
                   
                    # IF Status Active and Age bigger or equal to ${age_rotate_key} and exists only One Key, to avoid loop of creation before the delete.                        
                    elif ( accesskey.get('Status') == 'Active' and accesskey.get('Age') >= age_rotate_key and len(aws_user.get('AccessKeys')) == 1 ):                        
                        # Creating a new Access Key
                        print("Creating Key for the following user: " + aws_user.get('UserName'))
                        new_access_key = lst_aws_users.create_access_key(UserName=aws_user.get('UserName'))                        
                        # IF more than one e-mail in the contact-email, send one by one.
                        print("Emails:",aws_user.get('Tags').get('contact-email'))
                        # Prepare the destination emails.
                        for user_email in aws_user.get('Tags').get('contact-email').split():
                            print("Sending email to: ", user_email)
                            send_email(new_access_key, user_email )

                    elif ( accesskey.get('Status') == 'Active' and accesskey.get('Age') >= age_deactivate_key and len(aws_user.get('AccessKeys')) > 1):
                    # IF Status Active and Age bigger or equal to ${age_deactivate_key} and has more than one Key for the IAM User.
                        print("Deactivating Key for the following user: " + aws_user.get('UserName'))
                        lst_aws_users.update_access_key(UserName=aws_user.get('UserName'), AccessKeyId=accesskey.get('AccessKeyId'), Status='Inactive')

    except Exception as e:
        print("Exception : " + repr(e))
        
    return 0      
    
def lambda_handler(event, context):

    for response in paginator.paginate():
        for user in response.get('Users'):
            # Check each user if they are set to rotate automatically.
            username = user.get('UserName')
            listtags = lst_aws_users.list_user_tags(UserName=username)

            user_data_dic={}
            # Check if has any Tag for this user
            if len(listtags.get('Tags')):
                user_data_dic['UserName'] = username;
                
                # Looping over the Tags for this user.
                tag_dic={}
                for tag in listtags.get('Tags'):
                    tag_dic[tag.get('Key')] = tag.get('Value')

                user_data_dic['Tags'] = tag_dic
                
                listkey = lst_aws_users.list_access_keys(UserName=username)

                # Initialize AccessKeys structure
                user_data_dic['AccessKeys'] = []
                for accesskey in listkey['AccessKeyMetadata']:
                    user_data_dic['AccessKeys'].append({'AccessKeyId':accesskey.get('AccessKeyId'), 'Status':accesskey.get('Status'), 'Age':get_key_age(accesskey.get('CreateDate'))})

                # Add the user into a list
                LIST_USERS.append(user_data_dic)
    
    return check_action(LIST_USERS)
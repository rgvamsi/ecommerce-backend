import os
import boto3

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

def send_reset_email(recipient_email: str, reset_token: str):
    ses = boto3.client(
        "ses",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )

    reset_link = f"http://localhost:8000/users/reset-password/{reset_token}"
    subject = "Password Reset Request"
    body = f"Click the link to reset your password: {reset_link}"

    ses.send_email(
        Source="vamshikrishna.katkam@atmecs.com",
        Destination={"ToAddresses": [recipient_email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}},
        },
    )

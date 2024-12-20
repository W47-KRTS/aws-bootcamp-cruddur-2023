import json
import psycopg2
import os
import hmac
import hashlib
import base64
import boto3

def generate_secret_hash(client_secret, username, client_id):
    """Generate the SecretHash required for app clients with a secret."""
    message = username + client_id
    dig = hmac.new(client_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(dig).decode()

def lambda_handler(event, context):
    # Extract user attributes from the event
    user = event['request']['userAttributes']
    print('userAttributes:', user)

    user_display_name = user['name']
    user_email = user['email']
    user_handle = user['preferred_username']
    user_cognito_id = user['sub']

    # Cognito client and secret
    client_id = os.getenv('COGNITO_CLIENT_ID')  # Set in Lambda environment variables
    client_secret = os.getenv('COGNITO_CLIENT_SECRET')  # Set in Lambda environment variables
    region = os.getenv('AWS_REGION')  # Set in Lambda environment variables
    cognito = boto3.client('cognito-idp', region_name=region)

    try:
        print('Processing Cognito sign-up...')
        
        # Generate SecretHash for Cognito
        secret_hash = generate_secret_hash(client_secret, user_email, client_id)

        # Perform sign-up with Cognito
        response = cognito.sign_up(
            ClientId=client_id,
            SecretHash=secret_hash,
            Username=user_email,
            Password="TemporaryPassword123!",  # Placeholder password; may vary based on your logic
            UserAttributes=[
                {'Name': 'email', 'Value': user_email},
                {'Name': 'name', 'Value': user_display_name},
                {'Name': 'preferred_username', 'Value': user_handle},
            ],
        )
        print('Cognito sign-up successful:', response)

        print('Inserting user into the database...')
        # SQL to insert user details into PostgreSQL
        sql = """
            INSERT INTO public.users (
                display_name, 
                email,
                handle, 
                cognito_user_id
            ) 
            VALUES(%s, %s, %s, %s)
        """
        conn = psycopg2.connect(os.getenv('CONNECTION_URL'))
        cur = conn.cursor()
        params = [
            user_display_name,
            user_email,
            user_handle,
            user_cognito_id
        ]
        cur.execute(sql, params)  # Corrected params usage for execute()
        conn.commit()
        print('User inserted into the database successfully.')

    except (Exception, psycopg2.DatabaseError) as error:
        print('Error:', error)
    finally:
        if conn:
            cur.close()
            conn.close()
            print('Database connection closed.')

    return event

# 1:03:34:53
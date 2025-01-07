# THE ORIGINAL CODE FROM THE TUTORIAL
# 1:03:34:53
import json
import psycopg2
import os

def lambda_handler(event, context):
    user = event['request']['userAttributes']
    print('userAttributes')
    print(user)

    user_display_name  = user['name']
    user_email         = user['email']
    user_handle        = user['preferred_username']
    user_cognito_id    = user['sub']
    conn = None
    try:
        print('entered-try')
        sql = """
            INSERT INTO public.users (
                display_name, 
                email,
                handle, 
                cognito_user_id
            ) 
            VALUES (%s, %s, %s, %s)
        """
        print('SQL Statement ----')
        print(sql)
        conn = psycopg2.connect(os.getenv('CONNECTION_URL'))
        cur = conn.cursor()

        params = [
            user_display_name,
            user_email,
            user_handle,
            user_cognito_id
        ]
        cur.execute(sql, params)
        conn.commit() 
        print("Data inserted successfully")
    
    except Exception as error:
        print(f"An error occurred: {error}")
    
    finally:
        if conn is not None:
            cur.close()
            conn.close()
            print('Database connection closed.')

    return event

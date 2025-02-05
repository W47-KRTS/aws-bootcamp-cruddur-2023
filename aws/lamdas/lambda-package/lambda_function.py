import json
import psycopg2
import os

def lambda_handler(event, context):
    user = event['request']['userAttributes']
    print('userAttributes:', user)

    user_display_name = user.get('name', 'Unknown')
    user_email = user.get('email', 'no-email@example.com')
    user_handle = user.get('preferred_username', user.get('sub'))  # Fallback to 'sub' if missing
    user_cognito_id = user.get('sub')

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
        if conn:
            cur.close()
            conn.close()
            print('Database connection closed.')

    return event

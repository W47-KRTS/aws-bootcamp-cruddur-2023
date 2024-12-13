import json
import os
import psycopg2

def lamda_handler(event, context):
    user = event['request']['userAttributes']
    print('userAttributes')
    print(user)

    user_display_name   = user['name']
    user_email          = user['email']
    user_handle          = user['preffered_username']
    user_cognito_id     = user['sub']

    try:
        conn = psycopg2.connect(os.getenv('CONNECTION_URL'))
        cur = conn.cursor()
        (user['name'], user['email'], user['sub'])

        sql = f"""
        "INSERT INTO users (
        display_name, 
        email,
        handle, 
        cognito_user_id
        ) 
        VALUES(
            {user_display_name}, 
            {user_email}, 
            {user_handle},
            {user_cognito_id}
        )"
        """
        cur.execute(sql)
        conn.commit()

    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            cur.close()
            conn.close()
            print('Database connection closed.')

    return event

# 1:03:34:53
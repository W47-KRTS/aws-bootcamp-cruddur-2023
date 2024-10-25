import json
import os
import psycopg2

def lamda_handler(event, context):
    user = event['request']['userAttributes']
    try:
        conn = psycopg2.connect(os.getenv('CONNECTION_URL'))
        cur = conn.cursor()
        sql = f"""
        "INSERT INTO users (display_name, handle, cognito_user_id) 
        VALUES({name}, {email}, {sub})"
        """
        cur.execute("INSERT INTO users (display_name, handle, cognito_user_id) VALUES(%s, %s, %s)", (user['name'], user['email'], user['sub']))
        conn.commit()

    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            cur.close()
            conn.close()
            print('Database connection closed.')

    return event

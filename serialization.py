import json
import os
import psycopg2

import user_store


# Where the Database is located
DATABASE_URL = os.environ['DATABASE_URL']


def write_user_map_to_db(user_map):
    """ Writes a dict representation of the user_map to a database """
    print("writing user_map to db")

    try:
        for user in user_map:
            put_user_in_table(user_map[user].to_dict())
            user_map[user].set_is_new_user(False)
    except IOError:
        print("Error writing to DB.")


def load_user_map_from_db():
    """ Loads database users into the bot's user_map """
    user_map = {}

    try:
        users = get_users_from_table()
        for user in users:
            user_dict = {
                "user_id" : user[0],
                "username" : user[1],
                "id_last_message_sent" : user[2],
                "id_last_message_stickered" : user[3],
                "count_since_last_stickered" : user[4],
                "is_new_user" : False
            }
            us = user_store.UserStore(data_dict=user_dict)
            user_map[us.get_user_id()] = us
        print("user_map loaded")
    except IOError:
        print("Database load failed.  Loading empty user_map.")
    
    return user_map


def create_new_user_table():
    """ Creates a new table in the database for user data if does not exist """
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    # Open a cursor to perform db operations
    cur = conn.cursor()
    # Create the table
    cur.execute("""
        CREATE TABLE test (
            user_id int NOT NULL PRIMARY KEY,
            username varchar(255),
            id_last_message_sent int,
            id_last_message_stickered int,
            count_since_last_stickered int
        );
        """
    )
    # Commit and close connection
    conn.commit()
    cur.close()
    conn.close()


def put_user_in_table(user_dict):
    """ Adds or updates a user in the database based on their in memory data """
     # Connect to database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    # Open a cursor to perform db operations
    cur = conn.cursor()
    # Insert the user if they do not exist
    if user_dict["is_new_user"] == True:
        cur.execute("""
            INSERT INTO test (user_id, username, id_last_message_sent, 
                id_last_message_stickered, count_since_last_stickered)
            VALUES (%s, %s, %s, %s, %s)
            ;
            """,
            (
                user_dict["user_id"],
                user_dict["username"], 
                user_dict["id_last_message_sent"], 
                user_dict["id_last_message_stickered"],
                user_dict["count_since_last_stickered"]
            )
        )
    # Update the user if they do exist
    else:
        cur.execute("""
            UPDATE test 
            SET username = %(username)s, 
                id_last_message_sent = %(IdLMS)s, 
                id_last_message_stickered = %(IdLMSt)s,
                count_since_last_stickered = %(CSLSt)s
            WHERE user_id = %(user_id)s
            ;
            """,
            {
                "user_id" :  user_dict["user_id"],
                "username" : user_dict["username"], 
                "IdLMS" : user_dict["id_last_message_sent"], 
                "IdLMSt" : user_dict["id_last_message_stickered"],
                "CSLSt" : user_dict["count_since_last_stickered"]
            }
        )
    # Commit and close connection
    conn.commit()
    cur.close()
    conn.close()

def get_users_from_table():
    """ Retrieves all of the users from database and returns the list """
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    # Open a cursor to perform db operations
    cur = conn.cursor()
    # Query the table
    cur.execute("""
        SELECT *
        FROM test 
        ;
        """
    )
    rows = cur.fetchall()
    # Commit and close connection
    conn.commit()
    cur.close()
    conn.close()
    return rows

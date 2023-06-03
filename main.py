import psycopg2
import db_settings
from client import Client

def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""DROP TABLE IF EXISTS client, phone_number""")

        cur.execute("""CREATE TABLE IF NOT EXISTS client(
        client_id SERIAL PRIMARY KEY,
        name VARCHAR(40) NOT NULL,
        surname VARCHAR(40) NOT NULL,
        email VARCHAR(20));
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS phone_number(
        number INTEGER PRIMARY KEY,
        client_id INTEGER REFERENCES client(client_id));
        """)
        conn.commit()

def add_client(conn, client):
    with conn.cursor() as cur:
        numbers = get_all_phones(cur)
        if check_client_data():
            cur.execute("""INSERT INTO client(name, surname, email) VALUES (%s, %s, %s) RETURNING client_id""", (client.name, client.surname, client.email))
            id = cur.fetchone()
            for num in client.phone_numbers:
                cur.execute("""INSERT INTO phone_number(number, client_id) VALUES (%s, %s)""",
                                (num, id)) if num not in numbers else print(f'Wrong phone number {num} was not added to database')
            conn.commit()
        else: print('Wrong data!')

def add_phone(conn, phone_number, client_id):
    with conn.cursor() as cur:
        if (check_client_id(cur, client_id)):
            numbers = get_all_phones(cur)
            cur.execute("""INSERT INTO phone_number(number, client_id) VALUES (%s, %s)""", (phone_number, client_id)) if phone_number not in numbers else print("Wrong phone number!")
            conn.commit()
        else:
            print("Wrong client id!")

def update_client(conn, old_client_id, new_client):
    with conn.cursor() as cur:
        if check_client_data(new_client):
            cur.execute("""UPDATE client 
            SET name = %s, surname = %s, email = %s
            WHERE client_id = %s""", (new_client.name, new_client.email, new_client.surname, old_client_id))
            conn.commit()
        else:
            print("Wrong new client data")

def delete_phone(conn, phone_number):
    with conn.cursor() as cur:
        cur.execute("""DELETE FROM phone_number WHERE number = %s""", (phone_number,))
        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""DELETE FROM phone_number WHERE client_id = %s""", (client_id,))
        cur.execute("""DELETE FROM client WHERE client_id = %s""", (client_id,))
        conn.commit()

def get_client(conn, name='%', surname='%', email='%', phone=None):
    with conn.cursor() as cur:
        if phone is None:
            cur.execute("""SELECT c.client_id, c.name, c.surname, c.email FROM client c
            WHERE name LIKE %s AND surname LIKE %s AND email LIKE %s""", (name, surname, email))
        else:
            cur.execute("""SELECT c.client_id, c.name, c.surname, c.email FROM client c
            JOIN phone_number p_n on p_n.client_id = c.client_id
            WHERE name LIKE %s AND surname LIKE %s AND email LIKE %s AND p_n.number = %s""", (name, surname, email, phone))
        return cur.fetchall()

def get_all_phones(cur):
    cur.execute("""SELECT p.number FROM phone_number p""")
    numbers = list(map(lambda x: x[0], cur.fetchall()))
    return numbers

def check_client_data(client):
    return isinstance(client, Client) and len(client.name) <= 40 and len(client.surname) <= 40 and len(client.email) <= 40

def check_client_id(cur, client_id):
    cur.execute("""SELECT * FROM client WHERE client_id = %s""", (client_id,))
    return cur.fetchone()

def main():
    conn = psycopg2.connect(database=db_settings.database, user=db_settings.user, password=db_settings.password)
    conn.close()

if __name__ == '__main__':
    main()
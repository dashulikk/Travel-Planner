import psycopg2
from psycopg2.extensions import connection as postgres_connection, cursor as postgres_cursor
import os


class Database:
    def __init__(self):
        try:
            dbname = os.environ['RDS_DB_NAME']
            user = os.environ['RDS_USERNAME']
            host = os.environ['RDS_ENDPOINT']
            password = os.environ['RDS_PASSWORD']
            port = os.environ['RDS_PORT']
            self.conn: postgres_connection = psycopg2.connect(
                database=dbname,
                user=user,
                host=host,
                password=password,
                port=port
            )
            self.cursor: postgres_cursor = self.conn.cursor()
            print("Database connection established successfully.")
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            raise
    def add_user(self, username: str, email: str, password_hash: str, salt: str):
        try:
            self.cursor.execute("""
                INSERT INTO users (username, email, password_hash, salt)
                VALUES (%s, %s, %s, %s) RETURNING id;
            """, (username, email, password_hash, salt))
            self.conn.commit()
            user_id = self.cursor.fetchone()[0]
            print("User added successfully.")
            return user_id
        except Exception as e:
            self.conn.rollback()
            print(f"Error adding user: {e}")
            raise

    def get_user_by_email(self, email: str):
        try:
            self.cursor.execute("""
                SELECT id, username, email, password_hash, salt
                FROM users
                WHERE email = %s;
            """, (email,))
            user = self.cursor.fetchone()
            if user:
                return {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "password_hash": user[3],
                    "salt": user[4]
                }
            return None
        except Exception as e:
            print(f"Error retrieving user: {e}")
            raise

    def create_trip(self, user_id: int, name: str, city: str, country: str, start_date: str, end_date: str):
        self.cursor.execute("""
            INSERT INTO trips (user_id, name, city, country, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, reference_id;
        """, (user_id, name, city, country, start_date, end_date))
        self.conn.commit()
        return self.cursor.fetchone()

    def add_checklist_item(self, trip_id: int, description: str, estimated_cost: float):
        self.cursor.execute("""
            INSERT INTO checklist (trip_id, description, estimated_cost)
            VALUES (%s, %s, %s) RETURNING id;
        """, (trip_id, description, estimated_cost))
        self.conn.commit()
        return self.cursor.fetchone()[0]

    def update_checklist_item(self, item_id: int, is_completed: bool):
        self.cursor.execute("""
            UPDATE checklist SET is_completed = %s WHERE id = %s;
        """, (is_completed, item_id))
        self.conn.commit()

    def add_hotel(self, trip_id: int, name: str, check_in: str, check_out: str, estimated_cost: float):
        self.cursor.execute("""
            INSERT INTO hotels (trip_id, name, check_in, check_out, estimated_cost)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """, (trip_id, name, check_in, check_out, estimated_cost))
        self.conn.commit()
        return self.cursor.fetchone()[0]

    def add_transport(self, trip_id: int, type_: str, company: str, departure_city: str, arrival_city: str,
                      departure_time: str, arrival_time: str, estimated_cost: float):
        self.cursor.execute("""
            INSERT INTO transport (trip_id, type, company, departure_city, arrival_city, departure_time, arrival_time, estimated_cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """, (trip_id, type_, company, departure_city, arrival_city, departure_time, arrival_time, estimated_cost))
        self.conn.commit()
        return self.cursor.fetchone()[0]

    def close_connection(self):
        try:
            self.cursor.close()
            self.conn.close()
            print("Database connection closed.")
        except Exception as e:
            print(f"Error closing the connection: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_connection()

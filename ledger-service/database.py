import os
import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="ledger",
        user="postgres",
        password="postgres",
        host="postgres",
        port=5432
    )
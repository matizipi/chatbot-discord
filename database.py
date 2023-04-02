import mysql.connector

# Credenciales de la base de datos
host = 'bpjt6mwo9pnwdc7l2wzr-mysql.services.clever-cloud.com'
database = 'bpjt6mwo9pnwdc7l2wzr'
user = 'uigdbnmivcd5qpcf'
password = 'WnjwQwnC98o7LU3jKFcq'


def create_tables(mydb):
    cursor = mydb.cursor()

    # Crea tabla 'support_chatbot'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_chatbot (
            id INT AUTO_INCREMENT PRIMARY KEY,
            question VARCHAR(255) NOT NULL,
            answer VARCHAR(255) NOT NULL,
            helpful_responses INT NOT NULL DEFAULT 0,
            unhelpful_responses INT NOT NULL DEFAULT 0,
            state_answer VARCHAR(255) NOT NULL DEFAULT "appropiate"
        )
    """)
    # Crea tabla 'questions'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            question VARCHAR(255) NOT NULL
        )
    """)

    mydb.commit()
    cursor.close()


def connect_database():

    # Conectar a la base de datos
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    create_tables(mydb)

    return mydb

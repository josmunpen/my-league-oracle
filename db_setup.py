import sqlite3

def create_sqlite_database(filename):
    """ create a database connection to an SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(filename)
        print(f"Connecting to db {filename}...")
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def create_tables():
    sql_statements = [ 
        """CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY,
                team_id INTEGER,
                query_date DATE,
                name TEXT, 
                history TEXT,
                total_played INT,
                wins_home INT,
                wins_away INT,
                draws_home INT,
                draws_away INT,
                loses_home INT,
                loses_away INT,
                goals_for_home INT,
                goals_for_away INT,
                goals_against_home INT,
                goals_against_away INT
        );""",
        """CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY,
                fixture INT,
                match_date DATE,
                team_home INT, 
                team_away INT,
                result_predict TEXT,
                result_real TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS requests (
                date DATE PRIMARY KEY,
                num_requests INTEGER
        );"""]
    # create a database connection
    try:
        with sqlite3.connect('soccer.db') as conn:
            cursor = conn.cursor()
            for statement in sql_statements:
                cursor.execute(statement)
            
            conn.commit()
    except sqlite3.Error as e:
        print(e)


if __name__ == '__main__':
    create_sqlite_database("soccer.db")
    create_tables()
"""turbo_palm_tree (tpt) database manager"""

import os, time, sys
import psycopg2
import sqlite3



class TPTDatabaseManager:

    def __init__(self):
        root_dir = os.path.dirname(__file__)
        db_filename = 'tpt.db'
        db_file_path = os.path.join(root_dir, db_filename)

        self.connection = sqlite3.connect(db_file_path)
        self.cursor = self.connection.cursor()

        # create table
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS reddit_downloads (
            id serial PRIMARY KEY,
            subreddit varchar,
            title varchar,
            url varchar,
            reddit_id varchar,
            file_path varchar);""")

        # insert some data
        self.cursor.execute("INSERT INTO reddit_downloads (subreddit, title)\
            VALUES ('pics', 'crazy pic title!!!')")

        # write changes to db file
        self.connection.commit()

        # select all, get all
        self.cursor.execute("SELECT * FROM reddit_downloads")
        rows = self.cursor.fetchall()

        for row in rows:
            print(row)


if __name__ == "__main__":
    db = TPTDatabaseManager()

"""turbo_palm_tree (tpt) database manager"""

import os, time, sys
import sqlite3


class TPTDatabaseManager:
    """`tpt.db` is the database name and `reddit_downloads` is the table name"""


    def __init__(self):
        """Create db and table if not created"""
        root_dir = os.path.dirname(__file__)
        db_filename = 'tpt.db'
        db_file_path = os.path.join(root_dir, db_filename)

        self.connection = sqlite3.connect(db_file_path)
        self.cursor = self.connection.cursor()

        # create table
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS reddit_downloads (
            id integer primary key autoincrement,
            subreddit varchar,
            title varchar,
            url varchar,
            comments_url varchar,
            reddit_id varchar,
            file_path varchar,
            dl_time time);""")


    def insert_data(self, data):
        """Insert data into table
        :param data: dictionary with keys of table column names and values to
            insert
        """
        self.cursor.execute("""INSERT INTO reddit_downloads
            (subreddit, title, url, comments_url, reddit_id, file_path, dl_time)
            VALUES (:subreddit, :title, :url, :comments_url, :reddit_id,
                :file_path, :dl_time);""",
            data)


    def print_all(self):
        """select all, fetch all, print all"""
        self.cursor.execute("SELECT * FROM reddit_downloads")
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)


    def close(self):
        """Close & save changes made to database, should be done before
        program exit
        """
        self.connection.commit()
        self.connection.close()


if __name__ == "__main__":
    db = TPTDatabaseManager()
    my_data = {
        'subreddit': 'pics',
        'title': 'This also Japan',
        'url': 'http://i.imgur.com/z16hW1S.jpg',
        'comments_url': 'https://www.reddit.com/r/pics/comments/58ocl8/this_also_japan/',
        'reddit_id': '58ocl8',
        'file_path': '/home/j/Downloads/walking\ the\ dog.jpg',
        'dl_time': '10/10/16 13:00'
    }
    db.insert_data(my_data)
    db.close()

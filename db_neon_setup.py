import pandas as pd
from sqlalchemy.orm import Session
import sqlite3
import logging
import argparse

from backend.db import engine
from backend import db_models

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

def db_setup(to_populate, to_export, to_remove=False):

    # Export
    if to_export:
        try:
            for table in to_export:
                export_db(table, year=2022)
        except Exception as e:
            log.warn(f'Unable to export table {table}', repr(e))

    # Delete tables
    if to_remove == True:
        try: 
            # Deleting old tables
            log.info("Droping all tables")
            db_models.Base.metadata.drop_all(engine)
        except Exception as e:
            log.warn('Unable to create tables', repr(e))


    # Create tables
    log.info("Creating all tables")
    db_models.Base.metadata.create_all(engine)

    # Populate tables
    if to_populate:
        db = Session(engine)
        try:
            for table in to_populate:
                populate_table(db, table)
        except Exception as e:
            db.rollback()
            log.warn('Unable to populate tables', repr(e))
        else:
            db.commit()
            log.info(f'Data commited successfully')

def populate_table(db, table, year=2022):
    log.info(f"Populating table {table} with {year} data")
    df = pd.read_csv(f"./exports/{year}_{table}.csv")
    df.to_sql(table, db.bind, if_exists="append", index=False)

def export_db(table, year=2022):
    log.info(f"Exporting data with {year} data")
    with sqlite3.connect('../db/soccer.db') as conn:
        df = pd.read_sql(f'select * from {table}', conn)
    df.to_csv(f"./exports/{year}_{table}.csv", index=False)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--delete', dest='to_remove', action='store_true', help='Remove all tables')
    parser.add_argument('--populate', dest='to_populate', nargs='+', help='Populate tables')
    parser.add_argument('--export', dest='to_export', nargs='+', help="Tables to export")
    # parser.add_argument('--export_year', dest='to_export_year', nargs='+', help="Tables to export")
    args = parser.parse_args()

    db_setup(to_remove = args.to_remove,
             to_populate = args.to_populate,
             to_export = args.to_export)

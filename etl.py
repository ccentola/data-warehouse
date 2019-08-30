import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    """ 
    loads data from S3 buckets to Redshift
    """
    for query in copy_table_queries:
        print(f'Loading data: {query}')
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    """ 
    insert from staging tables to fact and dimension tables 
    """
    for query in insert_table_queries:
        print(f'Insert data: {query}')
        cur.execute(query)
        conn.commit()


def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    print('Connecting to Redshift')
    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    print('Connected to Redshift')
    
    # execute staging tables
    try:
        print('Loading staging tables')
        load_staging_tables(cur, conn)
        print('Loading staging tables SUCCESS')
    except Exception as e:
        print(e)
        print('Loading staging tables FAILED')
    
    # execute table inserts
    try:
        print('Transform from staging')
        insert_tables(cur, conn)
        print('Transform from staging SUCCESS')
    except Exception as e:
        print(e)
        print('Transform from staging FAILED')

    conn.close()
    print('ETL completed')


if __name__ == "__main__":
    main()
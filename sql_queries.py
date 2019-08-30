import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplay"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create = ("""
CREATE TABLE staging_events(
    event_id            IDENTITY(0,1),
    artist_name               VARCHAR,
    auth                      VARCHAR,
    user_first_name           VARCHAR,
    user_gender               VARCHAR,
    item_in_session	          INTEGER,
    user_last_name            VARCHAR,
    song_length	              NUMERIC, 
    user_level                VARCHAR,
    location                  VARCHAR,	
    method                    VARCHAR,
    page                      VARCHAR,	
    registration              VARCHAR,	
    session_id	               BIGINT,
    song_title                VARCHAR,
    status                    INTEGER,	
    ts                        VARCHAR,
    user_agent                   TEXT,	
    user_id                   VARCHAR,
    PRIMARY KEY (event_id)
)
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs (
    num_songs          INTEGER,
    artist_id          VARCHAR,
    artist_latitude    NUMERIC,
    artist_longitude   NUMERIC,
    artist_location    VARCHAR,
    artist_name        VARCHAR,
    song_id            VARCHAR,
    title              VARCHAR,
    duration           NUMERIC,
    year                   INT
)
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplay (
    songplay_id bigint      IDENTITY(0,1),
    start_time           VARCHAR NOT NULL,
    user_id              VARCHAR NOT NULL,
    level                         VARCHAR,
    song_id                       VARCHAR,
    artist_id                     VARCHAR,
    session_id                    VARCHAR,
    location                      VARCHAR,
    user_agent                    VARCHAR,
    PRIMARY KEY (songplay_id)
)
""")

user_table_create = ("""
CREATE TABLE users(
    user_id        VARCHAR,
    first_name     VARCHAR,
    last_name      VARCHAR,
    gender         VARCHAR,
    level          VARCHAR,
    PRIMARY KEY (user_id)
)
""")

song_table_create = ("""
CREATE TABLE songs(
    song_id                VARCHAR,
    title                  VARCHAR,
    artist_id     VARCHAR NOT NULL,
    year                   INTEGER,
    duration               NUMERIC,
    PRIMARY KEY (song_id)
)
""")

artist_table_create = ("""
CREATE TABLE artists(
    artist_id          VARCHAR,
    name               VARCHAR,
    location           VARCHAR,
    latitude           NUMERIC,
    longitude          NUMERIC,
    PRIMARY KEY (artist_id)
)
""")

time_table_create = ("""
CREATE TABLE time(
    start_time        TIMESTAMP,
    hour                INTEGER,
    day                 INTEGER,
    week                INTEGER,
    month               INTEGER,
    year                INTEGER,
    weekday             INTEGER,
    PRIMARY KEY (start_time)
)
""")

# STAGING TABLES

# SQL queries for copying data from s3 into redshift staging table
staging_events_copy = ("""
COPY staging_events from 's3://udacity-dend/log_data'
CREDENTIALS 'aws_iam_role=arn:aws:iam::575425287772:role/myRedshitRole'
REGION 'us-west-2'
COMPUPDATE OFF STATUPDATE OFF
FORMAT AS JSON 's3://udacity-dend/log_json_path.json';
""")

staging_songs_copy = ("""
copy staging_songs from 's3://udacity-dend/song_data'
CREDENTIALS 'aws_iam_role=arn:aws:iam::575425287772:role/myRedshitRole'
REGION 'us-west-2'
COMPUPDATE OFF STATUPDATE OFF
JSON 'auto';
""")
#.format(config['IAM_ROLE']['ARN'])

# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplay (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent) 
    SELECT DISTINCT 
        TIMESTAMP 'epoch' + ts/1000 *INTERVAL '1 second' as start_time, 
        e.user_id, 
        e.user_level,
        s.song_id,
        s.artist_id,
        e.session_id,
        e.location,
        e.user_agent
    FROM staging_events e, staging_songs s
    WHERE e.page = 'NextSong'
    AND e.song_title = s.title
    AND user_id NOT IN (SELECT DISTINCT s.user_id FROM songplay s WHERE s.user_id = user_id
                       AND s.start_time = start_time AND s.session_id = session_id )
""")
 
user_table_insert = ("""INSERT INTO users (user_id, first_name, last_name, gender, level)  
    SELECT DISTINCT 
        user_id,
        user_first_name,
        user_last_name,
        user_gender, 
        user_level
    FROM staging_events
    WHERE page = 'NextSong'
    AND user_id NOT IN (SELECT DISTINCT user_id FROM users)
""")

song_table_insert = ("""INSERT INTO songs (song_id, title, artist_id, year, duration) 
    SELECT DISTINCT 
        song_id, 
        title,
        artist_id,
        year,
        duration
    FROM staging_songs
    WHERE song_id NOT IN (SELECT DISTINCT song_id FROM songs)
""")

artist_table_insert = ("""INSERT INTO artists (artist_id, name, location, latitude, longitude) 
    SELECT DISTINCT 
        artist_id,
        artist_name,
        artist_location,
        artist_latitude,
        artist_longitude
    FROM staging_songs
    WHERE artist_id NOT IN (SELECT DISTINCT artist_id FROM artists)
""")

time_table_insert = ("""INSERT INTO time (start_time, hour, day, week, month, year, weekday)
    SELECT 
        start_time, 
        EXTRACT(hr from start_time) AS hour,
        EXTRACT(d from start_time) AS day,
        EXTRACT(w from start_time) AS week,
        EXTRACT(mon from start_time) AS month,
        EXTRACT(yr from start_time) AS year, 
        EXTRACT(weekday from start_time) AS weekday 
    FROM (
    	SELECT DISTINCT  TIMESTAMP 'epoch' + ts/1000 *INTERVAL '1 second' as start_time 
        FROM staging_events s     
    )
    WHERE start_time NOT IN (SELECT DISTINCT start_time FROM time)
""")

# QUERY LISTS

create_table_queries = [
    staging_events_table_create, 
    staging_songs_table_create, 
    songplay_table_create, 
    user_table_create, 
    song_table_create, 
    artist_table_create, 
    time_table_create
]

drop_table_queries = [
    staging_events_table_drop, 
    staging_songs_table_drop, 
    songplay_table_drop, 
    user_table_drop, 
    song_table_drop, 
    artist_table_drop, 
    time_table_drop
]

copy_table_queries = [
    staging_events_copy, 
    staging_songs_copy
]

insert_table_queries = [
    songplay_table_insert, 
    user_table_insert, 
    song_table_insert, 
    artist_table_insert, 
    time_table_insert
]

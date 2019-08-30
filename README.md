# Sparkify Data Warehouse

## Summary

Sparkify, the music streaming app, has gained popularity (and a number of new users in the process). In order to stay true to thir commitment of finding insights through songs that their users are listening to, Sparkify is now considering data warehouse solution sin the cloud.

All of Sparkify's user logs and song data now reside in S3. This project creates an ETL pipeline that stages the log and song data in Redshift and transforms the data into a set of fact and dimensional tables to facilitate further investigation by the analytics team.

## Project Structure

This repository is structured as follows:

```
.
├── dhw.cfg           # Configuration file containing Redshift, IAM, and S3 credentials
├── sql_queries.py    # Contains SQL queries executed by create_tables.py and etl.py
├── create_tables.py  # Creates Redshift tables; drops if they exists
├── etl.py            # Extracts data from S3 and load into Redshift
├── requirements.txt  # Python libraries required to recreate
└── README.md

```

## Database Design
This project implements a star schema. `songplays` is the fact table in the data model, while `users`, `songs`, `artists`, and `time` are all dimensional tables.

**Staging Tables**
Used to stage raw files from S3 into Redshift for further transformation.
* `staging_events`
* `staging_songs`

**Fact Table**
* `songplays` - records in event data associated with song plays (records with page = NextSong)
  * `songplay_id`, `start_time`, `user_id`, `level`, `song_id`, `artist_id`, `session_id`, `location`, `user_agent`

**Dimension Tables**
* `users` - users of the Sparkify app.
  * `user_id`, `first_name`, `last_name`, `gender`, `level`
* `songs` - collection of songs.
  * `song_id`, `title`, `artist_id`, `year`, `duration`
* `artists` - information about artists.
  * `artist_id`, `name`, `location`, `lattitude`, `longitude`
* `time` - timestamps of records in songplays deconstructed into various date-time parts.
  * `start_time`, `hour`, `day`, `week`, `month`, `year`, `weekday`


## How to Run

In order to complete the ETL process successfully, you must have an AWS Redshift Cluster up and running with an associated IAM role with the correct permissions: `AmazonS3ReadOnlyAccess`, `AmazonRedshiftFullAccess`. Once the cluster is running, provide the following information in dwh.cfg:
* `HOST`
* `DB_NAME`
* `DB_USER`
* `DB_PASSWORD`
* `DB_PORT`
* `IAM_ROLE`

All of these credientials will be a part of the cluster creation process in AWS. Once all the credentials are gathered, run the following scripts:
1. Run `create_tables.py` to clean the environment and create new tables.
2. Run `etl.py` to extract data from JSON files in S3, stage in Redshift, and store in the dimensional tables. (***note*** that this step may take a while depending on the number of nodes in your cluster configuration)
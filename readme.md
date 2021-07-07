# What's this?

This is a simple tool downloads a list of CTI feeds, then compares current downloaded version with previos (hashes) and send statistics to Clickhouse database.

## How can I use it?

* Git clone this repo
* Make your own `.env` file (use `.env.sample` for example)
* Just run: `docker-compose up -d`

## Which CTI feeds?

Take a look at `/src/config/feeds.yaml`

## How often CTI feeds will be cheked?

Default value is every 60 minutes. If you want to use your own value — specify it in variable `FEEDS_UPDATE_INTERVAL` in your `.env` file.

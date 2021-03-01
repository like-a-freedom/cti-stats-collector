# What's this?

This is a simple tool downloads a list of CTI feeds, then compares current downloaded version with previos (hashes) and send statistics to InfluxDB database.

## How can I use it?

* Git clone this repo
* Make your own `.env` file (use `.env.sample` for example)
* Just run: `docker-compose up -d`

## Which CTI feeds?

Take a look at `/src/config/feeds.yaml`

# MineOps Web Application

MineOps is a lightweight Flask based web app intended for internal LAN use on a remote mine site. It consolidates patrol logging, hazard tracking, maintenance records and trail cam photo review in one interface.

## Features
* Dashboard with navigation to each module
* Log security patrols with optional photo uploads
* Record and track hazards with severity/status fields
* Track equipment maintenance
* Upload and view trail camera photos
* Export data to CSV or PDF

## Running locally with Docker
```bash
cd mineops
docker-compose build
docker-compose up
```
Navigate to `http://localhost:5000`.

To populate sample data run:
```bash
docker-compose run mineops python sample_data.py
```

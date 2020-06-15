# Folding@Home Stats Backend

This directory contains the backend component for monitoring team statistics.

Attention: The current state is quick & dirty and was created within a very short time. We are trying to adapt the code and the description at short notice.

## Purpose

The development of the team ranking is to be monitored in order to be able to show the progress. The backend takes care of the query of the team statistics and the persistence of the relevant data.

## Configuration

In the file ``folding-stats.json``` the required configurations can be set. The configuration that applies to our team is attached and can be adapted to the respective needs.

```
{
    "baseurl":"https://stats.foldingathome.org/api/team/",
    "team": 263581,
    "database":{
        "sqlite": "data/folding-stats.db",
        "csv": "data/folding-stats.csv",
        "rid":"data/folding-stats.rid"
    }
}
```
```baseurl```: Base url of Folding at Home API
```team```: numeric value representing your team
```database/sqlite```: relative path to sqlite database
```database/csv```: relative path to csv file
```database/rid```: relative path to rank id file (last known rank)

## Local execution

### Installation

Only Python and the corresponding modules must be installed.

### Execution

The backend can be started by the call

```
python3 folding-stats.py
```

can be executed.

## Docker execution

### Build

Build docker container:

```
docker build --pull -t generaliinformatik/folding-stats .
```

### Execution

Run container with command:
```
docker run -d generaliinformatik/folding-stats
```

To mount local directories to your container we suggest the following command. Replace <local> with the path to a valid local directory and place at least the configuration file into this path.

```
docker run -d -v <local>/backend/folding-stats.json:/code/folding-stats.json -v <local>/backend/data/:/code/data/ -v <local>/backend/logs/:/code/logs/ generaliinformatik/folding-stats
```

## Test

Delete the file ```data/folding-stats.rid``` to force a write of the current data. The script thinks that the rank has changed and writes the information to the database/CSV with the current timestamp.
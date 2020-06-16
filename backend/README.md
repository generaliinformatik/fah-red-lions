# Folding@Home Stats (Backend)

This directory contains the backend component for monitoring team statistics.

Attention: The current state is quick & dirty and was created within a very short time. We are trying to adapt the code and the description at short notice.

## Purpose

The development of the team ranking is to be monitored in order to be able to show the progress. The backend takes care of the query of the team statistics and the persistence of the relevant data.

## Configuration

In the file ```folding-stats.json``` the required configurations can be set. The configuration that applies to our team is attached and can be adapted to the respective needs.

```sql
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

```bash
python3 folding-stats.py
```

can be executed.

## Docker execution

### Build

Build docker container:

```bash
docker build --pull -t generaliinformatik/folding-stats .
```

### Execution

Run container with command:

```bash
docker run -d generaliinformatik/folding-stats
```

To mount local directories to your container we suggest the following command. Replace ```<local>``` with the path to a valid local directory and place at least the configuration file into this path.

```bash
docker run -d -v <local>/backend/folding-stats.json:/code/folding-stats.json -v <local>/backend/data/:/code/data/ -v <local>/backend/logs/:/code/logs/ generaliinformatik/folding-stats
```
## Pre-build image

Auf Docker Hub steht ein Image für den Gebrauch zur Verfügung. Das Image wird immer aktualisiert, wenn der Master Branch in diesem Repository aktualisiert wird. Für die Nutzung dieses Images empfehlen wir die Konfiguration mit den oben dokumentierten Mount-Volumes.

Docker Hub: [generaliinformatik/fah-red-lions-backend](https://hub.docker.com/repository/docker/generaliinformatik/fah-red-lions-backend)

## Test

Delete the file ```data/folding-stats.rid``` to force a write of the current data. The script thinks that the rank has changed and writes the information to the database/CSV with the current timestamp.

## Database

### Schemes

#### Table 'stats'

In the table ```stats``` the ranking information of the team is recorded. The recording is usually done when the rank changes (or the *.rid file is deleted)).

```sql
CREATE TABLE IF NOT EXISTS stats (
  "datetime" text,
  team integer,
  rank integer
);
```

#### Table 'team'

In the Team table, the team members are recorded with the relevant attributes in order to be able to evaluate their trends historically. At a later stage, the changes can be displayed as a graph or time line, for example. The data is only captured if there have been changes to the rank of the team, since in this case there must have been a change to the attributes ```rank``` or ```credit``` for at least one team member.

```sql
CREATE TABLE IF NOT EXISTS team (
  "datetime" text,
  id integer,
  name text,
  rank integer,
  credit integer
);
```

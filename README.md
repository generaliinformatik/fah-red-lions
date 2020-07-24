# Folding@Home Stats

![line](images/line.png)  
🇩🇪 Die Anleitung zur Einrichtung des Folding@Home-Clients als Team-Mitglied von "The Red Insurance Lions - Worldwide" ist [hier](http://bit.ly/red-lions-instructions-german) zu finden. Wir haben das Format für eine bessere Lesbarkeit auf Gitbook umgestellt.

🇬🇧 Instructions for setting up the Folding@Home client as a team member of "The Red Insurance Lions - Worldwide" can be found [here](http://bit.ly/red-lions-instructions-english). We have changed the format to Gitbook for better readability.
![line](images/line.png). 

## Purpose

The development of the team ranking is to be monitored in order to be able to show the progress. The backend takes care of the query of the team statistics and the persistence of the relevant data.

<img src="https://github.com/generaliinformatik/fah-red-lions/blob/master/images/dashboard.png?raw=true" alt="dashboard" width="100%"/>
Example of dashboard

## Configuration

In the file ```folding-stats.json``` the required configurations can be set. The configuration that applies to our team is attached and can be adapted to the respective needs.

```sql
{
    "baseurl":"https://stats.foldingathome.org/api/team/",
    "team": 263581,
    "database":{
        "sqlite": "data/folding-stats.db",
        "csv": "data/folding-stats.csv",
        "supporter": "data/supporter.csv"
    }
}
```

```baseurl```: Base url of Folding at Home API  
```database/sqlite```: relative path to sqlite database  
```database/csv```: relative path to csv file  
```database/supporter```: relative path to supporter file

## Local execution

### Installation

Only Python and the corresponding modules must be installed:

```bash
pip3 install -r requirements.txt
```

### Manual Execution

At first you have to set the environment variable `FAH_TEAMID` which represents the team id. `0`(zero) is the dafault team, please change it to your team id.

```bash
export FAH_TEAMID=0
export FAH_LIMITDAYS=14
export FAH_MILESTONE1=10000
export FAH_MILESTONE2=5000
export FAH_MILESTONE3=1000
export FAH_GOAL=150
```

The backend which collects stat information can be started by the call

```bash
python3 folding-stats.py
```

The websevice to display the stats can be started by the call

```bash
python3 -m http.server 8888 &.
```

## Docker execution

### Compose

```
version: '2'
services:
  fah-red-lions-backend:
    build: generaliinformatik/fah-red-lions-backend
    ports:
      - "8888:8888"
    volumes:
      - <local>/backend/data/:/code/data/
      - <local>/backend/logs/:/code/logs/
    environment:
      FAH_TEAMID: 0
      FAH_LIMITDAYS: 14
      FAH_MILESTONE1: 10000
      FAH_MILESTONE2: 5000
      FAH_MILESTONE3: 1000
      FAH_GOAL: 150
    restart: unless-stopped
```

### Build

Build docker container:

```bash
docker build --pull -t generaliinformatik/folding-stats .
```

### Docker Container Execution

Run container with command:

```bash
docker run -d generaliinformatik/folding-stats
```

To mount local directories to your container we suggest the following command. Replace ```<local>``` with the path to a valid local directory and place at least the configuration file into this path.

```bash
docker run -d -v <local>/backend/folding-stats.json:/code/folding-stats.json -v <local>/backend/data/:/code/data/ -v <local>/backend/logs/:/code/logs/ -e FAH_TEAMID=0 generaliinformatik/folding-stats
```

**Note**: please change the given team id `0` to your team id. In this sample all other environment parameters are set to default values.

## Pre-build image

An image is available for use on Docker Hub. The image is always updated when the master branch is updated in this repository. To use this image, we recommend the configuration with the mount volumes documented above.

Docker Hub: [generaliinformatik/fah-red-lions-backend](https://hub.docker.com/repository/docker/generaliinformatik/fah-red-lions-backend)

**Note**: If you use this image on a Synology, please make sure to clear the cache. You would have to delete the content after re-downloading the updated image (Docker -> Container -> Action -> Clear)

## Supported environment variables

The display in the graph can be controlled via the following environment variables. When executing in a Docker Container, make sure that the container is restarted as a precaution after a change. If you want to ensure that old values are not used, it is safer to clean the cache beforehand.

| Variable | Required |Default value | Description | Recommended value
| --- | --- | --- | --- | --- |
| FAH_TEAMID | yes | 0 | Tead ID of your Folding@Home team | ? |
| FAH_LIMITDAYS | no | 9999 | Days to be shown in graph | 14 |
| FAH_MILESTONE1 | no | -1 | 1st milestone line | 10000 |
| FAH_MILESTONE2 | no | -1 | 2nd milestone line | 5000 |
| FAH_MILESTONE3 | no | -1 | 3rd milestone line | 1000 |
| FAH_GOAL | no | 1 | Red goal line | 150 |

## Test

Delete the file ```data/<id>.rid``` to force a write of the current data. The script thinks that the rank has changed and writes the information to the database/CSV with the current timestamp. `<id>` is the given team id via environment var `FAH_TEAMID`.

## Visualization

The values read out can be displayed in the container in the browser via a simple web server on port 8888. For this purpose, the IP of the container with port 8888 must be called up. Alternatively, the port can be redirected when the container is started.

```bash
docker run -d -v <local>/backend/folding-stats.json:/code/folding-stats.json -v <local>/backend/data/:/code/data/ -v <local>/backend/logs/:/code/logs/ -p 8888:8888 generaliinformatik/folding-stats
```

Note: This is a Quick & Dirty solution to make the data viewable outside the console.

## Database

### Schemes

#### Table 'stats'

In the table ```stats``` the ranking information of the team is recorded. The recording is usually done when the rank changes (or the *.rid file is deleted)).

```sql
CREATE TABLE IF NOT EXISTS stats (
  "datetime" text,
  "uid_datetime" text,
  team integer,
  rank integer,
  change integer
);
```

#### Table 'team'

In the Team table, the team members are recorded with the relevant attributes in order to be able to evaluate their trends historically. At a later stage, the changes can be displayed as a graph or time line, for example. The data is only captured if there have been changes to the rank of the team, since in this case there must have been a change to the attributes ```rank``` or ```credit``` for at least one team member.

The account or accounts responsible for the current change are marked with ```supporter=1```. This check is performed for each ranking change, so that an evaluation of the contributing accounts is possible.

```sql
CREATE TABLE IF NOT EXISTS team (
  "datetime" text,
  "uid_datetime" text,
  team integer,
  id integer,
  name text,
  rank integer,
  credit integer,
  supporter integer
);
```

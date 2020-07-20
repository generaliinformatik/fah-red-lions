# Folding@Home Stats (Backend)

To set up the client on PC systems, please read the setup instructions in [gitbook.io](https://rfuehrer.gitbook.io/red-lions). You can find our previous instructions under [german instructions](INSTRUCTIONS.de.md) or [english instructions](INSTRUCTIONS.md).

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
```

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

### Docker Container Execution

Run container with command:

```bash
docker run -d generaliinformatik/folding-stats
```

To mount local directories to your container we suggest the following command. Replace ```<local>``` with the path to a valid local directory and place at least the configuration file into this path.

```bash
docker run -d -v <local>/backend/folding-stats.json:/code/folding-stats.json -v <local>/backend/data/:/code/data/ -v <local>/backend/logs/:/code/logs/ -e FAH_TEAMID=0 generaliinformatik/folding-stats
```

**Note**: please change the given team id `0` to your team id

## Pre-build image

An image is available for use on Docker Hub. The image is always updated when the master branch is updated in this repository. To use this image, we recommend the configuration with the mount volumes documented above.

Docker Hub: [generaliinformatik/fah-red-lions-backend](https://hub.docker.com/repository/docker/generaliinformatik/fah-red-lions-backend)

**Note**: If you use this image on a Synology, please make sure to clear the cache. You would have to delete the content after re-downloading the updated image (Docker -> Container -> Action -> Clear)

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

![Travis CI](https://travis-ci.org/generaliinformatik/fah-red-lions.svg?branch=master) [![codecov](https://codecov.io/gh/generaliinformatik/fah-red-lions/branch/master/graph/badge.svg)](https://codecov.io/gh/generaliinformatik/fah-red-lions)

# Folding@Home Stats

![line](images/line.png)
🇩🇪 Die Anleitung zur Einrichtung des Folding@Home-Clients als Team-Mitglied von "The Red Insurance Lions - Worldwide" ist [hier](http://bit.ly/red-lions-instructions-german) zu finden. Wir haben das Format für eine bessere Lesbarkeit auf Gitbook umgestellt.

🇬🇧 Instructions for setting up the Folding@Home client as a team member of "The Red Insurance Lions - Worldwide" can be found [here](http://bit.ly/red-lions-instructions-english). We have changed the format to Gitbook for better readability.
![line](images/line.png)

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

## Email notification

The script to query the rank is executed every minute via the included cron job. It is therefore inevitable that an automatic notification at a certain time can be made by specifying hour:minute. If the environment variable `FAH_PUSHRANK_TIME` is set, a message with the current rank is sent by email when this time is reached. The notification is sent regardless of whether the rank has changed in this query.

Alternatively or as a supplement, the variable `FAH_PUSHRANK_CHANGE` can be set to the value `1` to send a notification for each change. This option is not recommended for frequent changes in ranking. However, if the rank remains reasonably stable, this option can be activated.

Background: A fixed time is used for reporting rank development. In previous versions of the script, the development may have had to be researched via the website. With this feature, reporting is done proactively as a push notification.

## Python execution

### Installation

Only Python and the corresponding modules must be installed:

```bash
pip3 install -r requirements.txt
```

### Manual Execution

At first you have to set the environment variable `FAH_TEAMID` which represents the team id. `0` (zero) is the dafault team, please change it to your team id.

```bash
# required settings
export FAH_TEAMID=0
# recommended settings
export FAH_LIMITDAYS=14
export FAH_MILESTONE1=10000
export FAH_MILESTONE2=5000
export FAH_MILESTONE3=1000
export FAH_GOAL=150
# optional settings
export FAH_EMAIL_SERVER=smtp.gmail.com
export FAH_EMAIL_PORT=587
export FAH_EMAIL_FROM=*****
export FAH_EMAIL_TO="name1@email, name2@email"
export FAH_EMAIL_PASSWORD=*****
export FAH_PUSHRANK_TIME=0800
export FAH_PUSHRANK_CHANGE=1
export FAH_PUSHRANK_FORCE=0
```

The backend which collects stat information can be started by the call

```bash
python3 folding-stats.py
```

The websevice to display the stats can be started by the call

```bash
python3 -m http.server 8888 &.
```

## Docker execution (self-hosted)

### Definition/Compose (self-hosted)

```yaml
version: '2'
services:
  fah-red-lions-backend:
    build: .
    ports:
      - "8888:8888"
    volumes:
      - ./data/:/code/data/
      - ./logs/:/code/logs/
    environment:
      TZ=Europe/Berlin
      FAH_TEAMID: 0
      FAH_LIMITDAYS: 14
      FAH_MILESTONE1: 10000
      FAH_MILESTONE2: 5000
      FAH_MILESTONE3: 1000
      FAH_GOAL: 150
      FAH_EMAIL_SERVER: smtp.gmail.com
      FAH_EMAIL_PORT: 587
      FAH_EMAIL_FROM: *****
      FAH_EMAIL_TO: name1@email, name2@email
      FAH_EMAIL_PASSWORD: *****
      FAH_PUSHRANK_TIME: 0800
      FAH_PUSHRANK_CHANGE: 1
      FAH_PUSHRANK_FORCE: 0
    restart: unless-stopped
```

**Notes**: please change the given team id within the yaml `0` to your team id. The given settings for SMTP server and credentials have to be set to your settings.

### Docker Container Execution

To build and run the image/container:

```bash
docker-compose build
docker-compose up
```

## Docker execution (pre-build)

### Definition/Compose (pre-build)

An image is available for use on Docker Hub. The image is always updated when the master branch is updated in this repository. To use this image, we recommend the configuration with the mount volumes documented above.

Docker Hub: [generaliinformatik/fah-red-lions-backend](https://hub.docker.com/repository/docker/generaliinformatik/fah-red-lions-backend)

**Note**: If you use this image on a Synology, please make sure to clear the cache. You would have to delete the content after re-downloading the updated image (Docker -> Container -> Action -> Clear)

```yaml
version: '2'
services:
  fah-red-lions-backend:
    image: generaliinformatik/fah-red-lions-backend
    container_name: fah-red-lions-backend
    ports:
      - "8888:8888"
    volumes:
      - ./data/:/code/data/
      - ./logs/:/code/logs/
    environment:
      TZ=Europe/Berlin
      FAH_TEAMID: 0
      FAH_LIMITDAYS: 14
      FAH_MILESTONE1: 10000
      FAH_MILESTONE2: 5000
      FAH_MILESTONE3: 1000
      FAH_GOAL: 150
      FAH_EMAIL_SERVER: smtp.gmail.com
      FAH_EMAIL_PORT: 587
      FAH_EMAIL_FROM: *****
      FAH_EMAIL_TO: name1@email, name2@email
      FAH_EMAIL_PASSWORD: *****
      FAH_PUSHRANK_TIME: 0800
      FAH_PUSHRANK_CHANGE: 1
      FAH_PUSHRANK_FORCE: 0
    restart: unless-stopped
```

**Notes**: please change the given team id within the yaml `0` to your team id. The given settings for SMTP server and credentials have to be set to your settings.

### Docker container execution

To run the container:

```bash
docker-compose up
```

## Supported environment variables

The display in the graph can be controlled via the following environment variables. When executing in a Docker Container, make sure that the container is restarted as a precaution after a change. If you want to ensure that old values are not used, it is safer to clean the cache beforehand.

| Variable | Required |Default value | Description | Recommended value
| --- | --- | --- | --- | --- |
| TZ | no | UTC | Timezone to display right timestamps in log and to check FAH_PUSHRANK_TIME at the right time |  |
| FAH_TEAMID | yes | 0 | Team ID of your Folding@Home team | ? |
| FAH_LIMITDAYS | no | 9999 | Days to be shown in graph | 14 |
| FAH_MILESTONE1 | no | -1 | 1st milestone line | 10000 |
| FAH_MILESTONE2 | no | -1 | 2nd milestone line | 5000 |
| FAH_MILESTONE3 | no | -1 | 3rd milestone line | 1000 |
| FAH_GOAL | no | 1 | Red goal line | 150 |
| FAH_EMAIL_SERVER| no |  | SMTP email server | |
| FAH_EMAIL_PORT| no |  | SMTP email server port | |
| FAH_EMAIL_FROM| no |  | Email sender & SMTP username | |
| FAH_EMAIL_TO| no |  | List of push notification receiver; comma separated list of email addresses | |
| FAH_EMAIL_PASSWORD| no |  |  Email SMTP server password | |
| FAH_PUSHRANK_TIME| no |  | Military time format (4 digits, 24-hour-format, leading zeros) to send notification (e.g. 1503 for 03:03pm or 15:03) | |
| FAH_PUSHRANK_CHANGE| no |  | Send notification if rank changed (1) | 1 |
| FAH_PUSHRANK_FORCE| no |  | Send push notification every check (0). Only recommanded to test email notification | 0 |

## Functional test (black box tests)

To reset a previous saved rank, please delete the file ```data/<id>.rid``` to force a write of the current data. The script thinks that the rank has changed and writes the information to the database/CSV with the current timestamp. `<id>` is the given team id via environment var `FAH_TEAMID`.

## Technical test (static test)

### pre-commit

Configuration files are included in this repository to allow the program to be tested with static code analysis. For a pull request, it is expected that these were executed before a commit and that the messages that occurred were corrected (or deliberately excluded). The commands for setting up the tools must be executed in the repository:

```bash
pip3 install pre-commit
pip3 install black
pip3 install flake8
pre-commit install
```

The last command installs the pre-commit hook and checks the repository before each commit. If an error occurs, the commit is not committed. If necessary, the tools make minor corrections themselves, which means that the commit is not yet committed in the first operation, but the second attempt is only successful with the previously changed files.

To perform the pre-commit hook checks manually, the hook can be started from the command line with the command:

```bash
pre-commit run --all-files
```

### Travis CI

The repository is connected to Travis CI. The checks of the pre-commit are also executed in the CI pipeline, so that the code quality can be equally assured. It is therefore recommended that the pre-commit hooks be executed before a pull request to ensure error-free checks in the CI pipeline.

## Visualization

The values read out can be displayed in the browser via a simple web server on port 8888. For this purpose, please call [http://127.0.0.1:8888](http://127.0.0.1:8888).

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

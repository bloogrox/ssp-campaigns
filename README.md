#### Create virtual environment

    python -m venv venv

#### Activate virtual environment

    source venv/bin/activate

#### Install python dependencies

    pip install -r requirements.txt

#### Local settings

    cp settings/local.sample.py settings/local.py

#### Start databases in Docker

    docker-compose up

#### Start nameko services

    nameko run services.timer

    nameko run services.campaigns_runner

and etc.

Please read the docs for [nameko](https://nameko.readthedocs.io/en/stable/cli.html#running-a-service)

#### Run tests

    python -m pytest

#### Run code quality checks

    flake8

### System Diagram

![Alt text](https://g.gravizo.com/source/diagram1?https%3A%2F%2Fraw.githubusercontent.com%2Fbloogrox%2Fssp-campaigns%2Fmaster%2FREADME.md)
<details>
<summary></summary>
diagram1
@startuml;
left to right direction;
queue "queue: campaigns" as campaigns;
queue "queue: subscribers" as subscribers;
queue "queue: sell subscriber" as sell_sub;
queue "queue: auction finished" as auc_fin;
queue "queue: push sent" as push_sent;
rectangle "worker: process campaign" as camp_proc;
rectangle "worker: run campaigns" as camp_run;
rectangle "worker: process subscriber" as sub_proc;
database postgresql as pg;
database elasticsearch as es;
database redis;
rectangle "worker: exchange" as x;
usecase dsp;
rectangle "worker: send push" as send_push;
rectangle "worker: update counters" as counter;
rectangle "worker: notify win" as win;
usecase push_api;
pg -up-> camp_run: get campaigns;
camp_run -> campaigns;
campaigns -> camp_proc;
es -up-> camp_proc: get subscribers;
redis -up-> camp_proc: get counters;
camp_proc -> subscribers;
subscribers -> sub_proc;
redis -up-> sub_proc: get counters;
sub_proc -> sell_sub;
sell_sub -> x;
x -down-> dsp: bid request;
dsp --> x: bid response;
x -> auc_fin;
auc_fin -> send_push;
auc_fin -> win;
counter ---> redis;
win -> dsp: notify win;
send_push -down-> push_api;
send_push -> push_sent;
push_sent -down-> counter;
@enduml
diagram1
</details>

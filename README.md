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

### Diagrams

![Bid-Picture](https://g.gravizo.com/source/svg?https://raw.githubusercontent.com/bloogrox/ssp-campaigns/diagrams/master/big-picture.plantuml)


![Services](https://g.gravizo.com/source/svg?https://raw.githubusercontent.com/bloogrox/ssp-campaigns/diagrams/master/services.plantuml)

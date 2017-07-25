#### Create virtual environment

    python -m venv venv

#### Activate virtual environment

    source venv/bin/activate

#### Install python dependencies

    pip install -r requirements.txt

#### Local settings

    cp settings/local.sample.py settings/local.py

#### Start all nameko services

    nameko run app

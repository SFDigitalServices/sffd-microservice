# SFFD microservice.py [![CircleCI](https://badgen.net/circleci/github/SFDigitalServices/sffd-microservice-py/master)](https://circleci.com/gh/SFDigitalServices/sffd-microservice-py) [![Coverage Status](https://coveralls.io/repos/github/SFDigitalServices/sffd-microservice-py/badge.svg?branch=master)](https://coveralls.io/github/SFDigitalServices/sffd-microservice-py?branch=master)

## Get started

The following environment variables need to be set:
    FIRE_DB_URL - Url to the fire db
    DS_PROXY_TOKEN - header value to access the proxy server
    FIRE_API_KEY - header value to access the fire db
    ACCESS_KEY (optional) - access key to lock down access (for example, only respond to requests from apigee)

Install Pipenv (if needed)
> $ pip install --user pipenv

Install included packages
> $ pipenv install

Start WSGI Server
> $ pipenv run gunicorn 'service.microservice:start_service()'

Run Pytest
> $ pipenv run python -m pytest

Get code coverage report
> $ pipenv run python -m pytest --cov=service tests/ --cov-fail-under=100

Open with cURL or web browser
> $curl http://127.0.0.1:8000/welcome

## How to fork in own repo (SFDigitalServices use only)
reference: [How to fork your own repo in Github](http://kroltech.com/2014/01/01/quick-tip-how-to-fork-your-own-repo-in-github/)

### Create a new blank repo
First, create a new blank repo that you want to ultimately be a fork of your existing repo. We will call this new repo "my-awesome-microservice-py".

### Clone that new repo on your local machine
Next, make a clone of that new blank repo on your machine:
> $ git clone https://github.com/SFDigitalServices/my-awesome-microservice-py.git

### Add an upstream remote to your original repo
While this technically isn’t forking, its basically the same thing. What you want to do is add a remote upstream to this new empty repo that points to your original repo you want to fork:
> $ git remote add upstream https://github.com/SFDigitalServices/microservice-py.git

### Pull down a copy of the original repo to your new repo
The last step is to pull down a complete copy of the original repo:
> $ git fetch upstream

> $ git merge upstream/master

Or, an easier way:
> $ git pull upstream master

Now, you can work on your new repo to your hearts content. If any changes are made to the original repo, simply execute a `git pull upstream master` and your new repo will receive the updates that were made to the original!

Psst: Don’t forget to upload the fresh copy of your new repo back up to git:

> $ git push origin master

## Troubleshooting
* CircleCI builds fail when trying to run coveralls.
    1. Log into coveralls.io to obtain the coverall token for your repo.
    2. Create an environment variable in CircleCI with the name COVERALLS_REPO_TOKEN and the coverall token value.

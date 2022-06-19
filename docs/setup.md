# Run WalkRollMap Flask app locally
This doc summarizes setting up WalkRollMap locally for project development. There may be some mac-specific instructions.

## Clone (copy) the WalkRollMap repo
Learn more about cloning <a href='https://www.atlassian.com/git/tutorials/setting-up-a-repository/git-clone'>here</a> or enter the desired directory in your terminal and run:

`git clone https://github.com/Mobility-Access/walk-roll-map-flask.git`

## Install Python 3

<a href='https://docs.python-guide.org/starting/install3/osx/'>Instructions for a system install of Python 3 here</a>

I prefer using pyenv to manage python versions and am using 3.6.1 for this project. Using <a href='https://brew.sh/'>homebrew</a> to install:
``` bash
brew update
brew install pyenv
pyenv install 3.6.1
```
More docs on pyenv <a href='https://github.com/pyenv/pyenv#installation'>here</a>.


To see which python versions are downloaded and available to pyenv: `pyenv versions`

To switch versions: `pyenv global 3.6.1`

To see current python path: `which python`

## Set up virtual environment

It is advisable to run a python virtual environment for the WalkRollMap project. This guarantees an isolated context for your python version and dependencies, which avoids issues with conflicts between this project and your other projects or your system.

venv is the newer version of virtualenv that ships with python3, so it doesn't need to be installed.

Virtual environments can be stored in their own directory separate from the projects they are associated with. To create one if it doesn't already exist:

`mkdir /Users/your-username/virtualenvs && cd $_`

Create and activate a new venv for the walkrollmap project:
``` bash
python -m venv wrm_venv
. wrm_venv/bin/activate
```

Verify the environment has the correct python version: `python -V`

To exit the venv: `deactivate`

## Set up database

I've found the easiest way to run a PostgreSQL server is with <a href='https://postgresapp.com/'>Postgres.app</a>.

Once the server is running using PostgreSQL 13, create the walkrollmap database with 'postgres' as the user:
``` bash
createdb -U postgres walkrollmap
```

Verify you can connect to the database: `psql -U postgres -d walkrollmap`

View tables: `\dt+`

Exit: `\q`

Postgres.app includes the postgis extension out of the box, but if necessary install with:

`psql -U postgres -d walkrollmap -c "CREATE EXTENSION postgis;"`

## Connect Flask app to database
In the walk-roll-map-flask directory, create a '.env' file with the following line:

`DATABASE_URL = 'postgresql://postgres:password@localhost:5432/walkrollmap'`

Note the 'postgres' is the user, 'password' is the password, 'localhost' is the host, '5432' is the port, and 'walkrollmap' is the database name. These should be updated if you used any custom configuration.

## Run Flask project

From the WalkRollMap project directory with the virtual environment activated, install the requirements with the most recent version of pip.
``` bash
pip install --upgrade pip
pip install -r requirements.txt
```

Apply the Flask database migrations and run the project:
``` bash
flask db upgrade
flask run
```

The development server should be running at 127.0.0.1:5000. This can be used to connect to the frontend project, [mobility-access-react](https://github.com/Mobility-Access/mobility-access-react).

Exit with ctrl-c.

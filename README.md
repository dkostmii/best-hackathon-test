# best-hackathon-test

## Documentation

all the documentation is available on the [http://localhost:8000/docs](http://localhost:8000/docs)

Users data:

- Helper
  - name: Helper
  - password: 123123123

- User
  - name: NeedHelp
  - password: 123123123

## Development Rules

Run flake8 before pushing

```bash
flake8
```

## Installing using GitHub locally

1.Clone the repository:

```bash
git clone https://github.com/dkostmii/best-hackathon-test
```

2.Change to the project's directory:

```bash
cd best-hackathon-test
```

3.Once you're in the desired directory, run the following command to create a virtual environment:

```bash
python -m venv venv
```

4.Activate the virtual environment:

On macOS and Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

5.Install the dependencies localy

```bash
pip install -r requirements.txt
```

6.Create a .env file in the root of the project and add the variables, same as in env_sample file
7.Run the app

```bash
alembic upgrade head &&
python3 -m uvicorn app.main:base_app --host 0.0.0.0 --port 8000 --reload
```

## Docker

Docker should be installed

1.to build and run the app

```bash
utils/up_services.sh build
```

2.load data to the database

```bash
utils/up_services.sh load_data
```

3.to run the app

```bash
utils/up_services.sh
```

## DATABASE

1.Add new model to alembic/env.py, just import Base
2.Create a migration

```bash
utils/create_migration.sh migration_message
```

migration will up automatically after running the app

To downgrade the migration

```bash
utils/downgrade_migration.sh
```

# best-hackathon-test

## Documentation

All the documentation is available on the [http://localhost:8000/docs](http://localhost:8000/docs)

Users data:

- Helper
  - username:

    ```text
    Helper
    ```

  - password

    ```text
    123123123
    ```

- NeedHelp
  - username:

    ```text
    NeedHelp
    ```

  - password

    ```text
    123123123
    ```

## Development Rules

Run flake8 before pushing

```bash
flake8
```

## Installing using GitHub locally

> **Note**
> If you want to choose location in the form
> provide your `MAPBOX_ACCESS_TOKEN` in `.env`.
> See example in [`.env_example`](./.env_example)

1. Clone the repository:

    ```bash
    git clone https://github.com/dkostmii/best-hackathon-test
    ```

2. Change to the project's directory:

    ```bash
    cd best-hackathon-test
    ```

3. Once you're in the desired directory, run the following command to create a virtual environment:

    ```bash
    python -m venv venv
    ```

4. Activate the virtual environment:

    On macOS and Linux:

    ```bash
    source venv/bin/activate
    ```

    On Windows:

    ```bash
    venv\Scripts\activate
    ```

5. Install the dependencies localy

    ```bash
    pip install -r requirements.txt
    ```

6. Create a `.env` file in the root of the project and add the variables, same as in [`.env_example`](./.env_example) file.

7. Run the app

    ```bash
    alembic upgrade head &&
    python3 -m uvicorn app.main:base_app --host 0.0.0.0 --port 8000 --reload
    ```

## Docker

> **Note**
> If you want to choose location in the form
> provide your `MAPBOX_ACCESS_TOKEN` in `.env`.
> See example in [`.env_example`](./.env_example)
>
> **Prerequesites**
> Docker should be installed.

1. To build and run the app

    ```bash
    ./utils/up_server.sh build
    ```

2. Load data to the database:

    ```bash
    ./utils/up_server.sh load_data
    ```

3. To run the app:

    ```bash
    ./utils/up_server.sh
    ```

## Database

1. Models already are accessible in [`alembic/env.py`](./alembic/env.py),
thanks to `from database import Base` statement.

2. Create a migration:

    ```bash
    ./utils/create_migration.sh migration_message
    ```

    Migration will up automatically after running the app.

    To downgrade the migration, run:

    ```bash
    ./utils/downgrade_migration.sh
    ```

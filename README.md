# best-hackathon-test

## Installing using GitHub:

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

## Docker

Docker should be installed

1. to build and run the app
```bash
utils/up_services.sh build
```
3. to run the app
```bash
utils/up_services.sh
```

## Getting access

localhost:8000/docs - Swagger UI(documentation)

## DATABASE

1. Add new model to alembic/env.py, just import Base
2. Create a migration
```bash
utils/create_migration.sh migration message
```
migration will up automatically after running the app

To downgrade the migration
```bash
utils/downgrade_migration.sh
```
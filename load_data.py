import json
import uuid
from datetime import datetime

from sqlalchemy import insert
from sqlalchemy.orm import class_mapper

from database import SessionLocal
from app.routers.user.model import User
from app.routers.request_task.model import RequestTask, Priority

MODELS = {
    "User": User,
    "RequestTask": RequestTask,
    "Priority": Priority,
}


def deserialize_datetime(dt_str):
    if isinstance(dt_str, str):
        return datetime.fromisoformat(dt_str)
    return dt_str


def deserialize_uuid(uuid_str):
    return uuid.UUID(uuid_str)


def load_data_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    with SessionLocal() as session:
        for model_name, serialized_instances in data.items():
            print(f"Loading {model_name}")
            Model = MODELS[model_name]

            # Check if the table is empty
            existing_records = session.query(Model).limit(1).all()
            if existing_records:
                print(f"Data already added for {model_name}. Skipping.")
                continue

            mapped_rows = []
            for serialized_instance in serialized_instances:
                deserialized_instance = {}
                for key, value in serialized_instance.items():
                    column = class_mapper(Model).columns[key]
                    if column.type.python_type == uuid.UUID:
                        deserialized_instance[key] = deserialize_uuid(value)
                    elif column.type.python_type == datetime:
                        deserialized_instance[key] = deserialize_datetime(value)
                    else:
                        deserialized_instance[key] = value
                mapped_rows.append(deserialized_instance)

            if mapped_rows:
                session.execute(insert(Model).values(mapped_rows))
                session.commit()
                print(f"Successfully loaded {len(mapped_rows)} {model_name} records.")
            else:
                print(f"No data found for {model_name}. Skipping.")


load_data_from_json("data.json")

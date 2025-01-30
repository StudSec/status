from flask import *
import importlib
import inspect
from pathlib import Path
import uuid
import re
import os
import datetime

import pymongo
from pymongo import MongoClient


app = Flask(__name__)

DB_SECRET_PATH = "/etc/secret/mongopass.env"
REPORTER_SECRET_PATH = "/etc/secret/secret.txt"

# Load services
services = {}
secrets = []
for file in (Path(__file__).parent / "services").glob("*.py"):
    if file.stem == "common" or file.stem == "__init__":
        continue

    module_name = f"services.{file.stem}"
    module = importlib.import_module(module_name)

    for name, obj in inspect.getmembers(module, inspect.isclass):
        # Check if the class is defined in the current module (exclude imports)
        if obj.__module__ == module_name:
            service = obj()
            assert (
                service.secret not in secrets
            ), f"Duplicate hmac secret in {service.name}"
            assert (
                service.uuid
            ), f"No uuid for {service.name} here is one {uuid.uuid4()}"
            assert service.uuid not in list(
                services.keys()
            ), f"Duplicate uuid {service.uuid} here is a new one: {uuid.uuid4()}"
            services[service.uuid] = service
del secrets


def get_db_secrets():
    """fetches database secrets from file"""
    uname = ""
    passwd = ""

    uname_reg = re.compile(r"MONGO_INITDB_ROOT_USERNAME=\w*\n?")
    passwd_reg = re.compile(r"MONGO_INITDB_ROOT_PASSWORD=\w*\n?")

    if not os.stat(DB_SECRET_PATH):
        print(f"{DB_SECRET_PATH} not found")
        exit(1)

    with open(DB_SECRET_PATH, "r", encoding="utf8") as secretfile:

        text = secretfile.read()
        uname_matches = uname_reg.findall(text)
        passwd_matches = passwd_reg.findall(text)

        if len(uname_matches) != 1 or len(passwd_matches) != 1:
            print(
                f"""could not find db secrets in {DB_SECRET_PATH}, found 
            {len(uname_matches)} unames and {len(passwd_matches)} passwds"""
            )

        uname = (
            uname_matches[0]
            .replace("MONGO_INITDB_ROOT_USERNAME=", "")
            .replace("\n", "")
        )
        passwd = (
            passwd_matches[0]
            .replace("MONGO_INITDB_ROOT_PASSWORD=", "")
            .replace("\n", "")
        )
    return uname, passwd


def get_db():
    """Opens the database, returns a database object"""
    uname, passwd = get_db_secrets()
    client = MongoClient(
        host="test_mongodb",
        port=27017,
        username=uname,
        password=passwd,
        authSource="admin",
    )
    database = client["reports"]
    del uname, passwd

    print(
        f"database up! {database} available tables: {database.list_collection_names()}"
    )
    return database


db = get_db()


@app.route("/")
def status_public():
    """main public page"""
    for uuid in services:
        services[uuid].update_test()
    return render_template(
        "index.html", services=[dict(x) for _, x in services.items()]
    )

def check_reporter_secret(secret: str):
    """checks secret of a logger requesting to insert logs in db"""
    if(os.stat(REPORTER_SECRET_PATH) is None):
        print(f"secret could not be checked as file {REPORTER_SECRET_PATH} not found!")
        return False

    with open(REPORTER_SECRET_PATH, "r", encoding='utf8') as secretfile:
        secret_text = secretfile.read()
        return secret == secret_text  # HEY AIDEN IS THIS SAFE?


def json_err_handler(e):
    """for debugging purposes"""
    print(f"failed to parse json: {e}")
    return 415


Request.on_json_loading_failed = json_err_handler


@app.route("/report/<uuid>/<hmac>", methods=["POST"])
def report(uuid, hmac):
    """The reporter endpoint"""
    print(
        f"Hey! received {request.content_length} bytes from {request.user_agent}"
    )

    data = request.get_json(force=True, silent=True)

    if data is None:
        return "bad json", 400

    if not check_reporter_secret(request.json["secret"]):
        print(f"    Wrong secret!")
        return "", 403

    entry = {
        "message":request.json["data"],
        "time_received":datetime.datetime.now()
    }
    db['reports'][uuid].insert_one(entry)

    return "", 200


@app.route("/service/<uuid>")
def service_status(uuid):
    # See details of service (deployment history, log ouput, etc) -> authenticated
    pass


@app.route("/admin")
def status_private():
    # Overview of all services with more detail -> authenticated
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import *
import importlib
import inspect
from pathlib import Path
import uuid


app = Flask(__name__)

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
            assert service.secret not in secrets, f"Duplicate hmac secret in {service.name}"
            assert service.uuid, f"No uuid for {service.name} here is one {uuid.uuid4()}"
            assert service.uuid not in list(services.keys()), \
                f"Duplicate uuid {service.uuid} here is a new one: {uuid.uuid4()}"
            services[service.uuid] = service
del secrets


@app.route("/")
def status_public():
    for uuid in services:
        services[uuid].update_test()
    return render_template("index.html", services=[dict(x) for _, x in services.items()])


@app.route("/report/<uuid>/<hmac>")
def report(uuid, hmac):
    # Add functionality for a service to upload logs and report their status
    pass


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
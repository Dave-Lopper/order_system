from datetime import datetime
from flask import Flask, request  # type: ignore

from src.allocation.domain import commands
from src.allocation.adapters import orm
from src.allocation.service_layer import messagebus, unit_of_work
from src.allocation.service_layer.handlers import InvalidSku

app = Flask(__name__)
orm.start_mappers()


@app.route("/add_batch", methods=["POST"])
def add_batch():
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()

    command = commands.CreateBatch(
        request.json["ref"], request.json["sku"], request.json["qty"], eta
    )
    messagebus.handle(command, unit_of_work.SqlAlchemyUnitOfWork())

    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    try:
        command = commands.Allocate(
            request.json["orderid"], request.json["sku"], request.json["qty"]
        )
        results = messagebus.handle(command, unit_of_work.SqlAlchemyUnitOfWork())
        batchref = results.pop(0)
    except InvalidSku as e:
        return {"message": str(e)}, 400
    
    if batchref is None:
        return {"message": f"Out of stock for sku {request.json['sku']}"}, 422

    return {"batchref": batchref}, 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5005)
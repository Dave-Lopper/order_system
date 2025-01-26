from datetime import datetime
from flask import Flask, jsonify, request  # type: ignore

from src.allocation import bootstrap, views
from src.allocation.domain import commands
from src.allocation.service_layer.handlers import InvalidSku

app = Flask(__name__)
bus = bootstrap.bootstrap()


@app.route("/add_batch", methods=["POST"])
def add_batch():
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()

    command = commands.CreateBatch(
        request.json["ref"], request.json["sku"], request.json["qty"], eta
    )
    bus.handle(command)

    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    try:
        command = commands.Allocate(
            request.json["orderid"], request.json["sku"], request.json["qty"]
        )
        bus.handle(command)
    except InvalidSku as e:
        return {"message": str(e)}, 400

    return "OK", 202

@app.route("/allocations/<orderid>", methods=["GET"])
def allocations_view_endpoint(orderid):
    result = views.allocations(orderid, bus.uow)
    if not result:
        return "not found", 404
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5005)
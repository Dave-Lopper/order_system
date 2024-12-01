from datetime import datetime

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from order_system import (
    config,
    orm,
    domain,
    services,
    unit_of_work,
)


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_db_uri()))
app = Flask(__name__)


@app.route("/batch", methods=["POST"])
def add_batch():
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        ref=request.json["ref"],
        sku=request.json["sku"],
        quantity=request.json["quantity"],
        eta=eta,
        uow=unit_of_work.SqlAlchemyUnitOfWork(),
    )
    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    try:
        batchref = services.allocate(
            order_id=request.json["orderid"],
            sku=request.json["sku"],
            quantity=request.json["quantity"],
            uow=unit_of_work.SqlAlchemyUnitOfWork()
        )
    except services.InvalidSku as e:
        return {"message": str(e)}, 400
    
    if batchref is None:
        return {"message": f"Out of stock for sku {request.json['sku']}"}, 422

    return {"batchref": batchref}, 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5005)

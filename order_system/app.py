from datetime import datetime

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from order_system import config, orm, repository, domain, services


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route("/batch", methods=["POST"])
def add_batch():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        ref=request.json["ref"],
        sku=request.json["sku"],
        qty=request.json["quantity"],
        eta=eta,
        repo=repo,
        session=session,
    )
    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)

    try:
        batchref = services.allocate(
            order_id=request.json["orderid"],
            sku=request.json["sku"],
            quantity=request.json["qty"],
            repo=repo,
            session=session,
        )
    except services.InvalidSku as e:
        return {"message": str(e)}, 400
    except domain.OutOfStock as e:
        return {"message": str(e)}, 422

    return {"batchref": batchref}, 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5005)

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from order_system import domain


def test_orderline_mapper_can_load_lines(session: Session):  # (1)
    session.execute(
        text(
            "INSERT INTO order_lines (order_ref, sku, quantity) "
            "VALUES (:orderid, :sku, :quantity)"
        ),
        [
            {"orderid": "order1", "sku": "RED-CHAIR", "quantity": 12},
            {"orderid": "order1", "sku": "RED-TABLE", "quantity": 13},
            {"orderid": "order2", "sku": "BLUE-LIPSTICK", "quantity": 14},
        ],
    )
    expected = [
        domain.OrderLine("order1", "RED-CHAIR", 12),
        domain.OrderLine("order1", "RED-TABLE", 13),
        domain.OrderLine("order2", "BLUE-LIPSTICK", 14),
    ]
    assert session.query(domain.OrderLine).all() == expected


def test_orderline_mapper_can_save_lines(session: Session):
    new_line = domain.OrderLine(
        order_ref="order1", sku="DECORATIVE-WIDGET", quantity=12
    )
    session.add(new_line)
    session.commit()

    rows = list(
        session.execute(
            text("SELECT order_ref, sku, quantity FROM order_lines")
        )
    )
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]

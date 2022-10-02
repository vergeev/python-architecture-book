import abc
import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        try:
            [[batch_id]] = self.session.execute(
                "SELECT id from batches WHERE reference=:ref",
                dict(ref=batch.reference),
            )
        except ValueError:
            self.session.execute(
                "INSERT INTO batches"
                " (reference, sku, _purchased_quantity, eta)"
                " VALUES"
                " (:reference, :sku, :_purchased_quantity, :eta)",
                dict(
                    reference=batch.reference,
                    sku=batch.sku,
                    _purchased_quantity=batch._purchased_quantity,
                    eta=batch.eta,
                ),
            )
            [[batch_id]] = self.session.execute(
                "SELECT id from batches WHERE reference=:ref",
                dict(ref=batch.reference),
            )

        new_order_line_ids = set()
        for order_line in batch._allocations:
            try:
                [[order_line_id]] = self.session.execute(
                    "SELECT id from order_lines WHERE orderid = :orderid",
                    dict(orderid=order_line.orderid),
                )
            except ValueError:
                self.session.execute(
                    "INSERT INTO order_lines"
                    " (orderid, sku, qty)"
                    " VALUES"
                    " (:orderid, :sku, :qty)",
                    dict(
                        orderid=order_line.orderid,
                        sku=order_line.sku,
                        qty=order_line.qty,
                    ),
                )
                [[order_line_id]] = self.session.execute(
                    "SELECT id from order_lines WHERE orderid = :orderid",
                    dict(orderid=order_line.orderid),
                )
                new_order_line_ids.add(order_line_id)

        for order_line_id in new_order_line_ids:
            self.session.execute(
                "INSERT INTO allocations"
                " (orderline_id, batch_id)"
                " VALUES"
                " (:orderline_id, :batch_id)",
                dict(
                    orderline_id=order_line_id,
                    batch_id=batch_id,
                ),
            )

    def get(self, reference) -> model.Batch:
        [[reference, sku, _purchased_quantity, eta]] = self.session.execute(
            "SELECT reference, sku, _purchased_quantity, eta FROM batches WHERE reference=:reference",
            dict(reference=reference),
        )
        batch = model.Batch(
            ref=reference,
            sku=sku,
            qty=_purchased_quantity,
            eta=eta,
        )
        allocations = self.session.execute(
            "SELECT order_lines.orderid, order_lines.sku, order_lines.qty"
            " FROM allocations"
            " JOIN order_lines ON allocations.orderline_id = order_lines.id"
            " JOIN batches ON allocations.batch_id = batches.id"
            " WHERE batches.reference = :reference",
            dict(reference=reference),
        )
        for allocation in allocations:
            batch._allocations.add(
                model.OrderLine(
                    orderid=allocation[0],
                    sku=allocation[1],
                    qty=allocation[2],
                )
            )
        return batch

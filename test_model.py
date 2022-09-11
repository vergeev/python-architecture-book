from datetime import date, timedelta
import pytest

from model import Batch, Order, OrderLine, random_unique_reference

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


@pytest.mark.xfail(raises=AssertionError)
def test_allocating_to_a_batch_reduces_the_available_quantity():
    batches = [
        Batch(
            batch_reference=random_unique_reference(),
            sku="TABLE-SMALL",
            available_quantity=20,
            eta=None,
        )
    ]
    order_lines = [
        OrderLine(
            sku="TABLE-SMALL",
            quantity=2,
        )
    ]

    Order.allocate_order_lines(order_lines=order_lines, batches=batches)

    assert batches[0].available_quantity == 18


@pytest.mark.xfail(raises=AssertionError)
def test_multiple_order_lines_reduce_the_available_quantity_in_multiple_batches():
    batches = [
        Batch(
            batch_reference=random_unique_reference(),
            sku="CHAIR-RED",
            available_quantity=10,
            eta=None,
        ),
        Batch(
            batch_reference=random_unique_reference(),
            sku="TABLE-SMALL",
            available_quantity=10,
            eta=None,
        ),
        Batch(
            batch_reference=random_unique_reference(),
            sku="LAMP-TASTELESS",
            available_quantity=1,
            eta=None,
        ),
    ]
    order_lines = [
        OrderLine(
            sku="CHAIR-RED",
            quantity=2,
        ),
        OrderLine(
            sku="CHAIR-RED",
            quantity=3,
        ),
        OrderLine(
            sku="TABLE-SMALL",
            quantity=3,
        ),
    ]

    Order.allocate_order_lines(order_lines=order_lines, batches=batches)

    assert batches[0].available_quantity == 5
    assert batches[1].available_quantity == 7
    assert batches[2].available_quantity == 1


@pytest.mark.xfail(raises=AssertionError)
def test_the_same_order_line_does_not_reduce_available_quantity_more_than_one_time():
    batches = [
        Batch(
            batch_reference=random_unique_reference(),
            sku="VASE-BLUE",
            available_quantity=10,
            eta=None,
        ),
    ]
    order_line = OrderLine(
        sku="VASE-BLUE",
        quantity=2,
    )
    order_lines = [order_line, order_line]

    Order.allocate_order_lines(order_lines=order_lines, batches=batches)

    assert batches[0].available_quantity == 8


@pytest.mark.xfail(raises=AssertionError)
def test_can_allocate_if_available_greater_than_required():
    batches = [
        Batch(
            batch_reference=random_unique_reference(),
            sku="TABLE-SMALL",
            available_quantity=20,
            eta=None,
        )
    ]
    order_lines = [
        OrderLine(
            sku="TABLE-SMALL",
            quantity=2,
        )
    ]

    order = Order.allocate_order_lines(order_lines=order_lines, batches=batches)

    assert order.order_lines == order_lines


@pytest.mark.xfail()
def test_cannot_allocate_if_available_smaller_than_required():
    batches = [
        Batch(
            batch_reference=random_unique_reference(),
            sku="PILLOW-BLUE",
            available_quantity=1,
            eta=None,
        ),
    ]
    order_lines = [
        OrderLine(
            sku="PILLOW-BLUE",
            quantity=2,
        ),
    ]

    with pytest.raises(ValueError):
        Order.allocate_order_lines(order_lines=order_lines, batches=batches)


@pytest.mark.xfail(raises=AssertionError)
def test_can_allocate_if_available_equal_to_required():
    batches = [
        Batch(
            batch_reference=random_unique_reference(),
            sku="TABLE-SMALL",
            available_quantity=20,
            eta=None,
        ),
    ]
    order_lines = [
        OrderLine(
            sku="TABLE-SMALL",
            quantity=20,
        )
    ]

    order = Order.allocate_order_lines(order_lines=order_lines, batches=batches)

    assert order.order_lines == order_lines


@pytest.mark.xfail(raises=AssertionError)
def test_prefers_warehouse_batches_to_shipments():
    batches = [
        Batch(
            batch_reference=random_unique_reference(),
            sku="TABLE-SMALL",
            available_quantity=20,
            eta=None,
        ),
        Batch(
            batch_reference=random_unique_reference(),
            sku="TABLE-SMALL",
            available_quantity=20,
            eta=today,
        ),
    ]
    order_lines = [
        OrderLine(
            sku="TABLE-SMALL",
            quantity=2,
        )
    ]

    order = Order.allocate_order_lines(order_lines=order_lines, batches=batches)

    assert batches[0].available_quantity == 18
    assert batches[0].is_warehouse_stock
    assert batches[1].available_quantity == 20


@pytest.mark.xfail(raises=AssertionError)
def test_prefers_earlier_batches():
    batches = [
        Batch(
            batch_reference=random_unique_reference(),
            sku="TABLE-SMALL",
            available_quantity=20,
            eta=tomorrow,
        ),
        Batch(
            batch_reference=random_unique_reference(),
            sku="TABLE-SMALL",
            available_quantity=20,
            eta=later,
        ),
        Batch(
            batch_reference=random_unique_reference(),
            sku="TABLE-SMALL",
            available_quantity=20,
            eta=today,
        ),
    ]
    order_lines = [
        OrderLine(
            sku="TABLE-SMALL",
            quantity=2,
        )
    ]

    order = Order.allocate_order_lines(order_lines=order_lines, batches=batches)

    assert batches[0].available_quantity == 20
    assert batches[1].available_quantity == 20
    assert batches[2].available_quantity == 18

import dataclasses
from unittest.mock import Mock

import pytest
from utils import hours_ago

from nsst import ItemAlreadyExists
from nsst import ItemNotFound
from nsst import OptimisticConcurrencyError


@dataclasses.dataclass
class Foo:
    title: str
    version: int = 1


def make_foo(item):
    return Foo(title=item["title"], version=item["version"])


def test_get_item(table, items):
    foo = table.get_item(pk="foo#5", sk="foo#5", transformer=make_foo)
    assert foo.title == "Test item 5"
    assert foo.version == 1


def test_get_item_not_found(table, items):
    on_not_found = Mock()
    item = table.get_item(pk="foo#999", sk="foo#999", on_not_found=on_not_found)
    assert on_not_found.call_count == 1
    assert item is None


def test_delete_item(table, items):
    table.delete_item(pk="foo#5", sk="foo#5")
    assert table.get_item(pk="foo#5", sk="foo#5") is None


def test_put_existing_item(table, items):
    table.put_item(
        pk="foo#5",
        sk="foo#5",
        gsi1pk="foo#",
        gsi1sk=hours_ago(15).isoformat(),
        title="Updated item",
        version=2,
    )
    foo = table.get_item(pk="foo#5", sk="foo#5", transformer=make_foo)
    assert foo.title == "Updated item"


def test_update_existing_item(table, items):
    table.update_item(pk="foo#5", sk="foo#5", title="Updated item")
    foo = table.get_item(pk="foo#5", sk="foo#5", transformer=make_foo)
    assert foo.title == "Updated item"
    assert foo.version == 1


def test_update_non_existing_item(table, items):
    with pytest.raises(ItemNotFound):
        table.update_item(pk="foo#999", sk="foo#999", title="New item")


def test_put_with_same_version(table, items):
    with pytest.raises(OptimisticConcurrencyError):
        table.put_item(
            pk="foo#5",
            sk="foo#5",
            gsi1pk="foo#",
            gsi1sk=hours_ago(15).isoformat(),
            title="Updated item",
            version=1,
        )


def test_put_with_no_version_attribute(table, items):
    table.put_item(
        pk="foo#5",
        sk="foo#5",
        gsi1pk="foo#",
        gsi1sk=hours_ago(15).isoformat(),
        title="Updated item",
    )
    foo = table.get_item(pk="foo#5", sk="foo#5")
    assert foo["title"] == "Updated item"


def test_put_item_if_not_exists(table, items):
    with pytest.raises(ItemAlreadyExists):
        table.put_item_if_not_exists(
            pk="foo#1",
            sk="foo#1",
            gsi1pk="foo#",
            gsi1sk=hours_ago(15).isoformat(),
            title="New item",
            version=1,
        )


def test_query_gsi1(table, items):
    foos = list(table.query_gsi1(gsi1pk="foo#", transformer=make_foo))
    assert len(foos) == 10
    assert foos[0].title == "Test item 1"


def test_query_gsi1_in_reverse(table, items):
    foos = list(table.query_gsi1(gsi1pk="foo#", transformer=make_foo, reverse=True))
    assert len(foos) == 10
    assert foos[0].title == "Test item 10"


def test_query_gsi1_auto_paging(table, items):
    foos = list(
        table.query_gsi1(gsi1pk="foo#", transformer=make_foo, auto_page=True, limit=2)
    )
    assert len(foos) == 10
    assert foos[0].title == "Test item 1"


def test_query_gsi1_manual_paging(table, items):
    foos, lek = table.query_gsi1(
        gsi1pk="foo#", transformer=make_foo, auto_page=False, limit=6
    )
    assert len(list(foos)) == 6
    assert foos[0].title == "Test item 1"

    foos, lek = table.query_gsi1(
        gsi1pk="foo#", transformer=make_foo, auto_page=False, limit=6, esk=lek
    )
    assert len(list(foos)) == 4
    assert foos[3].title == "Test item 10"


def test_scan(table, items):
    foos = list(table.scan())
    assert len(foos) == 10
    assert foos[0]["title"] == "Test item 1"


def test_truncate(table, items):
    table.truncate()
    assert len(list(table.scan())) == 0


def test_delete_items(table, items):
    table.delete_items(
        [
            dict(pk="foo#5", sk="foo#5"),
            dict(pk="foo#1", sk="foo#1"),
            dict(pk="foo#10", sk="foo#10"),
        ]
    )
    remaining = list(table.scan())
    assert len(remaining) == 7
    assert remaining[0]["title"] == "Test item 2"
    assert remaining[6]["title"] == "Test item 9"


def test_batch_write(table, create_table):
    table.batch_write(
        [
            dict(
                pk="foo#1",
                sk="foo#1",
                gsi1pk="foo#",
                gsi1sk=hours_ago(10).isoformat(),
                title="Test item 1",
            ),
            dict(
                pk="foo#2",
                sk="foo#2",
                gsi1pk="foo#",
                gsi1sk=hours_ago(9).isoformat(),
                title="Test item 2",
            ),
            dict(
                pk="foo#3",
                sk="foo#3",
                gsi1pk="foo#",
                gsi1sk=hours_ago(8).isoformat(),
                title="Test item 3",
            ),
        ]
    )
    foos = list(table.scan())
    assert len(foos) == 3

import json

import moto
from click.testing import CliRunner
from pytest import fixture

from nsst.cli import cli


@fixture
def runner(monkeypatch, table_name):
    monkeypatch.setenv("NSST_TABLE_NAME", table_name)
    with moto.mock_aws():
        yield CliRunner()


def test_create_table(runner, table):
    result = runner.invoke(cli, ["create-table"])
    assert result.output == ""
    assert result.exit_code == 0
    table.put_item_if_not_exists(
        pk="foo#1",
        sk="#foo#1",
        gsi1pk="foo#",
        gsi1sk="2024-11-25T19:33:05",
        title="bob",
    )
    item = table.get_item(pk="foo#1", sk="#foo#1")
    assert item["title"] == "bob"


def test_put_item(runner, table, create_table):
    result = runner.invoke(
        cli,
        [
            "put-item",
            "--pk",
            "foo#1",
            "--sk",
            "#foo#1",
            "--gsi1pk",
            "foo#",
            "--gsi1sk",
            "2024-11-25T19:33:05",
            "--item",
            '{"title": "bob"}',
        ],
    )
    assert result.output == ""
    assert result.exit_code == 0
    item = table.get_item(pk="foo#1", sk="#foo#1")
    assert item["title"] == "bob"


def test_put_item_required_options(runner, create_table, table):
    inputs = ["foo#1", "foo#1", "foo#", "2024-11-25T19:33:05", '{"title": "bob"}']
    print("\n".join(inputs))
    result = runner.invoke(cli, ["put-item"], input="\n".join(inputs))
    assert result.exit_code == 0, result.output
    assert result.output.split("\n") == [
        "pk: foo#1",
        "sk: foo#1",
        "gsi1pk: foo#",
        "gsi1sk: 2024-11-25T19:33:05",
        'Item: {"title": "bob"}',
        "",
    ]
    item = table.get_item(pk="foo#1", sk="foo#1")
    assert item["title"] == "bob"


def test_put_item_if_not_exists(runner, table, create_table):
    result = runner.invoke(
        cli,
        [
            "put-item",
            "--pk",
            "foo#1",
            "--sk",
            "#foo#1",
            "--gsi1pk",
            "foo#",
            "--gsi1sk",
            "2024-11-25T19:33:05",
            "--item",
            '{"title": "bob"}',
            "--if-not-exists",
        ],
    )
    assert result.output == ""
    assert result.exit_code == 0
    item = table.get_item(pk="foo#1", sk="#foo#1")
    assert item["title"] == "bob"
    result = runner.invoke(
        cli,
        [
            "put-item",
            "--pk",
            "foo#1",
            "--sk",
            "#foo#1",
            "--gsi1pk",
            "foo#",
            "--gsi1sk",
            "2024-11-25T19:33:05",
            "--item",
            '{"title": "updated"}',
            "--if-not-exists",
        ],
    )
    assert "Item already exists" in result.output
    assert result.exit_code > 0
    item = table.get_item(pk="foo#1", sk="#foo#1")
    assert item["title"] == "bob"


def test_put_versioned_item(runner, table, create_table):
    result = runner.invoke(
        cli,
        [
            "put-item",
            "--pk",
            "foo#1",
            "--sk",
            "#foo#1",
            "--gsi1pk",
            "foo#",
            "--if-not-exists",
            "--gsi1sk",
            "2024-11-25T19:33:05",
            "--item",
            '{"title": "bob", "version": 1}',
        ],
    )
    assert result.output == ""
    assert result.exit_code == 0

    result = runner.invoke(
        cli,
        [
            "put-item",
            "--pk",
            "foo#1",
            "--sk",
            "#foo#1",
            "--gsi1pk",
            "foo#",
            "--gsi1sk",
            "2024-11-25T19:33:05",
            "--item",
            '{"title": "updated", "version": 1}',
        ],
    )
    assert "A more recent version of this item already exists" in result.output
    assert result.exit_code > 0

    result = runner.invoke(
        cli,
        [
            "put-item",
            "--pk",
            "foo#1",
            "--sk",
            "#foo#1",
            "--gsi1pk",
            "foo#",
            "--gsi1sk",
            "2024-11-25T19:33:05",
            "--item",
            '{"title": "updated", "version": 2}',
        ],
    )
    assert result.output == ""
    assert result.exit_code == 0

    item = table.get_item(pk="foo#1", sk="#foo#1")
    assert item["title"] == "updated"


def test_get_item(runner, items):
    result = runner.invoke(cli, ["get-item", "--pk", "foo#1", "--sk", "foo#1"])
    assert result.exit_code == 0, result.output
    item = json.loads(result.output)
    assert item["title"] == "Test item 1"


def test_get_item_required_options(runner, items):
    inputs = ["foo#1", "foo#1"]
    result = runner.invoke(cli, ["get-item"], input="\n".join(inputs))
    assert result.exit_code == 0, result.output
    assert result.output.startswith("pk: foo#1\nsk: foo#1\n")
    item = json.loads(result.output.replace("pk: foo#1\nsk: foo#1\n", ""))
    assert item["title"] == "Test item 1"


def test_get_item_that_does_not_exist(runner, items):
    result = runner.invoke(cli, ["get-item", "--pk", "foo#999", "--sk", "foo#999"])
    assert result.exit_code > 0
    assert "Item does not exist" in result.output


def test_delete_item(runner, items, table):
    result = runner.invoke(cli, ["delete-item", "--pk", "foo#1", "--sk", "foo#1"])
    assert result.exit_code == 0, result.output
    assert result.output == ""
    item = table.get_item(pk="foo#1", sk="foo#1")
    assert item is None


def test_delete_item_required_options(runner, items, table):
    inputs = ["foo#1", "foo#1"]
    result = runner.invoke(cli, ["delete-item"], input="\n".join(inputs))
    assert result.exit_code == 0, result.output
    assert result.output.startswith("pk: foo#1\nsk: foo#1\n")
    item = table.get_item(pk="foo#1", sk="foo#1")
    assert item is None


def test_delete_item_that_does_not_exist(runner, items):
    result = runner.invoke(cli, ["delete-item", "--pk", "foo#999", "--sk", "foo#999"])
    assert result.exit_code == 0, result.output
    assert result.output == ""


def test_query_gsi1(runner, items):
    result = runner.invoke(cli, ["query-gsi1", "--gsi1pk", "foo#"])
    assert result.exit_code == 0, result.output
    items = json.loads(result.output)
    assert len(items) == 10
    assert items[0]["title"] == "Test item 1"
    assert items[9]["title"] == "Test item 10"


def test_query_gsi1_reverse(runner, items):
    result = runner.invoke(cli, ["query-gsi1", "--gsi1pk", "foo#", "-r"])
    assert result.exit_code == 0, result.output
    items = json.loads(result.output)
    assert len(items) == 10
    assert items[9]["title"] == "Test item 1"
    assert items[0]["title"] == "Test item 10"


def test_query_gsi1_with_limit(runner, items):
    result = runner.invoke(cli, ["query-gsi1", "--gsi1pk", "foo#", "--limit", "2"])
    assert result.exit_code == 0, result.output
    items = json.loads(result.output)
    assert len(items) == 2
    assert items[0]["title"] == "Test item 1"
    assert items[1]["title"] == "Test item 2"


def test_scan_with_limit(runner, items):
    result = runner.invoke(cli, ["scan", "--limit", "2"])
    assert result.exit_code == 0, result.output
    items = json.loads(result.output)
    assert len(items) == 2


def test_delete_table(runner, create_table):
    result = runner.invoke(cli, ["delete-table", "--yes"])
    assert result.exit_code == 0
    assert result.output == ""


def test_delete_table_needs_confirmation(runner):
    result = runner.invoke(cli, ["delete-table"])
    assert "Are you sure" in result.output


def test_truncate(runner, items, table):
    result = runner.invoke(cli, ["truncate", "--yes"])
    assert result.exit_code == 0
    assert result.output == ""
    assert len(list(table.scan())) == 0


def test_truncate_needs_confirmation(runner):
    result = runner.invoke(cli, ["truncate"])
    assert "Are you sure" in result.output

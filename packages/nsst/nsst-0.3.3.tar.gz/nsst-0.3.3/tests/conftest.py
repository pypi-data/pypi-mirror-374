import moto
import pytest
from utils import hours_ago

import nsst


@pytest.fixture
def table_name():
    return "Nsst"


@pytest.fixture(autouse=True)
def aws_creds(monkeypatch):
    # Make sure that no tests try to use real AWS creds
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture
def create_table(table):
    table.create_table()


@pytest.fixture
def table(table_name):
    with moto.mock_aws():
        yield nsst.Table(table_name)


@pytest.fixture
def items(table, create_table):
    for i in range(1, 11):
        table.put_item_if_not_exists(
            pk=f"foo#{i}",
            sk=f"foo#{i}",
            gsi1pk="foo#",
            gsi1sk=hours_ago(20 - i).isoformat(),
            title=f"Test item {i}",
            version=1,
        )

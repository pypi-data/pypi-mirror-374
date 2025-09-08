import decimal
import json

import boto3
import click

import nsst


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)  # or str(obj) if you want to keep precision
        return super().default(obj)


class CliContext:
    def __init__(self):
        self._table = None

    def connect_to_ddb(self, table_name):
        self._table = nsst.Table(table_name)

    @property
    def table(self) -> nsst.Table:
        if self._table is None:
            raise RuntimeError("Not connected to a table")
        return self._table


ctx = CliContext()


def pformat(data):
    return json.dumps(data, indent=2, cls=JSONEncoder)


@click.command()
def create_table():
    ctx.table.create_table()


def abort_if_false(ctx, _, value):
    if not value:
        ctx.abort()


@click.command()
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to delete the table?",
)
def delete_table():
    dynamodb = boto3.resource("dynamodb")
    dynamodb.Table(ctx.table.table_name).delete()


@click.command()
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to delete all items?",
)
def truncate():
    ctx.table.truncate()


@click.command()
@click.option("-l", "--limit", help="Limit the results", default=100, show_default=True)
def scan(limit):
    items = list(ctx.table.scan())[:limit]
    click.echo(pformat(items))


@click.command()
@click.option("--gsi1pk", help="The primary key for GSI 1", prompt=True, required=True)
@click.option(
    "-r", "--reverse", help="Reverse the order", flag_value=True, default=False
)
@click.option("-l", "--limit", help="Limit the results", default=100, show_default=True)
def query_gsi1(gsi1pk, reverse, limit):
    items = list(ctx.table.query_gsi1(gsi1pk=gsi1pk, reverse=reverse))[:limit]
    click.echo(pformat(items))


@click.command()
@click.option("--pk", help="The primary key", prompt="pk", required=True)
@click.option("--sk", help="The the sort key", prompt="sk", required=True)
@click.option(
    "--gsi1pk", help="The primary key for GSI 1", prompt="gsi1pk", required=True
)
@click.option(
    "--gsi1sk", help="The the sort key for GSI 1", prompt="gsi1sk", required=True
)
@click.option("--item", help="The item", prompt=True, required=True)
@click.option(
    "--if-not-exists",
    help="Only put if the item does not exist",
    flag_value=True,
    default=False,
)
def put_item(pk, sk, gsi1pk, gsi1sk, item, if_not_exists):
    item = json.loads(item)
    if if_not_exists:
        try:
            ctx.table.put_item_if_not_exists(
                pk=pk, sk=sk, gsi1pk=gsi1pk, gsi1sk=gsi1sk, **item
            )
        except nsst.ItemAlreadyExists as e:
            raise click.ClickException("Item already exists") from e
    else:
        try:
            ctx.table.put_item(pk=pk, sk=sk, gsi1pk=gsi1pk, gsi1sk=gsi1sk, **item)
        except nsst.OptimisticConcurrencyError as e:
            raise click.ClickException(
                "A more recent version of this item already exists"
            ) from e


@click.command()
@click.option("--pk", help="The primary key", prompt="pk", required=True)
@click.option("--sk", help="The sort key", prompt="sk", required=True)
def get_item(pk, sk):
    def on_not_found():
        raise click.ClickException("Item does not exist")

    item = ctx.table.get_item(pk=pk, sk=sk, on_not_found=on_not_found)
    click.echo(pformat(item))


@click.command()
@click.option("--pk", help="The primary key", prompt="pk", required=True)
@click.option("--sk", help="The sort key", prompt="sk", required=True)
def delete_item(pk, sk):
    ctx.table.delete_item(pk=pk, sk=sk)


@click.group()
@click.option(
    "-t",
    "--table-name",
    help="The name of the dynamodb table",
    prompt=True,
    envvar="NSST_TABLE_NAME",
    required=True,
)
def cli(table_name):
    ctx.connect_to_ddb(table_name)


cli.add_command(scan)
cli.add_command(create_table)
cli.add_command(delete_table)
cli.add_command(put_item)
cli.add_command(get_item)
cli.add_command(query_gsi1)
cli.add_command(truncate)
cli.add_command(delete_item)


if __name__ == "__main__":
    cli()

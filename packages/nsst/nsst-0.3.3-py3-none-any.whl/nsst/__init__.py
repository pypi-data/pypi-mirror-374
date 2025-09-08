import boto3
from botocore.exceptions import ClientError


def _id(x):
    return x


def _ignore():
    pass


class ItemAlreadyExists(Exception):
    pass


class ItemNotFound(Exception):
    pass


class OptimisticConcurrencyError(Exception):
    pass


def _handle_ddb_error(e, conditional_check_failed_error_cls):
    if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
        raise conditional_check_failed_error_cls()
    else:
        raise e


class Table:
    def __init__(self, table_name):
        self.table_name = table_name
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def update_item(self, pk, sk, **kwargs):
        try:
            self.table.update_item(
                Key={"pk": pk, "sk": sk},
                UpdateExpression="SET "
                + ", ".join(f"{k} = :{k}" for k in kwargs.keys()),
                ExpressionAttributeValues={f":{k}": v for k, v in kwargs.items()},
                ConditionExpression="attribute_exists(pk)",
            )
        except ClientError as e:
            _handle_ddb_error(e, ItemNotFound)

    def put_item(self, pk, sk, gsi1pk, gsi1sk, **kwargs):
        item = dict(pk=pk, sk=sk, gsi1pk=gsi1pk, gsi1sk=gsi1sk)
        item.update(kwargs)
        args = dict(Item=item)
        if "version" in item:
            args["ConditionExpression"] = "version = :version"
            args["ExpressionAttributeValues"] = {":version": item["version"] - 1}
        try:
            self.table.put_item(**args)
        except ClientError as e:
            _handle_ddb_error(e, OptimisticConcurrencyError)

    def get_item(self, pk, sk, on_not_found=_ignore, transformer=_id):
        response = self.table.get_item(Key={"pk": pk, "sk": sk})
        if "Item" not in response:
            on_not_found()
            return None
        return transformer(response["Item"])

    def delete_item(self, pk, sk):
        self.table.delete_item(Key={"pk": pk, "sk": sk})

    def put_item_if_not_exists(self, pk, sk, gsi1pk, gsi1sk, **kwargs):
        item = dict(pk=pk, sk=sk, gsi1pk=gsi1pk, gsi1sk=gsi1sk)
        item.update(kwargs)

        try:
            self.table.put_item(
                Item=item, ConditionExpression="attribute_not_exists(pk)"
            )
        except ClientError as e:
            _handle_ddb_error(e, ItemAlreadyExists)

    def query(
        self,
        key_condition,
        expression_attribute_values,
        index_name,
        limit=100,
        esk=None,
        transformer=_id,
        reverse=False,
        auto_page=True,
    ):
        query_args = dict(
            KeyConditionExpression=key_condition,
            ExpressionAttributeValues=expression_attribute_values,
            IndexName=index_name,
            ScanIndexForward=not reverse,
            Limit=limit,
        )

        if esk:
            query_args["ExclusiveStartKey"] = esk

        def _auto_page(esk):
            if esk:
                query_args["ExclusiveStartKey"] = esk
            response = self.table.query(**query_args)
            for item in response["Items"]:
                yield transformer(item)

            if "LastEvaluatedKey" in response:
                yield from _auto_page(esk=response["LastEvaluatedKey"])

        def _manual_page():
            response = self.table.query(**query_args)
            items = [transformer(item) for item in response["Items"]]
            lek = response.get("LastEvaluatedKey", None)
            return items, lek

        if auto_page:
            return _auto_page(esk=esk)
        else:
            return _manual_page()

    def query_gsi1(
        self,
        gsi1pk,
        limit=100,
        esk=None,
        transformer=_id,
        reverse=False,
        auto_page=True,
    ):
        return self.query(
            key_condition="gsi1pk = :gsi1pk",
            expression_attribute_values={":gsi1pk": gsi1pk},
            index_name="gsi1",
            reverse=reverse,
            limit=limit,
            esk=esk,
            transformer=transformer,
            auto_page=auto_page,
        )

    def scan(self, esk=None):
        scan_args = {}
        if esk:
            scan_args["ExclusiveStartKey"] = esk

        response = self.table.scan(**scan_args)
        yield from response["Items"]

        if "LastEvaluatedKey" in response:
            yield from self.scan(response["LastEvaluatedKey"])

    def delete_all(self, items):
        with self.table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={"pk": item["pk"], "sk": item["sk"]})

    def truncate(self):
        self.delete_all(self.scan())

    def delete_items(self, keys):
        with self.table.batch_writer() as batch:
            for key in keys:
                batch.delete_item(Key=key)

    def get_items(self, keys, transformer=_id):
        response = self.dynamodb.batch_get_item(
            RequestItems={self.table_name: {"Keys": keys}}
        )
        return [transformer(item) for item in response["Responses"][self.table_name]]

    def batch_write(self, puts, deletes=None):
        deletes = deletes or []
        with self.table.batch_writer() as batch:
            for put in puts:
                batch.put_item(Item=put)
            for delete in deletes:
                batch.delete_item(Key=delete)

    def create_table(self):
        self.dynamodb.create_table(
            TableName=self.table_name,
            KeySchema=[
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
                {"AttributeName": "gsi1pk", "AttributeType": "S"},
                {"AttributeName": "gsi1sk", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "gsi1",
                    "KeySchema": [
                        {"AttributeName": "gsi1pk", "KeyType": "HASH"},
                        {"AttributeName": "gsi1sk", "KeyType": "RANGE"},
                    ],
                    "Projection": {
                        "ProjectionType": "ALL",
                    },
                }
            ],
        )

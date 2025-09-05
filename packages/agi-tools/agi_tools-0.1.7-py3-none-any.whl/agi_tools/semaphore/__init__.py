import boto3
import pytz
from agi_tools.tools import get_config
from agi_tools.spark import AgiTools
from datetime import datetime, date
from pyspark.sql import Row
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, BooleanType, DateType
from pyspark.sql.session import SparkSession


class AgiSemaphore:


    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.semaphore_config = get_config('semaphore', 'semaphores')


    def __get_table_description(self, table_name: str):
        return self.spark.sql(f"DESCRIBE FORMATTED {table_name}")


    def __check_difference_fields(self, schema1, schema2):
        fields1 = {field.name: field.dataType for field in schema1.fields}
        fields2 = {field.name: field.dataType for field in schema2.fields}

        difference_fields = []
        common_fields = set(fields1.keys()) & set(fields2.keys())

        for field in common_fields:
            if fields1[field] != fields2[field]:
                difference_fields.append(
                    Row(
                        Coluna=field,
                        Origem=fields1[field],
                        Destino=fields2[field]
                    )
                )

        self.difference_fields = difference_fields


    def __check_table_schema(self, database: str, table_name: str, columns: list[str] = []) -> bool:
        current_schema = self.__get_current_table_schema(f'{database}.{table_name}')
        historical_schema = self.__get_historical_table_schema(f'{database}.{table_name}')


        if historical_schema == current_schema:
            return True
        elif len(columns):
            historical_table_schema = [field for field in historical_schema if field[0].lower() in columns]
            current_table_schema = [field for field in current_schema if field[0].lower() in columns]
            if historical_table_schema == current_table_schema:
                return True
            else:
                self.__check_difference_fields(historical_table_schema, current_table_schema)

        return False


    def __get_current_table_schema(self, table_name: str):
        table_description = self.__get_table_description(table_name)
        descriptions = table_description.collect()
        current_schema = []
        for description in descriptions:
            if description.col_name and description.data_type:
                if description.col_name.startswith('#'):
                    break
                current_schema.append(
                    Row(
                        coluna=description.col_name,
                        tipo=description.data_type
                    )
                )
        return current_schema


    def __get_historical_table_schema(self, table_name: str) -> list[Row]:
        historical_table = self.semaphore_config.get('historical_table', '')
        schema = []

        if schema := self.spark.sql(historical_table % table_name).collect()[0][0]:
            if not len(schema):
                if self.save_table_schema(table_name):
                    schema = self.spark.sql(historical_table % table_name).collect()[0][0]
            return schema
        return schema


    def __read_parquet_file(self, path: str) -> dict:
        try:
            df = self.spark.read.parquet(path)
            result = df.collect()[0].asDict()
            if result.get('execution_time') >= date.today():
                return result
            else:
                return {
                    "semaphore": result.get('semaphore'),
                    "success": False,
                    "execution_time": result.get('execution_time')
                }
        except Exception:
            return {
                    "semaphore": 'Not Found',
                    "success": False,
                    "execution_time": 'Not Found'
                }


    def __write_parquet_file(self, path: str, data: dict):
        schema = StructType(
            [
                StructField('semaphore', StringType()),
                StructField('success', BooleanType()),
                StructField('execution_time', DateType())
            ]
        )
        try:
            df = self.spark.createDataFrame([Row(**data)], schema=schema)
            df.write.mode("overwrite").parquet(path)
            return True
        except Exception:
            return False


    def put_semaphore(self, name: str):
        path = f"{self.semaphore_config.get('path')}/semaphore_{name}.parquet"
        semaphores = self.semaphore_config.get(name, {})
        tables = semaphores.keys()

        status = True
        last_update = []

        for table in tables:
            table_config = semaphores.get(table, {})
            database = table_config.get('database')
            table_name = table_config.get('table')
            update = self.get_last_updated(f"{database}.{table_name}")
            status = (
                status
                and
                self.__check_table_schema(
                    database,
                    table_name,
                    table_config.get('columns', [])
                )
                and
                update.date() == date.today()
            )
            last_update.append(update)

        data = {
            "semaphore": name,
            "success": status,
            "execution_time": min(last_update)
        }

        return self.__write_parquet_file(path, data)


    def get_last_updated(self, table_name: str) -> datetime:
        table_description = self.__get_table_description(table_name)
        boto_client = boto3.client('s3')
        description = (
            table_description
            .where(
                (F.col('col_name') == 'Location')
                |
                (F.col('col_name') == 'Created Time')
            )
            .select(['data_type'])
            .collect()
        )

        create_time = (
            datetime
            .strptime(description[0][0], '%a %b %d %H:%M:%S %Z %Y')
            .astimezone(pytz.timezone("America/Sao_Paulo"))
        )

        table_info = (
            description[1][0]
            .split('/')
        )

        bucket_name = table_info[2]
        file_name = table_info[3]

        response = boto_client.list_objects_v2(Bucket=bucket_name, Prefix=file_name)
        objetos = response.get('Contents')

        for obj in objetos:
            if obj.get('Key').endswith('_SUCCESS') & obj.get('Key').startswith(f'{file_name}/'):
                return obj.get('LastModified').astimezone(pytz.timezone("America/Sao_Paulo"))

        return create_time


    def get_semaphore(self, name: str) -> dict:
        path = f"{self.semaphore_config.get('path')}/semaphore_{name}.parquet"
        return self.__read_parquet_file(path)


    def save_table_schema(self, table_name: str) -> bool:
        try:
            agi = AgiTools(private=True)
            destination_table = self.semaphore_config.get('table_name', '')
            spark = agi.create_spark_session(session_name=destination_table)

            df =  (
                spark
                .createDataFrame(
                    [
                        Row(
                            table_name=table_name,
                            schema=self.__get_current_table_schema(table_name)
                        )
                    ]
                )
                .withColumn(
                    'last_update',
                    F.from_utc_timestamp(F.current_timestamp(), "America/Sao_Paulo")
                )
                .select(['table_name', 'last_update', 'schema'])
            )

            agi.insert_into_lake(
                data=df,
                write_mode='append'
            )
            return True
        except Exception:
            return False

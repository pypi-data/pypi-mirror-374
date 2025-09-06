import json
from typing import Callable

from dataforge._base_session import _Base_Session
import sys
from snowflake.snowpark.context import get_active_session
import streamlit as st
from snowflake.snowpark.dataframe import DataFrame

class _Snowflake_Session(_Base_Session):
    """Base session class for Snowflake platform.
    Class should not be instantiated by user directly: use process-specific Session classes instead
    Adds Snowpark session
    """

    def __init__(self):
        pg_connection_string_read = st.secrets['DATAFORGE_PG_READ']
        core_jwt_token = st.secrets['DATAFORGE_CORE_JWT']
        params = self.parse_key_value_args()
        process_id = params.get('process_id')
        self.input_id = params.get('input_id')

        super().__init__(pg_connection_string_read, core_jwt_token, process_id)
        self.snowpark_session = get_active_session()
        self.process_parameters["start_process_flag"] = process_id is None

        self.logger.info(f"Initialized Snowflake base session for {self.__class__.__name__} with parameters {self.process_parameters}")


    @staticmethod
    def parse_key_value_args():
        """
        Parse command line arguments formatted as key=value into a dict.
        Example: python script.py foo=123 bar=hello

        Returns: {'foo': '123', 'bar': 'hello'}
        """
        argv = sys.argv
        params: dict[str,str] = {}
        for arg in argv:
            if "=" in arg:
                key, value = arg.split("=", 1)  # split only on first '='
                params[key] = value
            else:
                raise ValueError(f"Invalid argument format (expected key=value): {arg}")
        return params

    def ingest(self,df: DataFrame | Callable[[], DataFrame] | None = None):
        """Ingest the provided DataFrame into the DataForge and update input record.

        Writes the DataFrame to raw Snowflake table

        Args:
            df (Callable[[], DataFrame] | DataFrame): parameterless def that you defined, returning the Spark DataFrame to ingest (recommended),
                or spark DataFrame
        """
        try:
            if not self._is_open:
                raise Exception("Session is closed")
            table = f"{self._systemConfiguration.dataLakeDbName}.{self._systemConfiguration.dataLakeSchemaName}.INPUT_{self.process.inputId}"
            self.log(f"Writing dataframe to table {table}")
            df.write.save_as_table(
                name=table,
                mode="overwrite",
                table_type="transient"
            )
            self.log(f"Table {table} written")
            if self.process.startProcessFlag:
                # process started by IngestionSession, tell Core to continue and not run Notebook
                self._pg.sql("SELECT sparky.sdk_complete_manual_process(%s)", [self.process.processId], fetch=False)
        except Exception as e:
            self._log_fail(e)
            if self.process.startProcessFlag:
                # Fail input and process to prevent core from executing it
                failure_update_json = {
                "process_id": self.process.processId,
                "ingestion_status_code": "F"
                }
                self._pg.sql("SELECT meta.prc_iw_in_update_input_record(%s)",
                         (json.dumps(failure_update_json),), fetch=False)
        finally:
            self.close()
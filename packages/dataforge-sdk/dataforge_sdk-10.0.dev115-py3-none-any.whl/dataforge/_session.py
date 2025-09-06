# Pick base class at import time
if "spark" in globals() and type(spark).__name__ == 'SparkSession':
    from dataforge._databricks_session import _Databricks_Session
    _Session = _Databricks_Session
else:
    from dataforge._snowflake_session import _Snowflake_Session
    _Session = _Snowflake_Session
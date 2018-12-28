import sys

from sqlalchemy import (
    create_engine,
    inspect,
)

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)

try:
    from your_package import (
        BaseDeclarativeModel as BaseDeclarativeModel,
    )
except:
    print("Incorrect package name for importing base declarative model")
    sys.exit(-1)

def _compare_sets(set_metadata, set_schema, compared_object):
    if not isinstance(set_metadata, set):
        return
    if not isinstance(set_schema, set):
        return

    objects_only_in_schema = set_schema.difference(set_metadata)
    if objects_only_in_schema:
        for table_name in objects_only_in_schema:
            print("{} '{}' only in schema".format(str(compared_object), table_name))
    objects_only_in_metadata = set_metadata.difference(set_schema)
    if objects_only_in_metadata:
        for table_name in objects_only_in_metadata:
            print("{} '{}' only in metadata".format(str(compared_object), table_name))


def _compare_tables(db_inspector, model_base):
    inspected_table_names = set(db_inspector.get_table_names())
    model_table_names = set(model_base.metadata.tables.keys())
    _compare_sets(model_table_names, inspected_table_names, "table")


def _compare_column_details(db_inspector, model_base, inspected_table_name):
    inspected_columns = set(["{}/nullable={}".format(column_dict["name"], column_dict["nullable"])
        for column_dict in db_inspector.get_columns(inspected_table_name)])
    model_columns = set(["{}/nullable={}".format(column.name, column.nullable)
        for column in model_base.metadata.tables[inspected_table_name].columns.values()])
    _compare_sets(model_columns, inspected_columns, "column in table {}".format(inspected_table_name))


def _compare_columns(db_inspector, model_base):
    for inspected_table_name in db_inspector.get_table_names():
        if inspected_table_name not in model_base.metadata.tables:
            continue
        _compare_column_details(db_inspector, model_base, inspected_table_name)


def compare_model_and_schema(model_base, db_session):
    """
    Documentation for SQLAlchemy metadata:
        https://docs.sqlalchemy.org/en/latest/core/metadata.html
    Documentation for SQLAlchemy inspector:
        https://docs.sqlalchemy.org/en/latest/core/reflection.html
    """

    db_engine = db_session.get_bind()
    db_inspector = inspect(db_engine)

    _compare_tables(db_inspector, model_base)
    _compare_columns(db_inspector, model_base)


if __name__ == '__main__':
    database_url = "postgresql+psycopg2://username:secret@127.0.0.1/db_name"
    try:
        engine = create_engine(database_url)
    except:
        print("Invalid database credentials")
        sys.exit(-1)

    db_session = scoped_session(sessionmaker())
    db_session.configure(bind=engine)

    BaseDeclarativeModel.metadata.bind = engine

    compare_model_and_schema(
        model_base=BaseDeclarativeModel,
        db_session=db_session,)

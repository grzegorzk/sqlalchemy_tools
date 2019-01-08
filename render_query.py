import sys
import datetime

from sqlalchemy.orm import Query
import sqlalchemy.orm

def render_query(query, bind=None):
    """
    Render query with parameters; to be used only for debugging purposes

    :param query: Instance of `sqlalchemy.orm.query.Query` to render
    """
    if not isinstance(query, sqlalchemy.orm.query.Query):
        raise ValueError("render_query: `query` argument of incorrect type passed to method.")
    else:
        statement = query.statement

    if bind is None:
        bind = statement.bind

    if bind and not isinstance(bind, sqlalchemy.engine.base.Engine):
        raise ValueError("render_query: uninitialised `bind` or incorrect argument type.")

    dialect = bind.dialect
    compiler = statement._compiler(dialect)

    class LiteralCompiler(compiler.__class__):
        def visit_bindparam(self, bindparam, within_columns_clause=False,
                literal_binds=False, **kwargs):
            return super(LiteralCompiler, self).render_literal_bindparam(
                bindparam,
                within_columns_clause=within_columns_clause,
                literal_binds=literal_binds,
                 **kwargs)
        def render_literal_value(self, value, type_):
            if value is None:
                return "NULL"
            elif isinstance(value, (float, int)):
                return repr(value)
            else:
                return str("'%s'" % value)

    compiler = LiteralCompiler(dialect, statement)

    return compiler.process(statement)

"""
# Example usage
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from render_query import render_query
from your_package.models import *
try:
    engine = create_engine(database_url)
except:
    print("Invalid database credentials")
    sys.exit(-1)
initialize_sql(engine=engine)
db_session = scoped_session(sessionmaker())
db_session.configure(bind=engine)
query = db_session.query(YourTable)
render_query(query)
"""

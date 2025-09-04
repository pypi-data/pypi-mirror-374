"""
PyPika is divided into a couple of modules, primarily the ``queries`` and ``terms`` modules.

pypika.analytics
----------------

Wrappers for SQL analytic functions

pypika.dialects
---------------

This contains all of the dialect specific implementations of the ``Query`` class.

pypika.enums
------------

Enumerated values are kept in this package which are used as options for Queries and Terms.

pypika.functions
----------------

Wrappers for common SQL functions are stored in this package.

pypika.pseudocolumns
--------------------

Wrappers for common SQL pseudocolumns are stored in this package.

pypika.queries
--------------

This is where the ``Query`` class can be found which is the core class in PyPika.  Also, other top level classes such
as ``Table`` can be found here.  ``Query`` is a container that holds all of the ``Term`` types together and also
serializes the builder to a string.

pypika.terms
------------

This module contains the classes which represent individual parts of queries that extend the ``Term`` base class.

pypika.utils
------------

This contains all of the utility classes such as exceptions and decorators.
"""

# noinspection PyUnresolvedReferences
from pypika.dialects import (
    ClickHouseQuery,
    Dialects,
    MSSQLQuery,
    MySQLQuery,
    OracleQuery,
    PostgreSQLQuery,
    RedshiftQuery,
    SQLLiteQuery,
    VerticaQuery,
)

# noinspection PyUnresolvedReferences
from pypika.enums import (
    DatePart,
    JoinType,
    Order,
)

# noinspection PyUnresolvedReferences
from pypika.queries import (
    AliasedQuery,
    Column,
    Database,
    Query,
    Schema,
    Table,
    Values,
    ValuesTuple,
)
from pypika.queries import (
    make_columns as Columns,
)
from pypika.queries import (
    make_tables as Tables,
)

# noinspection PyUnresolvedReferences
from pypika.terms import (
    JSON,
    Array,
    Bracket,
    Case,
    Criterion,
    CustomFunction,
    EmptyCriterion,
    Field,
    FormatParameter,
    Index,
    Interval,
    NamedParameter,
    Not,
    NullValue,
    NumericParameter,
    Parameter,
    PyformatParameter,
    QmarkParameter,
    Rollup,
    SystemTimeValue,
    Tuple,
)

# noinspection PyUnresolvedReferences
from pypika.utils import (
    CaseException,
    FunctionException,
    GroupingException,
    JoinException,
    QueryException,
    RollupException,
    SetOperationException,
)

__author__ = "Timothy Heys"
__email__ = "theys@kayak.com"
__version__ = "0.51.0"

NULL = NullValue()
SYSTEM_TIME = SystemTimeValue()

__all__ = (
    'JSON',
    'NULL',
    'SYSTEM_TIME',
    'AliasedQuery',
    'Array',
    'Bracket',
    'Case',
    'CaseException',
    'ClickHouseQuery',
    'Column',
    'Columns',
    'Criterion',
    'CustomFunction',
    'Database',
    'DatePart',
    'Dialects',
    'EmptyCriterion',
    'Field',
    'FormatParameter',
    'FunctionException',
    'GroupingException',
    'Index',
    'Interval',
    'JoinException',
    'JoinType',
    'MSSQLQuery',
    'MySQLQuery',
    'NamedParameter',
    'Not',
    'NullValue',
    'NumericParameter',
    'OracleQuery',
    'Order',
    'Parameter',
    'PostgreSQLQuery',
    'PyformatParameter',
    'QmarkParameter',
    'Query',
    'QueryException',
    'RedshiftQuery',
    'Rollup',
    'RollupException',
    'SQLLiteQuery',
    'Schema',
    'SetOperationException',
    'SystemTimeValue',
    'Table',
    'Tables',
    'Tuple',
    'Values',
    'VerticaQuery',
    'ValuesTuple',
)

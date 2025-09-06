"""Public entry points for the :mod:`chalkdf` library.

This module exposes the :class:`~chalkdf.dataframe.DataFrame` type along with
expression helpers and testing utilities so that users can simply ``import
chalkdf`` and access the core API.
"""

from __future__ import annotations

from .dataframe import DataFrame
from .lazyframe import LazyFrame
from .libchalk.chalktable import AggExpr, Expr
from .testing import Testing

__all__ = ["DataFrame", "LazyFrame", "Expr", "AggExpr", "Testing"]

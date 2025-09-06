from __future__ import annotations

import operator
import typing
from collections.abc import Callable
from dataclasses import dataclass
from decimal import ROUND_HALF_UP
from decimal import Decimal
from typing import Annotated

from docnote import ClcNote

import finnr._moneymath
from finnr._moneymath import MoneyMathImpl

if typing.TYPE_CHECKING:
    from finnr.currency import Currency


amount_getter: Annotated[
    Callable[[Money], Decimal],
    ClcNote('''The ``amount_getter`` is a convenience method for use in
        ``min``, ``max``, sorting, etc. Use it instead of defining a lambda
        for every comparison:

        > ``amount_getter`` examples
        __embed__: 'code/python'
            max(money1, money2, key=amount_getter)
            sorted([money1, money2], key=amount_getter)
        ''')
] = operator.attrgetter('amount')


@dataclass(slots=True)
class Money(MoneyMathImpl):
    """``Money`` objects, in addition to specifying an explicit
    amount and currency, also include a number of math functions
    that match your intuitive expectation of how money math actually
    works.

    Note that monetary amounts are not limited in precision to the
    minor denominator of their associated currency. To round the amount
    to the nearest unit, call ``round_to_major`` or ``round_to_minor``,
    both of which will return a new ``Money`` object.
    """
    amount: Decimal
    currency: Currency

    def round_to_major(self, rounding=ROUND_HALF_UP) -> Money: ...
    def round_to_minor(self, rounding=ROUND_HALF_UP) -> Money: ...

    @property
    def is_nominal_division(self) -> bool: ...
        # Returns whether or not the amount can be expressed as an
        # integer multiple of the minor unit

    @property
    def is_nominal_major(self) -> bool: ...
        # Returns whether or not the amount can be expressed as an
        # integer multiple of the major unit


# This injects the Money object into the _moneymath namespace to avoid it
# having a circular import
finnr._moneymath.Money = Money

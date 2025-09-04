"""The module that defines the ``CoursePurchaseSummary`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

from __future__ import annotations

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .course_price import CoursePrice


@dataclass
class CoursePurchaseSummary:
    """A summary of a direct course purchase."""

    #: The scope of the purchase.
    scope: t.Literal["course"]
    #: The id of the transaction.
    id: str
    #: Timestamp when the purchase was successful.
    success_at: datetime.datetime
    #: The specific, immutable price object that was purchased.
    purchased_item: CoursePrice

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "scope",
                rqa.StringEnum("course"),
                doc="The scope of the purchase.",
            ),
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of the transaction.",
            ),
            rqa.RequiredArgument(
                "success_at",
                rqa.RichValue.DateTime,
                doc="Timestamp when the purchase was successful.",
            ),
            rqa.RequiredArgument(
                "purchased_item",
                parsers.ParserFor.make(CoursePrice),
                doc="The specific, immutable price object that was purchased.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "scope": to_dict(self.scope),
            "id": to_dict(self.id),
            "success_at": to_dict(self.success_at),
            "purchased_item": to_dict(self.purchased_item),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type[CoursePurchaseSummary], d: t.Dict[str, t.Any]
    ) -> CoursePurchaseSummary:
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            scope=parsed.scope,
            id=parsed.id,
            success_at=parsed.success_at,
            purchased_item=parsed.purchased_item,
        )
        res.raw_data = d
        return res

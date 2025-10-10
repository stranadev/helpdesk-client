from enum import Enum


class SortEnum(Enum):
    asc = "asc"
    desc = "desc"


class SearchCriteriaFieldEnum(Enum):
    requester_email = "requester.email_id"
    status_name = "status.name"


class SearchCriteriaConditionEnum(Enum):
    eq = "eq"
    neq = "neq"
    contains = "contains"


class SearchCriteriaLogicalOperatorEnum(Enum):
    or_ = "or"
    and_ = "and"

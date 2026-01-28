from enum import StrEnum, IntEnum


class UserRoles(StrEnum):
    ADMIN = "admin"
    DIRECTOR = "director"
    HEAD_MANAGER = "head manager"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    USER = "user"


class PriceCategories(IntEnum):
    CATEGORY_1 = 1
    CATEGORY_2 = 2
    CATEGORY_3 = 3
    CATEGORY_4 = 4
    CATEGORY_5 = 5


class Weekdays(IntEnum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class VisitRoles(StrEnum):
    PRESENT = "present"
    ILL_WITH_AVIDENCE = "ill with evidence"
    ILL = "ill"
    MISSING = "missing"
    VACATION = "vacation"
    TRIAL_VISIT = "trial visit"
    SUBSTITUTION = "substitution"
    CANCELED = "canceled"
    ON_TRACK = "on track"
    POSTPONED = "postponed"
    PLANED = "planed"
    PASSED = "passed"

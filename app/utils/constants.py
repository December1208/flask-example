class TimeConstant:
    DAYS_PER_WEEK = 7
    DAYS_PER_YEAR = 366

    THREE_SECOND = 3

    ONE_MINUTE = 60
    THREE_MINUTE = ONE_MINUTE * 5
    FIVE_MINUTE = ONE_MINUTE * 5
    TEN_MINUTE = ONE_MINUTE * 10
    FIFTEEN_MINUTE = ONE_MINUTE * 15

    ONE_HOUR = ONE_MINUTE * 60
    HALF_HOUR = ONE_MINUTE * 30
    TWO_HOUR = ONE_HOUR * 2
    THREE_HOUR = ONE_HOUR * 3
    SIX_HOUR = ONE_HOUR * 6
    TEN_HOUR = ONE_HOUR * 10

    HALF_DAY = ONE_HOUR * 12
    ONE_DAY = 24 * ONE_HOUR
    THREE_DAY = 3 * ONE_DAY
    ONE_WEEK = DAYS_PER_WEEK * ONE_DAY
    TWO_WEEK = ONE_DAY * 14

    THIRTY_DAYS = ONE_DAY * 30

    ONE_YEAR = DAYS_PER_YEAR * ONE_DAY
    TEN_YEARS = 10 * 365 * 86400
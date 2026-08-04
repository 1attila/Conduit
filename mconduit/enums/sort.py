import enum


class Sort(enum.StrEnum):
    ARBITRARY = "arbitrary"
    FURTHEST  = "furthest"
    NEAREST   = "nearest"
    RANDOM    = "random"
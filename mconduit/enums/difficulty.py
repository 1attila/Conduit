import enum


class Difficulty(str, enum.Enum):
    Peaceful = "peaceful"
    Easy = "easy"
    Normal = "normal"
    Hard = "hard"
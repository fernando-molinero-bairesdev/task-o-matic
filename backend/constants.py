from enum import Enum, IntEnum

class Status(str, Enum):
    TO_DO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"

class Priority(IntEnum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

from enum import Enum
from typing import List, Optional, Generic
from msgspec import Struct
from typing_extensions import TypeVar

T = TypeVar("T", default=str)


COT_SYSTEM_MESSAGE = """
You must structure your reasoning using the 'ChainOfThoughts' schema.

Start with any assumptions (if relevant).
Break down your reasoning into a sequence of steps:
  * Each step must include its explanation, and output.
Conclude with the final_answer.

Keep it concise. Optional fields may be omitted.
"""


class Step(Struct):
    explanation: str
    output: str


class ChainOfThoughts(Struct, Generic[T], kw_only=True):
    assumptions: Optional[List[str]]
    steps: List[Step]
    final_answer: T

ChainOfThoughts.system_message = COT_SYSTEM_MESSAGE

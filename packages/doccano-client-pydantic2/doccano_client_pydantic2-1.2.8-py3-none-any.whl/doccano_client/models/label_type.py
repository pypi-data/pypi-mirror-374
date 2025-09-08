import random
import re
from typing import Literal, Optional, Annotated

from pydantic import BaseModel, Field, model_validator

PREFIX_KEY = Literal["ctrl", "shift", "ctrl shift"]
SUFFIX_KEY = Literal[
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
]


def generate_random_hex_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"


Text = Annotated[str, Field(min_length=1, max_length=100, strip_whitespace=True)]

Color = Annotated[str, Field(pattern=r"#[a-fA-F0-9]{6}")]

class LabelType(BaseModel):
    id: Optional[int]
    text: Text
    prefix_key: Optional[PREFIX_KEY] = None
    suffix_key: Optional[SUFFIX_KEY] = None
    background_color: Color = Field(default_factory=generate_random_hex_color)
    text_color: Color = Field(default="#ffffff")

    @model_validator(mode="after")
    def deny_only_prefix_key(cls, values):
        prefix_key = values.get("prefix_key")
        suffix_key = values.get("suffix_key")
        if prefix_key and suffix_key is None:
            raise ValueError("You must specify a suffix_key if you specify a prefix_key.")
        return values

    @classmethod
    def create(
        cls,
        text: str,
        prefix_key: PREFIX_KEY = None,
        suffix_key: SUFFIX_KEY = None,
        color: Optional[str] = None,
        id: Optional[int] = None,
    ):
        if color is None:
            return cls(id=id, text=text, prefix_key=prefix_key, suffix_key=suffix_key)
        else:
            return cls(id=id, text=text, prefix_key=prefix_key, suffix_key=suffix_key, background_color=color)


CategoryType = LabelType
SpanType = LabelType
RelationType = LabelType

from pathlib import Path
from attrs import define, field
import json
from typing import List

recipient_folder = Path(__file__).parent / "data/recipients"
sender_folder = Path(__file__).parent / "data/senders"


@define(kw_only=True, slots=True, repr=False, eq=False)
class Person:
    name: str = field()
    path: Path = field()

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        if self.name == other:
            return True


available_senders = [
    Person(name=x.stem.lower(), path=x) for x in sender_folder.glob("*.json")
]
available_recipients = [
    Person(name=x.stem.lower(), path=x)
    for x in recipient_folder.glob("*.json")
]

print(available_senders)
print(available_recipients)


@define(kw_only=True, slots=True)
class Sender:
    name: str = field(default="")
    role: str = field(default="")
    street: str = field(default="")
    city: str = field(default="")
    state: str = field(default="")
    country: str = field(default="")
    zip: str = field(default="")
    phone: str = field(default="")
    email: str = field(default="")
    website: str = field(default="")
    image: str = field(default="")

    @classmethod
    def from_json(cls, path: Path):
        with open(path, 'r') as f:
            details = dict(json.load(f))
        return cls(**details)


@define(kw_only=True, slots=True)
class Recipient:
    name: str = field(default="")
    company: str = field(default="")
    street: str = field(default="")
    city: str = field(default="")
    state: str = field(default="")
    country: str = field(default="")
    zip: str = field(default="")
    phone: str = field(default="")

    @classmethod
    def from_json(cls, path: Path):
        with open(path, 'r') as f:
            details = dict(json.load(f))
        return cls(**details)

    @property
    def shipping(self) -> List[str]:
        return [
            self.name, self.company, self.street,
            f"{self.city}, {self.state} {self.zip}", self.phone
        ]

from pathlib import Path
from attrs import define, field
import json
from typing import List

recipient_folder = Path(__file__).parent / "data/recipients"
sender_folder = Path(__file__).parent / "data/senders"


@define(kw_only=True, slots=True)
class Sender:
    name: str = field()
    role: str = field()
    street: str = field()
    city: str = field()
    state: str = field()
    country: str = field()
    zip: int = field()
    phone: str = field()
    email: str = field()
    website: str = field(default="")

    @classmethod
    def from_json(cls, path: Path):
        with open(path, 'r') as f:
            details = dict(json.load(f))
        return cls(name=details['name'],
                   role=details['role'],
                   street=details['street'],
                   city=details['city'],
                   state=details['state'],
                   zip=details['zip'],
                   country=details['country'],
                   phone=details['phone'],
                   email=details['email'],
                   website=details['website'])


@define(kw_only=True, slots=True)
class Recipient:
    name: str = field(default="")
    company: str = field()
    street: str = field()
    city: str = field()
    state: str = field()
    country: str = field()
    zip: int = field()
    phone: str = field()

    @classmethod
    def from_json(cls, path: Path):
        with open(path, 'r') as f:
            details = dict(json.load(f))
        return cls(
            name=details['name'],
            company=details['company'],
            street=details['street'],
            city=details['city'],
            state=details['state'],
            zip=details['zip'],
            country=details['country'],
            phone=details['phone'],
        )

    @property
    def shipping(self) -> List[str]:
        return [
            self.name, self.company, self.street,
            f"{self.city}, {self.state} {self.zip}", self.phone
        ]

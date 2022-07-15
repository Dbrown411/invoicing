from pathlib import Path
from attrs import define, field
import json
from people import Recipient, Sender
import hashlib
import datetime


def date_by_adding_business_days(from_date, add_days):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += datetime.timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5:  # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date


@define(kw_only=True, slots=True)
class Job:
    date: str = field()
    sender: "Sender" = field()
    recipient: "Recipient" = field()
    invoice_number: int = field(init=False)

    def __attrs_post_init__(self):
        self.invoice_number = assign_invoice_number(self.date,
                                                    self.recipient.company)


def assign_invoice_number(date: str, company: str):
    return int(
        hashlib.sha256(f"{date}{company}".encode('utf-8')).hexdigest(),
        16) % 10**8

from pathlib import Path
from attrs import define, field
import json
from .people import Recipient, Sender, available_recipients, available_senders
import hashlib
from datetime import datetime, timedelta


def date_by_adding_business_days(from_date: datetime,
                                 add_days: int) -> datetime:
    """ add business days to initial date, naive of holidays"""
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5:  # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date


def assign_invoice_number(code: str) -> int:
    return int(hashlib.sha256(code.encode('utf-8')).hexdigest(), 16) % 10**8


@define(kw_only=True, slots=True)
class LineItem:
    description: str = field()
    hours: int = field()
    rate: int = field()
    linetotal: str = field(init=False)

    def __attrs_post_init__(self):
        self.linetotal = self.hours * self.rate

    @classmethod
    def from_dict(cls, data: dict):
        return cls(description=data.get("description"),
                   hours=data.get('hours'),
                   rate=data.get("rate"))


@define(kw_only=True, slots=True)
class Job:
    invoice_number: int = field(init=False)
    date: str = field()
    sender: "Sender" = field()
    recipient: "Recipient" = field()
    line_items: list["LineItem"] = field(factory=list)
    discounts: int = field(default=0)
    tax: int = field(default=0)
    subtotal: int = field(init=False)
    total: int = field(init=False)
    reference: str = field()
    paypal: str = field()
    shipping: bool = field(default=False)

    def __attrs_post_init__(self):
        job_code = f"{self.date}{self.recipient.company}{self.recipient.name}"
        self.invoice_number = assign_invoice_number(job_code)
        self.subtotal = sum([x.linetotal for x in self.line_items])
        self.total = self.subtotal - self.discounts + self.tax

    @classmethod
    def from_json(cls, path: Path):
        with open(path, 'r') as f:
            details = dict(json.load(f))

        line_items = details['line_items']

        sender_name = details['sender']
        if sender_name not in available_senders:
            sender_name = 'default'
        first_sender_index = available_senders.index(sender_name)
        sender = Sender.from_json(available_senders[first_sender_index].path)

        recipient_name = details['recipient']
        if recipient_name not in available_recipients:
            recipient_name = 'default'
        first_recipient_index = available_senders.index(recipient_name)
        recipient = Recipient.from_json(
            available_recipients[first_recipient_index].path)

        try:
            paypal = f"https://www.paypal.com/invoice/p/{details['paypal_id']}"
        except KeyError:
            paypal = ""
        try:
            reference = details['reference']
        except KeyError:
            reference = ""
        return cls(sender=sender,
                   date=details['date'],
                   recipient=recipient,
                   line_items=[LineItem.from_dict(d) for d in line_items],
                   shipping=details['shipping'],
                   paypal=paypal,
                   reference=reference)

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .jobs import Job
from .jobs import date_by_adding_business_days
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from borb.pdf import Document, Page, Image, SingleColumnLayout, PDF
from borb.pdf import TableCell, HexColor, X11Color, Paragraph, Alignment
from borb.pdf import FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.annotation.remote_go_to_annotation import (
    RemoteGoToAnnotation, )

output_dir = Path("./output")
today = datetime.now()


def _build_invoice_information(job: "Job", due_date):

    sender = job.sender
    table_001 = Table(number_of_rows=6, number_of_columns=3)
    table_001.add(Paragraph(sender.name))
    table_001.add(
        Paragraph("Date",
                  font="Helvetica-Bold",
                  horizontal_alignment=Alignment.RIGHT))
    table_001.add(Paragraph("%d/%d/%d" % (today.month, today.day, today.year)))

    table_001.add(Paragraph(sender.street))
    table_001.add(
        Paragraph("Invoice #",
                  font="Helvetica-Bold",
                  horizontal_alignment=Alignment.RIGHT))
    table_001.add(Paragraph(f"{job.invoice_number}"))

    table_001.add(Paragraph(f"{sender.city}, {sender.state} {sender.zip}"))
    table_001.add(
        Paragraph("Due Date",
                  font="Helvetica-Bold",
                  horizontal_alignment=Alignment.RIGHT))
    table_001.add(
        Paragraph("%d/%d/%d" % (due_date.month, due_date.day, due_date.year)))

    table_001.add(Paragraph(sender.phone))

    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))

    table_001.add(Paragraph(sender.email))
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))

    table_001.add(Paragraph(sender.website))
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))

    table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2),
                                       Decimal(2))
    table_001.no_borders()
    return table_001


def _build_billing_and_shipping_information(job: "Job"):
    table_001 = Table(number_of_rows=6, number_of_columns=2)
    recipient = job.recipient

    billing_header = Paragraph(
        "BILL TO",
        background_color=HexColor("263238"),
        font_color=X11Color("White"),
    )
    shipping_header = Paragraph(
        "SHIP TO",
        background_color=HexColor("263238"),
        font_color=X11Color("White"),
    )
    billing_info = shipping_info = recipient.shipping
    if not job.shipping:
        shipping_info = [" " for x in shipping_info]
        shipping_header = Paragraph(" ")

    table_001.add(billing_header)
    table_001.add(shipping_header)

    info = zip(billing_info, shipping_info)
    for b, s in info:
        table_001.add(Paragraph(b))  # BILLING
        table_001.add(Paragraph(s))  # SHIPPING
    table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2),
                                       Decimal(2))
    table_001.no_borders()
    return table_001


def _build_itemized_description_table(job: "Job"):
    min_lineitems = 8
    n_items = n_rows = len(job.line_items)

    if n_rows < min_lineitems:
        n_rows = min_lineitems
    table_001 = Table(number_of_rows=n_rows + 5, number_of_columns=4)
    for h in ["DESCRIPTION", "QTY/HRS", "UNIT PRICE/RATE", "AMOUNT"]:
        table_001.add(
            TableCell(
                Paragraph(h, font_color=X11Color("White")),
                background_color=HexColor("016934"),
            ))

    odd_color = HexColor("BBBBBB")
    even_color = HexColor("FFFFFF")
    for row_number, line_item in enumerate(job.line_items):
        c = even_color if row_number % 2 == 0 else odd_color
        table_001.add(
            TableCell(Paragraph(line_item.description), background_color=c))
        table_001.add(
            TableCell(Paragraph(f"{line_item.hours:.3f}"), background_color=c))
        table_001.add(
            TableCell(Paragraph(f"$ {line_item.rate:.2f}"),
                      background_color=c))
        table_001.add(
            TableCell(Paragraph(f"$ {line_item.linetotal:.2f}"),
                      background_color=c))


# Optionally add some empty rows to have a fixed number of rows for styling purposes
    for row_number in range(1 + n_items, 1 + n_rows):
        c = even_color if row_number % 2 == 0 else odd_color
        for _ in range(0, 4):
            table_001.add(TableCell(Paragraph(" "), background_color=c))

    table_001.add(
        TableCell(
            Paragraph(
                "Subtotal",
                font="Helvetica-Bold",
                horizontal_alignment=Alignment.RIGHT,
            ),
            col_span=3,
        ))
    table_001.add(
        TableCell(
            Paragraph(f"$ {job.subtotal:07.2f}",
                      horizontal_alignment=Alignment.RIGHT)))
    table_001.add(
        TableCell(
            Paragraph(
                "Discounts",
                font="Helvetica-Bold",
                horizontal_alignment=Alignment.RIGHT,
            ),
            col_span=3,
        ))
    table_001.add(
        TableCell(
            Paragraph(f"$ {job.discounts:07.2f}",
                      horizontal_alignment=Alignment.RIGHT)))
    table_001.add(
        TableCell(
            Paragraph("Taxes",
                      font="Helvetica-Bold",
                      horizontal_alignment=Alignment.RIGHT),
            col_span=3,
        ))
    table_001.add(
        TableCell(
            Paragraph(f"$ {job.tax:07.2f}",
                      horizontal_alignment=Alignment.RIGHT)))
    table_001.add(
        TableCell(
            Paragraph("Total",
                      font="Helvetica-Bold",
                      horizontal_alignment=Alignment.RIGHT),
            col_span=3,
        ))
    table_001.add(
        TableCell(
            Paragraph(f"$ {job.total:07.2f}",
                      horizontal_alignment=Alignment.RIGHT)))
    # table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2),
    #                                    Decimal(2))
    table_001.no_borders()
    return table_001


def _build_addendums(job: "Job"):
    table_001 = Table(number_of_rows=1, number_of_columns=3)
    table_001.add(
        Paragraph("Reference:",
                  font="Helvetica-Bold",
                  horizontal_alignment=Alignment.RIGHT))
    table_001.add(Paragraph(job.reference))
    table_001.add(Paragraph(" "))
    table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2),
                                       Decimal(2))
    table_001.no_borders()

    return table_001


def build_invoice(job: "Job", days_due=30):
    due_date = date_by_adding_business_days(today, 30)
    job_name = f"{job.date.replace('/','')}-{job.recipient.company}-{job.recipient.name}"
    output_file = output_dir / f"{job_name}.pdf"

    # Create document
    pdf = Document()

    # Add page
    page = Page()
    pdf.add_page(page)

    page_layout = SingleColumnLayout(page)
    page_layout.vertical_margin = page.get_page_info().get_height() * Decimal(
        0.02)

    # Empty paragraph for spacing
    add_space = lambda: page_layout.add(Paragraph(" "))

    # page_layout.add(
    #     Image(
    #         "https://s3.stackabuse.com/media/articles/creating-an-invoice-in-python-with-ptext-1.png",
    #         width=Decimal(128),
    #         height=Decimal(128),
    #     ))

    # Invoice information table
    page_layout.add(_build_invoice_information(job, due_date))
    add_space()

    # Billing and shipping information table
    page_layout.add(_build_billing_and_shipping_information(job))
    add_space()

    # Itemized description
    page_layout.add(_build_itemized_description_table(job))
    add_space()

    if job.reference != "":
        page_layout.add(_build_addendums(job))

    if job.paypal != "":
        hyperlink = Paragraph("Online Payment via PayPal",
                              font="Helvetica-Bold",
                              horizontal_alignment=Alignment.CENTERED)
        page_layout.add(hyperlink)

        page.add_annotation(
            RemoteGoToAnnotation(hyperlink.get_bounding_box(), uri=job.paypal))

    with open(output_file, "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, pdf)
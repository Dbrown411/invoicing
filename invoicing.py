from pathlib import Path
from decimal import Decimal
import random, json
from datetime import datetime
from borb.pdf import Document, Page, Image, SingleColumnLayout, PDF
from borb.pdf import TableCell, HexColor, X11Color, Paragraph, Alignment
from borb.pdf import FixedColumnWidthTable as Table
from people import Sender, Recipient
from jobs import Job, assign_invoice_number, date_by_adding_business_days

output_dir = Path("./invoices")
today = datetime.now()
due_date = date_by_adding_business_days(today, 30)


def _build_invoice_information(job: "Job"):

    sender = job.sender
    table_001 = Table(number_of_rows=5, number_of_columns=3)

    table_001.add(Paragraph(sender.street))
    table_001.add(
        Paragraph("Date",
                  font="Helvetica-Bold",
                  horizontal_alignment=Alignment.RIGHT))
    table_001.add(Paragraph("%d/%d/%d" % (today.month, today.day, today.year)))
    table_001.add(Paragraph(f"{sender.city}, {sender.state} {sender.zip}"))
    table_001.add(
        Paragraph("Invoice #",
                  font="Helvetica-Bold",
                  horizontal_alignment=Alignment.RIGHT))
    table_001.add(Paragraph(f"{job.invoice_number}"))

    table_001.add(Paragraph(sender.phone))
    table_001.add(
        Paragraph("Due Date",
                  font="Helvetica-Bold",
                  horizontal_alignment=Alignment.RIGHT))
    table_001.add(
        Paragraph("%d/%d/%d" % (due_date.month, due_date.day, due_date.year)))

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
    recipient = job.recipient
    table_001 = Table(number_of_rows=6, number_of_columns=2)

    table_001.add(
        Paragraph(
            "BILL TO",
            background_color=HexColor("263238"),
            font_color=X11Color("White"),
        ))
    table_001.add(
        Paragraph(
            "SHIP TO",
            background_color=HexColor("263238"),
            font_color=X11Color("White"),
        ))
    address_line2 = f"{recipient.city}, {recipient.state} {recipient.zip}"
    table_001.add(Paragraph(recipient.name))  # BILLING
    table_001.add(Paragraph(recipient.name))  # SHIPPING
    table_001.add(Paragraph(recipient.company))  # BILLING
    table_001.add(Paragraph(recipient.company))  # SHIPPING
    table_001.add(Paragraph(recipient.street))  # BILLING
    table_001.add(Paragraph(recipient.street))  # SHIPPING
    table_001.add(Paragraph(address_line2))  # BILLING
    table_001.add(Paragraph(address_line2))  # SHIPPING
    table_001.add(Paragraph(recipient.phone))  # Phone
    table_001.add(Paragraph(recipient.phone))  # Phone
    table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2),
                                       Decimal(2))
    table_001.no_borders()
    return table_001


def _build_itemized_description_table(job: "Job"):
    table_001 = Table(number_of_rows=15, number_of_columns=4)
    for h in ["DESCRIPTION", "QTY", "UNIT PRICE", "AMOUNT"]:
        table_001.add(
            TableCell(
                Paragraph(h, font_color=X11Color("White")),
                background_color=HexColor("016934"),
            ))

    odd_color = HexColor("BBBBBB")
    even_color = HexColor("FFFFFF")
    for row_number, item in enumerate([("Product 1", 2, 50),
                                       ("Product 2", 4, 60),
                                       ("Labor", 14, 60)]):
        c = even_color if row_number % 2 == 0 else odd_color
        table_001.add(TableCell(Paragraph(item[0]), background_color=c))
        table_001.add(TableCell(Paragraph(str(item[1])), background_color=c))
        table_001.add(TableCell(Paragraph(f"$ {item[2]}"), background_color=c))
        table_001.add(
            TableCell(Paragraph(f"$ {item[1] * item[2]}"), background_color=c))


# Optionally add some empty rows to have a fixed number of rows for styling purposes
    for row_number in range(3, 10):
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
        TableCell(Paragraph("$ 1,180.00",
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
        TableCell(Paragraph("$ 177.00", horizontal_alignment=Alignment.RIGHT)))
    table_001.add(
        TableCell(
            Paragraph("Taxes",
                      font="Helvetica-Bold",
                      horizontal_alignment=Alignment.RIGHT),
            col_span=3,
        ))
    table_001.add(
        TableCell(Paragraph("$ 100.30", horizontal_alignment=Alignment.RIGHT)))
    table_001.add(
        TableCell(
            Paragraph("Total",
                      font="Helvetica-Bold",
                      horizontal_alignment=Alignment.RIGHT),
            col_span=3,
        ))
    table_001.add(
        TableCell(Paragraph("$ 1163.30",
                            horizontal_alignment=Alignment.RIGHT)))
    table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2),
                                       Decimal(2))
    table_001.no_borders()
    return table_001


def main():
    sender = Sender.from_json(Path('./sender/default.json'))
    recipient = Recipient.from_json(Path('./recipients/spective.json'))
    job = Job(date='20220715', sender=sender, recipient=recipient)
    output_file = output_dir / "test.pdf"
    # Create document
    pdf = Document()

    # Add page
    page = Page()
    pdf.add_page(page)

    page_layout = SingleColumnLayout(page)
    page_layout.vertical_margin = page.get_page_info().get_height() * Decimal(
        0.02)

    page_layout.add(
        Image(
            "https://s3.stackabuse.com/media/articles/creating-an-invoice-in-python-with-ptext-1.png",
            width=Decimal(128),
            height=Decimal(128),
        ))

    # Invoice information table
    page_layout.add(_build_invoice_information(job))

    # Empty paragraph for spacing
    page_layout.add(Paragraph(" "))

    # Billing and shipping information table
    page_layout.add(_build_billing_and_shipping_information(job))

    # Itemized description
    page_layout.add(_build_itemized_description_table(job))

    with open(output_file, "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, pdf)


if __name__ == "__main__":
    main()
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os


def seatspdf(available_seats: dict, concert_id: str):
    Story = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    Story.append(Paragraph("Available Tickets for Concert" +
                           concert_id, styles["Center"]))

    for seat in available_seats:
        doc = SimpleDocTemplate(concert_id + ".pdf", pagesize=letter)
        table = Table([(seat.row, seat.seat)], colWidths=10, rowHeights=20)
        Story.append(table)
    doc.build(Story)


def TicketOrdered(ticket_info):
    Story = []
    for index, each in enumerate(ticket_info):
        doc = SimpleDocTemplate("pdftickets/"+each[0] + each[1] + "_ticket.pdf", pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))

        # specifics
        show_logo = 'vms/' + each[8]
        concert_show_name = each[2]

        qr_code = each[7]

        amt_of_tickets = len(ticket_info)

        concert_show_name = each[2]

        customer_name = each[0] + " " + each[1]

        type_of_ticket = "Seat Type: " + each[9]

        date_of_show = "Date of Show: " + each[3]

        customer_seat = "Row: " + each[4] + " Seat: " + each[5]

        show_image = Image(show_logo, 2*inch, 2*inch)
        qr_image = Image(qr_code, 2*inch, 2*inch)

        # Show Logo
        Story.append(show_image)

        # Concert name
        Story.append(Spacer(1, 12))
        ptext = '<font size=12>%s</font>' % concert_show_name
        Story.append(Paragraph(ptext, styles["Center"]))

        # QR Code
        Story.append(Spacer(3, 12))
        Story.append(qr_image)

        # Date of Show
        Story.append(Spacer(1, 12))
        ptext = '<font size=12>%s</font>' % date_of_show
        Story.append(Paragraph(ptext, styles["Center"]))

        # Customer Name
        Story.append(Spacer(5, 60))
        ptext = '<font size=18>%s</font>' % customer_name
        Story.append(Paragraph(ptext, styles["Center"]))

        # Type of Ticket
        Story.append(Spacer(1, 12))
        ptext = '<font size=12>%s</font>' % type_of_ticket
        Story.append(Paragraph(ptext, styles["Center"]))

        # Location
        Story.append(Spacer(5, 30))
        ptext = '<font size=18>%s</font>' % each[6]
        Story.append(Paragraph(ptext, styles["Center"]))

        # Seat
        Story.append(Spacer(10, 30))
        ptext = '<font size=10>%s</font>' % customer_seat
        Story.append(Paragraph(ptext, styles["Center"]))
        Story.append(PageBreak())

    doc.build(Story)
    return "pdftickets/"+each[0] + each[1] + "_ticket.pdf"


def GenTicket(ticket_info):
    Story = []
    for each in ticket_info:
        doc = SimpleDocTemplate("pdftickets/"+each[0] + each[1] + "_ticket.pdf", pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))

        # specifics

        show_logo = "vms/" + each[10]
        concert_show_name = each[2]

        qr_code = each[7]

        customer_name = each[0] + " " + each[1]

        date_of_show = "Date of Show: " + each[3]

        customer_seat = "Row: " + each[4] + " Seat: " + each[5]

        show_image = Image(show_logo, 2*inch, 2*inch)
        qr_image = Image(qr_code, 2*inch, 2*inch)

        # Show Logo
        Story.append(show_image)

        # Concert name
        Story.append(Spacer(1, 12))
        ptext = '<font size=12>%s</font>' % concert_show_name
        Story.append(Paragraph(ptext, styles["Center"]))

        # QR Code
        Story.append(Spacer(3, 12))
        Story.append(qr_image)

        # Date of Show
        Story.append(Spacer(1, 12))
        ptext = '<font size=12>%s</font>' % date_of_show
        Story.append(Paragraph(ptext, styles["Center"]))

        # Customer Name
        Story.append(Spacer(5, 60))
        ptext = '<font size=18>%s</font>' % customer_name
        Story.append(Paragraph(ptext, styles["Center"]))

        # Location
        Story.append(Spacer(5, 30))
        ptext = '<font size=18>%s</font>' % each[6]
        Story.append(Paragraph(ptext, styles["Center"]))

        # Seat
        Story.append(Spacer(10, 30))
        ptext = '<font size=10>%s</font>' % customer_seat
        Story.append(Paragraph(ptext, styles["Center"]))
        Story.append(PageBreak())
    doc.build(Story)
    return "pdftickets/"+each[0] + each[1] + "_ticket.pdf"

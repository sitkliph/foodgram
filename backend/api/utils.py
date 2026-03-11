from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (HRFlowable, Image, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

from backend.settings import BASE_DIR


def generate_shopping_cart_pdf(ingredients, user) -> BytesIO:
    """Функция генерации PDF документа со списком покупок пользователя."""
    pdfmetrics.registerFont(TTFont(
        'Raleway', BASE_DIR / 'pdf_static' / 'fonts' / 'Raleway-Regular.ttf'
    ))
    pdfmetrics.registerFont(TTFont(
        'Raleway-Bold', BASE_DIR / 'pdf_static' / 'fonts' / 'Raleway-Bold.ttf'
    ))

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontName='Raleway-Bold',
        fontSize=16,
        spaceAfter=0,
        textTransform='uppercase'
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='Raleway',
        fontSize=12,
        textColor=colors.HexColor('#333333'),
    )

    elements = []

    header = Table([
        (
            Image(BASE_DIR / 'pdf_static' / 'logo.png', width=160, height=45),
            Paragraph('Список покупок', title_style)
        )
    ], colWidths=[60 * mm, 110 * mm])
    header.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0)
    ]))

    elements.append(header)
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width='100%', thickness=1))
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(
        f'Пользователь: {user.first_name} {user.last_name}', normal_style)
    )
    elements.append(Spacer(1, 10))

    if ingredients:
        data = [('№', 'Ингредиент', 'Количество')]

        for index, item in enumerate(ingredients, start=1):
            data.append((
                str(index),
                item['ingredient__name'],
                (
                    f'{item['total_amount']} '
                    f'{item['ingredient__measurement_unit']}'
                ),
            ))

        table = Table(data, colWidths=[20 * mm, 100 * mm, 50 * mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EAEAEA')),
            ('FONTNAME', (0, 0), (-1, 0), 'Raleway-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Raleway'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D0D0D0')),
        ]))

        elements.append(table)
    else:
        elements.append(Paragraph('Список покупок пуст!', normal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

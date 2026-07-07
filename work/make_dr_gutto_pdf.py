from pathlib import Path

from PIL import Image, ImageOps
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
TMP = ROOT / "tmp" / "pdfs"
ASSETS = OUTPUTS / "assets"
PDF_PATH = OUTPUTS / "dr-gutto-vilhena-apresentacao-site.pdf"

INSTAGRAM_URL = "https://www.instagram.com/dr.guttovilhena/"
WHATSAPP_URL = "https://wa.me/5535991338862"
SITE_URL = "https://www.drguttovilhena.com.br/"
MAPS_URL = "https://maps.app.goo.gl/GqoGFmA3ZqCaj3mr6"
PHONE_DISPLAY = "+55 35 99133-8862"
EMAIL_DISPLAY = "guttodentista@outlook.com"
EMAIL_URL = f"mailto:{EMAIL_DISPLAY}"
ADDRESS_DISPLAY = "Rua Martins Alfenas, 1918 - Centro, Alfenas-MG"
HOURS_DISPLAY = "Seg. a sex., 8h30 às 19h | Sáb., 9h às 12h"

PAGE_W, PAGE_H = landscape(A4)

INK = colors.HexColor("#172125")
MUTED = colors.HexColor("#5f6d70")
LINE = colors.HexColor("#dce5e3")
PAPER = colors.HexColor("#ffffff")
SOFT = colors.HexColor("#f4f8f7")
MIST = colors.HexColor("#e8f0ee")
TEAL = colors.HexColor("#176863")
TEAL_DARK = colors.HexColor("#0d3b3a")
COPPER = colors.HexColor("#b76c43")


styles = getSampleStyleSheet()
BODY = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=12.5,
    leading=18,
    textColor=MUTED,
    spaceAfter=0,
)
BODY_WHITE = ParagraphStyle(
    "BodyWhite",
    parent=BODY,
    textColor=colors.Color(1, 1, 1, alpha=0.82),
)
PROCESS_WHITE = ParagraphStyle(
    "ProcessWhite",
    parent=BODY_WHITE,
    fontSize=10.5,
    leading=14,
)
SMALL = ParagraphStyle(
    "Small",
    parent=BODY,
    fontSize=9.5,
    leading=13,
)
CARD_TEXT = ParagraphStyle(
    "CardText",
    parent=BODY,
    fontSize=10.8,
    leading=15.4,
)


def prepare_image_cover(src, name, size_px, centering=(0.5, 0.5)):
    TMP.mkdir(parents=True, exist_ok=True)
    out = TMP / name
    img = Image.open(src).convert("RGB")
    fitted = ImageOps.fit(img, size_px, method=Image.Resampling.LANCZOS, centering=centering)
    fitted.save(out, quality=94)
    return out


def draw_image(c, src, x, y, w, h):
    c.drawImage(str(src), x, y, width=w, height=h, preserveAspectRatio=False, mask="auto")


def paragraph(c, text, x, y_top, w, style=BODY):
    p = Paragraph(text, style)
    _, h = p.wrap(w, PAGE_H)
    p.drawOn(c, x, y_top - h)
    return h


def draw_label(c, text, x, y, color=COPPER):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(x, y, text.upper())


def draw_title(c, text, x, y, max_width, font_size=44, leading=46, color=INK):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", font_size)
    words = text.split()
    lines = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if stringWidth(candidate, "Helvetica-Bold", font_size) <= max_width:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    for i, line in enumerate(lines):
        c.drawString(x, y - i * leading, line)
    return len(lines) * leading


def rounded_rect(c, x, y, w, h, fill, stroke=None, radius=8, alpha=1):
    c.saveState()
    c.setFillColor(fill)
    c.setFillAlpha(alpha)
    if stroke:
        c.setStrokeColor(stroke)
        c.setStrokeAlpha(1)
    else:
        c.setStrokeAlpha(0)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1 if stroke else 0)
    c.restoreState()


def button(c, label, x, y, w, h, fill=TEAL_DARK, text_color=PAPER, link=None):
    rounded_rect(c, x, y, w, h, fill, radius=h / 2)
    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(x + w / 2, y + h / 2 - 4, label)
    if link:
        c.linkURL(link, (x, y, x + w, y + h), relative=0)


def footer(c, page, label="www.drguttovilhena.com.br"):
    c.setStrokeColor(LINE)
    c.line(44, 34, PAGE_W - 44, 34)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8.5)
    c.drawString(44, 18, "Dr. Gutto Jordão Vilhena | CRO 64064-MG")
    c.drawCentredString(PAGE_W / 2, 18, label)
    c.linkURL(SITE_URL, (PAGE_W / 2 - 80, 10, PAGE_W / 2 + 80, 28), relative=0)
    c.drawRightString(PAGE_W - 44, 18, f"{page}/4")


def draw_qr(c, url, x, y, size):
    widget = qr.QrCodeWidget(url)
    bounds = widget.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    drawing = Drawing(
        size,
        size,
        transform=[size / width, 0, 0, size / height, 0, 0],
    )
    drawing.add(widget)
    renderPDF.draw(drawing, c, x, y)
    c.linkURL(url, (x, y, x + size, y + size), relative=0)


def page_cover(c, hero):
    draw_image(c, hero, 0, 0, PAGE_W, PAGE_H)
    rounded_rect(c, 0, 0, PAGE_W * 0.6, PAGE_H, PAPER, alpha=0.92, radius=0)
    rounded_rect(c, 44, PAGE_H - 104, 306, 52, PAPER, stroke=LINE, radius=26, alpha=0.96)
    draw_image(c, ASSETS / "dr-gutto-profile.jpg", 58, PAGE_H - 94, 32, 32)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(102, PAGE_H - 76, "Dr. Gutto Vilhena")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawString(102, PAGE_H - 90, "Cirurgião Dentista | CRO 64064-MG")

    x = 58
    draw_label(c, "site profissional", x, PAGE_H - 170)
    draw_title(c, "Dr. Gutto Jordão Vilhena", x, PAGE_H - 208, 410, font_size=43, leading=46)
    paragraph(
        c,
        "Landing page profissional para apresentar atendimento odontológico com foco em implantes dentários e ortodontia, com comunicação clara, visual limpo e caminho direto para contato.",
        x,
        PAGE_H - 325,
        405,
        BODY,
    )

    button(c, "Chamar no WhatsApp", x, 126, 154, 38, link=WHATSAPP_URL)
    button(c, "Abrir site", x + 168, 126, 166, 38, fill=PAPER, text_color=INK, link=SITE_URL)
    rounded_rect(c, x, 64, 352, 36, PAPER, stroke=LINE, radius=8, alpha=0.86)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(x + 16, 78, "Implantes Dentários    Ortodontia    CRO 64064-MG")

    c.setFillColor(colors.Color(0, 0, 0, alpha=0.22))
    c.rect(0, 0, PAGE_W, 12, fill=1, stroke=0)


def page_home_preview(c, hero):
    c.setFillColor(SOFT)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_label(c, "prévia da primeira tela", 44, PAGE_H - 66)
    draw_title(c, "A página inicial em formato de site", 44, PAGE_H - 98, 470, font_size=31, leading=35)
    paragraph(
        c,
        "O primeiro contato destaca nome, áreas de atendimento e registro profissional, com botões diretos para avaliação e tratamentos.",
        44,
        PAGE_H - 176,
        420,
        BODY,
    )

    browser_x, browser_y, browser_w, browser_h = 54, 66, 734, 300
    rounded_rect(c, browser_x, browser_y, browser_w, browser_h, PAPER, stroke=LINE, radius=12)
    rounded_rect(c, browser_x, browser_y + browser_h - 42, browser_w, 42, PAPER, stroke=LINE, radius=12)
    c.setFillColor(colors.HexColor("#d8e4e2"))
    for i in range(3):
        c.circle(browser_x + 20 + i * 16, browser_y + browser_h - 22, 4.5, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(browser_x + 86, browser_y + browser_h - 26, "Dr. Gutto Vilhena")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawRightString(browser_x + browser_w - 24, browser_y + browser_h - 26, "Atendimentos    Abordagem    Contato")

    inner_x, inner_y = browser_x, browser_y
    inner_w, inner_h = browser_w, browser_h - 42
    draw_image(c, hero, inner_x + inner_w * 0.38, inner_y, inner_w * 0.62, inner_h)
    rounded_rect(c, inner_x, inner_y, inner_w * 0.58, inner_h, PAPER, alpha=0.9, radius=0)
    draw_label(c, "cirurgião dentista", inner_x + 34, inner_y + inner_h - 64)
    draw_title(c, "Dr. Gutto Jordão Vilhena", inner_x + 34, inner_y + inner_h - 95, 330, font_size=27, leading=30)
    paragraph(
        c,
        "Atendimento odontológico com foco em implantes dentários e ortodontia, conduzido com planejamento claro.",
        inner_x + 34,
        inner_y + inner_h - 148,
        320,
        ParagraphStyle("PreviewBody", parent=BODY, fontSize=8.9, leading=11.6),
    )
    button(c, "Agendar avaliação", inner_x + 34, inner_y + 36, 128, 28, fill=TEAL_DARK, link=WHATSAPP_URL)
    button(
        c,
        "Ver tratamentos",
        inner_x + 174,
        inner_y + 36,
        122,
        28,
        fill=PAPER,
        text_color=INK,
        link=f"{SITE_URL}#especialidades",
    )

    rounded_rect(c, 530, 438, 258, 84, PAPER, stroke=LINE, radius=8)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(552, 489, "Direção visual")
    paragraph(
        c,
        "Clínico, limpo e confiável. A imagem valoriza tecnologia e cuidado sem criar promessa clínica ou informação não confirmada.",
        552,
        470,
        210,
        SMALL,
    )
    footer(c, 2)


def page_services(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_label(c, "conteúdo do site", 44, PAGE_H - 66)
    draw_title(c, "Atendimentos e jornada do paciente", 44, PAGE_H - 98, 720, font_size=31, leading=35)

    cards = [
        ("Implantes dentários", "Planejamento para reabilitação oral com atenção a diagnóstico, previsibilidade e orientação sobre cada etapa do tratamento."),
        ("Ortodontia", "Avaliação da mordida e alinhamento dentário para construir um plano compatível com a rotina e a necessidade do paciente."),
        ("Avaliação odontológica", "Conversa inicial, exame clínico e orientações para que o paciente entenda opções, limites e próximos passos."),
    ]
    x0, y0, gap = 44, 274, 16
    card_w, card_h = (PAGE_W - 88 - gap * 2) / 3, 154
    for i, (title, text) in enumerate(cards):
        x = x0 + i * (card_w + gap)
        rounded_rect(c, x, y0, card_w, card_h, SOFT, stroke=LINE, radius=8)
        c.setFillColor(COPPER)
        c.circle(x + 28, y0 + card_h - 34, 14, fill=1, stroke=0)
        c.setFillColor(PAPER)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(x + 28, y0 + card_h - 39, str(i + 1))
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 15)
        c.drawString(x + 54, y0 + card_h - 40, title)
        paragraph(c, text, x + 24, y0 + card_h - 76, card_w - 48, CARD_TEXT)

    rounded_rect(c, 44, 72, PAGE_W - 88, 148, TEAL_DARK, radius=10)
    c.setFillColor(PAPER)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(74, 182, "Abordagem em 3 passos")
    steps = [
        ("01", "Avaliação", "Escuta, exame clínico e necessidades principais."),
        ("02", "Planejamento", "Alternativas, etapas e cuidados esperados."),
        ("03", "Acompanhamento", "Retornos e orientações durante o tratamento."),
    ]
    step_w = (PAGE_W - 160) / 3
    for i, (num, title, text) in enumerate(steps):
        x = 74 + i * step_w
        c.setFillColor(COPPER)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, 150, num)
        c.setFillColor(PAPER)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(x, 130, title)
        paragraph(c, text, x, 111, step_w - 22, PROCESS_WHITE)
    footer(c, 3)


def page_contact(c):
    c.setFillColor(SOFT)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_label(c, "dados oficiais", 44, PAGE_H - 66)
    draw_title(c, "Contato direto e dados do consultório", 44, PAGE_H - 98, 560, font_size=32, leading=36)
    paragraph(
        c,
        "A versão atual já mostra WhatsApp, telefone, e-mail, endereço, rota no Google Maps e horários de funcionamento para facilitar o agendamento.",
        44,
        PAGE_H - 174,
        485,
        BODY,
    )

    rounded_rect(c, 44, 184, 330, 186, PAPER, stroke=LINE, radius=8)
    draw_image(c, ASSETS / "dr-gutto-profile.jpg", 70, 302, 50, 50)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(140, 332, PHONE_DISPLAY)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 11)
    c.drawString(140, 314, "WhatsApp do consultório")
    button(c, "Iniciar conversa", 70, 262, 130, 34, link=WHATSAPP_URL)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawString(216, 274, "Instagram: @dr.guttovilhena")
    c.linkURL(INSTAGRAM_URL, (216, 267, 353, 282), relative=0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(70, 232, EMAIL_DISPLAY)
    c.linkURL(EMAIL_URL, (70, 226, 244, 240), relative=0)
    c.setFont("Helvetica", 9)
    c.drawString(70, 211, HOURS_DISPLAY)

    rounded_rect(c, 414, 172, 158, 198, PAPER, stroke=LINE, radius=8)
    draw_qr(c, WHATSAPP_URL, 440, 212, 106)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(493, 192, "QR do WhatsApp")

    rounded_rect(c, 604, 136, 194, 234, PAPER, stroke=LINE, radius=8)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(626, 334, "Próximos ajustes")
    checklist = [
        "Fotos reais do espaço",
        "Logo final aprovado",
        "Perfil da Empresa no Google",
        "Search Console",
        "Revisão final do profissional",
    ]
    y = 302
    for item in checklist:
        c.setStrokeColor(TEAL)
        c.circle(632, y + 3, 5, fill=0, stroke=1)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 10.5)
        c.drawString(648, y, item)
        y -= 28

    rounded_rect(c, 44, 66, PAGE_W - 88, 72, TEAL_DARK, radius=8)
    c.setFillColor(PAPER)
    c.setFont("Helvetica-Bold", 11.5)
    c.drawString(66, 112, ADDRESS_DISPLAY)
    c.linkURL(MAPS_URL, (66, 106, 360, 122), relative=0)
    c.setFont("Helvetica", 10)
    c.drawString(66, 91, "Rota no Google Maps integrada ao site")
    c.drawRightString(PAGE_W - 66, 91, "CRO-MG 64.064")
    footer(c, 4)


def main():
    hero = prepare_image_cover(
        ASSETS / "dental-clinic-hero.png",
        "hero_pdf_cover.jpg",
        (1800, 1272),
        centering=(0.62, 0.5),
    )
    c = canvas.Canvas(str(PDF_PATH), pagesize=landscape(A4))
    c.setTitle("Apresentação do site - Dr. Gutto Jordão Vilhena")
    c.setAuthor("Codex")

    page_cover(c, hero)
    c.showPage()
    page_home_preview(c, hero)
    c.showPage()
    page_services(c)
    c.showPage()
    page_contact(c)
    c.save()
    print(PDF_PATH)


if __name__ == "__main__":
    main()

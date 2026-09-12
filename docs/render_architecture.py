#!/usr/bin/env python3
"""Render docs/architecture.png — dark-theme stack diagram."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).with_name("architecture.png")
W, H = 2200, 1580
BG = (11, 15, 20)
CARD = (18, 24, 33)
CARD_LINE = (47, 111, 237)
GROUP = (16, 20, 28)
GROUP_LINE = (55, 70, 92)
TEXT = (230, 235, 241)
MUTED = (139, 148, 158)
ACCENT = (56, 139, 253)
GREEN = (63, 185, 80)
AMBER = (210, 153, 34)
TEAL = (63, 185, 168)

FONT_REG = "/usr/share/fonts/truetype/lato/Lato-Medium.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"


def fnt(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def rounded(draw, box, fill, outline, radius=22, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_size(draw, text, font):
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1]


def center_text(draw, xy, text, font, fill=TEXT):
    x, y = xy
    tw, th = text_size(draw, text, font)
    draw.text((x - tw / 2, y - th / 2), text, font=font, fill=fill)


def card(draw, box, title, subtitle, title_fill=TEXT, outline=CARD_LINE):
    rounded(draw, box, CARD, outline, radius=20, width=2)
    cx = (box[0] + box[2]) / 2
    cy = (box[1] + box[3]) / 2
    center_text(draw, (cx, cy - 16), title, fnt(28, True), title_fill)
    center_text(draw, (cx, cy + 22), subtitle, fnt(20), MUTED)
    return box


def vline(draw, x, y1, y2, color=ACCENT, width=3):
    draw.line((x, y1, x, y2), fill=color, width=width)


def hline(draw, x1, x2, y, color=ACCENT, width=3):
    draw.line((x1, y, x2, y), fill=color, width=width)


def down_arrow(draw, x, y, color=ACCENT):
    draw.polygon([(x, y), (x - 8, y - 14), (x + 8, y - 14)], fill=color)


def right_arrow(draw, x, y, color=ACCENT):
    draw.polygon([(x, y), (x - 14, y - 8), (x - 14, y + 8)], fill=color)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Reverse proxy
    center_text(d, (160, 200), "Reverse proxy", fnt(18), MUTED)
    center_text(d, (160, 226), "(TLS)", fnt(18), MUTED)
    hline(d, 250, 318, 213, MUTED, 2)
    right_arrow(d, 318, 213, MUTED)

    # UIs
    ui = (340, 70, 2060, 300)
    rounded(d, ui, GROUP, GROUP_LINE, radius=28, width=2)
    center_text(d, (1200, 104), "Observability UIs", fnt(24, True), MUTED)
    card(d, (400, 140, 860, 270), "Grafana", ":3000")
    card(d, (930, 140, 1390, 270), "Prometheus", ":9090")
    card(d, (1460, 140, 2000, 270), "Alertmanager", ":9093")

    # Stem + bus to scrape targets
    bus_y = 360
    vline(d, 1160, 300, bus_y, GROUP_LINE)
    down_arrow(d, 1160, bus_y, GROUP_LINE)
    center_text(d, (1160, 328), "private monitoring network", fnt(18), MUTED)

    targets = [
        (140, 430, 620, 590, "Django app", "/metrics  +  OTLP", GREEN, CARD_LINE),
        (680, 430, 1100, 590, "postgres_exporter", ":9187", TEXT, CARD_LINE),
        (1160, 430, 1580, 590, "celery_exporter", ":9808", TEXT, CARD_LINE),
    ]
    xs = []
    for box in targets:
        card(d, box[:4], box[4], box[5], box[6], box[7])
        xs.append((box[0] + box[2]) / 2)

    hline(d, xs[0], xs[2], bus_y, GROUP_LINE)
    for x in xs:
        vline(d, x, bus_y, 430, GROUP_LINE)
        down_arrow(d, x, 428, GROUP_LINE)
    center_text(d, (380, 388), "scrape /metrics", fnt(18), MUTED)

    # Collector row
    otel = card(
        d,
        (680, 720, 1580, 880),
        "OpenTelemetry Collector",
        "OTLP :4317 / :4318     scrape :8888",
        ACCENT,
        ACCENT,
    )
    otel_x = 1130

    # OTLP from Django (and implied Celery) down then into collector
    d_x = 380
    vline(d, d_x, 590, 800, GREEN)
    hline(d, d_x, 680, 800, GREEN)
    right_arrow(d, 678, 800, GREEN)
    center_text(d, (500, 770), "OTLP traces / logs", fnt(18), GREEN)

    # Prometheus scrape of collector internals (route around the right)
    far_x = 1920
    vline(d, far_x, 300, 800, MUTED)
    hline(d, 1580, far_x, 800, MUTED)
    d.polygon([(1580, 800), (1594, 792), (1594, 808)], fill=MUTED)
    center_text(d, (1920, 640), "scrape :8888", fnt(18), MUTED)

    # OpenSearch
    os_box = (140, 1000, 2060, 1420)
    rounded(d, os_box, GROUP, GROUP_LINE, radius=28, width=2)
    center_text(d, (1100, 1040), "OpenSearch on LKE", fnt(24, True), MUTED)

    master = (220, 1090, 740, 1340)
    hot = (820, 1090, 1380, 1340)
    medium = (1460, 1090, 1980, 1340)
    rounded(d, master, CARD, (80, 90, 110), radius=20, width=2)
    rounded(d, hot, CARD, AMBER, radius=20, width=3)
    rounded(d, medium, CARD, TEAL, radius=20, width=2)

    center_text(d, (480, 1155), "3 master", fnt(32, True))
    center_text(d, (480, 1210), "cluster_manager only", fnt(22), MUTED)
    center_text(d, (480, 1258), "no ingest   ·   no data", fnt(20), MUTED)

    center_text(d, (1100, 1155), "3 hot", fnt(32, True), AMBER)
    center_text(d, (1100, 1210), "data + ingest", fnt(22), MUTED)
    center_text(d, (1100, 1258), "new traces and logs", fnt(20), MUTED)

    center_text(d, (1720, 1155), "3 medium", fnt(32, True), TEAL)
    center_text(d, (1720, 1210), "data only", fnt(22), MUTED)
    center_text(d, (1720, 1258), "indices older than 7 days", fnt(20), MUTED)

    # collector -> hot
    vline(d, otel_x, 880, 1090, AMBER)
    down_arrow(d, otel_x, 1088, AMBER)
    center_text(d, (1260, 960), "write to hot nodes", fnt(18), AMBER)

    # ISM hot -> medium
    hline(d, 1380, 1460, 1215, TEAL)
    right_arrow(d, 1460, 1215, TEAL)
    center_text(d, (1420, 1185), "ISM 7d", fnt(16), TEAL)

    center_text(
        d,
        (1100, 1485),
        "Metrics stay on Prometheus.   Traces and logs go Django / Celery → collector → OpenSearch hot.",
        fnt(20),
        MUTED,
    )
    center_text(
        d,
        (1100, 1530),
        "LKE HA control plane (3) is separate from the 3 OpenSearch master workers.",
        fnt(18),
        MUTED,
    )

    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

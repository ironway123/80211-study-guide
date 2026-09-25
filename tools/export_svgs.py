"""Export the study guide's diagrams as standalone, theme-aware SVG files.

Usage (from the repo root):  python3 tools/export_svgs.py
Reads the inline SVGs from source/80211-study-guide.html, draws the 2.4 GHz channel
chart and both key hierarchies here, and writes everything to images/.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source" / "80211-study-guide.html"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "images"
OUT.mkdir(parents=True, exist_ok=True)

LIGHT = dict(SURFACE="#FFFFFF", SURFACE2="#EAEFF3", INK="#15212B", MUTED="#56646F", LINE="#D3DBE1",
             ACCENT="#1E4E8C", ACCENTSOFT="#E2EBF7", B24="#B25F08", B5="#0A7381", B5SOFT="#DAEFF1",
             B6="#6947BF", OKSOFT="#DFF0E6", WARN="#A0441A")
DARK = dict(SURFACE="#141C23", SURFACE2="#1C2630", INK="#E2E8ED", MUTED="#98A5AF", LINE="#29353F",
            ACCENT="#8DB4EE", ACCENTSOFT="#1A2A3E", B24="#EDA24E", B5="#4CC1CD", B5SOFT="#0E2A2E",
            B6="#AE95F3", OKSOFT="#13281C", WARN="#EE9467")
SANS = "'IBM Plex Sans',system-ui,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

RULES = """
.bg{fill:SURFACE;stroke:LINE;stroke-width:1}
text{font-family:SANSF;fill:INK}
.t-mono{font-family:MONOF}
.t-muted{fill:MUTED}
.ink{fill:INK}
.axis{stroke:MUTED;stroke-width:1;fill:none}
.grid{stroke:LINE;stroke-width:1;fill:none}
.ch-main{fill:B24;fill-opacity:.16;stroke:B24;stroke-width:2}
.ch-other{fill:none;stroke:MUTED;stroke-width:1;stroke-dasharray:3 3;opacity:.75}
.ch-jp{fill:none;stroke:MUTED;stroke-width:1;stroke-dasharray:1 3;opacity:.6}
.f24{fill:B24}.f5{fill:B5}.f6{fill:B6}
.t24{fill:B24}.t5{fill:B5}.t6{fill:B6}
.mk{fill:ACCENT}.mk-ink{fill:INK}
.ray{stroke:ACCENT;stroke-width:2;fill:none;stroke-linecap:round}
.ray.thin{stroke-width:1.3}
.surf{stroke:INK;stroke-width:3;fill:none}
.hatch{stroke:MUTED;stroke-width:1;fill:none}
.guide{stroke:MUTED;stroke-width:1;stroke-dasharray:3 3;fill:none}
.medium{fill:B5SOFT;stroke:none}
.block{fill:MUTED;fill-opacity:.55;stroke:none}
.block-soft{fill:B5;fill-opacity:.22;stroke:B5;stroke-width:1}
.shadow{fill:MUTED;fill-opacity:.12;stroke:none}
.wave{stroke:B5;stroke-width:1.5;fill:none}
.particle{fill:INK}
.lifeline{stroke:LINE;stroke-width:2;stroke-dasharray:5 4;fill:none}
.actor{fill:SURFACE2;stroke:LINE;stroke-width:1}
.msg{stroke:INK;stroke-width:1.8;fill:none}
.msg.wired{stroke:MUTED;stroke-dasharray:5 4}
.note{fill:SURFACE2;stroke:none}
.pre{fill:ACCENTSOFT;stroke:none}
.done{fill:OKSOFT;stroke:none}
.dfs{fill:url(#dfs-hatch)}
.hatch-line{stroke:SURFACE;stroke-width:1.6}
.kb{fill:SURFACE2;stroke:none}
.kb-acc{fill:ACCENTSOFT;stroke:none}
.kb-gtk{fill:B5SOFT;stroke:none}
.kt-acc{fill:ACCENT}
.kt-gtk{fill:B5}
.kline{stroke:MUTED;stroke-width:1.5;fill:none}
.wired-zone{fill:SURFACE2;stroke:none}
.halo{paint-order:stroke;stroke:SURFACE;stroke-width:5px;stroke-linejoin:round}
.relay{fill:SURFACE;stroke:INK;stroke-width:1.5}
.fld{fill:SURFACE2;stroke:LINE;stroke-width:1}
.fld-opt{fill:SURFACE;stroke:MUTED;stroke-width:1;stroke-dasharray:3 3}
.fld-hi{fill:ACCENTSOFT;stroke:ACCENT;stroke-width:1}
.busy{fill:MUTED;fill-opacity:.35;stroke:none}
.ifs{fill:SURFACE;stroke:MUTED;stroke-width:1;stroke-dasharray:2 2}
.tx-a{fill:ACCENT;stroke:none}
.tx-b{fill:B5;stroke:none}
.on-fill{fill:SURFACE}
.ackbox{fill:SURFACE;stroke:INK;stroke-width:1.5}
.slot{fill:SURFACE;stroke:MUTED;stroke-width:1}
.frozen{fill:MUTED;fill-opacity:.12;stroke:MUTED;stroke-width:1;stroke-dasharray:4 3}
.nav{fill:B6;fill-opacity:.2;stroke:B6;stroke-width:1}
.t-nav{fill:B6}
.range-a{fill:ACCENT;fill-opacity:.07;stroke:ACCENT;stroke-width:1.2;stroke-dasharray:5 4}
.range-b{fill:B5;fill-opacity:.07;stroke:B5;stroke-width:1.2;stroke-dasharray:5 4}
.t-acc{fill:ACCENT}
.dev{fill:SURFACE;stroke:INK;stroke-width:1.5}
.warn-f{fill:WARN}
.warn-s{stroke:WARN;stroke-width:1.5;fill:none;stroke-dasharray:4 4}
.t-warn{fill:WARN}
.row-line{stroke:LINE;stroke-width:1;fill:none}
"""

DEFS = """<defs>
<marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" class="mk"/></marker>
<marker id="arr-ink" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" class="mk-ink"/></marker>
<pattern id="dfs-hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" class="f5"/><line x1="0" y1="0" x2="0" y2="5" class="hatch-line"/></pattern>
</defs>"""


def fill(tokens):
    css = RULES.replace("SANSF", SANS).replace("MONOF", MONO)
    # Longest names first so SURFACE2 is not clobbered by SURFACE.
    for k in sorted(tokens, key=len, reverse=True):
        css = css.replace(k, tokens[k])
    return css


STYLE = "<style>" + fill(LIGHT) + "@media (prefers-color-scheme: dark){" + fill(DARK) + "}</style>"


def wrap(inner, w, h, label, pad=12):
    W, H = w + 2 * pad, h + 2 * pad
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'role="img" aria-label="{label}">\n{STYLE}\n{DEFS}\n'
            f'<rect class="bg" x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10"/>\n'
            f'<g transform="translate({pad},{pad})">\n{inner}\n</g>\n</svg>\n')


def clean(inner):
    inner = inner.replace('class="t-mono" style="fill:var(--ink)"', 'class="t-mono ink"')
    assert "var(" not in inner, inner[:200]
    return inner.strip()


html = SRC.read_text()
main = html[html.index("<main>"):]
svgs = re.findall(r"<svg([^>]*)>(.*?)</svg>", main, re.S)


def vb(attrs):
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', attrs)
    return int(m.group(1)), int(m.group(2))


def aria(attrs, default):
    m = re.search(r'aria-label="([^"]*)"', attrs)
    return m.group(1) if m else default


names = ["bands-spectrum", "channels-2.4ghz", "reflection", "refraction", "diffraction",
         "scattering", "absorption", "four-way-handshake", "eap-exchange", "sae-exchange", "ft-over-the-air"]
assert len(svgs) == len(names), len(svgs)


def channels_24():
    f0, k, x0, base, top = 2395, 650 / 105, 40, 172, 70
    half = 11 * k
    x = lambda f: x0 + (f - f0) * k
    out = []
    for e in (2400, 2483.5):
        out.append(f'<line x1="{x(e):.1f}" y1="40" x2="{x(e):.1f}" y2="{base}" class="grid" stroke-dasharray="2 3"/>')
    main_ch = {1, 6, 11}
    for n in [2, 3, 4, 5, 7, 8, 9, 10, 12, 13, 14, 1, 6, 11]:
        c = x(2484 if n == 14 else 2407 + 5 * n)
        cls = "ch-main" if n in main_ch else ("ch-jp" if n == 14 else "ch-other")
        d = (f"M{c-half:.1f} {base} C{c-half*0.53:.1f} {base} {c-half*0.47:.1f} {top} {c:.1f} {top} "
             f"S{c+half*0.53:.1f} {base} {c+half:.1f} {base}")
        out.append(f'<path d="{d}" class="{cls}"/>')
    for n in range(1, 15):
        c = x(2484 if n == 14 else 2407 + 5 * n)
        if n in main_ch:
            out.append(f'<text x="{c:.1f}" y="{top-8}" text-anchor="middle" font-size="13" font-weight="700" class="t-mono t24">{n}</text>')
        else:
            out.append(f'<text x="{c:.1f}" y="{top-8}" text-anchor="middle" font-size="11.5" class="t-mono t-muted">{n}</text>')
    out.append(f'<text x="{x(2407):.1f}" y="32" class="t-muted" font-size="11.5">channel</text>')
    out.append(f'<line x1="{x0}" y1="{base}" x2="690" y2="{base}" class="axis"/>')
    for f, lbl in [(2400, "2.400"), (2412, "2.412"), (2437, "2.437"), (2462, "2.462"), (2483.5, "2.4835")]:
        out.append(f'<line x1="{x(f):.1f}" y1="{base}" x2="{x(f):.1f}" y2="{base+5}" class="axis"/>')
        out.append(f'<text x="{x(f):.1f}" y="{base+20}" text-anchor="middle" font-size="11" class="t-mono t-muted">{lbl}</text>')
    out.append(f'<text x="690" y="{base+36}" text-anchor="end" font-size="11" class="t-muted">GHz</text>')
    return "\n".join(out)


for name, (attrs, inner) in zip(names, svgs):
    w, h = vb(attrs)
    if name == "channels-2.4ghz":
        inner = channels_24()
    pad = 8 if w <= 160 else 12
    label = aria(attrs, name.replace("-", " ").capitalize() + " diagram")
    (OUT / f"{name}.svg").write_text(wrap(clean(inner), w, h, label, pad))


# ---- Key hierarchy diagrams (HTML boxes on the page, redrawn as SVG) ----
def box(x, y, w, h, title, lines, kind="kb"):
    tcls = {"kb": "", "kb-acc": " kt-acc", "kb-gtk": " kt-gtk"}[kind]
    cx = x + w / 2
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" class="{kind}"/>',
             f'<text x="{cx}" y="{y+20}" text-anchor="middle" font-size="13" font-weight="600" class="t-mono{tcls}">{title}</text>']
    for i, ln in enumerate(lines):
        parts.append(f'<text x="{cx}" y="{y+38+i*16}" text-anchor="middle" font-size="12" class="t-muted">{ln}</text>')
    return "\n".join(parts)


def arrow(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="kline" marker-end="url(#arr-ink)"/>'


def label(x, y, text):
    return f'<text x="{x}" y="{y}" font-size="11.5" class="t-mono t-muted">{text}</text>'


# Standard WPA2/WPA3 hierarchy
p = []
srcs = [("WPA2-Personal", ["PBKDF2(passphrase, SSID, 4096)", "same for every client"]),
        ("WPA3-Personal", ["output of the SAE exchange", "unique per session"]),
        ("Enterprise (802.1X)", ["first 256 bits of the EAP MSK", "unique per user and session"])]
for i, (t, ls) in enumerate(srcs):
    x = 10 + i * 240
    p.append(box(x, 0, 220, 72, t, ls))
    p.append(arrow(x + 110, 72, 350 + (i - 1) * 60, 110))
p.append(box(150, 112, 400, 50, "PMK · 256 bits", ["never transmitted over the air"], "kb-acc"))
p.append(arrow(350, 162, 350, 206))
p.append(label(362, 188, "PRF(PMK, ANonce, SNonce, AP MAC, client MAC)"))
p.append(box(150, 208, 400, 50, "PTK · Pairwise Transient Key", ["fresh every session · 384 bits with CCMP"], "kb-acc"))
ptk = [("KCK", ["Key Confirmation Key", "computes the EAPOL-Key MIC"]),
       ("KEK", ["Key Encryption Key", "encrypts the GTK in M3"]),
       ("TK", ["Temporal Key", "encrypts unicast data"])]
for i, (t, ls) in enumerate(ptk):
    x = 10 + i * 240
    p.append(arrow(350 + (i - 1) * 60, 258, x + 110, 294))
    p.append(box(x, 296, 220, 72, t, ls))
p.append(box(10, 388, 700, 56, "GTK · Group Temporal Key",
             ["created by the AP from its GMK · shared by all clients for broadcast/multicast · delivered in M3"], "kb-gtk"))
(OUT / "key-hierarchy.svg").write_text(wrap("\n".join(p), 720, 444,
    "WPA2/WPA3 key hierarchy: PSK, SAE or EAP produce the PMK, which with both nonces and MAC addresses produces the PTK, split into KCK, KEK and TK; the AP's GTK protects broadcast traffic."))

# 802.11r FT hierarchy
p = []
srcs = [("FT-802.1X", ["XXKey = second 256 bits", "of the EAP MSK"]),
        ("FT-PSK", ["XXKey = the PSK", "(from the passphrase)"]),
        ("FT-SAE", ["XXKey = the PMK from", "the SAE exchange"])]
for i, (t, ls) in enumerate(srcs):
    x = 10 + i * 240
    p.append(box(x, 0, 220, 72, t, ls))
    p.append(f'<line x1="{x+110}" y1="72" x2="350" y2="94" class="kline"/>')
p.append(arrow(350, 94, 350, 138))
p.append(label(362, 122, "KDF(XXKey, SSID, MDID, R0KH-ID, client MAC)"))
p.append(box(120, 140, 460, 50, "PMK-R0", ["held by the controller (R0KH) · one per client per mobility domain"], "kb-acc"))
p.append(arrow(350, 190, 350, 234))
p.append(label(362, 216, "KDF(PMK-R0, R1KH-ID, client MAC)"))
p.append(box(120, 236, 460, 50, "PMK-R1", ["held by each AP (R1KH) · a different one per AP"], "kb-acc"))
p.append(arrow(350, 286, 350, 330))
p.append(label(362, 312, "KDF(PMK-R1, ANonce, SNonce, BSSID, client MAC)"))
p.append(box(120, 332, 460, 50, "PTK", ["same KCK / KEK / TK split · fresh every association"], "kb-acc"))
(OUT / "ft-key-hierarchy.svg").write_text(wrap("\n".join(p), 720, 382,
    "802.11r key hierarchy: XXKey from 802.1X, PSK or SAE produces PMK-R0 on the controller, which produces a PMK-R1 for each AP, which produces the PTK."))


# ---- MAC layer diagrams (section 3: frames and CSMA/CA), drawn here in Python ----
def rect(x, y, w, h, cls, rx=3):
    return f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{rx}" class="{cls}"/>'


def txt(x, y, s, size=11, cls="", anchor="middle", weight=None):
    w = f' font-weight="{weight}"' if weight else ""
    c = f' class="{cls}"' if cls else ""
    return f'<text x="{x:.1f}" y="{y}" text-anchor="{anchor}" font-size="{size}"{c}{w}>{s}</text>'


def two_line(cx, y_top, h, l1, l2, size=11, cls=""):
    if l2:
        return [txt(cx, y_top + h / 2 - 2, l1, size, cls), txt(cx, y_top + h / 2 + 12, l2, size, cls)]
    return [txt(cx, y_top + h / 2 + 4, l1, size, cls)]


def frame_format():
    out, x0, W = [], 50, 670
    fields = [("Frame", "Control", "2", 58, "fld-hi"), ("Duration", "/ ID", "2", 58, "fld"),
              ("Address", "1", "6", 62, "fld"), ("Address", "2", "6", 62, "fld"), ("Address", "3", "6", 62, "fld"),
              ("Sequence", "Control", "2", 62, "fld"), ("Address", "4", "6", 62, "fld-opt"),
              ("QoS", "Control", "2", 58, "fld-opt"), ("HT", "Control", "4", 58, "fld-opt"),
              ("Frame body", "", "0–n", 110, "fld"), ("FCS", "", "4", 46, "fld")]
    k = W / sum(f[3] for f in fields)
    x, edges = x0, []
    for l1, l2, size, w, cls in fields:
        w *= k
        out.append(rect(x + 1, 30, w - 2, 44, cls))
        out += two_line(x + w / 2, 30, 44, l1, l2, 11)
        out.append(txt(x + w / 2, 90, size, 11, "t-mono t-muted"))
        edges.append((x, x + w))
        x += w
    out.append(txt(0, 90, "bytes", 11, "t-muted", "start"))
    # brackets: header / body / FCS
    for (a, b), label in [((edges[0][0], edges[8][1]), "MAC header · 24 bytes, up to 36 with optional fields"),
                          ((edges[9][0], edges[9][1]), "payload"), ((edges[10][0], edges[10][1]), "CRC-32")]:
        out.append(f'<path d="M{a+3:.1f} 25 V19 H{b-3:.1f} V25" class="grid"/>')
        out.append(txt((a + b) / 2, 13, label, 11, "t-muted"))
    out.append(rect(x0, 104, 18, 12, "fld-opt", 2))
    out.append(txt(x0 + 24, 114, "only in some frames (4-address WDS/mesh, QoS data, HT and later)", 11, "t-muted", "start"))
    # zoom from Frame Control to its bits
    fc_a, fc_b = edges[0]
    out.append(f'<path d="M{fc_a+1:.1f} 74 L{x0} 146 M{fc_b-1:.1f} 74 L{x0+W} 146" class="grid" stroke-dasharray="3 3"/>')
    bits = [("Protocol", "version", 2, "fld"), ("Type", "", 2, "fld-hi"), ("Subtype", "", 4, "fld-hi"),
            ("To", "DS", 1, "fld-hi"), ("From", "DS", 1, "fld-hi"), ("More", "Frag", 1, "fld"),
            ("Retry", "", 1, "fld-hi"), ("Pwr", "Mgmt", 1, "fld"), ("More", "Data", 1, "fld"),
            ("Prot.", "Frame", 1, "fld-hi"), ("+HTC", "/Order", 1, "fld")]
    bw, x = W / 16, x0
    for l1, l2, n, cls in bits:
        w = bw * n
        out.append(rect(x + 1, 150, w - 2, 40, cls))
        out += two_line(x + w / 2, 150, 40, l1, l2, 10.5)
        out.append(txt(x + w / 2, 206, str(n), 11, "t-mono t-muted"))
        x += w
    out.append(txt(0, 206, "bits", 11, "t-muted", "start"))
    out.append(txt(0, 174, "Frame", 11, "t-muted", "start"))
    out.append(txt(0, 188, "Control", 11, "t-muted", "start"))
    return "\n".join(out), 720, 212


def csma_ca():
    out = []
    rows = {"Medium": 40, "Station A": 100, "Station B": 160}
    H = 30
    for xg in (210, 276, 446, 486, 530):
        out.append(f'<line x1="{xg}" y1="34" x2="{xg}" y2="212" class="grid" stroke-dasharray="2 3"/>')
    for name, y in rows.items():
        out.append(txt(0, y + 20, name, 12, "", "start", 600))
        out.append(f'<line x1="100" y1="{y+H}" x2="710" y2="{y+H}" class="row-line"/>')
    m = rows["Medium"]
    out += [rect(100, m, 70, H, "busy"), txt(135, m + 19, "busy", 11),
            rect(170, m, 40, H, "ifs"), txt(190, m + 19, "DIFS", 10, "t-mono"),
            txt(243, m + 19, "backoff", 10.5, "t-muted"),
            rect(276, m, 110, H, "tx-a"), txt(331, m + 19, "A · DATA", 11.5, "on-fill", weight=600),
            rect(386, m, 20, H, "ifs"), txt(396, m - 5, "SIFS", 9.5, "t-mono t-muted"),
            rect(406, m, 40, H, "ackbox"), txt(426, m + 19, "ACK", 11, "t-mono", weight=600),
            rect(446, m, 40, H, "ifs"), txt(466, m + 19, "DIFS", 10, "t-mono"),
            txt(508, m + 19, "backoff", 10.5, "t-muted"),
            rect(530, m, 110, H, "tx-b"), txt(585, m + 19, "B · DATA", 11.5, "on-fill", weight=600),
            rect(640, m, 20, H, "ifs"), txt(650, m - 5, "SIFS", 9.5, "t-mono t-muted"),
            rect(660, m, 40, H, "ackbox"), txt(680, m + 19, "ACK", 11, "t-mono", weight=600)]
    a = rows["Station A"]
    out.append(txt(204, a + 19, "draws 3", 11, "t-muted", "end"))
    for i, n in enumerate((3, 2, 1)):
        out += [rect(210 + 22 * i + 1, a + 4, 20, H - 8, "slot", 2), txt(221 + 22 * i, a + 19, str(n), 11, "t-mono")]
    out += [rect(276, a, 110, H, "tx-a"), txt(331, a + 19, "transmits", 11, "on-fill", weight=600),
            txt(410, a + 19, "✓ ACK received", 11, "t-muted", "start")]
    b = rows["Station B"]
    out.append(txt(204, b + 19, "draws 5", 11, "t-muted", "end"))
    for i, n in enumerate((5, 4, 3)):
        out += [rect(210 + 22 * i + 1, b + 4, 20, H - 8, "slot", 2), txt(221 + 22 * i, b + 19, str(n), 11, "t-mono")]
    out += [rect(276, b, 210, H, "frozen"), txt(381, b + 19, "frozen · 2 slots left", 11, "t-muted")]
    for i, n in enumerate((2, 1)):
        out += [rect(486 + 22 * i + 1, b + 4, 20, H - 8, "slot", 2), txt(497 + 22 * i, b + 19, str(n), 11, "t-mono")]
    out += [rect(530, b, 110, H, "tx-b"), txt(585, b + 19, "transmits", 11, "on-fill", weight=600),
            rect(280, b + 36, 166, 10, "nav", 2), txt(452, b + 45, "NAV set from A’s Duration field", 10.5, "t-nav", "start"),
            f'<line x1="100" y1="228" x2="706" y2="228" class="msg" marker-end="url(#arr-ink)"/>',
            txt(100, 244, "time (not to scale)", 11, "t-muted", "start")]
    return "\n".join(out), 720, 250


def hidden_node():
    import math
    out = ['<ellipse cx="190" cy="120" rx="190" ry="90" class="range-a"/>',
           '<ellipse cx="530" cy="120" rx="190" ry="90" class="range-b"/>',
           txt(190, 22, "A’s range", 12, "t-acc", weight=600), txt(530, 22, "B’s range", 12, "t5", weight=600),
           '<circle cx="190" cy="120" r="16" class="dev"/>', rect(344, 106, 32, 28, "dev", 5),
           '<circle cx="530" cy="120" r="16" class="dev"/>',
           txt(190, 156, "Client A", 12.5, "", weight=600), txt(360, 156, "AP", 12.5, "", weight=600),
           txt(530, 156, "Client B", 12.5, "", weight=600),
           '<line x1="208" y1="120" x2="338" y2="120" class="msg" marker-end="url(#arr-ink)"/>',
           txt(273, 112, "DATA", 11.5, "t-mono", weight=600),
           '<line x1="512" y1="120" x2="382" y2="120" class="msg" marker-end="url(#arr-ink)"/>',
           txt(447, 112, "DATA", 11.5, "t-mono", weight=600)]
    pts = []
    for i in range(16):
        r = 14 if i % 2 == 0 else 6
        ang = math.pi * i / 8
        pts.append(f"{360 + r * math.cos(ang):.1f},{86 + r * math.sin(ang):.1f}")
    out += [f'<polygon points="{" ".join(pts)}" class="warn-f"/>',
            txt(380, 90, "collision at the AP", 12.5, "t-warn", "start", 600),
            '<line x1="190" y1="190" x2="530" y2="190" class="warn-s"/>',
            txt(360, 195, "✕", 14, "t-warn", weight=700),
            txt(360, 236, "A and B can’t hear each other, so carrier sense can’t stop them transmitting together", 12, "t-muted")]
    return "\n".join(out), 720, 246


def rts_cts():
    out = []
    rows = {"Client A": 30, "AP": 80, "Station near A": 140, "Client B (hidden)": 190}
    H = 28
    for xg in (190, 255, 625):
        out.append(f'<line x1="{xg}" y1="24" x2="{xg}" y2="222" class="grid" stroke-dasharray="2 3"/>')
    for name, y in rows.items():
        out.append(txt(0, y + 18, name, 12, "", "start", 600))
        out.append(f'<line x1="130" y1="{y+H}" x2="710" y2="{y+H}" class="row-line"/>')
    a, ap, n, b = rows.values()
    out += [rect(140, a, 50, H, "tx-a"), txt(165, a + 18, "RTS", 11.5, "on-fill t-mono", weight=600),
            rect(275, a, 285, H, "tx-a"), txt(417, a + 18, "DATA", 11.5, "on-fill t-mono", weight=600),
            rect(210, ap, 45, H, "ackbox"), txt(232, ap + 18, "CTS", 11.5, "t-mono", weight=600),
            rect(580, ap, 45, H, "ackbox"), txt(602, ap + 18, "ACK", 11.5, "t-mono", weight=600)]
    for cx in (200, 265, 570):
        out.append(txt(cx, 72, "SIFS", 9.5, "t-mono t-muted"))
    out += [rect(190, n + 4, 435, H - 8, "nav", 3), txt(407, n + 18, "NAV set from the RTS Duration field · stays quiet", 11, "t-nav"),
            txt(248, b + 18, "can’t hear the RTS", 11, "t-muted", "end"),
            rect(255, b + 4, 370, H - 8, "nav", 3), txt(440, b + 18, "NAV set from the AP’s CTS · stays quiet", 11, "t-nav"),
            f'<line x1="130" y1="236" x2="706" y2="236" class="msg" marker-end="url(#arr-ink)"/>',
            txt(130, 252, "time (not to scale)", 11, "t-muted", "start")]
    return "\n".join(out), 720, 256


for name, fn, label in [
    ("frame-format", frame_format, "802.11 MAC frame format: Frame Control, Duration/ID, Addresses 1 to 3, Sequence Control, optional Address 4, QoS Control and HT Control, frame body and FCS, with the Frame Control field expanded into its bit fields."),
    ("csma-ca", csma_ca, "CSMA/CA timeline: after the medium goes idle both stations wait DIFS and count down random backoff slots. Station A reaches zero first and transmits; the AP ACKs after SIFS. Station B freezes its backoff with 2 slots left, sets its NAV, and resumes after the next DIFS."),
    ("hidden-node", hidden_node, "Hidden node problem: clients A and B are each in range of the AP but not of each other, so their transmissions collide at the AP."),
    ("rts-cts", rts_cts, "RTS/CTS timeline: client A sends RTS, the AP answers CTS, then DATA and ACK follow, each after SIFS. Stations near A set their NAV from the RTS; hidden client B sets its NAV from the CTS."),
]:
    inner, w, h = fn()
    (OUT / f"{name}.svg").write_text(wrap(inner, w, h, label))

print("\n".join(sorted(f.name for f in OUT.iterdir())))

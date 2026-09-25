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
             B6="#6947BF", OKSOFT="#DFF0E6")
DARK = dict(SURFACE="#141C23", SURFACE2="#1C2630", INK="#E2E8ED", MUTED="#98A5AF", LINE="#29353F",
            ACCENT="#8DB4EE", ACCENTSOFT="#1A2A3E", B24="#EDA24E", B5="#4CC1CD", B5SOFT="#0E2A2E",
            B6="#AE95F3", OKSOFT="#13281C")
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
         "scattering", "absorption", "four-way-handshake", "sae-exchange", "ft-over-the-air"]
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

print("\n".join(sorted(f.name for f in OUT.iterdir())))

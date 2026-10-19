#!/usr/bin/env python3
"""Render a 9:16 Reel (1080x1920 MP4) from photos and video clips, with text and an end card.

    /usr/bin/python3 scripts/reel.py reels/01-countdown-40.json

Spec (JSON):
{
  "out": "assets/reels/01-countdown-40.mp4",
  "segments": [
    {"image": "assets/story/LM_06229.jpg", "dur": 2.6},
    {"video": "clips/IMG_4669.mov", "start": 3.0, "dur": 3.0},
    {"endcard": true, "dur": 2.6, "line1": "Hokkaido, this winter", "line2": "wildr.shop"}
  ],
  "texts": [
    {"t0": 0.2, "t1": 2.5, "text": "40 DAYS", "style": "Huge"},
    {"t0": 0.6, "t1": 2.5, "text": "until the lifts open in Hokkaido", "style": "Sub"}
  ]
}
Text times are on the final timeline. Photos get a slow zoom, segments crossfade (XF seconds).
No music: add a trending sound in Instagram when publishing.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
FFMPEG = str(pathlib.Path.home() / ".local/bin/ffmpeg")
W, H, FPS, XF = 1080, 1920, 30, 0.4
NAVY = (15, 23, 42)
LOGO = ROOT / "assets/brand/wildr-logo.png"
FUTURA = "/System/Library/Fonts/Supplemental/Futura.ttc"

ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Huge,DIN Condensed,320,&H00FFFFFF,&H00FFFFFF,&H50000000,&H64000000,-1,0,0,0,100,100,2,0,1,4,6,5,60,60,0,1
Style: Big,DIN Condensed,160,&H00FFFFFF,&H00FFFFFF,&H50000000,&H64000000,-1,0,0,0,100,100,1,0,1,4,5,5,80,80,0,1
Style: Sub,Futura,70,&H00FFFFFF,&H00FFFFFF,&H6E0F172A,&H00000000,-1,0,0,0,100,100,0,0,3,20,0,5,90,90,0,1
Style: Low,Futura,74,&H00FFFFFF,&H00FFFFFF,&H6E0F172A,&H00000000,-1,0,0,0,100,100,0,0,3,20,0,2,90,90,300,1
Style: Hook,Futura,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,3,4,8,80,80,330,1
Style: Serif,Georgia,76,&H00FFFFFF,&H00FFFFFF,&H70000000,&H50000000,0,0,0,0,100,100,0,0,1,1.6,3,5,110,110,0,1
Style: Top,DIN Condensed,130,&H00FFFFFF,&H00FFFFFF,&H50000000,&H64000000,-1,0,0,0,100,100,1,0,1,4,5,8,80,80,240,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ts(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def run(args):
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def endcard(seg, path):
    """Navy card with a white Wildr logo and two lines of text."""
    im = Image.new("RGB", (W, H), NAVY)
    logo = Image.open(LOGO).convert("RGBA")
    white = Image.new("RGBA", logo.size, (255, 255, 255, 255))
    white.putalpha(logo.getchannel("A"))
    white = white.resize((540, int(540 * logo.height / logo.width)))
    im.paste(white, ((W - white.width) // 2, 560), white)
    d = ImageDraw.Draw(im)
    for text, size, y in ((seg.get("line1", ""), 64, 1140), (seg.get("line2", "wildr.shop"), 54, 1240)):
        f = ImageFont.truetype(FUTURA, size)
        w = d.textlength(text, font=f)
        d.text(((W - w) / 2, y), text, font=f, fill=(220, 231, 242))
    im.save(path, quality=95)


def segment(seg, path, tmp):
    frames = int(round(seg["dur"] * FPS))
    if seg.get("endcard"):
        card = tmp / f"{path.stem}.jpg"
        endcard(seg, card)
        src, vf = ["-loop", "1", "-t", str(seg["dur"]), "-i", str(card)], f"fps={FPS},format=yuv420p"
    elif "image" in seg:
        z = seg.get("zoom", 0.0007)
        # upscale 2x before zoompan so the slow zoom does not shimmer
        vf = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
              f"zoompan=z='min(zoom+{z},1.12)':d={frames}:s={W}x{H}:fps={FPS}"
              ":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',format=yuv420p")
        src = ["-loop", "1", "-t", str(seg["dur"]), "-i", str(ROOT / seg["image"])]
    else:
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
              f"setpts=PTS/{seg.get('speed', 1.0)},format=yuv420p")
        if seg.get("grade"):  # e.g. "eq=saturation=0.25:contrast=1.05" for the muted Still going look
            vf = vf.replace(",format=yuv420p", "," + seg["grade"] + ",format=yuv420p")
        src = ["-ss", str(seg.get("start", 0)), "-t", str(seg["dur"] * seg.get("speed", 1.0)),
               "-i", str(ROOT / seg["video"])]
    run([*src, "-vf", vf, "-frames:v", str(frames), "-an", "-c:v", "libx264", "-preset", "medium",
         "-crf", "18", str(path)])


def main():
    global XF
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
    XF = spec.get("xf", XF)  # 0.04 = near hard cut (viral formats)
    out = ROOT / spec["out"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        parts = []
        for i, seg in enumerate(spec["segments"]):
            p = tmp / f"s{i:02d}.mp4"
            segment(seg, p, tmp)
            parts.append((p, seg["dur"]))
        # crossfade chain; each fade overlaps XF seconds, so the timeline shrinks by XF per cut
        inputs, chain, offset, last = [], [], 0.0, "0:v"
        for i, (p, dur) in enumerate(parts):
            inputs += ["-i", str(p)]
            if i == 0:
                offset = dur - XF
                continue
            label = f"x{i}"
            chain.append(f"[{last}][{i}:v]xfade=transition=fade:duration={XF}:offset={offset:.3f}[{label}]")
            last, offset = label, offset + dur - XF
        total = offset + XF
        ass = tmp / "t.ass"
        lines = []
        for t in spec.get("texts", []):
            tags = "\\fad(300,300)" + ("\\pos(%d,%d)" % tuple(t["pos"]) if "pos" in t else "")
            text = t["text"].replace("\n", "\\N")
            lines.append(f"Dialogue: 0,{ts(t['t0'])},{ts(t['t1'])},{t.get('style', 'Sub')},,0,0,0,,{{{tags}}}{text}\n")
        ass.write_text(ASS_HEAD + "".join(lines))
        chain.append(f"[{last}]ass='{ass}'[v]" if chain else f"[0:v]ass='{ass}'[v]")
        run([*inputs, "-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=44100:cl=stereo",
             "-filter_complex", ";".join(chain), "-map", "[v]", "-map", f"{len(parts)}:a",
             "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(out)])
    print(f"{out.relative_to(ROOT)}  {total:.1f}s")


if __name__ == "__main__":
    main()

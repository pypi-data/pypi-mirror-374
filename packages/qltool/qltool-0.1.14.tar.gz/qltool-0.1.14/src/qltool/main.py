#!/usr/bin/env python3
"""
#---------text
 rm /tmp/tmp_qrcode.png ; uv run src/qltool/main.py "Ahoj
aaa
456 8jgqy 789 456 456 " --font-size 55 --font-size 45

# ---- create QR

uv run src/qltool/main.py "ahoj
momo
123 456 789 jjj" -p -q

# -------- use any image/qrcode
uv run src/qltool/main.py "Užaj jetů" --qr /tmp/baba.png

uv run src/qltool/main.py "Už je tuná" --qr /tmp/baba.png -p

"""
import shlex
import subprocess as sp
import glob
import tempfile
import sys

import click
from importlib_resources import files, as_file
from PIL import Image, ImageDraw, ImageFont
# uv add Pillow
import cv2
# uv add opencv-python
import numpy as np
from console import fg, bg

import os
import re

import qrcode

# =====================================================================
#
# ----------------------------------------------------------------------
def is_user_in_lp_group():
    """
    Return True if 'lp' appears in the output of the `groups` command.
    Uses runme() to call `groups`.
    """
    try:
        out = runme("groups", reallyrun=True)
    except Exception:
        return False
    tokens = re.findall(r"\w+", out)
    return "lp" in tokens

# --- helpers (kept similar to your original) ---
# =====================================================================
#
# ----------------------------------------------------------------------
def get_data_path():
    #src = files("data").joinpath("ql570")
    src = files("qltool").joinpath("data", "ql570")
    with as_file(src) as p:
        return str(p)

# =====================================================================
#
# ----------------------------------------------------------------------
def check_lpx():
    prs = glob.glob("/dev/usb/lp*")
    if not prs:
        raise RuntimeError("No LP device found under /dev/usb/lp*")
    return prs[0]

# =====================================================================
#
# ----------------------------------------------------------------------
def runme(CMDi, silent=False, reallyrun=False):
    print("D...", fg.orange, CMDi, fg.default)
    CMD = shlex.split(CMDi)
    if not reallyrun:
        return "ok"
    res = sp.check_output(CMD).decode("utf8")
    if not silent:
        print("i... RESULT:", fg.darkslategray, res, fg.default)
    return res

# =====================================================================
#
# ----------------------------------------------------------------------
def get_tmp_fname():
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", dir="/tmp", delete=False)
    name = temp_file.name
    temp_file.close()
    return name

# =====================================================================
#
# ----------------------------------------------------------------------
# --- image creation ---
def make_bw_text_image(lines, width=714,
#                       font_path="/usr/share/fonts/truetype/freefont/FreeMono.ttf",
                       font_path="/usr/share/fonts/truetype/clear-sans/ClearSans-Regular.ttf",
                       font_size=None,
                       pad=13):
    # lines: list of 1-3 strings
    if not (1 <= len(lines) <= 3):
        raise ValueError("Provide 1 to 3 lines.")
    # choose font
    FSIZ = font_size or 36
    try:
        if font_path:
            font = ImageFont.truetype(font_path, FSIZ)
        else:
            # try a reasonably sized PIL default or fallback
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    PAD = int( (FSIZ / 36) * pad) # for 36 pad 12 is OK
    # compute sizes
    # use a big temporary image to measure text
    tmp = Image.new("L", (width, 2000), 255)
    draw = ImageDraw.Draw(tmp)
    #line_heights = []
    #line_widths = []
    line_sizes = []
    for ln in lines:
        bbox = draw.textbbox((0, 0), ln, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        line_sizes.append((w, h))
        #w, h = draw.textsize(ln, font=font)
        #line_widths.append(w)
        #line_heights.append(h)
    # compute total height with small spacing
    spacing = int(0.2 * (line_sizes[0][1] if line_sizes else 12)) or 4
    total_h = sum(h for _, h in line_sizes) + spacing * (len(lines) - 1) + PAD * 2
    # create final image
    im = Image.new("L", (width, total_h), 255)  # white background
    draw = ImageDraw.Draw(im)
    # center horizontally, stack lines vertically
    y = PAD
    for (w, h), ln in zip(line_sizes, lines):
        x = max((width - w) // 2, 0)
        draw.text((x, y), ln, font=font, fill=0)
        y += h + spacing
    return im.convert("RGB")

# =====================================================================
#
# ----------------------------------------------------------------------
def pil_to_cv2(im):
    arr = np.array(im)[:, :, ::-1]  # RGB->BGR
    return arr


# =====================================================================
#
# ----------------------------------------------------------------------
# --- mono conversion with Floyd-Steinberg and gray bias ---
def convert_to_mono_floyd(img_rgb, gray_percent=50):
    """
    img_rgb: PIL RGB image
    gray_percent: 0..100, default 50. 50 means no bias. Values>50 bias lighter, <50 bias darker.
    Returns a PIL Image in mode '1' (mono).
    """
    if not (0 <= gray_percent <= 100):
        raise ValueError("gray_percent must be 0..100")
    # convert to grayscale
    im_l = img_rgb.convert("L")
    # compute offset: 50 => 0, >50 => positive (lighter), <50 => negative (darker)
    offset = int(round((gray_percent - 50) * 255 / 100.0))
    if offset != 0:
        lut = [min(255, max(0, i + offset)) for i in range(256)]
        im_l = im_l.point(lut)
    # convert to 1-bit using Floyd-Steinberg
    mono = im_l.convert("1", dither=Image.FLOYDSTEINBERG)
    if mono.mode != "1":
        # fallback: force mode to '1'
        mono = mono.convert("1")
    return mono

# =====================================================================
#
# ----------------------------------------------------------------------
def rotate_mono_90(img, clockwise=True):
    """
    Rotate a mono (1-bit) image by 90 degrees.
    - img: PIL.Image or path to image file.
    - clockwise: True => rotate 90° clockwise, False => 90° counter-clockwise.
    Returns a PIL.Image in mode '1'.
    """
    if isinstance(img, str):
        img = Image.open(img)
    if img.mode != "1":
        img = img.convert("1")
    # Use transpose for exact 90° rotation without resampling
    return img.transpose(Image.ROTATE_270 if clockwise else Image.ROTATE_90)




# =====================================================================
#
# ----------------------------------------------------------------------
def create_qr(qr_path, lines, width=5):
    qrtag = ";".join(lines)#f"{lines}"
    qrtag = qrtag.replace(r"\n", ";")
    qrtag = qrtag.replace("     ", " ")
    qrtag = qrtag.replace("    ", " ")
    qrtag = qrtag.replace("   ", " ")
    qrtag = qrtag.replace("  ", " ")
    qrtag = qrtag.replace(" ;", ";")
    print(f"i... QRTAG /{fg.cyan}{qrtag}{fg.default}/")
    # I will join Name: asoidj ; owner: OKjd ; location: asd o; ID: 8998244;
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=width,
        border=3,
    )
    qr.add_data(qrtag)
    qr.make(fit=True)
    img = qr.make_image(fill_color="darkblue", back_color="white")
    img.save(qr_path)
    # ----------------------- QRDONE -------------
    # #qr = qrcode.make( qrtag, width=width)
    # qrs = qrtag.split(";")
    # # I have nlabel and slabel:  what about midlabel
    # nlabel, midlabel, slabel= None, None, None
    # for q in qrs:
    #     nam, *val= q.split(":")
    #     if len(val) == 0:continue
    #     # EXTRACT ID and NAME
    #     if nam.strip().find( "id") == 0:
    #         nlabel = val[0].strip()
    #     if nam.strip().find( "name") == 0:
    #         slabel = val[0].strip()
    #     if nam.strip().find( "owner") == 0:
    #         midlabel = val[0].strip()
    # print(f"i... LABELS SN: /{fg.green}{nlabel}{fg.default}/ x /{fg.yellow}{midlabel}{fg.default}/ x  /{fg.green}{slabel}{fg.default}/")



def make_bw_text_with_qr(lines,
                         qr_path,
                         width=714,
#                        font_path="/usr/share/fonts/truetype/freefont/FreeMono.ttf",
                         font_path="/usr/share/fonts/truetype/clear-sans/ClearSans-Regular.ttf",
                         font_size=None,
                         pad=13,
                         qr_max_width=350):
    """
    Compose an RGB image (width x dynamic height) with:
      - QR image placed at left (must be < qr_max_width),
      - text block (1-3 lines) placed on the right of the QR.
    Behavior of text layout follows your make_bw_text_image(), but horizontal
    placement is centered inside the area to the right of the QR. x_offset is
    computed as (qr_image_width + PAD) where PAD ~= scaled pad value.
    Returns a PIL.Image in RGB.
    """
    if not (1 <= len(lines) <= 3):
        raise ValueError("Provide 1 to 3 lines.")
    if not os.path.exists(qr_path):
        raise FileNotFoundError(qr_path)

    # load QR and check width
    qr = Image.open(qr_path).convert("RGB")
    if qr.width >= qr_max_width:
        #raise ValueError(f"QR image width {qr.width}px >= limit {qr_max_width}px")
        qr = qr.resize( (qr_max_width, qr_max_width) )

    # font choice
    FSIZ = font_size or 36
    try:
        font = ImageFont.truetype(font_path, FSIZ) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    PAD = int((FSIZ / 36) * pad)  # scaled pad

    # Measure text lines using a temp image (same as original)
    tmp = Image.new("L", (width, 2000), 255)
    draw_tmp = ImageDraw.Draw(tmp)
    line_sizes = []
    for ln in lines:
        bbox = draw_tmp.textbbox((0, 0), ln, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        line_sizes.append((w, h))

    spacing = int(0.2 * (line_sizes[0][1] if line_sizes else 12)) or 4
    text_content_h = sum(h for _, h in line_sizes) + spacing * (len(lines) - 1)
    text_total_h = text_content_h + PAD * 2
    qr_total_h = qr.height + PAD * 2

    # canvas height must fit both QR and text
    canvas_h = max(text_total_h, qr_total_h)
    canvas = Image.new("RGB", (width, canvas_h), "white")
    draw = ImageDraw.Draw(canvas)

    # place QR at left with left padding PAD, vertically centered
    qr_x = PAD
    qr_y = (canvas_h - qr.height) // 2
    canvas.paste(qr, (qr_x, qr_y))

    # compute x_offset = qr_image width + PAD (as requested)
    x_offset = qr.width + PAD

    # available width for text: leave right PAD margin
    available_for_text = width - x_offset - PAD
    if available_for_text < 0:
        available_for_text = 0

    # vertical start for text: center the text block vertically in canvas
    y = (canvas_h - text_content_h) // 2

    # draw each line centered inside the available area starting at x_offset
    for (w, h), ln in zip(line_sizes, lines):
        x = x_offset + max((available_for_text - w) // 2, 0)
        draw.text((x, y), ln, font=font, fill=0)
        y += h + spacing

    return canvas



# =====================================================================
#
# ----------------------------------------------------------------------

# --- CLI ---
@click.command()
@click.argument("lines", nargs=-1, required=True)
@click.option("-p", "--print", "do_print", is_flag=True, default=False, help="Send to printer (calls ql570).")
@click.option("-d", "--device", "device", default=None, help="Printer device (defaults to first /dev/usb/lp*).")
@click.option("-f", "--format", "fmt", default=62, help="Format code for ql570 (default 62 at the width of 714).")
@click.option("--width", default=714, show_default=True, help="Total image width.")
@click.option("--gray", "gray", default=50, show_default=True, help="Gray bias percent (0..100), default 50.")
@click.option("--font-size", "font_size", default=72, show_default=True, help="Font size for text.")
@click.option("--qr", "qr_path", default=None, show_default=True, help="QR image path.")
@click.option("-q", "qr_create", is_flag=True, default=False, show_default=True, help="do QR")
def cli(lines, do_print, device, fmt, width, gray, font_size, qr_path, qr_create):
    """
    Create a black-on-white PNG from 1-3 lines of text.
    By default displays the image with OpenCV. Use -p to print via ql570.
    """
    #print(lines, type(lines), len(lines))
    if type(lines)is not tuple:
        print("X... the text should be python-tuple for some reason....")
        sys.exit(1)

    if len(lines) > 3: #   "A" "B" "C"
        print("Error: max 3 lines allowed.", file=sys.stderr)
        sys.exit(2)

    if len(lines) == 1:
        #print("Q", lines[0].find("\n"))
        if lines[0].find("\n") > 0:
            print("Q... contains several lines, I understand...")
            lines = lines[0].split("\n")
        else:
            print("Q... lines ...I do not understand")

    if len(lines) > 3: #   "A" "B" "C"
        print("Error: max 3 lines allowed.", file=sys.stderr)
        sys.exit(2)


    # ------- decide on qr
    use_qr_version = False
    my_qr_path = None
    if qr_path is not None: # Existing PATH
        if os.path.exists(qr_path):
            use_qr_version = True
            my_qr_path = qr_path
            #create_qr(qr_path, lines)

    if qr_create:
        my_qr_path = "/tmp/tmp_qrcode.png"
        create_qr(my_qr_path, lines)
        use_qr_version = True

    # -----------------------------------   create image
    lines = ["\n".join(lines) ] # BACK TO NICE \n

    im = None
    if use_qr_version:
        im = make_bw_text_with_qr(list(lines), my_qr_path, width=714, font_size=font_size)
    else:
        im = make_bw_text_image(list(lines), width=714, font_size=font_size)

    mono = convert_to_mono_floyd(im, gray_percent=int(gray))
    mono = rotate_mono_90(mono, clockwise=True)

    out = get_tmp_fname()
    print(f"D.... {out}")
    mono.save(out, format="PNG")
    if not do_print:
        # display with cv2
        cvim = pil_to_cv2(im)
        cv2.imshow("Preview - press any key to close", cvim)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print("i... Saved:", out)
        return
    # printing path
    exe = get_data_path()
    dev = device if device else check_lpx()
    CMD = f"{exe} {dev} {fmt} {out}"

    if not  is_user_in_lp_group():
        print("X... ", fg.red, "you are not in lp group", fg.default)
        sys.exit(1)
    runme(CMD, reallyrun=True)
    print("i... Printed (and saved):", out)

# =====================================================================
#
# ----------------------------------------------------------------------
# =====================================================================
#
# ----------------------------------------------------------------------
# =====================================================================
#
# ----------------------------------------------------------------------

if __name__ == "__main__":
    cli()

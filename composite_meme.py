"""Compose the two bounty memes from repository-local artwork with Pillow."""
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SIZE = (1200, 675)


def find_font():
    for name in (
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
    ):
        if Path(name).is_file():
            return name
    for line in subprocess.check_output(['fc-list', '--format=%{file}\n'], text=True).splitlines():
        if 'NotoSans-Bold.' in line:
            return line
    raise RuntimeError('A bold sans font is required')


FONT = find_font()


def fit(text, width, size):
    while True:
        font = ImageFont.truetype(FONT, size)
        if font.getlength(text) <= width or size <= 12:
            return font
        size -= 1


def caption(draw, text, xy, width, size=52):
    draw.text(xy, text, font=fit(text, width, size), fill='white',
              stroke_width=4, stroke_fill='black', anchor='mt')


def base(pattern):
    im = Image.open(next(ROOT.glob(pattern))).convert('RGB')
    w, h = im.size
    crop_h = w * 9 // 16
    top = (h - crop_h) // 2
    im = im.crop((0, top, w, top + crop_h)).resize(SIZE, Image.Resampling.LANCZOS).convert('RGBA')
    band = Image.new('RGBA', SIZE)
    d = ImageDraw.Draw(band)
    for y in range(150):
        alpha = round(175 * (1 - y / 150) ** 1.3)
        d.line((0, y, 1200, y), fill=(0, 0, 0, alpha))
        d.line((0, 674-y, 1200, 674-y), fill=(0, 0, 0, alpha))
    return Image.alpha_composite(im, band), w, top


def badge(im, x, y, width, label=False):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x-12, y-12, x+width+12, y+width+(39 if label else 12)),
                        radius=24, fill=(8, 8, 20, 225))
    mark = Image.open(ROOT / 'mark-1024.png').convert('RGBA').resize((width, width), Image.Resampling.LANCZOS)
    im.alpha_composite(mark, (x, y))
    if label:
        d.text((x+width/2, y+width+3), 'make.fun', font=fit('make.fun', width, 30),
               fill='white', stroke_width=2, stroke_fill='black', anchor='mt')


main, _, _ = base('media-generation-gta6-meme-base-main-*.webp')
d = ImageDraw.Draw(main)
caption(d, 'JASON & LUCIA ROB BANKS IN VICE CITY.', (600, 23), 1140)
caption(d, 'I ROB BOUNTIES ON', (490, 540), 930, 52)
caption(d, 'MAKE.FUN. LEGALLY.', (490, 598), 930, 52)
badge(main, 1000, 442, 170, label=True)
main.convert('RGB').save(ROOT / 'meme-main.png')

alt, original_w, crop_top = base('media-generation-gta6-meme-base-alt-*.webp')
d = ImageDraw.Draw(alt)
scale = 1200 / original_w
x0, x1 = round(320*scale), round(860*scale)
y0, y1 = round((300-crop_top)*scale), round((500-crop_top)*scale)
d.rounded_rectangle((x0, y0, x1, y1), radius=12, fill=(0, 26, 33, 235))
label = 'GTA VI — Downloading... 98%'
d.text(((x0+x1)/2, y0+18), label, font=fit(label, x1-x0-18, 22),
       anchor='mt', fill='white', stroke_width=2, stroke_fill='black')
bar = (x0+15, y0+65, x1-15, y0+97)
d.rounded_rectangle(bar, radius=6, fill=(12, 16, 25), outline='white', width=3)
left, right = bar[0]+5, bar[2]-5
end = left + round((right-left)*0.98)
for x in range(left, end):
    t = (x-left)/max(1, end-left-1)
    d.line((x, bar[1]+5, x, bar[3]-5), fill=(round(255*(1-t)), round(220*t), 235))
caption(d, 'DOWNLOAD: 98%... 3 HOURS LEFT.', (500, 25), 950, 50)
caption(d, 'GOOD THING MAKE.FUN', (600, 542), 1140, 52)
caption(d, 'ALREADY PAID ME.', (600, 600), 1140, 52)
badge(alt, 1025, 20, 150)
alt.convert('RGB').save(ROOT / 'meme-alt.png')

for name in ('meme-main.png', 'meme-alt.png'):
    path = ROOT / name
    with Image.open(path) as im:
        assert im.size == SIZE
        assert path.stat().st_size > 100_000
        print(f'{name}: {im.width}x{im.height}, {path.stat().st_size} bytes')

"""Author only: generate the production CRT surface, without text or baked quips.

Uses Pillow; production needs only PySide6. No external font or image assets.
"""
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def generate(destination):
    rng = random.Random(20261102)
    surface = Image.new('RGB', (480, 306))
    pixels = surface.load()
    for y in range(306):
        for x in range(480):
            distance = ((x-239.5)/335)**2 + ((y-152.5)/260)**2
            grain = rng.choice((-1, 0, 0, 0, 1))
            raster = -5 if y % 4 in (0, 1) else 0
            value = max(0, 1-distance)
            pixels[x, y] = (max(0, round(7+2*value+grain+raster)),
                            max(0, round(11+3*value+grain+raster)),
                            max(0, round(15+4*value+grain+raster)))
    frames = []
    for index in range(60):
        image = surface.copy()
        draw = ImageDraw.Draw(image)
        scan_y = -20 + index * 346/59
        # Broader soft band, retaining the accepted amplitude, path and cadence.
        for y in range(max(3, int(scan_y)-42), min(303, int(scan_y)+43)):
            strength = math.exp(-((y-scan_y)/18)**2)
            for x in range(4, 476):
                old = surface.getpixel((x, y))
                image.putpixel((x, y), tuple(min(255, v+round(c*strength)) for v, c in zip(old, (2, 4, 6))))
        draw.rounded_rectangle((3, 3, 476, 302), radius=4, outline=(58, 93, 117), width=1)
        draw.rounded_rectangle((4, 4, 475, 301), radius=3, outline=(21, 39, 50), width=1)
        # Sparse perimeter imperfections, matching the small points in the references.
        for x, y in ((112, 3), (361, 3), (3, 68), (476, 216), (124, 302), (350, 302)):
            draw.line((x, y, x+2 if y in (3, 302) else x, y if y in (3, 302) else y+2), fill=(87, 143, 176))
        draw.line((114, 3, 117, 3), fill=(5, 9, 12))
        draw.line((348, 302, 350, 302), fill=(5, 9, 12))
        frames.append(image)
    # One shared palette for stable low-light texture throughout the loop.
    palette_source = Image.new('RGB', (480, 306*3))
    for row, frame in enumerate((frames[0], frames[22], frames[44])):
        palette_source.paste(frame, (0, 306*row))
    palette = palette_source.quantize(colors=128, dither=Image.Dither.NONE)
    frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    frames[0].save(destination, save_all=True, append_images=frames[1:], duration=50,
                   loop=0, disposal=2, optimize=False)
    with Image.open(destination) as movie:
        print('size:', movie.size, 'encoded frames:', movie.n_frames, 'loop:', movie.info.get('loop'))
        duration = 0
        for n in range(movie.n_frames):
            movie.seek(n)
            duration += movie.info['duration']
        print('loop duration ms:', duration)


if __name__ == '__main__':
    generate(ROOT/'assets/shutdown_system_optional.gif')

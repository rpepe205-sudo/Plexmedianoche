"""Vista previa aproximada de una ventana del skin (no es Kodi).

Dibuja imágenes, textos, botones, listas y barras a partir del XML preparado,
con datos de ejemplo, para revisar la composición sin un televisor.
Uso: python3 scripts/preview_kodi.py <skin preparado> <archivo.xml> <salida.png> <foco> [k=v ...]
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080


class Scene:
    def __init__(self, base, focus, props, items, fake):
        self.base, self.focus, self.props, self.items, self.fake = base, str(focus), props, items, fake
        self.fonts = {}
        for font in ET.parse(base / '1080i/Font.xml').getroot().find('fontset').findall('font'):
            self.fonts[font.findtext('name')] = (font.findtext('filename'), int(font.findtext('size')))
        self.variables = {}
        inc = ET.parse(base / '1080i/Includes_MediaNoche.xml').getroot()
        for var in inc.findall('variable'):
            self.variables[var.get('name')] = var.findall('value')
        self.cache = {}
        self.item = None

    # ------------------------------------------------------------ infolabels
    def info(self, name):
        item = self.item
        m = re.match(r'Container\((\d+)\)\.(ListItem\..*)', name)
        if m:
            saved, self.item = self.item, (self.items.get(m.group(1)) or [{}])[0]
            value = self.info(m.group(2))
            self.item = saved
            return value
        if name.startswith('ListItem.'):
            key = name[9:]
            if item is not None:
                return str(item.get(key, ''))
            return ''
        m = re.match(r'Window(?:\(home\))?\.Property\(([^)]+)\)', name)
        if m:
            return self.props.get(m.group(1), '')
        if name.startswith('System.Time'):
            return '22:47'
        if name.startswith('System.Date'):
            return 'dom 22 nov'
        m = re.match(r'Container\((\d+)\)\.NumItems', name)
        if m:
            return str(len(self.items.get(m.group(1), [])))
        return self.fake.get(name, '')

    def text(self, raw):
        if raw is None:
            return ''

        def var(match):
            for value in self.variables.get(match.group(1), []):
                if self.cond(value.get('condition')):
                    return self.text(value.text or '')
            return ''

        raw = re.sub(r'\$VAR\[([\w.]+)\]', var, raw)

        def info(match):
            parts = match.group(2).split(',')
            name = parts[0].strip()
            name = re.sub(r'\((h:mm|mins|mm|ddd d mmm)\)$', '', name)
            value = self.info(name)
            if not value:
                return ''
            pre = parts[1] if len(parts) > 1 else ''
            post = parts[2] if len(parts) > 2 else ''
            return pre + value + post

        raw = re.sub(r'\$(ESC)?INFO\[([^\]]*(?:\[[^\]]*\][^\]]*)*)\]', info, raw)
        return raw

    def cond(self, expr):
        if not expr:
            return True
        expr = expr.strip()
        tokens = re.findall(r'\[|\]|!|\+|\||[A-Za-z][\w.]*(?:\((?:[^()]|\([^()]*\))*\))?', expr)
        out = []
        for t in tokens:
            if t == '[':
                out.append('(')
            elif t == ']':
                out.append(')')
            elif t == '!':
                out.append(' not ')
            elif t == '+':
                out.append(' and ')
            elif t == '|':
                out.append(' or ')
            else:
                out.append(str(self.atom(t)))
        try:
            return bool(eval(''.join(out)))
        except Exception:
            return False

    def atom(self, t):
        m = re.match(r'Control\.HasFocus\((\d+)\)', t)
        if m:
            return m.group(1) == self.focus
        m = re.match(r'String\.IsEqual\(([^,]+(?:\([^)]*\))?),(.*)\)$', t)
        if m:
            right = m.group(2)
            right_value = self.info(right) if re.match(r'(ListItem|Window|Container|System)\b', right) else right
            return self.info(m.group(1)) == right_value
        m = re.match(r'String\.IsEmpty\((.*)\)$', t)
        if m:
            return self.info(m.group(1)) == ''
        m = re.match(r'Integer\.IsGreater\((.*),(\d+)\)$', t)
        if m:
            try:
                return int(self.info(m.group(1)) or 0) > int(m.group(2))
            except ValueError:
                return False
        m = re.match(r'Integer\.IsEqual\((.*),(\d+)\)$', t)
        if m:
            try:
                return int(self.info(m.group(1)) or 0) == int(m.group(2))
            except ValueError:
                return False
        if t in ('true',):
            return True
        if t.startswith('ListItem.IsWatched'):
            return bool(self.item and self.item.get('watched'))
        if t.startswith('ListItem.IsResumable'):
            return bool(self.item and self.item.get('resume'))
        return False

    # --------------------------------------------------------------- dibujo
    def font(self, name):
        filename, size = self.fonts.get(name, ('MN-Inter-Regular.ttf', 22))
        key = (filename, size)
        if key not in self.cache:
            path = self.base / 'fonts' / filename
            try:
                self.cache[key] = ImageFont.truetype(str(path), size)
            except OSError:
                self.cache[key] = ImageFont.truetype(str(self.base / 'fonts/MN-Inter-Regular.ttf'), size)
        return self.cache[key]

    def texture(self, path, w, h, border=None):
        if not path:
            return None
        if path.startswith('fake:'):
            seed = sum(map(ord, path))
            im = Image.new('RGBA', (w, h))
            hue = [(181, 69, 47), (47, 111, 160), (106, 79, 181), (47, 156, 132), (201, 162, 74),
                   (194, 48, 122), (94, 143, 58), (208, 138, 70)][seed % 8]
            d = ImageDraw.Draw(im)
            for y in range(h):
                t = y / max(1, h)
                d.line([(0, y), (w, y)], fill=tuple(int(c * (1 - t) + 10 * t) for c in hue) + (255,))
            d.ellipse((w * .45, h * .15, w * .85, h * .15 + w * .4), fill=(240, 200, 120, 200))
            return im
        if path == 'common/white.png':
            return Image.new('RGBA', (w, h), (255, 255, 255, 255))
        if path.startswith('special://skin/'):
            file = self.base / path[len('special://skin/'):]
        else:
            file = self.base / 'media' / path
        if not file.is_file():
            return None
        src = Image.open(file).convert('RGBA')
        if border:
            b = int(border)
            sw, sh = src.size
            b = min(b, sw // 2, sh // 2, w // 2, h // 2)
            out = Image.new('RGBA', (w, h))
            boxes = [(0, b), (b, sw - b), (sw - b, sw)]
            dest = [(0, b), (b, w - b), (w - b, w)]
            boxes_y = [(0, b), (b, sh - b), (sh - b, sh)]
            dest_y = [(0, b), (b, h - b), (h - b, h)]
            for (sx0, sx1), (dx0, dx1) in zip(boxes, dest):
                for (sy0, sy1), (dy0, dy1) in zip(boxes_y, dest_y):
                    if sx1 > sx0 and sy1 > sy0 and dx1 > dx0 and dy1 > dy0:
                        out.paste(src.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0)), (dx0, dy0))
            return out
        return src.resize((max(1, w), max(1, h)))

    def paste(self, canvas, im, x, y, color=None, diffuse=None):
        if im is None:
            return
        if diffuse:
            mask = self.texture(diffuse, *im.size)
            if mask:
                alpha = Image.composite(im.getchannel('A'), Image.new('L', im.size, 0), mask.getchannel('A'))
                im.putalpha(alpha)
        if color:
            a, r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), int(color[6:8], 16)
            tint = Image.new('RGBA', im.size, (r, g, b, 255))
            im = Image.composite(Image.blend(im, im, 0), im, im.getchannel('A'))
            px = Image.merge('RGBA', [Image.eval(im.getchannel(i), lambda v, k=k: v * k // 255)
                                      for i, k in zip(range(3), (r, g, b))] + [im.getchannel('A').point(lambda v: v * a // 255)])
            im = px
        canvas.alpha_composite(im, (int(x), int(y))) if 0 <= x and 0 <= y and x + im.width <= canvas.width and y + im.height <= canvas.height else canvas.paste(im, (int(x), int(y)), im)

    def draw_text(self, canvas, x, y, w, h, text, font, color, align='left', aligny='center', wrap=False):
        text = re.sub(r'\[/?(COLOR[^\]]*|B|I|UPPERCASE)\]', '', text).replace('[CR]', '\n')
        if not text:
            return
        f = self.font(font)
        d = ImageDraw.Draw(canvas)
        col = tuple(int(color[i:i + 2], 16) for i in (2, 4, 6)) + (int(color[0:2], 16),)
        lines = []
        for para in text.split('\n'):
            if wrap:
                words, line = para.split(' '), ''
                for word in words:
                    test = (line + ' ' + word).strip()
                    if d.textlength(test, font=f) <= w:
                        line = test
                    else:
                        lines.append(line)
                        line = word
                lines.append(line)
            else:
                while para and d.textlength(para, font=f) > w:
                    para = para[:-2]
                lines.append(para)
        size = f.size
        lh = int(size * 1.35)
        total = lh * len(lines)
        ty = y + (h - total) / 2 if aligny == 'center' else y
        layer = Image.new('RGBA', canvas.size)
        ld = ImageDraw.Draw(layer)
        for line in lines:
            if ty + lh > y + h + 4 and wrap:
                break
            tw = ld.textlength(line, font=f)
            tx = x + (w - tw if align == 'right' else (w - tw) / 2 if align == 'center' else 0)
            ld.text((tx, ty + (lh - size) / 2 - size * 0.1), line, font=f, fill=col)
            ty += lh
        canvas.alpha_composite(layer)

    def render_controls(self, canvas, parent, ox, oy):
        for c in parent.findall('control'):
            if not self.cond(' + '.join(f'[{v.text}]' for v in c.findall('visible') if v.text)):
                continue
            kind = c.get('type')
            x = ox + int(c.findtext('left', '0'))
            y = oy + int(c.findtext('top', '0'))
            w = int(c.findtext('width', '0') or 0) if (c.findtext('width') or '').isdigit() else 0
            h = int(c.findtext('height', '0') or 0) if (c.findtext('height') or '').isdigit() else 0
            if kind == 'group':
                self.render_controls(canvas, c, x, y)
            elif kind == 'image':
                tex = c.find('texture')
                path = self.text(tex.text or '')
                im = self.texture(path, w, h, tex.get('border'))
                if im is None and tex.get('fallback'):
                    im = self.texture('fake:' + str(x) + str(y), w, h)
                self.paste(canvas, im, x, y, tex.get('colordiffuse'), tex.get('diffuse'))
            elif kind == 'label':
                self.draw_text(canvas, x, y, w, h, self.text(c.findtext('label')), c.findtext('font', 'MN_Body'),
                               c.findtext('textcolor', 'FFFFFFFF'), c.findtext('align', 'left'),
                               c.findtext('aligny', 'center'), c.findtext('wrapmultiline') == 'true')
            elif kind == 'textbox':
                self.draw_text(canvas, x, y, w, h, self.text(c.findtext('label')), c.findtext('font', 'MN_Body'),
                               c.findtext('textcolor', 'FFFFFFFF'), 'left', 'top', True)
            elif kind == 'button':
                focused = c.get('id') == self.focus
                tex = c.find('texturefocus' if focused else 'texturenofocus')
                if tex is not None and tex.text:
                    self.paste(canvas, self.texture(tex.text, w, h, tex.get('border')), x, y, tex.get('colordiffuse'))
                color = c.findtext('focusedcolor' if focused else 'textcolor', 'FFFFFFFF') or 'FFFFFFFF'
                off = int(c.findtext('textoffsetx', '0') or 0)
                self.draw_text(canvas, x + off, y, w - off, h, self.text(c.findtext('label')),
                               c.findtext('font', 'MN_Body'), color, c.findtext('align', 'left'))
            elif kind == 'grouplist':
                cx = x
                for b in c.findall('control'):
                    if not self.cond(' + '.join(f'[{v.text}]' for v in b.findall('visible'))):
                        continue
                    label = self.text(b.findtext('label'))
                    f = self.font(b.findtext('font'))
                    bw = int(ImageDraw.Draw(canvas).textlength(label, font=f)) + 24
                    bh = int(b.findtext('height'))
                    tex = b.find('texturenofocus')
                    self.paste(canvas, self.texture(tex.text, bw, bh, tex.get('border')), cx, y, tex.get('colordiffuse'))
                    self.draw_text(canvas, cx + 12, y, bw, bh, label, b.findtext('font'), 'FFFFFFFF')
                    cx += bw + int(c.findtext('itemgap', '0'))
            elif kind == 'panel':
                items = self.items.get(c.get('id'), [])
                cx = cy = 0
                for index, item in enumerate(items):
                    layout = c.find('focusedlayout' if index == 0 else 'itemlayout')
                    lw, lh = int(layout.get('width')), int(layout.get('height'))
                    if cx + lw > w:
                        cx, cy = 0, cy + lh
                    if cy + lh > h + lh // 2:
                        break
                    self.item = item
                    self.render_controls(canvas, layout, x + cx, y + cy)
                    self.item = None
                    cx += lw
            elif kind == 'list':
                ident = c.get('id')
                items = self.items.get(ident, [])
                vertical = c.findtext('orientation') == 'vertical'
                pos = 0
                for index, item in enumerate(items):
                    current = index == 0
                    layout = c.find('focusedlayout' if current else 'itemlayout')
                    lw, lh = int(layout.get('width')), int(layout.get('height'))
                    if (vertical and pos > h) or (not vertical and pos > w):
                        break
                    self.item = item
                    self.render_controls(canvas, layout, x + (0 if vertical else pos), y + (pos if vertical else 0))
                    self.item = None
                    pos += lh if vertical else lw
            elif kind == 'progress':
                info = c.findtext('info')
                bg = c.find('texturebg')
                self.paste(canvas, self.texture(bg.text, w, h), x, y, bg.get('colordiffuse'))
                pct = int((self.item or {}).get('PercentPlayed', 0))
                mid = c.find('midtexture')
                if pct:
                    self.paste(canvas, self.texture(mid.text, max(1, w * pct // 100), h), x, y, mid.get('colordiffuse'))


def render(base, xml, out, focus, props, items, fake):
    scene = Scene(base, focus, props, items, fake)
    root = ET.parse(base / '1080i' / xml).getroot()
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    scene.render_controls(canvas, root.find('controls'), 0, 0)
    canvas.convert('RGB').save(out)

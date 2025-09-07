from wand.image import Image
from wand.color import Color
from wand.display import display
from wand.drawing import Drawing
from wand.font import Font
import re
import os
from datetime import datetime, timedelta
import glob
import math
import textwrap
from types import SimpleNamespace
import logging
import sys
import tempfile
import subprocess
from importlib import resources
import hashlib

from . import timer
from .collect import GameCollection
from .collect_tk import Worker
from .res import CHAR_TO_FILE, colours, colr_res, file_res

logger = logging.getLogger(__name__)

class BaseGame:
    font = SimpleNamespace(family='Noto-Sans-CJK-TC', size=18)

    def __repr__(self):
        return "<{class_name} from {game_name}>".format(
            class_name=type(self).__qualname__,
            game_name=self.orig_filename,
        )

    def __init__(self, orig_filename, caption, result_rows, rows, cols, success):
        self.orig_filename = orig_filename
        self.caption = caption
        self.result_rows = result_rows
        self.rows = rows
        self.cols = cols
        self.success = success

    @classmethod
    def from_base_game(cls, base_game):
        pass

    @classmethod
    def load(cls, linelist, filename=None):
        res = dict(orig_filename=filename, caption=[], result_rows=[], rows=0, cols=0)
        for line in linelist:
            if re.search('[A-Za-z0-9]', line): # result lines
                res['caption'].append(line)
            elif line[0] in {'\n', chr(0xFE0F)} and res['rows'] == 0: # blank lines
                continue
            elif line[0] in {'\n', chr(0xFE0F)}:
                res['result_rows'].append('')
                res['rows'] += 1
            else:
                line = line.rstrip()
                if res['rows'] == 0:
                    res['cols'] = sum(1 for i in line if i in CHAR_TO_FILE.keys())
                res['rows'] += 1
                res['result_rows'].append(line)
        while 0 < len(res['result_rows']) and res['result_rows'][-1] == '':
            res['result_rows'].pop()
        res['caption'] = ''.join(res['caption']).rstrip()
        res['success'] = not re.search('X/[0-9]|-/[0-9]|X&[0-9]/[0-9]', res['caption'])
        parsed = cls(**res)
        for c in cls.__subclasses__():
            if specialised := c.from_base_game(parsed):
                logger.info(f'Found {specialised} for {filename}')
                return specialised
        logger.info(f'Used {parsed} for {filename}')
        return parsed

    @classmethod
    def load_file(cls, filename):
        with open(filename) as f:
            return cls.load(f, filename)

    @classmethod
    def load_string(cls, string):
        return cls.load([i + '\n' for i in string.splitlines()])

    def upgrade_self(self, subclass):
        this_class_name = BaseGame.__class__.__qualname__
        if not self.__class__ == BaseGame:
            raise ValueError(f'{self} must be of class {this_class_name}')
        if not subclass in self.__class__.__subclasses__():
            raise ValueError(f'{subclass} must be a direct subclass of {this_class_name}')
        return subclass(**self.__dict__)

    def populate_result_grid(self, result_grid):
        for row in self.result_rows:
            if row == '':
                for i in range(self.cols):
                    with Image(width=20, height=3, filename=colr_res(colours.white)) as item:
                        result_grid.image_add(item)
            else:
                for char in row:
                    if resource := CHAR_TO_FILE.get(char):
                        with Image(width=20, height=20, filename=resource) as item:
                            result_grid.image_add(item)
        result_grid.montage(
            tile=f'{self.cols}x{self.rows}',
            thumbnail='+2+2'
        )
        return result_grid

    def make_image(self, game_image=None):
        if game_image is None:
            game_image = Image()
        with Image() as result_grid:
            game_image.font = Font(
                self.font.family,
                self.font.size,
                colours.black if self.success else colours.red
            )
            game_image.read(filename=f"label:{self.caption}")
            game_image.image_add(self.populate_result_grid(result_grid))
            game_image.smush(stacked=True, offset=5)
            logger.info(f'Constructed image for {self}')
            return game_image

class Celtix(BaseGame):
    @classmethod
    def from_base_game(cls, base_game):
        if dat := re.search('Celtix ([0-9]+) using ([0-9]+) wall', base_game.caption):
            cols = 8
            score = int(dat.group(2))
            puzzle_number = dat.group(1)
            cells = math.ceil(score / cols) * cols
            inst = base_game.upgrade_self(cls)
            inst.caption = f'Celtix {puzzle_number}'
            inst.rows = cells // cols
            inst.cols = cols
            inst.result_rows = textwrap.wrap(
                (chr(0x1F7E5) * score).ljust(cells, chr(0x2B1C)),
                cols)
            inst.success = True
            return inst

class Connections(BaseGame):
    @classmethod
    def from_base_game(cls, base_game):
        if dat := re.search('Connections', base_game.caption):
            puzzle_number = re.search('Puzzle #([0-9]+)', base_game.caption).group(1)
            inst = base_game.upgrade_self(cls)
            inst.caption = f'Connections {puzzle_number}'
            last_row = base_game.result_rows[-1]
            inst.success = last_row == last_row[0] * len(last_row)
            return inst

class Kotoba(BaseGame):
    @classmethod
    def from_base_game(cls, base_game):
        matcher = '([0-9]+) (1?[0-9X])+/12(\\?)'
        if dat := re.search(matcher, base_game.caption):
            inst = base_game.upgrade_self(cls)
            inst.caption = f'言葉で遊ぼう\n{dat.group(1)} {dat.group(2)}/12{dat.group(3)}'
            return inst

class Hexcodle(BaseGame):
    @classmethod
    def from_base_game(cls, base_game):
        matcher_success = '^I got Hexcodle #([0-9]+) in ([0-9])! Score: ([0-9]+)%'
        matcher_fail = '^I didn\'t get Hexcodle #([0-9]+) :\\( Score: ([0-9]+)%'
        if dat := re.search(matcher_success, base_game.caption):
            inst = base_game.upgrade_self(cls)
            inst.caption = re.sub(matcher_success,
                                  r'Hexcodle \1 \2/5 @ \3%',
                                  base_game.caption)
            inst.success = True
            return inst
        elif dat := re.search(matcher_fail, base_game.caption):
            inst = base_game.upgrade_self(cls)
            inst.caption = re.sub(matcher_fail,
                                  r'Hexcodle \1 X/5 @ \2%',
                                  base_game.caption)
            inst.success = False
            return inst

class Diffle(BaseGame):
    @classmethod
    def from_base_game(cls, base_game):
        if dat := re.search('([0-9]+) words / ([0-9]+) letters', base_game.caption):
            inst = base_game.upgrade_self(cls)
            inst.caption = f'Diffle {dat.group(1)}/{dat.group(2)}'
            inst.image = re.sub('txt$', 'png', base_game.orig_filename)
            return inst

    def populate_result_grid(self, result_grid):
        result_grid.read(filename=self.image)
        result_grid.chop(width=0, height=70, gravity='north')
        return result_grid

class Redactle(BaseGame):
    @classmethod
    def from_base_game(cls, base_game):
        if dat := re.search(
                r'[#Q]([0-9]+) in ([0-9]+) guess(?:es)? with an accuracy of ([0-9]+\.[0-9]+)%',
                base_game.caption):
            inst = base_game.upgrade_self(cls)
            inst.caption = f'Redactle {dat.group(1)}'
            inst.accuracy = dat.group(3)
            inst.guesses = dat.group(2)
            return inst

    def populate_result_grid(self, result_grid):
        result_grid.read(filename=file_res('redactle-base.png'))
        guess_width = math.log(int(self.guesses), 10) * 100
        accuracy_width = float(self.accuracy) / 100 * 300
        with Drawing() as ctx:
            ctx.fill_color = Color(colours.red)
            ctx.rectangle(left=80, top=20, width=guess_width, height=10)
            ctx.fill_color = Color(colours.green)
            ctx.rectangle(left=80, top=60, width=accuracy_width, height=10)
            ctx.font = self.font.family
            ctx.font_size = self.font.size
            ctx.fill_color = Color('black')
            ctx.text(0, 18, self.guesses)
            ctx.text(0, 55, self.accuracy + '%')
            ctx(result_grid)
        return result_grid

class Mkimg:
    def __init__(self, config):
        self.config = config
        self.layout = config.dat['layouts'][0]
        BaseGame.font = config.outimg_font
        self.outcfg = config.outimg_config
        self.timeline_spec = config.timeline
        self.activitywatch = timer.Query(config)

    def _halfhour_bucket(self, timestamp):
        return timestamp.replace(minute=(timestamp.minute // 30) * 30,
                                 second=0,
                                 microsecond=0)

    def _read_timestamp(self, timestring):
        return datetime.fromisoformat(timestring).astimezone(self.activitywatch.timezone)

    def _in_bucket(self, timestamp, buckets):
        halfhour = self._halfhour_bucket(timestamp)
        for i, ts in enumerate(buckets):
            if halfhour == ts:
                return i

    def _timeline_rectangle(self, event, buckets, width_per_second, height_per_bucket, left_edge):
        event_timestamp = self._read_timestamp(event['timestamp'])
        x = left_edge + (event_timestamp.minute % 30 * 60 + event_timestamp.second) * width_per_second
        y = self._in_bucket(event_timestamp, buckets) * height_per_bucket
        w = event['duration'] * width_per_second
        h = height_per_bucket
        return (x, y, w, h)

    def timeline(self):
        events = self.activitywatch.matching_events()
        width_per_second = self.timeline_spec.width_per_second
        height_per_bucket = self.timeline_spec.height_per_bucket
        left_edge = self.timeline_spec.left_edge
        minutes_per_row = 30
        border_width = self.timeline_spec.border_width
        buckets = list(sorted({self._halfhour_bucket(self._read_timestamp(i['timestamp']))
                               for i in events}))

        # If there are no events, then don't bother with a timeline:
        if len(events) == 0:
            return Image(width=self.outcfg.width, height=border_width,
                         pseudo=colr_res(colours.border))
        # If the last entry extends past the half-hour mark, then add a new bucket:
        last_entry = events[-1]
        last_entry_ts = self._read_timestamp(last_entry['timestamp'])
        if (self._halfhour_bucket(last_entry_ts) !=
            self._halfhour_bucket(last_entry_ts
                                  + timedelta(seconds=last_entry['duration']))):
            buckets.append(buckets[-1] + timedelta(minutes=30))

        img = Image(width=int(width_per_second * minutes_per_row * 60) + left_edge,
                    height=len(buckets) * height_per_bucket,
                    pseudo=colr_res(colours.border))
        img.background_color = colours.border
        for i, b in enumerate(buckets): # Half hour labels
            img.caption(b.strftime('%H:%M'),
                        left=0, top=i * height_per_bucket,
                        width=left_edge, height=height_per_bucket,
                        gravity='center',
                        font=Font(self.timeline_spec.font,
                                  self.timeline_spec.font_size, colours.white))

        with Drawing() as ctx:
            # Background
            ctx.fill_color = Color(colours.white)
            ctx.rectangle(left=left_edge, top=0,
                          width=width_per_second * minutes_per_row * 60,
                          height=len(buckets) * height_per_bucket)
            for i in range(1, minutes_per_row): # 1 minute marks
                ctx.fill_color = Color(colours.border if i % 5 == 0
                                       else self.timeline_spec.colour)
                ctx.line((i * 60 * width_per_second + left_edge, 0),
                         (i * 60 * width_per_second + left_edge, height_per_bucket * len(buckets)))
            for i in events:
                ctx.fill_color = Color('#' + hashlib.md5(i['data']['title'].encode('utf-8')).hexdigest()[0:6])
                x, y, w, h = self._timeline_rectangle(i, buckets, width_per_second, height_per_bucket, left_edge)
                ctx.rectangle(left=x, top=y, width=w, height=h)
                if x + w > img.width: # Wrap around if event crosses the half-hour mark
                    ctx.rectangle(left=left_edge, top=y + height_per_bucket,
                                  right=x + w - width_per_second * minutes_per_row * 60,
                                  height=h)
            ctx.draw(img)
        img.extent(width=self.outcfg.width, height=img.height + 2 * border_width,
                   gravity='center')
        return img

    def header_image(self):
        img = Image()
        with Image(pseudo=colr_res(colours.theme2), height=45, width=self.outcfg.width) as title:
            title.font = Font(self.outcfg.font, self.outcfg.title_size, colours.theme1)
            title.label("Wordle-Like Statistics", gravity='center')
            img.image_add(title)
        with Image(pseudo=colr_res(colours.theme2), height=40, width=self.outcfg.width) as subtitle:
            subtitle.font = Font(self.outcfg.font, self.outcfg.subtitle_size, colours.theme1)
            time_taken = self.activitywatch.time_taken()
            subtitle.label(
                "{date:%Y-%m-%d}{time_taken}".format(
                    date=self.config.date,
                    time_taken=f' - {time_taken} minutes' if time_taken else '',
                ),
                gravity='center',
            )
            img.image_add(subtitle)
        img.image_add(self.timeline())
        img.smush(stacked=True)
        return img

    def summary_subsequence(self, seq, layout, keys, vertical, recur=0):
        if isinstance(layout, str):
            with Image() as game_image:
                seq.image_add(keys[layout].make_image(game_image))
        elif isinstance(layout, list):
            with Image() as subseq:
                for i in layout:
                    self.summary_subsequence(subseq, i, keys, not vertical, recur + 1)
                if recur == 0: # Centre the highest-level rows
                    for i in range(subseq.iterator_length()):
                        subseq.iterator_set(i)
                        logger.info(f'Row {i} is {subseq.width} x {subseq.height}')
                        subseq.extent(width=self.outcfg.width, gravity='north')
                subseq.smush(stacked=vertical, offset=self.outcfg.game_separation)
                seq.image_add(subseq)

    def summary_image(self):
        saved = dict()
        for i in glob.glob(f'*-{self.config.date:%Y-%m-%d}.txt'):
            saved[i.split('-')[0]] = BaseGame.load_file(i)
        with self.header_image() as final, \
             tempfile.NamedTemporaryFile(prefix=self.config.program_name.lower()) as f:
            final.gravity = 'north'
            self.summary_subsequence(final, self.layout, saved, True)
            final.smush(stacked=True,)
            final.format = 'png'
            final.save(f)
            outfile = self.config.autowordle_outfile()
            subprocess.run(['pngcrush', f.name, outfile])
            logger.info(f'Image sent to {outfile}.')

def send_result_to_clipboard(cfg):
    subprocess.run(
        ['xclip', '-sel', 'c', '-target', 'text/uri-list'],
        input=f'file://{cfg.autowordle_outfile()}',
        text=True)

class MkimgWorker(Worker):
    event_name = "<<MkimgDone>>"
    def exec(self):
        Mkimg(self.config).summary_image()
        send_result_to_clipboard(self.config)
    def hook(self):
        self.gui.new_status(f'Image constructed and sent to {self.config.autowordle_outfile()}')

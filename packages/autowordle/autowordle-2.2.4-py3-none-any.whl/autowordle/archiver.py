#!/usr/bin/env python3

import glob
from datetime import datetime
import os
import logging
import py7zr
import pytesseract
from PIL import Image
import re
import subprocess

from .collect_tk import Worker

logger = logging.getLogger(__name__)

yaml_fragment = """\
? ["{game}", "{date}"]
:
  dat: |
{text}
  timestamp: {timestamp}
"""

class Archiver:
    def __init__(self, config):
        self.config = config

    def game_object(self, filename):
        with open(filename) as f:
            dat = f.readlines()
        timestamp = datetime.fromtimestamp(
            os.stat(filename).st_mtime,
            tz=self.config.timezone
        ).isoformat()
        game, date = filename.split('-', 1)
        date = date[:-4]
        return yaml_fragment.format(
            game=game,
            date=date,
            timestamp=timestamp,
            text=''.join(' ' * (4 if l != '\n' else 0) + l for l in dat).rstrip())

    def strings_for_date(self, datestring):
        return ''.join(self.game_object(i) for i in glob.glob(f'*-{datestring}.txt'))

    def dump_to_file(self):
        outfile = self.config.yaml_archive_file()
        with open(outfile, 'a') as f:
            f.write(self.strings_for_date(self.config.date.strftime('%Y-%m-%d')))
        logger.info(f'Data sent to {outfile}.')

    def archive_to_7z(self):
        outfile = self.config.zip_archive_file()
        with py7zr.SevenZipFile(outfile, 'a') as archive:
            for i in (glob.glob(f'*-{self.config.date:%Y-%m-%d}.png')
                      + glob.glob(f'*-{self.config.date:%Y-%m-%d}.txt')):
                archive.write(i)
                os.remove(i)
        logger.info(f'Old items sent to {outfile}.')

    def celtix_cleanup(self):
        celtix_filename = f'celtix-{self.config.date:%Y-%m-%d}.png'
        if os.path.isfile(celtix_filename):
            with Image.open(celtix_filename) as img:
                img_text = pytesseract.image_to_string(img.crop((0, 0, 222, 74)))
                if puzzle_number := re.search('Celtix #([0-9]+)', img_text):
                    celtix_dest = os.path.expanduser(self.config.celtix_archive.format(
                        puznum=puzzle_number.group(1),
                        date=self.config.date))
                    os.rename(celtix_filename, celtix_dest)
                    logger.info(f'Moved Celtix result to {celtix_dest}.')
                else:
                    logger.warning(f'Cannot find Celtix puzzle number in {celtix_filename};')
                    logger.warning(f'Detected text was: {thing!r}.')
        else:
            logger.info(f'No Celtix result found, skipping.')

class ArchiverWorker(Worker):
    event_name = "<<ArchiveComplete>>"
    def exec(self):
        if self.config.do_cleanup:
            cleanup = Archiver(self.config)
            cleanup.celtix_cleanup()
            cleanup.dump_to_file()
            cleanup.archive_to_7z()
    def hook(self):
        subprocess.Popen([
            "paplay",
            "/usr/share/sounds/freedesktop/stereo/complete.oga"])
        self.gui.root.bind('<space>', lambda _: self.archive_and_quit())
        self.gui.quit_button.config(state='enabled', command=self.archive_and_quit)
    def archive_and_quit(self):
        self.config.do_cleanup = True
        self.gui.new_status("Cleaning up...")
        self.exec()
        self.gui.root.destroy()

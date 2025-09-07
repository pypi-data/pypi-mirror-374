import sqlite3
import logging
import yaml
import contextlib
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class Db:
    MAGIC_NUMBER = sum(int(b) * 1 << (8 * i) for i, b in enumerate(reversed(b'awdl')))

    def __enter__(self):
        self.con = sqlite3.connect(self.db_location)
        return self.con

    def __exit__(self, _exc_typ, _exc_val, _exc_tb):
        self.con.close()

    def __init__(self, cfg):
        self.db_location = os.path.expanduser(cfg.dat['archives']['db'])
        self.tz = cfg.timezone
        with (self as db,
              contextlib.closing(db.execute("PRAGMA application_id;")) as magic_number):
            if (actual_magic_number := magic_number.fetchone()[0]) != self.MAGIC_NUMBER:
                logger.error(f'Database not the right type: got {actual_magic_number}, '
                             f'should be {self.MAGIC_NUMBER}')

    def save(self, date, game, thing):
        with (self as db,
              contextlib.closing(db.cursor()) as cur,
              db):
            info = (date, game, datetime.now(tz=self.tz).isoformat(), thing)
            try:
                if isinstance(thing, str):
                    logger.info("Inserting a string to the database")
                    cur.execute('INSERT INTO dat (date, game, timestamp, text_data) '
                                'VALUES (?, ?, ?, ?)',
                                info)
                else:
                    logger.error(f"Don't know what to do with {thing}")
                    raise ValueError(f"Don't know what to do with {thing}")
            except sqlite.IntegrityError:
                logger.warning('Cannot insert game - may have already been inserted')
            # elif isinstance(thing, bytes):
            #     logger.info("Inserting an image to the database")
            #     cur.execute('INSERT INTO sqlar (name, mode, mtime, sz, data)'
            #                 'VALUES (?, ?, ?, ?, ?)',
            #                 )
            #     cur.execute('INSERT INTO dat (date, game, timestamp, image_data) '
            #                 'VALUES (?, ?, ?, ?)',
            #                 info)

    def load(self, date, game):
        pass

class TextArchiveLoader(yaml.SafeLoader):
    def construct_mapping(self, node):
        pairs = self.construct_pairs(node, deep=True)
        try:
            return dict(pairs)
        except TypeError:
            rv = {}
            for key, value in pairs:
                if isinstance(key, list):
                    key = tuple(key)
                    rv[key] = value
            return rv

TextArchiveLoader.add_constructor('tag:yaml.org,2002:map',
                                  TextArchiveLoader.construct_mapping)

def load_archives(filename):
    with open(filename) as f:
        return yaml.load(f, TextArchiveLoader)

def dump_to_db(filename, selected_date, db):
    for ((game, date), dat) in load_archives(filename).items():
        if selected_date == date:
            try:
                db.save(dat['timestamp'], game, dat['dat'])
            except sqlite3.IntegrityError:
                pass

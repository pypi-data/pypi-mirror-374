import logging
import os
import sys
from datetime import datetime
import yaml
from types import SimpleNamespace
import pytz
import subprocess
import argparse
import glob
import platformdirs

from .collect import GameCollection, CollectionStatus
from .db import Db
from . import collect_tk
from . import mkimg
from . import archiver
from . import desktop

logger = logging.getLogger(__name__)

class Config:
    program_name = 'Autowordle'
    default_config_filename = platformdirs.user_config_path(
        'autowordle', ensure_exists=True) / 'games.yaml'
    home_dir = platformdirs.user_data_dir('autowordle', ensure_exists=True)
    def __repr__(self):
        return '<{class_} {file_loc} {date:%Y-%m-%d}>'.format(
            class_=self.__class__.__qualname__,
            file_loc=self.location,
            date=self.date)
    def __init__(self, args):
        self.location = args.config
        self.do_cleanup = args.cleanup
        self.do_collect = args.collect
        self.check_already_collected = args.check_collected
        self.install_desktop_file = args.install_desktop_file
        with open(self.location) as f:
            self.dat = yaml.load(f, yaml.SafeLoader)
            self.collection = GameCollection(self.dat['games'])

        self.timezone = pytz.timezone(self.dat['timezone'])
        self.date = datetime.now(tz=self.timezone)

        self._outfile = os.path.expanduser(self.dat['output']['filename'])
        self.yaml_archive = self.dat['archives']['yaml']
        self.zip_archive = self.dat['archives']['zip']
        self.celtix_archive = self.dat['archives']['celtix']

        self.outimg_config = SimpleNamespace(
            width=self.dat['output']['width'],
            game_separation=self.dat['output']['game_separation'],
            title_size=self.dat['output']['title']['font_size'],
            subtitle_size=self.dat['output']['title']['subtitle_font_size'],
            font=self.dat['output']['title']['font'])
        self.outimg_font = SimpleNamespace(
            family=self.dat['output']['content_font'],
            size=self.dat['output']['content_font_size'],)
        self.timeline = SimpleNamespace(
            left_edge=self.dat['output']['timeline']['left_edge'],
            border_width=self.dat['output']['timeline']['border_width'],
            height_per_bucket=self.dat['output']['timeline']['height_per_bucket'],
            width_per_second=self.dat['output']['timeline']['width_per_second'],
            font=self.dat['output']['timeline']['font'],
            font_size=self.dat['output']['timeline']['font_size'],
            colour=self.dat['output']['timeline']['colour'])

    @classmethod
    def from_cmdline(cls):
        parser = argparse.ArgumentParser(
            description='Store and construct summary images for Wordle clones')
        for opt, desc in [('--cleanup', ('Clean up after image construction'
                                         ' (Overrideable in GUI)')),
                          ('--check-collected',
                           ("Exit if today's game is already collected"
                            " and collection is not in progress")),
                          ('--collect', 'Collect games')]:
            parser.add_argument(
                opt,
                action=argparse.BooleanOptionalAction,
                help=desc,
                default=True)
        parser.add_argument(
            '--install-desktop-file', help='Install a .desktop file, then exit',
            action='store_true')
        parser.add_argument(
            '--config',
            metavar='FILENAME',
            help='Configuration file location',
            default=cls.default_config_filename)
        return cls(parser.parse_args())

    @classmethod
    def from_args(cls, config_file=None, *,
                  collect=True, check_collected=True, cleanup=True,
                  install_desktop_file=False):
        return cls(SimpleNamespace(
            config=config_file or cls.default_config_filename,
            cleanup=cleanup,
            collect=collect,
            check_collected=check_collected,
            install_desktop_file=install_desktop_file))

    def autowordle_outfile(self):
        return self.date.strftime(os.path.expanduser(self._outfile))

    def yaml_archive_file(self):
        return self.date.strftime(os.path.expanduser(self.yaml_archive))

    def zip_archive_file(self):
        return self.date.strftime(os.path.expanduser(self.zip_archive))

    def window_titles(self):
        return {x.get("window_title") or x["name"] for x in self.dat["games"]}

    def db(self):
        return Db(self)

class EarlyExit(Exception):
    def __init__(self, exit_code=1):
        self.exit_code = exit_code
    def exit(self):
        sys.exit(self.exit_code)

def check_already_collected(cfg):
    if (os.path.isfile(cfg.autowordle_outfile())
        and cfg.check_already_collected
        and len(glob.glob(cfg.home_dir + '*.txt')) == 0):
        status = subprocess.run([
            'yad',
            "--button=Copy today's image!gtk-ok",
            '--button=Close!gtk-cancel',
            '--image=dialog-warning',
            '--window-icon=dialog-warning',
            '--text', f"Today ({cfg.date:%Y-%m-%d})'s games are already collected.",
            '--title', cfg.program_name
        ])
        if status.returncode == 0:
            mkimg.send_result_to_clipboard(cfg)
        raise EarlyExit(1)

def top():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    cfg = Config.from_cmdline()
    os.chdir(cfg.home_dir)

    try:
        if cfg.install_desktop_file:
            desktop.install_desktop_file()
            raise EarlyExit(0)
        check_already_collected(cfg)
        workers = [
            (mkimg.MkimgWorker(cfg), collect_tk.ClipwaitThread.finish_event_name),
            (archiver.ArchiverWorker(cfg), mkimg.MkimgWorker.event_name)]
        if cfg.do_collect:
            gui = collect_tk.GUI(cfg)
            cfg.do_cleanup = False # Don't clean up by default in GUI
            for worker, trigger in workers:
                gui.add_worker(worker, trigger)
            match gui.exec():
                case CollectionStatus.COMPLETE:
                    pass
                case CollectionStatus.COMPLETE_FOR_NOW:
                    logger.info('Collection complete for now')
                case CollectionStatus.INCOMPLETE:
                    logger.info('Collection aborted')
                    raise EarlyExit(1)
        else:
            for worker, _ in workers:
                worker.exec()
    except EarlyExit as e:
        e.exit()

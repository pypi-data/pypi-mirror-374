from enum import Enum
import pytesseract
import re
import io
import os
from PIL import Image
from datetime import datetime
import subprocess
import logging

logger = logging.getLogger(__name__)

class DetectionType(Enum):
    TEXT = "text"
    IMAGE = "image"

class GameStatus(Enum):
    OPTIONAL = 'optional'
    PARTIALLY_COLLECTED = 'partially_collected'
    COLLECTED = 'collected'
    UNCOLLECTED = 'uncollected'
    UNELIGIBLE = 'uneligible'
    def as_str(self):
        if self == GameStatus.OPTIONAL:
            return 'Optional'
        elif self == GameStatus.PARTIALLY_COLLECTED:
            return 'Awaiting text'
        elif self == GameStatus.COLLECTED:
            return 'Collected'
        elif self == GameStatus.UNCOLLECTED:
            return 'Uncollected'
        elif self == GameStatus.UNELIGIBLE:
            return 'Ineligible'

class Game:
    def __init__(self):
        self.date = datetime.today().strftime("%Y-%m-%d")
        self.gui = None
        self.db = None

    def log(self, text):
        if self.gui is not None:
            self.gui.new_status(text)
        else:
            logger.info(text)

    @classmethod
    def from_dict(cls, d):
        inst = cls()
        dat = {
            "detection": DetectionType.TEXT,
            "refresh_hour": 0,
            "short_name": d['name'].lower(),
            "name": None,
            "required": True,
            "target": None,
            "text_target": None,
        } | d
        inst.name = dat["name"]
        inst.required = dat["required"]
        inst.detection = DetectionType(dat["detection"])
        inst.refresh_hour = dat["refresh_hour"]

        if "short_name" in dat and dat["short_name"]:
            inst.short_name = dat["short_name"]
        else:
            inst.short_name = dat["name"].lower()
        inst.out_filename = f'{inst.short_name}-{inst.date}'
        if "target" in dat and dat["target"]:
            inst.target = re.compile(dat["target"])
        else:
            inst.target = re.compile("^" + dat["name"])
        if "text_target" in dat and dat['text_target']:
            inst.text_target = re.compile(dat["text_target"])
        else:
            inst.text_target = inst.target
        if not (inst.name and inst.target):
            raise ValueError("name and target must be defined.")
        return inst

    def __repr__(self):
        return "<{class_name} {game_name}{collectedp}>".format(
            class_name=type(self).__qualname__,
            game_name=str(self.name),
            collectedp=" collected" if self.collectedp() else "",
        )

    def eligiblep(self):
        return self.refresh_hour <= datetime.now().hour

    def collectedp(self):
        if self.detection == DetectionType.TEXT:
            return os.path.isfile(self.out_filename + '.txt')
        elif self.detection == DetectionType.IMAGE:
            return all(os.path.isfile(self.out_filename + x)
                       for x in ['.txt', '.png'])

    def status(self):
        if self.collectedp():
            return GameStatus.COLLECTED
        elif not self.eligiblep():
            return GameStatus.UNELIGIBLE
        elif (os.path.isfile(self.out_filename + ".png")
              and not os.path.isfile(self.out_filename + ".txt")):
            return GameStatus.PARTIALLY_COLLECTED
        elif self.required:
            return GameStatus.UNCOLLECTED
        else:
            return GameStatus.OPTIONAL

    def save_text_to_file(self, thing):
        with open(self.out_filename + '.txt', 'w') as f:
            f.write("\n".join(line for line in thing.splitlines()
                              if not line.startswith("http")))
            f.write("\n")

    def save_text_to_db(self, thing):
        if self.db is not None:
            self.db.save(self.date, self.short_name, thing)

    def collect_if_match(self, thing):
        if self.collectedp() or not self.eligiblep():
            return None
        elif self.detection == DetectionType.TEXT and isinstance(thing, str):
            if self.target.search(thing):
                self.save_text_to_file(thing)
                self.save_text_to_db(thing)
                self.log(f'Collected text of {self.name}')
                play_sound("/usr/share/sounds/freedesktop/stereo/complete.oga")
                return self
        elif (self.detection == DetectionType.IMAGE
              and isinstance(thing, str)
              and os.path.isfile(self.out_filename + ".png")
              and self.text_target.search(thing)):
            self.save_text_to_file(thing)
            self.save_text_to_db(thing)
            self.log(f'Collected text of {self.name}')
            play_sound("/usr/share/sounds/freedesktop/stereo/complete.oga")
            return self
        elif self.detection == DetectionType.IMAGE and isinstance(thing, Image.Image):
            text = pytesseract.image_to_string(thing)
            text_cropped = pytesseract.image_to_string( # for Celtix
                thing.crop((0, 0, 222, 74)))
            if self.target.search(text) or self.target.search(text_cropped):
                thing.save(self.out_filename + ".png")
                # Cue to accept text response
                play_sound("~/.local/share/sounds/ready.mp3")
                self.log(f'Collected image of {self.name}')
                return self
        else:
            return None

class CollectionStatus(Enum):
    INCOMPLETE = 'incomplete'
    COMPLETE_FOR_NOW = 'complete-for-now'
    COMPLETE = 'complete'

class GameCollection:
    def __init__(self, collection):
        self.collection = [Game.from_dict(i) for i in collection]

    def __repr__(self):
        return f"<{type(self).__qualname__}, {len(self.collection)} entries>"

    def inject_gui(self, gui):
        for i in self.collection:
            i.gui = gui

    def inject_db(self, db):
        for i in self.collection:
            i.db = db

    def eligible(self):
        return [x for x in self.collection if x.eligiblep()]

    def status(self):
        if all(x.collectedp() for x in self.collection):
            return CollectionStatus.COMPLETE
        elif all(x.collectedp() for x in self.eligible()):
            return CollectionStatus.COMPLETE_FOR_NOW
        else:
            return CollectionStatus.INCOMPLETE

    def get(self, game_name):
        return next(x for x in self.collection if x.name == game_name)

    def find_matching_game(self, thing):
        for i in self.eligible():
            if res := i.collect_if_match(thing):
                return res
        return None

def play_sound(path):
    subprocess.Popen(["paplay", os.path.expanduser(path)])

def clipboard():
    if re.search(
            "image/",
            subprocess.run(
                ["xclip", "-sel", "c", "-target", "TARGETS", "-out"],
                capture_output=True).stdout.decode("UTF-8")):
        return Image.open(
            io.BytesIO(
                subprocess.run(
                    ["xclip", "-sel", "c", "-target", "image/png", "-out"],
                    capture_output=True).stdout))
    else:
        return subprocess.run(
            ["xclip", "-sel", "c", "-out"],
            capture_output=True).stdout.decode("UTF-8")

import os
import configparser
import tempfile
import subprocess
import platformdirs

def install_desktop_file():
    desktop_file = configparser.RawConfigParser()
    desktop_file.optionxform = lambda option: option
    desktop_file['Desktop Entry'] = {
        'Type': 'Application',
        'Exec': 'autowordle',
        'Name': 'Autowordle',
        'GenericName': 'Wordle clone collector',
        'Categories': 'Game',
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = 'autowordle.desktop'
        with open(filename, 'w') as f:
            desktop_file.write(f)
        subprocess.run([
            'desktop-file-install',
            '--dir=' + platformdirs.user_data_dir('applications'),
            filename
        ])

if __name__ == "__main__":
    install_desktop_file()

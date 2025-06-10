from setuptools import setup

APP = ['main.py']
DATA_FILES = ['assets']  # Include your assets folder
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'assets/my_icon.icns',  # Path to your icon
    'packages': [],  # e.g., ['PyQt5']
    'includes': [],
}

setup(
    app=APP,
    name='Live Indicators',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
# Standard Library
import os, platform, pathlib, sys, typing

# Third Party Libraries
import toml
from loguru import logger

# Global constants
# For more information see:
# https://cloud.google.com/text-to-speech/docs/reference/rest/v1/text/synthesize
# https://cloud.google.com/text-to-speech/docs/voices 
GOOGLE_APIS_TTS_URL     = 'https://texttospeech.googleapis.com/v1/text:synthesize'
CONFIG_WINDOWS_DIR      = os.path.expandvars('%APPDATA%\TTS')
CONFIG_WINDOWS          = f'{CONFIG_WINDOWS_DIR}\config.toml'
CONFIG_LINUX_DIR        = '~/.config/tts'
CONFIG_LINUX            = f'{CONFIG_LINUX_DIR}/config.toml'
CHARSET                 = 'utf-8'
DEFAULT_AUDIO_ENCODING  = 'MP3'

# Helper Functions
def is_windows():
    return any(platform.win32_ver())

def expand(path):
    return pathlib.Path(path).expanduser()

def read_file(fname: str) -> str:
    ''' Reads a file into a string '''
    file = open(fname, 'r')
    res = file.read()
    file.close()
    return res

def collect_files(rootdir):
    ''' Recursively collects the names of every file in every subdirectory given a rootdir '''
    files = []
    for file in os.listdir(rootdir):
        f = os.path.join(rootdir, file)
        os.path.isfile(f)
        files.append(f)
        if os.path.isdir(f):
            files.append(collect_files(f))
    return files

is_win = is_windows()

def setup_logger(verbose: bool = False):
    # Setup logging
    logger.remove() # Override default logger
    # Format: [2022-09-01 23:36:01.792] [DEBUG] [bin_name.main:150] Hello!
    PROGRAM_LOG_MSG_FORMAT = '\x1b[0m\x1b[32m[{time:YYYY-MM-DD HH:mm:ss.SSS}]\x1b[0m [<lvl>{level}</>] [<c>{name}:{line}</>] {message}'
    loglevel = 'ERROR' if os.environ.get('LOGLEVEL') == None else os.environ.get('LOGLEVEL')
    if (verbose):
        loglevel = 'INFO'

    logger.add(sys.stdout, format=PROGRAM_LOG_MSG_FORMAT, level=loglevel)

def get_cfg():
    cfgfp = expand(CONFIG_LINUX) if not is_win else expand(CONFIG_WINDOWS)
    cfg = toml.loads(read_file(str(cfgfp)))
    return cfg

# TTS 

# TODO:
# Features that might be useful to add for this function are:
# - Displaying urls of cached sounds instead, or skipping sounds
# that have been cached in a separate `sounds_cached` attribute.
# - A cli option to ignore cached sounds and call the tts anyways
def skip_cached_sounds(cfg: dict[str, typing.Any], inp: str):
    ''' If a sound has already been created & cached,
    display the filepath to the file instead.
    '''
    # If the sound already exists in our configured sound_directories,
    if cfg['config'].__contains__('sound_directories'):
        soundsfp: list[str] = cfg['config']['sound_directories']
        sounds = []
        for fp in soundsfp:
            sounds.append(collect_files(expand(fp)))

        logger.info('Found Sounds:')
        logger.debug(sounds)

        # Then only display the path to it, and exit
        for sound_dir in sounds:
            for sp in sound_dir:
                if pathlib.Path(expand(sp)).stem == inp:
                    print(sp)
                    sys.exit(0)

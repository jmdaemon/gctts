# Imports
from gtts.cli import build_cli

# Standard Library
import json, base64, sys, platform, pathlib, os

# Third Party Libraries
import requests, toml

# Setup logging
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

# TTS API functions
def create_json_input(inp, voice, _format, model):
    data = {
        'input': {
            'text': inp
        },
        'voice': {
            'languageCode': voice,
            'name': fmt_model(voice, model),
            'ssmlGender': 'FEMALE'
        },
        'audioConfig': {
            'audioEncoding': _format
        }
    }
    return data

def fmt_model(voice, model):
    return f'{voice}-{model}'

def fmt_auth_token(token):
    return f'Bearer {token}'

def create_header(token):
    auth_token = fmt_auth_token(token)
    headers = {
        'Authorization' : auth_token,
        'Content-Type': f'application/json; charset={CHARSET}'
    }
    return headers

def main():
    # Parse command line arguments
    parser = build_cli()
    args = parser.parse_args()

    inp = args.input
    model = args.model
    output = args.output

    voice = args.language_code
    _format = args.format if (args.format) else DEFAULT_AUDIO_ENCODING
    verbose = args.verbose

    # Setup logging
    logger.remove() # Override default logger
    # Format: [2022-09-01 23:36:01.792] [DEBUG] [bin_name.main:150] Hello!
    PROGRAM_LOG_MSG_FORMAT = '\x1b[0m\x1b[32m[{time:YYYY-MM-DD HH:mm:ss.SSS}]\x1b[0m [<lvl>{level}</>] [<c>{name}:{line}</>] {message}'
    loglevel = 'ERROR' if os.environ.get('LOGLEVEL') == None else os.environ.get('LOGLEVEL')
    if (verbose):
        loglevel = 'INFO'

    logger.add(sys.stdout, format=PROGRAM_LOG_MSG_FORMAT, level=loglevel)

    logger.debug(f'input: {inp}')
    logger.debug(f'model: {model}')
    logger.debug(f'output: {output}')
    logger.debug(f'voice: {voice}')
    logger.debug(f'_format: {_format}')

    # Get the token
    cfgfp = expand(CONFIG_LINUX) if not is_win else expand(CONFIG_WINDOWS)
    cfg = toml.loads(read_file(str(cfgfp)))
    token = cfg['config']['token'] # Note that this assumes there is a [config] token variable

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

    # Send TTS API reuqest

    # Create json body
    json_request = create_json_input(inp, voice, _format, model)
    logger.info(f'Request JSON')
    logger.debug(json_request)

    # Create headers
    request_headers = create_header(token)
    logger.info(f'Request Headers')
    logger.debug(request_headers)

    # Send request
    r = requests.post(GOOGLE_APIS_TTS_URL, json=json_request, headers=request_headers)
    json_response =json.loads(r.content)
    logger.info(f'Response')
    logger.debug(json_response)

    if (r is None) or (r.status_code != 200):
        sys.exit(1)

    # Extract data into file 
    contents = base64.decodebytes(r.content)

    # Write file to disk
    with open(output, 'wb') as f:
        f.write(contents)

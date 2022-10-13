# Imports
from gtts.cli import build_cli
from gtts.tts import *

# Standard Library
import json, base64, sys, pathlib

# Third Party Libraries
import requests, toml
from loguru import logger

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

    setup_logger(verbose)

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

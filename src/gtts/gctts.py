# Imports
from gtts.cli import build_cli
from gtts.tts import (
    CONFIG,
    GOOGLE_APIS_TTS_URL,
    CHARSET,
    DEFAULT_AUDIO_ENCODING,
    get_cfg,
    setup_logger,
    skip_cached_sounds,
)

# Standard Library
import json, base64, sys, os

# Third Party Libraries
import requests
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
    parser.add_argument('model', type=str, help='TTS voice model')
    parser.add_argument('-f', '--format', type=str, help='Specify the audio format. (Choices: [MP3, OGG_OPUS, LINEAR16])')
    args = parser.parse_args()

    inp = args.input
    model = args.model
    output = args.output if args.output else f'{inp}.{DEFAULT_AUDIO_ENCODING}'

    voice = args.language_code if args.language_code else 'ja-JP'
    _format = args.format if (args.format) else DEFAULT_AUDIO_ENCODING
    verbose = args.verbose

    setup_logger(verbose)

    logger.debug(f'input: {inp}')
    logger.debug(f'model: {model}')
    logger.debug(f'output: {output}')
    logger.debug(f'voice: {voice}')
    logger.debug(f'_format: {_format}')

    token: str = ''
    if os.path.exists(CONFIG):
        cfg = get_cfg()
        if cfg['config'].__contains__('voice'):
            voice = cfg['config']['voice'] if cfg['config']['voice'] else voice

        if cfg.__contains__('gctts'):
            if cfg['gctts'].__contains__('token'):
                token = cfg['gctts']['token']
            else:
                print(f'You must set a valid \'token\' in {CONFIG}')
                sys.exit(1)
        else:
            print(f'You must define \'[gctts]\' table in {CONFIG}')
            sys.exit(1)

        skip_cached_sounds(cfg, inp)

    # Create json body
    json_request = create_json_input(inp, voice, _format, model)
    logger.info(f'Request JSON')
    logger.debug(json_request)

    # Create headers
    request_headers = create_header(token)
    logger.info(f'Request Headers')
    logger.debug(request_headers)

    # Send TTS API reuqest
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

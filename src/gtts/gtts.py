# Imports
from gtts.cli import build_cli
from gtts.tts import (
    CONFIG,
    CHARSET,
    get_cfg,
    setup_logger,
    skip_cached_sounds,
)

# Standard Library
import sys, os

# Third Party Libraries
import requests
from loguru import logger

GOOGLE_TTS_URL = 'https://translate.google.com/translate_tts'
GOOGLE_TTS_QUERY = ('{tts_url}'
                    '?ie={encoding}'
                    '&tl={voice}'
                    '&client=tw-ob'
                    '&q={inp}'
                   )

def main():
    # Parse command line arguments
    parser = build_cli()
    args = parser.parse_args()

    inp = args.input
    output = args.output if args.output else f'{inp}.wav'
    voice = args.language_code if args.language_code else 'ja-JP'
    verbose = args.verbose

    setup_logger(verbose)
    logger.debug(f'input: {inp}')
    logger.debug(f'output: {output}')
    logger.debug(f'voice: {voice}')

    if os.path.exists(CONFIG):
        cfg = get_cfg()
        if cfg['config'].__contains__('voice'):
            voice = cfg['config']['voice'] if cfg['config']['voice'] else voice
        skip_cached_sounds(cfg, inp)

    query = GOOGLE_TTS_QUERY.format(
        tts_url=GOOGLE_TTS_URL,
        encoding=CHARSET,
        voice=voice,
        inp=inp)
    logger.debug(f'{query}')
    r = requests.get(query)

    if (r is None) or (r.status_code != 200):
        sys.exit(1)

    # Write file to disk
    with open(output, 'wb') as f:
        f.write(r.content)

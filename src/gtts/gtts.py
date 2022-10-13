# Imports
from gtts.cli import build_cli
from gtts.tts import (
    CONFIG,
    is_win,
    CHARSET,
    get_cfg,
    setup_logger,
    skip_cached_sounds,
)

# Standard Library
import sys, os, subprocess

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
    parser.add_argument('-r', '--re-encode', action='store_true', help='Specify the voice to use')
    args = parser.parse_args()

    inp = args.input
    output = args.output if args.output else f'{inp}.wav'
    voice = args.language_code if args.language_code else 'ja-JP'
    verbose = args.verbose
    reencode = args.re_encode

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

    if reencode:
        output_file = f'{output}-test.wav'
        if is_win:
            subprocess.run([f'msound.ps1', f'-i {output}', f'-o {output_file}'], stdout=sys.stdout)
        else:
            subprocess.run([f'msound', output, output_file], stdout=sys.stdout)

        # Replace old file
        os.remove(output)
        os.rename(output_file, output)

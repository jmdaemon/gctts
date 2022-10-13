import argparse

def build_cli():
    parser = argparse.ArgumentParser(description='Queries Google\'s TTS API for voice lines')
    parser.add_argument('input', type=str, help='TTS input text')
    parser.add_argument('model', type=str, help='TTS voice model')
    parser.add_argument('output', type=str, help='Name of output audio file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show debug information')
    parser.add_argument('-s', '--sounds-dir', type=str, help='Path to sounds directory')
    parser.add_argument('-l', '--language-code', type=str, help='Specify the voice to use')
    parser.add_argument('-f', '--format', type=str, help='Specify the audio format. (Choices: [MP3, OGG_OPUS, LINEAR16])')
    return parser

import toml
import json
import argparse
import requests
import base64
import sys
import platform
import pathlib

GOOGLE_APIS_TTS_URL = 'https://texttospeech.googleapis.com/v1/text:synthesize'
CONFIG_WINDOWS = "%APPDATA%\TTS\config.toml"
CONFIG_LINUX = "~/.config/tts/config.toml"
CHARSET = 'utf-8'
DEFAULT_AUDIO_ENCODING = 'MP3'

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

is_win = is_windows()

# TTS API functions
def create_json_input(inp, voice, model):
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
            'audioEncoding': DEFAULT_AUDIO_ENCODING
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

# Parse command line arguments
parser = argparse.ArgumentParser(description='Queries Google\'s TTS API for voice lines')
parser.add_argument('input', type=str, help='TTS input text')
parser.add_argument('model', type=str, help='TTS voice model')
parser.add_argument('output', type=str, help='Name of output audio file')
parser.add_argument('-v', '--voice', type=str, help='Filepath to template directory')
args = parser.parse_args()
inp = args.input
voice = args.voice
model = args.model
output = args.output

# TODO: Input check
cfgfp = expand(CONFIG_LINUX) if not is_win else expand(CONFIG_WINDOWS)
cfg = toml.loads(read_file(cfgfp))
token = cfg['config']['token']

# Send reuqest
json_request = create_json_input(inp, voice, model)
print(f'Request JSON\n{json_request}')

request_headers = create_header(token)
print(f'Request Headers\n{request_headers}')

r = requests.post(GOOGLE_APIS_TTS_URL, json=json_request, headers=request_headers)
json_response =json.loads(r.content)
print(f'Response\n{json_response}')

if (r is None) or (r.status_code != 200):
    sys.exit(1)

# Extract data into file 
contents = base64.decodebytes(r.content)

# Write file to disk
with open(output, 'wb') as f:
    f.write(contents)

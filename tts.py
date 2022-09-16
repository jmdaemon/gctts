import toml, json, argparse, base64, sys, platform, pathlib, os
import requests

# Global constants
# For more information see:
# https://cloud.google.com/text-to-speech/docs/reference/rest/v1/text/synthesize
# https://cloud.google.com/text-to-speech/docs/voices 
GOOGLE_APIS_TTS_URL     = 'https://texttospeech.googleapis.com/v1/text:synthesize'
CONFIG_WINDOWS_DIR      = '%APPDATA%\\TTS'
CONFIG_WINDOWS          = f'{CONFIG_WINDOWS_DIR}\\config.toml'
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

# Get the token
cfgfp = expand(CONFIG_LINUX) if not is_win else expand(CONFIG_WINDOWS)
cfg = toml.loads(read_file(str(cfgfp)))
token = cfg['config']['token'] # Note that this assumes there is a [config] token variable

# If the sound already exists in our configured sound_directories,
soundsfp: list[str] = cfg['config']['sound_directories']
sounds = []
for fp in soundsfp:
    sounds.append(collect_files(expand(fp)))

print('Found Sounds:')
print(sounds)

# Then only display the path to it, and exit
for sound_dir in sounds:
    for sp in sound_dir:
        if pathlib.Path(expand(sp)).stem == inp:
            print(sp)
            sys.exit(0)

# Send TTS API reuqest
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

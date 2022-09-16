import json
import argparse
import requests
import base64
import sys

GOOGLE_APIS_TTS_URL = 'https://texttospeech.googleapis.com/v1/text:synthesize'
# GOOGLE_APIS_TTS_URL = 'https://texttospeech.googleapis.com/v1beta1/text:synthesize'
CHARSET = 'utf-8'
DEFAULT_AUDIO_ENCODING = 'MP3'

# TTS API functions
def create_json_input(inp, voice, model):
    data = {}
    data['input'] = {}
    data['input']['text'] = inp

    data['voice'] = {}
    data['voice']['languageCode'] = voice
    # data['voice'][f'{voice}-Wavenet-B'] = voice
    # data['voice'][f'{voice}-{model}'] = voice
    data['voice']['name'] = fmt_model(voice, model)
    data['voice']['ssmlGender'] = 'FEMALE'

    data['audioConfig'] = {}
    data['audioConfig']['audioEncoding'] = DEFAULT_AUDIO_ENCODING

    json_result = json.dumps(data)
    return json_result

def fmt_model(voice, model):
    return f'{voice}-{model}'

def fmt_auth_token(token):
    return f'Bearer {token}'

def create_header():
    auth_token = fmt_auth_token(
        # 'ya29.a0Aa4xrXOUFWU9FHRD9JyC3tNMa_GiMMl6GqjDN-a-bq_uFhdEd0kwDEJYqjJBASTzchIL31Or10eKwL2EQEb437v4X0L803U1KSHKZMQpWoVv8TbB-ic8VA08EI-2jK3eXJURP80fwRgbykcIp85vaUzJlisKHRwboY7X0lPdIMqu1c4WrVh_Rdz-peBL4PeyYssTSnDpVD37k7_ttVOacylvzP4bIJvGCwKrmGm2BUVQJuGl82dUXT6t3Du08SVwE9wW-AaCgYKATASARMSFQEjDvL9hBjLrXoeCz9_k7HZ9keRKQ0269')
        # 'ya29.c.b0AXv0zTNJk1Kk-4rqtbpeNkDs2-NSXLYxwKkuTfuIfsnjbM1pe8uqt858hV0WgW_xR-ORXBdQ2n6nX_vQdbvZvpT_Ieha5ZD8hdX_oMB55vT8BwcKQ3UTNofJlhrC5MFo99fQ3Hc6PhuR3SboOTRmKH05hwuD7gi1T6GDSRvwhEu73XSxWAA7egS0H_BlauMhdWR2kOH-8Y522l5Dsj6UfkrzoO884Ms')
        # 'ya29.c.b0AXv0zTOpItrmSd66FDLYaiwjEuakFRbbGbp_YAj-NWEugxBy0VHJZKieS-9PNbgUBXn48M6HscAm0QK30jYtFKkkkxN1iqG6bxEgxEN3wh-zCgYF2yg3X2rHOoBqvwTWd4AiRDOxehS00hwvNIQPrW0pzvX4jqCl9tiYEpMqFzUz7FYoypkGMHJ8J3Uj_UCMhn3LpgRXaGFdmHo_I7iq08osbhH71hQ')
        'ya29.c.b0AXv0zTOpItrmSd66FDLYaiwjEuakFRbbGbp_YAj-NWEugxBy0VHJZKieS-9PNbgUBXn48M6HscAm0QK30jYtFKkkkxN1iqG6bxEgxEN3wh-zCgYF2yg3X2rHOoBqvwTWd4AiRDOxehS00hwvNIQPrW0pzvX4jqCl9tiYEpMqFzUz7FYoypkGMHJ8J3Uj_UCMhn3LpgRXaGFdmHo_I7iq08osbhH71hQ........................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................')
    headers = {
        # 'Authorization' : fmt_auth_token('ya29.c.b0AXv0zTNJk1Kk-4rqtbpeNkDs2-NSXLYxwKkuTfuIfsnjbM1pe8uqt858hV0WgW_xR-ORXBdQ2n6nX_vQdbvZvpT_Ieha5ZD8hdX_oMB55vT8BwcKQ3UTNofJlhrC5MFo99fQ3Hc6PhuR3SboOTRmKH05hwuD7gi1T6GDSRvwhEu73XSxWAA7egS0H_BlauMhdWR2kOH-8Y522l5Dsj6UfkrzoO884Ms'),
        # 'Authorization' : fmt_auth_token('ya29.a0Aa4xrXOUFWU9FHRD9JyC3tNMa_GiMMl6GqjDN-a-bq_uFhdEd0kwDEJYqjJBASTzchIL31Or10eKwL2EQEb437v4X0L803U1KSHKZMQpWoVv8TbB-ic8VA08EI-2jK3eXJURP80fwRgbykc'),
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

# Send reuqest
json_request = create_json_input(inp, voice, model)
print(f'Request JSON\n{json_request}')

request_headers = create_header()
print(f'Request Headers\n{request_headers}')

r = requests.post(GOOGLE_APIS_TTS_URL, json=json_request, headers=request_headers)
json_response =json.loads(r.content)
print(f'Response\n{json_response}')

if (r is None) or (r.status_code != 200):
    sys.exit(1)

# Extract data into file 
# contents: str = str(r.content.decode(CHARSET))
# contents: str = r.content.decode(CHARSET)
contents = base64.decodebytes(r.content)
# contents = r.content.decode(CHARSET)

# Write file to disk
# with open(output, 'wb') as f:
with open(output, 'w') as f:
    f.write(contents)

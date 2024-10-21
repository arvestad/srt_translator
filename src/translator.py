import argparse
import itertools as it
import json
import logging
import requests
import sys
#import openai 
import os


def llama_setup(modelname):
    '''
    Prepare/connect server and return a function to
    use for chatting.
    '''
    logging.debug(f'Setting up Llama for {modelname}')
    logging.info('Note: you must have started an "ollama" server on your computer for this model to work.')
    return lambda prompt: llama_chatbot_response(modelname, prompt)


def llama_translate_chunk(model, text, context):
    '''
    Send a translation request to have "text" translated to English,
    given some text used as context.
    '''
    url = "http://localhost:11434/api/chat"    
    logging.debug(f'Sending "{prompt}" to server, running {model}')
    message_data = {
        "model": model,
        "messages": [
            {
                "role": "tool",
                "system": "Translate to English",
                "prompt": text,
                "context": context
            }
        ],
        "stream": False
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=message_data)
    response.raise_for_status()
    return response.json()["message"]["content"]
    
                          


models = {
    'llama3.2': { 'setup': llama_setup },
#    'gpt-4o-mini': { 'setup': openai_setup},
#    'gpt-3.5-turbo': { 'setup': openai_setup}
    }
default_model = list(models.keys())[0]

def setup_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', choices=list(models.keys()), default=default_model,
                    help=f'Choose AI system to use (default: {default_model})')
    ap.add_argument('-d', '--debug', action='store_true',
                    help='Output system info for debugging purposes')
    ap.add_argument('-m', '--chunksize', default=50,
                    help='Number of subtitles (~lines) to translate at a time.')
    ap.add_argument('-n', '--contextsize', default=100,
                    help='Number of previous subtitles (~lines) to use as context for the translation request.')
    ap.add_argument('input', help='An SRT file in Swedish, that should be translated to English.')
    return ap


def read_possible_integer(h):
    '''
    Return a positive integer if there is one on the next line, or zero otherwise.
    '''
    try: 
        s = h.readline()
        number = int(s)
        if number > 0:
            return number
        else:
            return 0            # End of file
    except:
        # We must be at end of file
        return 0

def read_subtitle_lines(h):
    '''
    Read one or more lines of text, until an empty line appears.
    Then return the collected text.
    '''
    line = 'start'
    screen_line = ''            # What is show as one subtitle
    while len(line) > 1:
        line = h.readline()
        screen_line += line
    return screen_line
    
def read_timestamp(h):
    line = h.readline()
    return line

def read_srt(h):
    subtitles = list()
    timestamps = list()
    while True:
        subtitle_num = read_possible_integer(h)
        if subtitle_num == 0:
            return subtitles, timestamps
        else:
            timestamp = read_timestamp(h)
            timestamps.append(timestamp)
            subtitle = read_subtitle_lines(h)
            subtitles.append(subtitle)
    return subtitles, timestamps
            

def srt_translator(model, subtitles, context_size):
    translations = list()
    for idx, line in enumerate(subtitles):
        start = max(0, idx - context_size)
        stop = idx-1
        context_lst = subtitles[start:stop]
        context = ''.join(context_lst)
        response = llama_translate_chunk(model, line, context)

        translation = response["message"]["content"]
        translations.append(translation)
    return translations



def main():
    ap = setup_args()
    args = ap.parse_args()

    if args.debug:
        logging.basicConfig(format='# %(levelname)s %(lineno)s: %(message)s', encoding='utf-8', level=logging.DEBUG)
    else:
        logging.basicConfig(encoding='utf-8', level=logging.INFO)

    model = args.model
    logging.debug(f'Using model "{model}"')
        
    # Get the functions to use, adapted to the service
    setup = models[model]['setup']

    # Prepare to translate
    translation_server = setup(model)

    with open(args.infile) as h:
        subtitles, timestamps = read_srt(h)
        translated_subtitles = srt_translator(subtitles)
        for idx, (timestamp, subtitle) in enumerate(zip(translated_subtitles, timestamps)):
            print(f'{idx}\n{timestamp}\n{subtitle}')


if __name__ == '__main__':
    main()
    

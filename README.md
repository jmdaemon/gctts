# TTS

A TTS cli tool to query Google Cloud's Text-To-Speech API to generate audio.

## Setup

## Setup with Google Cloud Platform

First you must setup Google's TTS service with GCP for your app.

You can do that [here]().

## Initial Environment Setup


## Install

Install with pip:

``` bash
pip install gctts
```

or install the package for Arch Linux:

``` bash
sudo pacman -S python-gctts
```

## Usage

``` bash
tts -v "ja-JP" "hello" "Standard-A" "hello.mp3"
tts -v "ja-JP" "hello" "Standard-A" "hello.mp3"
# tts -v [languageCode] [input] [model] [output_file]
```

## Config

### Reducing Repeated API Calls

To reduce the number of TTS calls you have to make.
You can save output files with the same input text they were given.
For every directory in `sound_directories`, sounds will be searched for,
and if they match the current input, a request will not be sent for the input.

## Features

Potential features to add

- Default language model configurations.
    - Either add them in a subdirectory of `~/.config/tts/` or
        different configurations in the same file
    - Ability to set default:
        - `languageCode`
        - `model`
        - `audioEncoding`

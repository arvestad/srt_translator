# srt_translater

Experimental local translation of SRT files using Ollama.

The goal is to have a program that does not get tired of generating translations.

## Functionality

- I choose to relieve the AI of managing the SRT format.
  + I want to reduce computation, so in principle that is beneficial (I hope).
  + While I saw that ChatGPT manages SRT files jsut brilliantly, I had an issue
    with subtitle numbering and subtext hallucinations when restarting
    translation of a longer SRT file (> 20 minutes reading).
- I will feed 1 line for translation, while providing _n_ previous lines of context. 
  I want to ensure that the translation is synced with the original subtitles and
  no weird line-breaking affects the result.
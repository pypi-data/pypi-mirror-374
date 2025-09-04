import pyperclip
import re


def read():
    return pyperclip.paste()

def write(text):
    pyperclip.copy(text)

def clean(text):
    return " ".join(text.split().strip())

def word_count(text):
    return len(text.strip().split())

def char_count(text):
    return len(text)
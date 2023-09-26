from envparse import env
import requests

env.read_envfile('.env')

link = env('LINK')

def timing():
    return requests.get(link).json()['sleep']


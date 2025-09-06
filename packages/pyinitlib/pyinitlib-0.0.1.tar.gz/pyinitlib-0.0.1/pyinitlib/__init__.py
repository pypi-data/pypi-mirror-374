import requests
import subprocess

def Initialyze(Target: str = "Python") -> None:
    if Target.lower().strip() == "pip":
        return
    else:
        return
import os
import pyttsx3

def read_image_names():
    engine = pyttsx3.init()
    engine.setProperty('rate', 200) 
    engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_viVN_An') 

    message = f"Chào mừng bạn Thanh đến với nhà của mình."
    print(message)
    engine.say(message)
    
    engine.runAndWait()

read_image_names()
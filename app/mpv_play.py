#!/bin/env python3

from pynput.keyboard import Key, Listener
import mpv

speed=1

#quick function to change speed via keyboard.
def on_press(key):
    global speed
    
    if key.char == ']':
        speed=speed+0.1
        player.speed=speed
    if key.char == '[':
        speed=speed-0.1
        player.speed=speed
        
player = mpv.MPV()
player.play('song.mp3')

with Listener(on_press=on_press) as listener:
    listener.join()
while True:
    player.speed=speed

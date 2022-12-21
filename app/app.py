#!/bin/env python3

import sys
import gi
import os
import locale


#import mpv

import pydub
from pydub.playback import play, _play_with_simpleaudio

from threading import Thread, Event

from pynput.keyboard import Key, Listener


gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

locale.setlocale(locale.LC_NUMERIC, 'C')

class Window(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        # custom CSS provider
        self.css_provider = None

    def load_css(self, css_fn):
        print('Loading css...')
        """create a provider for custom styling"""
        if css_fn and os.path.exists(css_fn):
            #print("css_fn and os.path.exists(css_fn)")
            css_provider = Gtk.CssProvider()
            try:
                css_provider.load_from_path(css_fn)
            except GLib.Error as e:
                print(f"Error loading CSS : {e} ")
                return None
            print(f'loading custom styling : {css_fn}')
            self.css_provider = css_provider

    def _add_widget_styling(self, widget):
        if self.css_provider:
            #print("_add_widget_styling")
            context = widget.get_style_context()
            context.add_provider(
                self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def add_custom_styling(self, widget):
        self._add_widget_styling(widget)
        # iterate children recursive
        for child in widget:
            self.add_custom_styling(child)

    def create_action(self, name, callback):
        """ Add an Action and connect to a callback """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        

class MainWindow(Window):
    def __init__(self, *args, **kwargs): #### INIT FUNCTION ##########################################
        super().__init__(*args, **kwargs)

        self.set_default_size(960, 480)
        #self.connect("size-allocate", self.on_size_allocate)
        
        self.window_height = self.get_height()
        self.window_width = self.get_width()
        
        #self.connect("destroy", self.on_destroy)
        
        self.app_path = f'{os.getcwd()}/app'
        self.music_path = f'{os.path.expanduser( "~" )}/Music'
        print(self.app_path)

        #self.load_css('/app/share/musicsheep/musicsheep/styles.css') #flatpak
        #self.load_css('styles.css') #relative path
        #self.load_css('/home/svindseth/Programming/Music-Sheep/app/styles.css') #real path
        self.load_css(f'{self.app_path}/styles.css')
        

        self.headerbar = Gtk.HeaderBar(css_classes=['color_background', 'header_bar'])
        self.headerbar_label = Gtk.Label(label='Music Sheep')

        self.headerbar.set_title_widget(self.headerbar_label)
        self.set_titlebar(self.headerbar)

        self.songs_dict = {}
        self.list_items = []
        self.list_item_labels = []
        
       

        self.list_view()

        #self.speed = 1
        #self.player = mpv.MPV()
        #self.song = f'{self.app_path}/song.m4a' # mpv expects a string here, hmm
        
        self.audio_thread = 0
        self.pause_event = Event()
        self.playback = 0
        
        self.song_file = pydub.AudioSegment.from_file('/home/svindseth/Music/Julespel-Track 02.mp3')
        self.song = self.speed_change(self.song_file, 1.5)
        
        self.is_playing = False

    # END OF __init__

#    def on_size_allocate(self, widget, allocation):
#        # Get the window height
#        window_height = self.get_allocated_height()
#        print(f'Window height: {window_height} pixels')

    def list_view(self):
    
        # MAIN LAYOUT
        self.main_layout_box = Gtk.CenterBox(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, vexpand=True, css_classes=['color_background', 'main_layout_box'])
        self.list_view_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True, css_classes=['list_view_box'])
        self.controls_view_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True, css_classes=['controls_view_box'])
        self.main_layout_separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL, vexpand=True)
        
        self.bottom_box = Gtk.CenterBox(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, vexpand=False, valign=Gtk.Align.END, css_classes=['color_background', 'bottom_box'])
        
        # PLAY CONTROLS
        self.controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True, hexpand=True, valign=Gtk.Align.CENTER, halign=Gtk.Align.CENTER, spacing=30)
        self.controls_art_frame = Gtk.Frame(margin_top=30, margin_start=10, margin_end=10, valign=Gtk.Align.CENTER, width_request=192, height_request=192, css_classes=['album_art_frame', 'drop_shadow'])
        self._add_widget_styling(self.controls_art_frame)
        self.controls_art = Gtk.Image(file=f'{self.app_path}/art_2.png', valign=Gtk.Align.CENTER, height_request=200, css_classes=['album_art', 'img'])
        self._add_widget_styling(self.controls_art)
        self.controls_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, margin_bottom=30, margin_start=10, margin_end=10, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, spacing=30, hexpand=True, css_classes=['play_controls', 'controls_box'])
        
        #self.controls_view_grid = Gtk.Grid(hexpand=True, vexpand=True)
        #self.controls_view_grid.insert_column(0)
        #self.controls_view_grid.insert_column(1)
        #self.controls_view_grid.insert_column(2)
        #self.controls_view_grid.insert_row(0)
        #self.controls_view_grid.insert_row(1)
        
        
        # PLAY BUTTON
        self.controls_play_button = Gtk.Button(has_frame=True, width_request=60, height_request=60, css_classes=['controls_play'])
        self.controls_play_icon_play = Gtk.Image(icon_name='media-playback-start-symbolic')
        self.controls_play_icon_pause = Gtk.Image(icon_name='media-playback-pause-symbolic')
        #self.controls_play_icon_play = Gtk.Image(icon_name='media-playback-start-symbolic')
        self.controls_play_button.set_child(self.controls_play_icon_play)
        self._add_widget_styling(self.controls_play_button)
        self.controls_play_button.connect('clicked', lambda controls_play_button: self.play_button())
        
        
        self.controls_prev_button = Gtk.Button(has_frame=True, width_request=40, height_request=40, margin_top=10, margin_bottom=10, css_classes=['controls_prev'])
        self.controls_prev_icon_play = Gtk.Image(icon_name='go-previous-symbolic')
        self.controls_prev_button.set_child(self.controls_prev_icon_play)
        self._add_widget_styling(self.controls_prev_button)
        self.controls_prev_button.connect('clicked', lambda _: self.speed_slower())
        
        self.controls_next_button = Gtk.Button(has_frame=True, width_request=40, height_request=40, margin_top=10, margin_bottom=10, css_classes=['controls_next'])
        self.controls_next_icon_play = Gtk.Image(icon_name='go-next-symbolic')
        self.controls_next_button.set_child(self.controls_next_icon_play)
        self._add_widget_styling(self.controls_next_button)
        self.controls_next_button.connect('clicked', lambda _: self.speed_faster())
        
        self.controls_controls.append(self.controls_prev_button)
        self.controls_controls.append(self.controls_play_button)
        self.controls_controls.append(self.controls_next_button)


        # SONG LIST
        self.list_view_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True, valign=Gtk.Align.START)
        self.list_view_frame = Gtk.ScrolledWindow(margin_start=10, margin_end=10, margin_top=10, margin_bottom=10, vexpand=True, vexpand_set=True, propagate_natural_height=True, propagate_natural_width=True, hscrollbar_policy=Gtk.PolicyType.EXTERNAL, has_frame=True)
        self.list_view_list = Gtk.ListBox(vexpand=True)

        self.set_child(self.main_layout_box)

        self.list_view_frame.set_child(self.list_view_list)
        self.list_view_box.append(self.list_view_frame)
        
        self.main_layout_box.set_start_widget(self.controls_view_box)
        self.main_layout_box.set_center_widget(self.main_layout_separator)
        self.main_layout_box.set_end_widget(self.list_view_box)

        #self.bottom_box.set_center_widget(self.controls_play_button)
        #self.headerbar.pack_end(self.controls_box)
        #self.main_layout_box.append(self.bottom_box)
        
        self.controls_view_box.append(self.controls_box)
        self.controls_box.append(self.controls_art_frame)
        self.controls_box.append(self.controls_controls)
        self.controls_art_frame.set_child(self.controls_art)
        #self.controls_view_box.append(self.controls_view_grid)
        #self.controls_view_grid.attach(self.controls_box, 1, 1, 30, 80)

        self._add_widget_styling(self.headerbar)
        self._add_widget_styling(self.main_layout_box)
        self._add_widget_styling(self.bottom_box)
        self._add_widget_styling(self.list_view_frame)
        self._add_widget_styling(self.controls_view_box)
        self._add_widget_styling(self.list_view_box)
        self._add_widget_styling(self.list_view_list)


        self.list_song_files(self.songs_dict) # list the files in ~/Music
        #print(self.songs_dict)
        
        
        #for i in range(len(self.songs_dict)):
        for i, file in enumerate(self.songs_dict.values()):
            
            list_item_label = Gtk.Label(label=f'{i + 1} - {file}', halign=Gtk.Align.START, margin_start=2)
            self.list_item_labels.append(list_item_label)
            
            list_item_button = Gtk.Button(child=list_item_label)
            list_item_button.connect('clicked', lambda _, index=i: self.load_song(self.songs_dict[index]))
            
            list_item = Gtk.ListBoxRow(child=list_item_button)
            self._add_widget_styling(list_item)
            list_item.activatable = True
            
            
            #list_item.connect('click', lambda _, index=i: self.load_song(self.songs_dict[index]))
            
            self.list_items.append(list_item)

#        for i in range(10):
#            list_item_label = Gtk.Label(label=f'Song no {i + 1}')
#            self.list_item_labels.append(list_item_label)
#            list_item = Gtk.ListBoxRow(child=list_item_label)
#            self._add_widget_styling(list_item)
#            list_item.activatable = True
#            list_item.connect('activate', lambda list_item: self.load_song(self.song)) #temporary implementation
#            self.list_items.append(list_item)
            

        for i in range(len(self.list_items)):
            self.list_view_list.append(self.list_items[i])
            
        self.list_song_files(self.songs_dict) # list the files in ~/Music
        #print(self.songs_dict)

    # END OF list_view
    
    def controls_view(self):
        pass
    
    # END OF controls_view

    def list_song_files(self, songs_dict):
        # Set the directory you want to list
        #directory = '/home/svindseth/Music'
        directory = self.music_path

        # Use os.listdir to list all the files in the directory
        files = os.listdir(directory)

        # Iterate through the files and add only the music tracks to songs_dict
        index = -1 # No idea why this needs to be -1 and not 0
        for i, file in enumerate(files):
            if file.endswith('.mp3') or file.endswith('.flac') or file.endswith('.m4a') or file.endswith('.opus') or file.endswith('.ogg') or file.endswith('.wav'):
                index = index + 1
                songs_dict[index] = file # add to dict
        


    # END OF list_song_files
    
    def load_playlist(self, playlist):
        pass

    # END OF load_playlist
    
    def load_song(self, song):
        print(song)
        self.song = f'/home/svindseth/Music/{song}'
        self.is_playing = True
        self.controls_play_button.set_child(self.controls_play_icon_pause)
        
        #Thread(target=self.play_song(f'/home/svindseth/Music/{song}')).start()
        
        _song = pydub.AudioSegment.from_file(self.song)
        _song = self.speed_change(_song, 0.85)
        self.playback = _play_with_simpleaudio(_song)
        
        #self.audio_thread = Thread(target=self.song_thread_func)
        #self.audio_thread.start()
        
    def song_thread_func(self):
        while True:
            self.pause_event.wait() # wait for start signal
            
            self.is_playing = True
            song = pydub.AudioSegment.from_file(self.song)
            song = self.speed_change(song, 0.85) # speed modifier here <---
            play(song)
            #_play_with_simpleaudio(song)
            
            self.is_playing = False
            self.pause_event.clear() # pause thread again
         
    
    def play_button(self):
        
        if self.is_playing == True:
            self.pause_song()
            self.controls_play_button.set_child(self.controls_play_icon_play)
        else:
            self.play_song()
            self.controls_play_button.set_child(self.controls_play_icon_pause)
    
    def play_song(self):
        self.is_playing = True
        self.playback.resume()
    
    def pause_song(self):
        self.is_playing = False
        self.playback.stop()
        
    def speed_change(self, sound, speed=1.0):
        # Manually override the frame_rate. This tells the computer how many
        # samples to play per second
        sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * speed)})
        # convert the sound with altered frame rate to a standard frame rate
        # so that regular playback programs will work right. They often only
        # know how to play audio at standard frame rate (like 44.1k)
        return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)
        
    def speed_slower(self):
        self.speed = self.speed - 0.1
        self.player.speed = self.speed 
        
    def speed_faster(self):
        self.speed = self.speed + 0.1
        self.player.speed = self.speed 
        
        
        
    # TESTING of THREADING
    def on_play_button_clicked(self):
        # Start a new thread to play the song
        Thread(target=self.play_song).start()
      


# END OF MainWindow

class Song():
    def __init__(self, file):
        print(f'Selected song {file}')
        self.file = file
        self.is_playing = False
        
# END OF Song



class SheepApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


app = SheepApp(application_id="net.svindseth.MusicSheep")
app.run(sys.argv)



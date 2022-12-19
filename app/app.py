#!/bin/env python3

import sys
import gi
import os
import mpv

print(sys.path)

# from pynput.keyboard import Key, Listener


gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(960, 480)

        self.load_css('/app/share/musicsheep/musicsheep/styles.css')

        self.headerbar = Gtk.HeaderBar(css_classes=['color_background', 'header_bar'])
        self.headerbar_label = Gtk.Label(label='Music Sheep')

        self.headerbar.set_title_widget(self.headerbar_label)
        self.set_titlebar(self.headerbar)

       
        self.list_items = []
        self.list_item_labels = []
        
        self.song = Song('')

        self.list_view()


    # END OF __init__
    

    def list_view(self):
        self.main_layout_box = Gtk.CenterBox(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, vexpand=True, css_classes=['color_background', 'main_layout_box'])
        self.list_view_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True, css_classes=['list_view_box'])
        self.controls_view_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True, css_classes=['controls_view_box'])
        self.main_layout_separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL, vexpand=True)
        
        self.bottom_box = Gtk.CenterBox(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, vexpand=False, valign=Gtk.Align.END, css_classes=['color_background', 'bottom_box'])
                
        self.controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True, hexpand=True, valign=Gtk.Align.CENTER, halign=Gtk.Align.CENTER, spacing=30)
        self.controls_art_frame = Gtk.Frame(margin_top=30, margin_start=10, margin_end=10, valign=Gtk.Align.CENTER, width_request=192, height_request=192, css_classes=['album_art_frame', 'drop_shadow'])
        self._add_widget_styling(self.controls_art_frame)
        self.controls_art = Gtk.Image(file='/app/share/musicsheep/musicsheep/art.png', valign=Gtk.Align.CENTER, height_request=200, css_classes=['album_art', 'img'])
        self._add_widget_styling(self.controls_art)
        self.controls_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, margin_bottom=30, margin_start=10, margin_end=10, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, spacing=30, hexpand=True, css_classes=['play_controls', 'controls_box'])
        
        #self.controls_view_grid = Gtk.Grid(hexpand=True, vexpand=True)
        #self.controls_view_grid.insert_column(0)
        #self.controls_view_grid.insert_column(1)
        #self.controls_view_grid.insert_column(2)
        #self.controls_view_grid.insert_row(0)
        #self.controls_view_grid.insert_row(1)
        
        self.controls_play_button = Gtk.Button(has_frame=True, width_request=60, height_request=60, css_classes=['controls_play'])
        self.controls_play_icon_play = Gtk.Image(icon_name='media-playback-start-symbolic')
        self.controls_play_button.set_child(self.controls_play_icon_play)
        self._add_widget_styling(self.controls_play_button)
        
        self.controls_prev_button = Gtk.Button(has_frame=True, width_request=40, height_request=40, margin_top=10, margin_bottom=10, css_classes=['controls_prev'])
        self.controls_prev_icon_play = Gtk.Image(icon_name='go-previous-symbolic')
        self.controls_prev_button.set_child(self.controls_prev_icon_play)
        self._add_widget_styling(self.controls_prev_button)
        
        self.controls_next_button = Gtk.Button(has_frame=True, width_request=40, height_request=40, margin_top=10, margin_bottom=10, css_classes=['controls_next'])
        self.controls_next_icon_play = Gtk.Image(icon_name='go-next-symbolic')
        self.controls_next_button.set_child(self.controls_next_icon_play)
        self._add_widget_styling(self.controls_next_button)
        
        self.controls_controls.append(self.controls_prev_button)
        self.controls_controls.append(self.controls_play_button)
        self.controls_controls.append(self.controls_next_button)

        self.list_view_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True, valign=Gtk.Align.START)
        self.list_view_frame = Gtk.Frame(margin_start=10, margin_end=10, margin_top=10, margin_bottom=10, vexpand=True)
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


        for i in range(10):
            list_item_label = Gtk.Label(label=f'Song no {i + 1}')
            self.list_item_labels.append(list_item_label)
            list_item = Gtk.ListBoxRow(child=list_item_label)
            self._add_widget_styling(list_item)
            self.list_items.append(list_item)

        for i in range(len(self.list_items)):
            self.list_view_list.append(self.list_items[i])

    # END OF list_view
    
    def controls_view(self):
        pass
    
    # END OF controls_view

    def list_song_files(self):
        pass

    # END OF list_song_files
    
    def load_playlist(self, playlist):
        pass

    # END OF load_playlist
    
    def load_song(self, song):
        pass
    
    def play_song(self):
        pass
    
    def pause_song(self):
        pass

    def load_css(self, css_fn):
        """create a provider for custom styling"""
        if css_fn and os.path.exists(css_fn):
            css_provider = Gtk.CssProvider()
            try:
                css_provider.load_from_path(css_fn)
            except GLib.Error as e:
                print(f"Error loading CSS : {e} ")
                return None
            print(f'loading custom styling : {css_fn}')
            self.css_provider = css_provider

    # END OF load_css

    def _add_widget_styling(self, widget):
        if self.css_provider:
            context = widget.get_style_context()
            context.add_provider(
                self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    # END OF _add_widget_styling
# END OF MainWindow

class Song():
    def __init__(self, file):
        print(f'Selected song {file}')
        self.file = file
        self.is_playing = False
        
# END OF Song

#class MyApp(Adw.Application):
#    def __init__(self, **kwargs):
#        super().__init__(**kwargs)
#        self.connect('activate', self.on_activate)
#
#    def on_activate(self, app):
#        self.win = MainWindow(application=app)
#        self.win.present()
#
#
#app = MyApp(application_id="net.svindseth.MusicSheep")
#app.run(sys.argv)

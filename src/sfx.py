"""
File Name: sfx.py
Module: src
Function: Define the SFX class used to manage the sound and music system through its methods.
Inputs: None.
Outputs: None.
Authors:
    Blake Carlson
    Logan Smith
    Jack Bauer
    Nifemi Lawal
    Dellie Wright
Creation Date: 9/29/2025

NOTE: All code in the file was authored by 1 or more of the authors. No outside sources were used for code
"""

from pygame import mixer # import pygame's audio system
import pygame # import pygame
import os # import os for path related tools
import random # so we can randomly select a song to play 


class SFX:
    def __init__(self, sound_dir):
        # Use a try-except block so that if there are any initialization errors (such as in the case the host lacks
        # an audio driver) the program won't crash. Instead, we appropriately set the "enabled" flag to disable 
        # the SFX system. 
        try: 
            # Create channel strictly for sound effects and music
            self.sound_dir = sound_dir
            mixer.init()
            
            self.sfx_channel = mixer.Channel(0)
            self.music_channel = mixer.Channel(1)
            mixer.set_reserved(1) # Ensure nothing else can play on music channel
            
            # Set channel volumes
            self.sfx_channel.set_volume(0.3)
            self.music_channel.set_volume(0.1)

            # Choose random background music from directory, create song name for printing
            background_music_choice = random.choice(os.listdir(os.path.join(sound_dir, "bgmusic")))
            print(f"{os.path.join(sound_dir, 'bgmusic', background_music_choice)}")
            self.background_music = mixer.Sound(os.path.join(sound_dir, "bgmusic", background_music_choice))
            music_choice = background_music_choice[:background_music_choice.index('-')].replace("_"," ")
            music_choice = ''.join([i for i in music_choice if not i.isdigit()])
            self.song_name = music_choice[1:]

            # Create pygame sound objects for music and game sounds
            self.bomb_clicked_sound = mixer.Sound(os.path.join(sound_dir,"bomb-clicked.mp3"))
            self.flag_placed_sound = mixer.Sound(os.path.join(sound_dir,"flag-placed.mp3"))
            self.loss_sound = mixer.Sound(os.path.join(sound_dir,"loss.mp3"))
            self.win_sound = mixer.Sound(os.path.join(sound_dir,"win.mp3"))
            self.square_revealed_sound = mixer.Sound(os.path.join(sound_dir,"square-revealed.mp3"))
            self.flagg_popped_sound = mixer.Sound(os.path.join(sound_dir, "flag-popped.mp3"))


            self.muted = False
            self.enabled = True            
        except:
            self.enabled = False

    def stop_sfx(self):
        # Stop any sounds from being played
        if self.enabled:
            self.sfx_channel.stop()

    def ensure_bgmusic(self):
        # Use short circuit evaluation to ensure that we are enabled before we call any SFX methods
        if self.enabled and not self.music_channel.get_busy():
                self.start_bgmusic()

    def play_flag_placed(self):
        # Play flag placed sound
        if self.enabled:
            self.sfx_channel.play(self.flag_placed_sound)
    def play_bomb_clicked(self):
        # Play bomb clicked sound
        if self.enabled:
            self.sfx_channel.play(self.bomb_clicked_sound)
    def play_win(self):
        # Play win sound
        if self.enabled:
            self.sfx_channel.play(self.win_sound)
    def play_loss(self):
        # Play loss sound
        if self.enabled:
            self.sfx_channel.play(self.loss_sound)
    def play_square_revealed(self):
        # Play revealed sound
        if self.enabled:
            self.sfx_channel.play(self.square_revealed_sound)
    def play_flag_popped(self):
        # Play popped sound
        if self.enabled:
            self.sfx_channel.play(self.flagg_popped_sound)
    def start_bgmusic(self):
        # Start background music
        if self.enabled:
            self.music_channel.play(self.background_music, loops=-1)

    def change_song(self):
        if not self.enabled:
            return
        # Stop music before change
        self.music_channel.stop()
        choice =None
        background_music_choice =None

        # Loop until we find a song that isn't the current one
        while choice == self.song_name or choice is None: 
            background_music_choice = random.choice(os.listdir(os.path.join(self.sound_dir, "bgmusic")))
            music_choice = background_music_choice[:background_music_choice.index('-')].replace("_"," ")
            music_choice = ''.join([i for i in music_choice if not i.isdigit()])
            choice = music_choice[1:]

        # Update music choice and play song
        self.background_music = mixer.Sound(os.path.join(self.sound_dir, "bgmusic", background_music_choice))
        self.song_name = choice
        self.start_bgmusic()


    def draw_sfx_info(self, surface, WIDTH, HEIGHT, WHITE, tiny_font):
        if not self.enabled:
            return
        # Panel geometry (bottom-center)
        panel_w, panel_h = WIDTH // 4, WIDTH // 6 
        panel_x = WIDTH - panel_w 
        panel_y = HEIGHT - panel_h - 200

        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        # Background + border (rounded corners)
        pygame.draw.rect(surface, (45, 45, 45), panel_rect, border_radius=12)
        pygame.draw.rect(surface, WHITE, panel_rect, 2, border_radius=12)

        # Title
        title = "Now Playing an 8-bit Version of:"
        title_surf = tiny_font.render(title, True, WHITE)
        surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2,
                                  panel_rect.top + 15))

        # Current song name
        msg = sfx.song_name
        title_surf = tiny_font.render(msg, True, WHITE)
        surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2,
                                  panel_rect.top + 30))

        # Album Info
        msg = "- A Kind Of Blue - Miles Davis"
        title_surf = tiny_font.render(msg, True, WHITE)
        surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2,
                                  panel_rect.top + 45))
        # Setting button coordinates
        pad = 1
        btn_w, btn_h = 100, 44
        btn_x = panel_rect.right - pad - btn_w
        btn_y = panel_rect.bottom - pad - btn_h 

        # Drawing buttons
        mute_button.rect.topleft = (btn_x, btn_y)
        mute_button.draw(surface, tiny_font)
        skip_button.rect.topleft = (btn_x - btn_w - 5, btn_y)
        skip_button.draw(surface, tiny_font)



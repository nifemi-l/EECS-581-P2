from pygame import mixer
import os
import random
from settings import ASSETS_DIR, NUM_DIR, SOUND_DIR 


class SFX:
    def __init__(self):
        self.sfx_channel = mixer.Channel(0)
        self.music_channel = mixer.Channel(1)

        background_music_choice = random.choice(os.listdir(os.path.join(SOUND_DIR, "bgmusic")))
        print(f"{os.path.join(SOUND_DIR, "bgmusic", background_music_choice)}")
        self.background_music = mixer.Sound(os.path.join(SOUND_DIR, "bgmusic", background_music_choice))

        self.bomb_clicked_sound = mixer.Sound(os.path.join(SOUND_DIR,"bomb-clicked.mp3"))
        self.flag_placed_sound = mixer.Sound(os.path.join(SOUND_DIR,"flag-placed.mp3"))
        self.loss_sound = mixer.Sound(os.path.join(SOUND_DIR,"loss.mp3"))
        self.win_sound = mixer.Sound(os.path.join(SOUND_DIR,"win.mp3"))
        self.square_revealed_sound = mixer.Sound(os.path.join(SOUND_DIR,"square-revealed.mp3"))
        self.flagg_popped_sound = mixer.Sound(os.path.join(SOUND_DIR, "flag-popped.mp3"))

    def play_flag_placed(self):
        self.sfx_channel.play(self.flag_placed_sound)
    def play_bomb_clicked(self):
        self.sfx_channel.play(self.bomb_clicked_sound)
    def play_win(self):
        self.sfx_channel.play(self.win_sound)
    def play_loss(self):
        self.sfx_channel.play(self.loss_sound)
    def play_square_revealed(self):
        self.sfx_channel.play(self.square_revealed_sound)
    def play_flag_popped(self):
        self.sfx_channel.play(self.flagg_popped_sound)
    def start_bgmusic(self):
        self.music_channel.play(self.background_music)

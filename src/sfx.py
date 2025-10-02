from pygame import mixer
import os
import random


class SFX:
    def __init__(self, sound_dir):
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
        if self.enabled:
            self.sfx_channel.stop()

    def ensure_bgmusic(self):
        # Use short circuit evaluation to ensure that we are enabled before we call any SFX methods
        if self.enabled and not self.music_channel.get_busy():
                self.start_bgmusic()

    def play_flag_placed(self):
        if self.enabled:
            self.sfx_channel.play(self.flag_placed_sound)
    def play_bomb_clicked(self):
        if self.enabled:
            self.sfx_channel.play(self.bomb_clicked_sound)
    def play_win(self):
        if self.enabled:
            self.sfx_channel.play(self.win_sound)
    def play_loss(self):
        if self.enabled:
            self.sfx_channel.play(self.loss_sound)
    def play_square_revealed(self):
        if self.enabled:
            self.sfx_channel.play(self.square_revealed_sound)
    def play_flag_popped(self):
        if self.enabled:
            self.sfx_channel.play(self.flagg_popped_sound)
    def start_bgmusic(self):
        if self.enabled:
            self.music_channel.play(self.background_music, loops=-1)
    def change_song(self):
        choice = ""
        background_music_choice = ""
        while choice is not self.song_name: 
            background_music_choice = random.choice(os.listdir(os.path.join(self.sound_dir, "bgmusic")))
            music_choice = background_music_choice[:background_music_choice.index('-')].replace("_"," ")
            music_choice = ''.join([i for i in music_choice if not i.isdigit()])
            choice = music_choice[1:]
        self.background_music = mixer.Sound(os.path.join(self.sound_dir, background_music_choice))
        self.music_channel.stop()
        self.music_channel.play(self.background_music, loops=-1)



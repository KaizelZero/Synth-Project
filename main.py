import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the Pygame window
size = (800, 400)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Two-Sound Synthesizer")

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = "#14213d"
light_gray = (230, 230, 230)

# Frequencies for each note
frequencies = {
    pygame.K_a: 523.25,  # C5
    pygame.K_s: 587.33,  # D5
    pygame.K_d: 659.25,  # E5
    pygame.K_f: 698.46,  # F5
    pygame.K_g: 783.99,  # G5
    pygame.K_h: 880.00,  # A5
    pygame.K_j: 987.77   # B5
}

pygame.mixer.init()
channels = {key: pygame.mixer.Channel(i) for i, key in enumerate(frequencies)}


sampling_rate = 44100
duration = 10.0

def generate_wave(freq, wave_type='sine'):
    t = np.linspace(0, duration, int(sampling_rate * duration), False)

    if wave_type == 'sine':
        wave = 20000 * np.sin(freq * 2 * np.pi * t)
    elif wave_type == 'square':
        wave = 20000 * np.sign(np.sin(freq * 2 * np.pi * t))

    # Apply fade-in and fade-out
    fade_in_time = 0.01  # in seconds
    fade_out_time = 0.01  # in seconds

    fade_in_samples = int(sampling_rate * fade_in_time)
    fade_out_samples = int(sampling_rate * fade_out_time)

    fade_in = np.linspace(0, 1, fade_in_samples)
    fade_out = np.linspace(1, 0, fade_out_samples)

    wave[:fade_in_samples] *= fade_in
    wave[-fade_out_samples:] *= fade_out

    return pygame.mixer.Sound(wave.astype('int16'))


waves = {
    key: {
        'sine': generate_wave(freq, wave_type='sine'),
        'square': generate_wave(freq, wave_type='square')
    }
    for key, freq in frequencies.items()
}

current_wave_type = 'sine'

class Key:
    def __init__(self, name, key_code, color, x, y, width, height):
        self.name = name
        self.key_code = key_code
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def render(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont('Calibri', 20, True, False)
        text = font.render(self.name, True, black)
        surface.blit(text, (self.x + 15, self.y + 150))
        text = font.render(pygame.key.name(self.key_code), True, black)
        surface.blit(text, (self.x + 15, self.y + 170))

    def highlight_key(self, highlight):
        self.color = light_gray if highlight else white

    def is_inside(self, x, y):
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

# Toggle wave type
toggle_size = (50, 50)
toggle_color = (200, 200, 200)
toggle_text = 'Sine'
toggle_font = pygame.font.SysFont('Calibri', 20, True, False)
toggle_text_surface = toggle_font.render(toggle_text, True, white)
toggle_text_x = 50 + (toggle_size[0] - toggle_text_surface.get_width()) / 2
toggle_text_y = 50 + (toggle_size[1] - toggle_text_surface.get_height()) / 2

def create_keys():
    key_size = (50, 200)
    key_spacing = 10
    key_start_x = 50
    key_start_y = 50
    key_names = ['C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B5']
    key_codes = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_j]

    keys = []
    for i in range(len(key_names)):
        x = key_start_x + (key_size[0] + key_spacing) * i
        y = key_start_y
        key = Key(key_names[i], key_codes[i], white, x, y, key_size[0], key_size[1])
        keys.append(key)

    return keys

keys = create_keys()

def main():
    sustain_duration = 300  # in milliseconds (300ms in this case)

    global current_wave_type

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_wave_type = 'square' if current_wave_type == 'sine' else 'sine'

                if event.key in waves:
                    channels[event.key].stop()
                    channels[event.key].play(waves[event.key][current_wave_type])
                    for key in keys:
                        if key.key_code == event.key:
                            key.highlight_key(True)
                
            if event.type == pygame.KEYUP:
                for key in keys:
                    if key.key_code == event.key:
                        key.highlight_key(False)
                        # Sustain the sound for a bit
                        channels[event.key].fadeout(sustain_duration)

        screen.fill(gray)

        # Draw toggle indicator
        toggle_x = 700
        toggle_y = 50

        if current_wave_type == 'sine':
            toggle_text = 'Sine'
            # Change channel volumes
            for channel in channels.values():
                channel.set_volume(1.0)
        else:
            toggle_text = 'Square'
            # Change channel volumes
            for channel in channels.values():
                channel.set_volume(0.3)
        toggle_font = pygame.font.SysFont('Calibri', 20, True, False)
        toggle_text_surface = toggle_font.render(toggle_text, True, white)
        screen.blit(toggle_text_surface, (toggle_x, toggle_y))

        for key in keys:
            key.render(screen)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()

import pygame
import numpy as np
import os

# Initialize Pygame
pygame.init()

# Set up the Pygame window
size = (570, 450)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Two-Sound Synthesizer")

# Define colors
WHITE, BLACK, BACKGROUND, LIGHT_GRAY = (
    255, 255, 255), (0, 0, 0), "#14213d", (230, 230, 230)

# Define frequencies for each key
frequencies = {
    pygame.K_a: 523.25,  # C5
    pygame.K_s: 587.33,  # D5
    pygame.K_d: 659.25,  # E5
    pygame.K_f: 698.46,  # F5
    pygame.K_g: 783.99,  # G5
    pygame.K_h: 880.00,  # A5
    pygame.K_j: 987.77,   # B5
    pygame.K_k: 1046.50  # C6
}

# Initialize Pygame mixer and create sounds
pygame.mixer.init()
channels = {key: pygame.mixer.Channel(i) for i, key in enumerate(frequencies)}

# Set up variables for the wave generator
sampling_rate = 44100
duration = 10.0
    

# Generate a sine wave with a given frequency and duration
# Default wave type is sine wave
def generate_wave(freq, wave_type='sine'):
    # t is an array of time values, spaced according to the sampling rate and duration
    t = np.linspace(0, duration, int(sampling_rate * duration), False)

    # Generate a sine wave or a square wave, depending on the wave_type parameter
    if wave_type == 'sine':
        wave = 20000 * np.sin(freq * 2 * np.pi * t)
    elif wave_type == 'square':
        wave = 20000 * np.sign(np.sin(freq * 2 * np.pi * t))

    # Apply a fade in and fade out to the waveform to avoid abrupt starts and ends
    fade_in_samples = int(sampling_rate * 0.01)
    fade_out_samples = int(sampling_rate * 0.01)
    wave[:fade_in_samples] *= np.linspace(0, .05, fade_in_samples)
    wave[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples)

    # Convert the waveform to a Pygame sound object and return it
    return pygame.mixer.Sound(wave.astype('int16'))


# Create a dictionary of waveforms using the generate_wave function
waves = {
    # For each note/frequency in the frequencies dictionary (assumed to be defined elsewhere in the code)
    key: {'sine': generate_wave(freq, 'sine'),  # generate a sine wave
          'square': generate_wave(freq, 'square')}  # generate a square wave
    # for each key, value pair in the frequencies dictionary
    for key, freq in frequencies.items()
}

# Set the default wave type to sine
current_wave_type = 'sine'


# Define a class for representing a piano key
class Key:
    def __init__(self, name, key_code, color, x, y, width, height):
        # Initialize the attributes of the key
        self.name, self.key_code, self.color = name, key_code, color
        self.x, self.y, self.width, self.height = x, y, width, height

    def render(self, surface):
        # Draw the key on the surface using the pygame draw.rect function
        pygame.draw.rect(surface, self.color,
                         (self.x, self.y + 100, self.width, self.height))
        # Add labels for the key name and corresponding keyboard key using the pygame blit function
        font = pygame.font.SysFont('Calibri', 20, True, False)
        for i, text in enumerate([self.name, pygame.key.name(self.key_code)]):
            surface.blit(font.render(text, True, BLACK),
                         (self.x + 15, self.y + 250 + 20 * i))

    def highlight_key(self, highlight):
        # Change the color of the key to LIGHT_GRAY if highlight is True, or WHITE otherwise
        self.color = LIGHT_GRAY if highlight else WHITE

    # Deprecated
    def is_inside(self, x, y):
        # Check if the given x and y coordinates are within the bounds of the key and shift the y coordinate by 100 pixels
        return self.x <= x <= self.x + self.width and self.y + 100 <= y <= self.y + 100 + self.height
    
    def get_frequency(self):
        # Get the frequency of the key from the frequencies dictionary
        return frequencies[self.key_code]


# Define a function to create piano keys
def create_keys():
    # Set the size of each key, the spacing between keys, and the starting position of the first key
    key_size, key_spacing, key_start_x, key_start_y = (50, 200), 10, 50, 50
    # Define the names and keyboard key codes of each key
    key_names = ['C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B5', 'C6']
    key_codes = [pygame.K_a, pygame.K_s, pygame.K_d,
                 pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_j, pygame.K_k]
    # Create a list of Key objects using a list comprehension
    return [
        # Create a Key object for each key using its name, keyboard key code, color, and position and size on the screen
        Key(key_names[i], key_codes[i], WHITE, key_start_x +
            (key_size[0] + key_spacing) * i, key_start_y, *key_size)
        for i in range(len(key_names))
    ]


# Call the create_keys function to create a list of piano keys
keys = create_keys()


# Main function
def main():
    sustain_duration = 300  # in milliseconds (300ms in this case)
    frequency_display = None

    global current_wave_type

    #  Main loop
    running = True
    while running:
        # Check for events
        for event in pygame.event.get():
            # If the user clicks the close button, stop the loop
            if event.type == pygame.QUIT:
                running = False

            # If the user presses a key
            if event.type == pygame.KEYDOWN:
                # If the key is the space bar, toggle the wave type
                if event.key == pygame.K_SPACE:
                    # Stop all currently playing sounds
                    for audio in channels.values():
                        audio.stop()
                    # Toggle the wave type
                    current_wave_type = 'square' if current_wave_type == 'sine' else 'sine'

                # If the key is a valid piano key, play the corrosponding note
                if event.key in waves:
                    channels[event.key].stop()
                    channels[event.key].play(
                        waves[event.key][current_wave_type])
                    for key in keys:
                        if key.key_code == event.key:
                            key.highlight_key(True)
                            frequency_display = key.get_frequency()

            # If the user releases a key, stop playing the note after the sustain duration
            if event.type == pygame.KEYUP:
                for key in keys:
                    if key.key_code == event.key:
                        key.highlight_key(False)
                        channels[event.key].fadeout(sustain_duration)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for key in keys:
                    if key.is_inside(mouse_x, mouse_y):
                        channels[key.key_code].stop()
                        channels[key.key_code].play(
                            waves[key.key_code][current_wave_type])
                        key.highlight_key(True)
                        frequency_display = key.get_frequency()

            if event.type == pygame.MOUSEBUTTONUP:
                for key in keys:
                    key.highlight_key(False)
                    channels[key.key_code].fadeout(sustain_duration)

        # Fill the screen with a dark color
        screen.fill(BACKGROUND)

        # Draw toggle indicator
        toggle_x, toggle_y = 50, 400

        # Wave type indicator
        if current_wave_type == 'sine':
            toggle_text = 'Sine'
            for channel in channels.values():
                channel.set_volume(0.1)
        else:
            toggle_text = 'Square'
            for channel in channels.values():
                channel.set_volume(0.04)

        # Draw the wave type on the screen
        toggle_font = pygame.font.SysFont('Calibri', 20, True, False)
        toggle_text_surface = toggle_font.render(toggle_text, True, WHITE)
        screen.blit(toggle_text_surface, (toggle_x, toggle_y))

        # Draw the instructions on the screen
        toggle_font = pygame.font.SysFont('Calibri', 20, True, False)
        toggle_text_surface = toggle_font.render(
            "Space - Toggle Wave Type", True, WHITE)
        screen.blit(toggle_text_surface, (toggle_x, toggle_y - 20))

        # Draw title at the top of the screen
        font_path = os.path.join("fonts", "beon-webfont.ttf")
        title_font = pygame.font.Font(font_path, 60)

        title_text_surface = title_font.render(
            "Software", True, WHITE)
        screen.blit(title_text_surface, (50, 10))
        title_text_surface = title_font.render(
            "Synthesizer", True, WHITE)
        screen.blit(title_text_surface, (50, 65))

        # Draw the keys on the screen
        for key in keys:
            key.render(screen)

        # Draw the frequency on the bottom right
        if frequency_display:
            frequency_font = pygame.font.SysFont('Calibri', 20, True, False)
            frequency_text_surface = frequency_font.render(
                "Frequency: {:.2f} Hz".format(frequency_display), True, WHITE)
            frequency_x = size[0] - frequency_text_surface.get_width() - 10
            frequency_y = size[1] - frequency_text_surface.get_height() - 10
            screen.blit(frequency_text_surface, (frequency_x, frequency_y))

        # Update the display
        pygame.display.update()

    # Quit the program
    pygame.quit()


# Call the main function
if __name__ == "__main__":
    main()

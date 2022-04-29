import pygame, cv2, random, os

class Tile(pygame.sprite.Sprite):
    def __init__(self, filename, x, y):
        super().__init__()

        self.name = filename.split('.')[0]

        self.original_image = pygame.image.load('images/planets/' + filename)

        self.back_image = pygame.image.load('images/planets/' + filename)
        pygame.draw.rect(self.back_image, WHITE, self.back_image.get_rect())

        self.image = self.back_image
        self.rect = self.image.get_rect(topleft = (x, y))
        self.shown = False

    def update(self):
        self.image = self.original_image if self.shown else self.back_image

    def show(self):
        self.shown = True
    def hide(self):
        self.shown = False

class Game():
    def __init__(self):
        self.level = 1
        self.level_complete = False

        # planets
        self.all_planets = [f for f in os.listdir('images/planets') if os.path.join('images/planets', f)]

        self.img_width, self.img_height = (128, 128)
        self.padding = 20
        self.margin_top = 160
        self.cols = 4
        self.rows = 2
        self.width = 1280

        self.tiles_group = pygame.sprite.Group()

        # flipping & timing
        self.flipped = []
        self.frame_count = 0
        self.block_game = False

        # generate first level
        self.generate_level(self.level)

        # initialize video
        self.is_video_playing = True
        self.play = pygame.image.load('images/play.png').convert_alpha()
        self.stop = pygame.image.load('images/stop.png').convert_alpha()
        self.video_toggle = self.play
        self.video_toggle_rect = self.video_toggle.get_rect(topright = (WINDOW_WIDTH - 50, 10))
        self.get_video()

        # initialize music
        self.is_music_playing = True
        self.sound_on = pygame.image.load('images/speaker.png').convert_alpha()
        self.sound_off = pygame.image.load('images/mute.png').convert_alpha()
        self.music_toggle = self.sound_on
        self.music_toggle_rect = self.music_toggle.get_rect(topright = (WINDOW_WIDTH - 10, 10))

        # load music
        pygame.mixer.music.load('sounds/bg-music.mp3')
        pygame.mixer.music.set_volume(.3)
        pygame.mixer.music.play()

    counter = 0
    counter_on = 1
    max_count = 100
    cards_visible = 1

    def main():
        global counter_on, counter, max_count, cards_visible
        global bonus

        game_init()
        squares_init()
        clock = pygame.time.Clock()
        loop = 1
        # pygame.mouse.set_visible(False)
        soundtrack("sounds/soave.ogg")
        while loop:
            screen.fill((0, 0, 0))
            text = font.render("Livello: " + str(score), 1, (255, 244, 0))
            screen.blit(text, (0, 0))
            if counter_on:
                text = font.render("time: " + str(max_count - counter), 1, (255, 244, 0))
                screen.blit(text, (200, 0))
                counter += 1
                if counter % 4 == 0:
                    play("click")
            for event in pygame.event.get():
                # ========================================= QUIT
                if event.type == pygame.QUIT:
                    loop = 0
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        loop = 0
                    if event.key == pygame.K_s:
                        g.update()
                        screen.fill((0, 0, 0))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Click mouse and stop the timer and hide the cards
                    if cards_visible:
                        hide_cards()
                        # bonus to click early: add to score if win
                        bonus = max_count - counter
                        cards_visible = 0
                        counter_on = 0
                        counter = 0
                    # This checks the cards you hit
                    for s in g:
                        mouse_collision(s)

            g.draw(screen)
            # Hides the number...
            if counter == max_count:
                hide_cards()
                counter = 0
                counter_on = 0

                # pygame.mouse.set_visible(True)
            pygame.display.update()
            clock.tick(20)

        pygame.quit()
    def update(self, event_list):
        if self.is_video_playing:
            self.success, self.img = self.cap.read()

        self.user_input(event_list)
        self.draw()
        self.check_level_complete(event_list)

    def check_level_complete(self, event_list):
        if not self.block_game:
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for tile in self.tiles_group:
                        if tile.rect.collidepoint(event.pos):
                            self.flipped.append(tile.name)
                            tile.show()
                            if len(self.flipped) == 2:
                                if self.flipped[0] != self.flipped[1]:
                                    self.block_game = True
                                else:
                                    self.flipped = []
                                    for tile in self.tiles_group:
                                        if tile.shown:
                                            self.level_complete = True
                                        else:
                                            self.level_complete = False
                                            break
        else:
            self.frame_count += 1
            if self.frame_count == FPS:
                self.frame_count = 0
                self.block_game = False

                for tile in self.tiles_group:
                    if tile.name in self.flipped:
                        tile.hide()
                self.flipped = []


    def generate_level(self, level):
        self.planets = self.select_random_planets(self.level)
        self.level_complete = False
        self.rows = self.level + 1
        self.cols = 4
        self.generate_tileset(self.planets)

    def generate_tileset(self, planets):
        self.cols = self.rows = self.cols if self.cols >= self.rows else self.rows

        TILES_WIDTH = (self.img_width * self.cols + self.padding * 3)
        LEFT_MARING = RIGHT_MARGIN = (self.width - TILES_WIDTH) // 2
        #tiles = []
        self.tiles_group.empty()

        for i in range(len(planets)):
            x = LEFT_MARING + ((self.img_width + self.padding) * (i % self.cols))
            y = self.margin_top + (i // self.rows * (self.img_height + self.padding))
            tile = Tile(planets[i], x, y)
            self.tiles_group.add(tile)


    def select_random_planets(self, level):
        planets = random.sample(self.all_planets, (self.level + self.level + 2))
        planets_copy = planets.copy()
        planets.extend(planets_copy)
        random.shuffle(planets)
        return planets

    def user_input(self, event_list):
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.music_toggle_rect.collidepoint(pygame.mouse.get_pos()):
                    if self.is_music_playing:
                        self.is_music_playing = False
                        self.music_toggle = self.sound_off
                        pygame.mixer.music.pause()
                    else:
                        self.is_music_playing = True
                        self.music_toggle = self.sound_on
                        pygame.mixer.music.unpause()
                if self.video_toggle_rect.collidepoint(pygame.mouse.get_pos()):
                    if self.is_video_playing:
                        self.is_video_playing = False
                        self.video_toggle = self.stop
                    else:
                        self.is_video_playing = True
                        self.video_toggle = self.play

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.level_complete:
                    self.level += 1
                    if self.level >= 6:
                        self.level = 1
                    self.generate_level(self.level)


    def draw(self):
        screen.fill(BLACK)

        # fonts
        title_font = pygame.font.Font('fonts/Little planets.ttf', 44)
        content_font = pygame.font.Font('fonts/Little planets.ttf', 24)

        # text
        title_text = title_font.render('Memory Game', True, WHITE)
        title_rect = title_text.get_rect(midtop = (WINDOW_WIDTH // 2, 10))

        level_text = content_font.render('Level ' + str(self.level), True, WHITE)
        level_rect = level_text.get_rect(midtop = (WINDOW_WIDTH // 2, 80))

        info_text = content_font.render('Find 2 of each', True, WHITE)
        info_rect = info_text.get_rect(midtop = (WINDOW_WIDTH // 2, 120))

        if self.is_video_playing:
            if self.success:
                screen.blit(pygame.image.frombuffer(self.img.tobytes(), self.shape, 'BGR'), (0, 120))
            else:
                self.get_video()
        else:
            screen.blit(pygame.image.frombuffer(self.img.tobytes(), self.shape, 'BGR'), (0, 120))

        if not self.level == 5:
            next_text = content_font.render('Level complete. Press Space for next level', True, WHITE)
        else:
            next_text = content_font.render('Congrats. You Won. Press Space to play again', True, WHITE)
        next_rect = next_text.get_rect(midbottom = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40))

        screen.blit(title_text, title_rect)
        screen.blit(level_text, level_rect)
        screen.blit(info_text, info_rect)
        pygame.draw.rect(screen, WHITE, (WINDOW_WIDTH - 90, 0, 100, 50))
        screen.blit(self.video_toggle, self.video_toggle_rect)
        screen.blit(self.music_toggle, self.music_toggle_rect)

        # draw tileset
        self.tiles_group.draw(screen)
        self.tiles_group.update()

        if self.level_complete:
            screen.blit(next_text, next_rect)

    def get_video(self):
        self.cap = cv2.VideoCapture('video/earth.mp4')
        self.success, self.img = self.cap.read()
        self.shape = self.img.shape[1::-1]

pygame.init()

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 860
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Memory Game')

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

FPS = 60
clock = pygame.time.Clock()

game = Game()

running = True
while running:
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            running = False

    game.update(event_list)

    pygame.display.update()
    clock.tick(FPS)


pygame.quit()

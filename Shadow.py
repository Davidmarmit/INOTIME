from random import randint
import pygame


# class Shadow

class Shadow(pygame.sprite.Sprite):

    # constructor Shadow: needs display, and start position
    def __init__(self, screen, x, y, image, obstacles):
        super().__init__()
        self.obstacles = None
        self.screen = screen
        self.x = x
        self.y = y
        self.direction = 1
        self.speed_x = 7 # randint(2, 5)
        self.speed_y = 7  # randint(2, 5)
        self.obstacles = obstacles

        # initializes player image, scales it, and masks it
        print("image: " + image)
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() / 3, self.image.get_height() / 3))
        self.mask_image = pygame.mask.from_surface(self.image)

        # sets the image rect to the same position as the image:
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.screen.blit(self.image, (self.x, self.y))

        # COLORS:
        self.count = 0  # counter of array colors
        self.step = 0

        self.array_color = [(207, 92, 54), (202, 103, 2), (238, 155, 0), (255, 207, 0), (73, 167, 155), (10, 147, 150),
                            (0, 96, 115), (0, 52, 89), (0, 18, 25), (52, 58, 64), (173, 181, 189), (218, 221, 223),
                            (255, 255, 255)]
        self.base_color = self.array_color[0]
        self.next_color = self.array_color[1]
        self.dead = False

    def move(self, array):
        if not self.dead:
            list_collide_border = pygame.sprite.spritecollide(self, self.obstacles, False, pygame.sprite.collide_mask)
            list_collide_shadows = pygame.sprite.spritecollide(self, array, False, pygame.sprite.collide_mask)

            if len(list_collide_border) or len(list_collide_shadows) > 1:
                # if self.rect.left <= 0 or self.rect.right >= 1000:
                self.direction *= -1
                lucky_num = randint(0, 5)
                if lucky_num == 5:
                    self.speed_x = -(3 * self.direction)  # randint(2, 5) * self.direction
                    self.speed_y = 2 * self.direction  # randint(2, 5) * self.direction
                elif lucky_num == 3:
                    self.speed_x = -(3 * self.direction)  # randint(2, 5) * self.direction
                    self.speed_y = -(2 * self.direction)  # randint(2, 5) * self.direction
                elif lucky_num == 1:
                    self.speed_x = 3 * self.direction  # randint(2, 5) * self.direction
                    self.speed_y = -(2 * self.direction)  # randint(2, 5) * self.direction
                else:
                    self.speed_x = 3 * self.direction  # randint(2, 5) * self.direction
                    self.speed_y = 2 * self.direction  # randint(2, 5) * self.direction

                # Changing the value if speed_x
                # and speed_y both are zero
                if self.speed_x == 0 and self.speed_y == 0:
                    self.speed_x = 3 * self.direction
                    self.speed_y = 3 * self.direction

            # Changing the direction and x,y coordinate
            # of the object if the coordinate of top
            # side is less than equal to 20 or bottom side coordinate
            # is greater than equal to 580

            # if len(list_collide):
            #     # if self.rect.top <= 0 or self.rect.bottom >= 700:
            #     self.direction *= -1
            #     self.speed_x = randint(0, 5) * self.direction
            #     self.speed_y = randint(0, 5) * self.direction
            #
            #     # Changing the value if speed_x
            #     # and speed_y both are zero
            #     if self.speed_x == 0 and self.speed_y == 0:
            #         self.speed_x = randint(2, 5) * self.direction
            #         self.speed_y = randint(2, 5) * self.direction

            # Adding speed_x and speed_y
            # in left and top coordinates of object

            self.rect.x += self.speed_x
            self.rect.y -= self.speed_y
            self.x = self.rect.x
            self.y = self.rect.y
            self.screen.blit(self.image, (self.rect.x, self.rect.y))

    # print(self.rect.x, self.rect.y)
    def set_shadow(self):
        self.screen.blit(self.image, (self.rect.x, self.rect.y))

    def fill(self, color):
        w, h = self.image.get_size()
        r, g, b, _ = color
        for x in range(w):
            for y in range(h):
                a = self.image.get_at((x, y))[3]
                self.image.set_at((x, y), pygame.Color(r, g, b, a))

    def fade_color(self, current_color):
        number_of_steps = 60 * 1
        self.step += 1
        print(self.step)
        # COLOR FADE STEPS:
        if self.step < number_of_steps:
            current_color = [x + (((y - x) / number_of_steps) * self.step) for x, y in
                             zip(pygame.color.Color(self.base_color), pygame.color.Color(self.next_color))]
        else:  # CHANGE TO NEXT COLOR
            self.step = 1
            self.base_color = self.array_color[self.count]
            if self.count < len(self.array_color) - 1:
                self.count += 1
                self.next_color = self.array_color[self.count]
            else:
                self.dead = True
                current_color = (0, 0, 0, 0)
        return current_color

# # Day 1: Not Quite Lisp
# # Problem statement: https://adventofcode.com/2022/day/1

# from math import ceil
# import sys
# import pygame as pg

# pg.init()

# day_title = "Not Quite Lisp"


# def part1(text_input):
#     up = text_input.count("(")
#     down = len(text_input) - up
#     return up - down


# def part2(text_input):
#     floor = 0
#     for i, char in enumerate(text_input):
#         if char == "(":
#             floor += 1
#         else:
#             floor -= 1
#         if floor == -1:
#             return i + 1


# RED = (255, 64, 64)
# GREY = (200, 200, 200)
# DARKGREY = (100, 100, 100)
# BLACK = (0, 0, 0)

# WIDTH = 640
# HEIGHT = 480
# FLOOR_HEIGHT = 120
# TEXT_ROW_HEIGHT = 80
# FLOORS_HEIGHT = HEIGHT - TEXT_ROW_HEIGHT
# PLAQUE_LEFT = 120
# PLAQUE_HEIGHT = 40
# PLAQUE_WIDTH = 90
# FPS = 60


# elevator_height = 0
# elevator_speed = 0
# elevator_direction = 1

# screen = pg.display.set_mode([WIDTH, HEIGHT])
# text_surface = pg.Surface((WIDTH, TEXT_ROW_HEIGHT))
# # text_surface.fill()

# pg.display.set_caption("Day 1 - Not Quite Lisp")
# plaque_font = pg.font.SysFont("monospace", int(0.5 * PLAQUE_HEIGHT))
# clock = pg.time.Clock()

# text_input = "(()))))"


# class Elevator(pg.sprite.Sprite):
#     def __init__(self):
#         super(Elevator, self).__init__()
#         self.width = 60
#         self.height = 90
#         self.open_value = 0
#         self.open_speed = 0
#         self.surf = pg.Surface((self.width, self.height))
#         self.surf.fill(DARKGREY)
#         self.rect = self.surf.get_rect(
#             center=(int(WIDTH / 2), HEIGHT // 2 + FLOOR_HEIGHT - self.height // 2)
#         )

#     def open(self):
#         self.open_speed = 1

#     def update(self):
#         if self.open_speed == 0:
#             pass
#         else:
#             self.surf.fill(DARKGREY)
#             opened = pg.Rect(0, 0, self.open_value, self.height)
#             opened.centerx = self.width // 2
#             self.surf.fill(GREY, opened)
#         if self.open_speed > 0:
#             self.open_value = min(self.width, self.open_value + self.open_speed)
#             if self.open_value == self.width:
#                 self.open_speed = 0
#         elif self.open_speed < 0:
#             self.open_value = max(0, self.open_value - self.open_speed)
#             if self.open_value == 0:
#                 self.open_speed = 0


# class Santa(pg.sprite.Sprite):
#     def __init__(self):
#         super(Santa, self).__init__()
#         self.width = 30
#         self.height = 60
#         self.x = WIDTH
#         self.target_x = self.x
#         self.walk_speed = 2
#         self.surf = pg.Surface((self.width, self.height))
#         self.surf.fill(RED)
#         self.rect = self.surf.get_rect(
#             bottom=HEIGHT // 2 + FLOOR_HEIGHT, centerx=self.x
#         )

#     def walk(self, dx):
#         self.target_x = self.x + dx

#     def walk_to(self, x):
#         self.target_x = x

#     def update(self):
#         if self.target_x < self.x:
#             self.x = max(self.target_x, self.x - self.walk_speed)
#         elif self.target_x > self.x:
#             self.x = min(self.target_x, self.x + self.walk_speed)
#         self.rect.centerx = self.x


# def draw_floor(top, floor_number):
#     floor_rect = pg.Rect(0, top, WIDTH, FLOOR_HEIGHT)
#     pg.draw.rect(screen, GREY, floor_rect, 1)
#     plaque_rect = pg.Rect(
#         PLAQUE_LEFT,
#         top + (FLOOR_HEIGHT - PLAQUE_HEIGHT) * 0.5,
#         PLAQUE_WIDTH,
#         PLAQUE_HEIGHT,
#     )
#     pg.draw.rect(screen, GREY, plaque_rect, 2)
#     plaque_text = plaque_font.render(str(floor_number), 1, GREY)
#     screen.blit(plaque_text, plaque_text.get_rect(center=plaque_rect.center))


# def draw_floors(elevator_height):
#     floor_number = elevator_height // FLOOR_HEIGHT
#     floor_top = HEIGHT / 2 + elevator_height % FLOOR_HEIGHT
#     extra_floors_top = ceil(floor_top / FLOOR_HEIGHT)
#     upmost_number = floor_number + extra_floors_top
#     upmost_top = floor_top - FLOOR_HEIGHT * extra_floors_top
#     while upmost_top < HEIGHT:
#         draw_floor(upmost_top, upmost_number)
#         upmost_top += FLOOR_HEIGHT
#         upmost_number -= 1


# running = True

# elevator = Elevator()
# santa = Santa()


# class SantaWalk:
#     def __init__(self):
#         pass

#     def setup(self):
#         santa.walk_to(WIDTH // 2)

#     def update(self):
#         santa.update()

#     def render(self):
#         draw_floors(0)
#         screen.blit(elevator.surf, elevator.rect)
#         screen.blit(santa.surf, santa.rect)

#     def next(self):
#         if santa.x == santa.target_x:
#             return ElevatorOpen()
#         else:
#             return self


# class ElevatorOpen:
#     def __init__(self):
#         pass

#     def setup(self):
#         elevator.open()

#     def update(self):
#         elevator.update()

#     def render(self):
#         draw_floors(0)
#         screen.blit(elevator.surf, elevator.rect)
#         screen.blit(santa.surf, santa.rect)

#     def next(self):
#         if elevator.open_speed == 0:
#             return ElevatorRide()
#         else:
#             return self


# class ElevatorRide:
#     def __init__(self):
#         self.elevator_speed = 0
#         self.elevator_height = 0

#     def setup(self):
#         self.elevator_speed = 2

#     def update(self):
#         if abs(self.elevator_height) > 7 * FLOOR_HEIGHT:
#             self.elevator_speed *= -1
#         self.elevator_height += self.elevator_speed

#     def render(self):
#         draw_floors(self.elevator_height)
#         screen.blit(elevator.surf, elevator.rect)
#         screen.blit(santa.surf, santa.rect)

#     def next(self):
#         return self


# stage = SantaWalk()
# stage.setup()

# while True:
#     clock.tick(FPS)
#     for event in pg.event.get():
#         if event.type == pg.QUIT:
#             pg.quit()
#             sys.exit()

#     screen.fill(BLACK)
#     stage.update()
#     stage.render()
#     next_stage = stage.next()
#     if next_stage != stage:
#         next_stage.setup()
#     stage = next_stage

#     # Flip the display
#     pg.display.flip()

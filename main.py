"""
    Loads a level and runs racer.
    Driver can be configured to player or AI.
"""

import pygame
import json
from objects import *
from drivers import *

pygame.init()
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
paused_between_gens = False

BORDER_WIDTH = 50
BORDER_RECTS = []
BORDER_RECTS.append(pygame.Rect(0, 0, SCREEN_WIDTH, BORDER_WIDTH))
BORDER_RECTS.append(pygame.Rect(0, SCREEN_HEIGHT -
                    BORDER_WIDTH, SCREEN_WIDTH, BORDER_WIDTH))
BORDER_RECTS.append(pygame.Rect(0, 0, BORDER_WIDTH, SCREEN_HEIGHT))
BORDER_RECTS.append(pygame.Rect(SCREEN_WIDTH - BORDER_WIDTH,
                    0, BORDER_WIDTH, SCREEN_HEIGHT))

FONT = pygame.font.SysFont(None, 24)
LINE_HEIGHT = 20

MSGBOX_WIDTH = 300
MSGBOX_HEIGHT = 200
MSGBOX_RECT = pygame.Rect((SCREEN_WIDTH / 2) - (MSGBOX_WIDTH / 2),
                          (SCREEN_HEIGHT / 2) - (MSGBOX_HEIGHT / 2),
                          MSGBOX_WIDTH, MSGBOX_HEIGHT)
MSGBOX_TEXT_PADDING = 15


def msgbox_show_text(text_lines):
    global screen, FONT

    pygame.draw.rect(screen, "#FBBA00", MSGBOX_RECT)

    line_level = MSGBOX_RECT.y + MSGBOX_TEXT_PADDING
    for line in text_lines:
        screen.blit(FONT.render(line, False, "#000000"),
                    (MSGBOX_RECT.x + MSGBOX_TEXT_PADDING,
                    line_level))
        line_level += LINE_HEIGHT


# Default car position
start_x = 0
start_y = 0
start_angle = 0
goals = []
obstacles = []
# Load level
with open("levels/straight.json") as level_f:
    level = json.loads(level_f.read())
    start_x = level["start"]["x"]
    start_y = level["start"]["y"]
    start_angle = level["start"]["angle"]
    if "goals" in level.keys():
        for level_goal in level["goals"]:
            goals.append(pygame.Rect(
                level_goal["left"], level_goal["top"], level_goal["width"], level_goal["height"]))
    if "obstacles" in level.keys():
        for level_obst in level["obstacles"]:
            obstacles.append(pygame.Rect(
                level_obst["left"], level_obst["top"], level_obst["width"], level_obst["height"]))

GEN_SIZE = 10
GEN_FRAMES = 300
gen_number = 1
gen_cur_frame = 0
gen_win_count = 0
gen_crash_count = 0
SELECTION_RATIO = 0.5
SELECTION_COUNT = GEN_SIZE * SELECTION_RATIO
cars = [LiDAR_Car(start_x, start_y, start_angle) for _ in range(GEN_SIZE)]
drivers = [No_Hidden_NN_Driver(car) for car in cars]
MAX_HYPOT = math.hypot(SCREEN_HEIGHT - (BORDER_WIDTH * 2),
                       SCREEN_WIDTH - (BORDER_WIDTH * 2))
driver_scores = [0] * GEN_SIZE
driver_finished = [False] * GEN_SIZE


def reset_car(car):
    car.force_position(start_x, start_y, start_angle)


def draw_static_objects():
    global goals, obstacles, BORDER_RECTS
    for goal in goals:
        pygame.draw.rect(screen, "#93F651", goal)
    for obst in obstacles:
        pygame.draw.rect(screen, "#F27549", obst)
    for border_rect in BORDER_RECTS:
        pygame.draw.rect(screen, "#111111", border_rect)


def handle_goal_collisions(car, goals):
    collided = False
    for goal in goals:
        if (car.collide_rect(goal)):
            collided = True
    return collided


def handle_crash_collisions(car, obstacles, BORDER_RECTS):
    collided = False
    for obst in obstacles:
        if (car.collide_rect(obst)):
            collided = True
        if type(car) is LiDAR_Car:
            car.beam_collide_rect_register(obst)

    for border_rect in BORDER_RECTS:
        if (car.collide_rect(border_rect)):
            collided = True
        if type(car) is LiDAR_Car:
            car.beam_collide_rect_register(border_rect)
    return collided


def drive_and_draw_cars():
    global screen, cars, drivers, driver_scores, driver_finished
    global gen_win_count, gen_crash_count

    for i in range(len(cars)):

        if driver_finished[i]:
            continue

        # Controls
        forward, turn_left = drivers[i].drive_command()
        cars[i].apply_command(forward, turn_left)

        # Update Car Position
        cars[i].simulate_friction()
        cars[i].position_frame_update()

        # Handle Collisions (including LiDAR beams)
        if handle_goal_collisions(cars[i], goals):
            # Reward win and short time to goal
            driver_scores[i] = (
                100 + (((GEN_FRAMES - gen_cur_frame) / GEN_FRAMES) * 100))
            driver_finished[i] = True
            gen_win_count += 1

        if handle_crash_collisions(cars[i], obstacles, BORDER_RECTS):
            # Reward survival time
            driver_scores[i] = (gen_cur_frame / GEN_FRAMES) * 100
            driver_finished[i] = True
            gen_crash_count += 1

        # Draw car on top
        cars[i].draw(screen)

        # Draw LiDAR Beams
        if type(cars[i]) is LiDAR_Car:
            cars[i].draw_beams(screen)


def conclude_gen():
    global screen, drivers, driver_scores, driver_finished

    # Calculate scores for non-collided drivers
    for i in range(len(driver_scores)):
        if driver_finished[i]:
            continue
        # Reward distance from
        driver_scores[i] = (math.hypot(
            cars[i].x - start_x, cars[i].y - start_y) / MAX_HYPOT)

    # Sort drivers by score
    combined = list(zip(driver_scores, drivers))
    combined.sort(reverse=True, key=lambda x: x[0])
    # Unpack
    driver_scores, drivers = zip(*combined)

    msgbox_show_text(["Press r for next gen",
                      "Top Scores: ",
                      "1st: " + str(driver_scores[0]),
                      "2nd: " + str(driver_scores[1]),
                      "3rd: " + str(driver_scores[2])])


def evolve_drivers():
    global drivers

    assert SELECTION_COUNT > 1, "At least 2 parents required for evolution"
    child_drivers = []
    for i in range(GEN_SIZE):
        # Choose two random, different parents and create child
        i_p1 = random.randint(0, SELECTION_COUNT - 1)
        i_p2 = int((i_p1 + random.randint(1, SELECTION_COUNT - 1)) %
                   SELECTION_COUNT)
        child_drivers.append(drivers[0].__class__.mate(
            drivers[i_p1], drivers[i_p2], cars[i]))

    drivers = child_drivers


# Main Game Loop
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Poll for resume
                if paused_between_gens:
                    # Do next gen
                    gen_number += 1
                    gen_cur_frame = 0
                    driver_scores = [0] * GEN_SIZE
                    driver_finished = [False] * GEN_SIZE
                    gen_win_count = 0
                    gen_crash_count = 0
                    for car in cars:
                        reset_car(car)
                    evolve_drivers()
                    paused_between_gens = False

    if not paused_between_gens:
        # Clears screen of last frame
        screen.fill("#eeeeee")

        draw_static_objects()

        drive_and_draw_cars()

        gen_cur_frame += 1
        if (gen_cur_frame >= GEN_FRAMES):
            conclude_gen()
            paused_between_gens = True

        # Text
        screen.blit(FONT.render("Generation: " + str(gen_number) +
                                " Frame: " + str(gen_cur_frame),
                                False, "#ffffff"), (50, 20))
        screen.blit(FONT.render("Win/Crash/Total: " + str(gen_win_count) +
                                "/" + str(gen_crash_count) +
                                "/" + str(GEN_SIZE),
                                False, "#ffffff"), (300, 20))

        # Displays changes to screen
        pygame.display.flip()

    clock.tick(60)

pygame.quit()

import pygame
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravitational Slingshot Effect")

PLANET_MASS = 100
SHIP_MASS = 5
G = 5
FPS = 60
PLANET_SIZE = 50
OBJ_SIZE = 5
SLING_FORCE = 0.05

BG = pygame.transform.scale(pygame.image.load(
    "background.jpg"), (WIDTH, HEIGHT))
PLANET = pygame.transform.scale(pygame.image.load(
    "jupiter.png"), (PLANET_SIZE * 2, PLANET_SIZE * 2))

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


class Planet:
    def __init__(self, x, y, mass):
        self.x = x
        self.y = y
        self.mass = mass

    def draw(self):
        win.blit(PLANET, (self.x - PLANET_SIZE, self.y - PLANET_SIZE))


class Spacecraft:
    def __init__(self, x, y, prev_x, prev_y, vel_x, vel_y, mass):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.mass = mass

    def move(self, planet=None):
        # if planet does not exist the spacecraft will follow straight direction
        # with constant velocity
        if planet != None:
            distance_sq = (self.x - planet.x) ** 2 + (self.y - planet.y) ** 2

            force = (G * self.mass * planet.mass) / distance_sq

            acceleration = force / self.mass
            angle = math.atan2(planet.y - self.y, planet.x - self.x)

            acceleration_x = acceleration * math.cos(angle)
            acceleration_y = acceleration * math.sin(angle)
            self.vel_x += acceleration_x
            self.vel_y += acceleration_y
        
        self.x += self.vel_x
        self.y += self.vel_y

    def rotate_points_around_pivot(self, points, pivot, angle):
        pp = pygame.math.Vector2(pivot)
        rotated_points = [
            (pygame.math.Vector2(x, y) - pp).rotate(angle) + pp for x, y in points]
        return rotated_points       

    def draw(self, planet):
        # draw a triangle that represent the ship's shape
        # it should point into the direction of travel
        angle = math.degrees(math.atan2(-self.vel_y, -self.vel_x)) + 90
        x_shift = 3 
        y_shift = 10 
        x = [self.x - x_shift, self.x + x_shift, self.x]
        y = [self.y - y_shift, self.y - y_shift, self.y + y_shift]
        points = list(zip(x, y))
        pivot = (self.x, self.y)        
        rotated_points = self.rotate_points_around_pivot(points, pivot, angle)

        pygame.draw.polygon(win, RED, rotated_points, 1)


def create_ship(mouse, start):
    m_x, m_y = mouse
    s_x, s_y = start
    shift_x = s_x - m_x
    shift_y = s_y - m_y

    distance_sq = shift_x**2 + shift_y**2
    # From a=F/m ; v=t*a ; D = a*t*t/2 
    vel = math.sqrt(2 * SLING_FORCE * distance_sq / SHIP_MASS)
    angle = math.atan2(shift_y, shift_x)

    vel_x = vel * math.cos(angle)
    vel_y = vel * math.sin(angle)

    obj = Spacecraft(m_x, m_y, s_x, s_y, vel_x, vel_y, SHIP_MASS)

    return obj


def main():
    running = True
    clock = pygame.time.Clock()

    planet = Planet(WIDTH // 2, HEIGHT // 2, PLANET_MASS)
    ships = []
    start_sling_pos = None

    while running:
        clock.tick(FPS)

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                start_sling_pos = mouse_pos                

            if event.type == pygame.MOUSEBUTTONUP:
                if start_sling_pos:
                    ship = create_ship(mouse_pos, start_sling_pos)
                    ships.append(ship)
                    
                    start_sling_pos = None

        win.blit(BG, (0, 0))

        if start_sling_pos:
            # it'd be nice to start drawing the ship on the mouse move, for now it is just a cirle
            pygame.draw.line(win, WHITE, start_sling_pos, mouse_pos, 2)
            pygame.draw.circle(win, RED, mouse_pos, OBJ_SIZE)

        for ship in ships[:]:
            ship.draw(planet)
            ship.move(planet)
            off_screen = ship.x < 0 or ship.x > WIDTH or ship.y < 0 or ship.y > HEIGHT
            collided = math.sqrt((ship.x - planet.x)**2 +
                                 (ship.y - planet.y)**2) <= PLANET_SIZE
            if off_screen or collided:
                ships.remove(ship)

        planet.draw()

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()

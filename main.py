import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the window
window_size = (1500, 1000)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Map Builder")

# Load the image & Store OG
original_map_image = pygame.image.load("map.png")
map_image = original_map_image.copy()
map_rect = map_image.get_rect()

zoom = 1.0
zoom_step = 0.5
offset = [0, 0]

click_locations = []  # List to store click locations
circle_radius = 5  # Base radius of circles at 1x zoom

# Function to calculate Bezier curve points
def cubic_bezier(t, p0, p1, p2, p3):
    u = 1 - t
    tt = t*t
    uu = u*u
    uuu = uu * u
    ttt = tt * t

    p = (uuu * p0[0], uuu * p0[1])  # First term
    p = (p[0] + 3 * uu * t * p1[0], p[1] + 3 * uu * t * p1[1])  # Second term
    p = (p[0] + 3 * u * tt * p2[0], p[1] + 3 * u * tt * p2[1])  # Third term
    p = (p[0] + ttt * p3[0], p[1] + ttt * p3[1])  # Fourth term

    return p

# Visual Continuity Granularity
CURVE_GRAN = 600

# Function to draw a cubic Bezier curve with scaling
def draw_bezier_curve(window, points, zoom, offset, color=(0, 0, 255)):
    scaled_points = [(int(p[0] * zoom + offset[0]), int(p[1] * zoom + offset[1])) for p in points]
    
    for t in range(CURVE_GRAN+1):
        t /= CURVE_GRAN
        p = cubic_bezier(t, scaled_points[0], scaled_points[1], scaled_points[2], scaled_points[3])
        pygame.draw.circle(window, color, (int(p[0]), int(p[1])), 1)



def get_pixel_coordinates(click_x, click_y, offset, zoom):
    print("Debug Z " + str(zoom))
    print("offset " + str(offset[0]) + " " + str(offset[1]))

    # Adjust for the zoom first
    adjusted_x = (click_x / zoom)
    adjusted_y = (click_y / zoom)

    # Then adjust for the offset
    pixel_x = int(adjusted_x - offset[0] / zoom)
    pixel_y = int(adjusted_y - offset[1] / zoom)

    click_locations.append((pixel_x, pixel_y)) 
    return pixel_x, pixel_y



# Function to handle zooming
def zoom_image(scale_factor):
    global map_image, map_rect, zoom, original_map_image
    zoom += scale_factor
    zoom = max(0.1, zoom)  # Prevent zoom from going negative
    width = int(map_rect.width * zoom)
    height = int(map_rect.height * zoom)
    map_image = pygame.transform.scale(original_map_image, (width, height))
    map_rect = map_image.get_rect(center=map_rect.center)


# Function to handle panning
def pan_image(x, y):
    global offset
    offset[0] += x
    offset[1] += y


# Initial flags for movement
move_left = move_right = move_up = move_down = False

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if left mouse button is pressed
            if event.button == 1:
                pixel_x, pixel_y = get_pixel_coordinates(event.pos[0], event.pos[1], offset, zoom)
                print(f"Clicked pixel coordinates: ({pixel_x}, {pixel_y})")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:  # Zoom in
                zoom_image(zoom_step)
            elif event.key == pygame.K_DOWN:  # Reset zoom and recenter
                zoom = 1.0
                offset = [0, 0]
                map_image = original_map_image.copy()
                map_rect = map_image.get_rect()
            elif event.key == pygame.K_a:  # Pan left
                move_left = True
            elif event.key == pygame.K_d:  # Pan right
                move_right = True
            elif event.key == pygame.K_w:  # Pan up
                move_up = True
            elif event.key == pygame.K_s:  # Pan down
                move_down = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:  # Stop moving left
                move_left = False
            elif event.key == pygame.K_d:  # Stop moving right
                move_right = False
            elif event.key == pygame.K_w:  # Stop moving up
                move_up = False
            elif event.key == pygame.K_s:  # Stop moving down
                move_down = False

    # Moving the image based on flags
    if move_left:
        pan_image(10, 0)
    if move_right:
        pan_image(-10, 0)
    if move_up:
        pan_image(0, 10)
    if move_down:
        pan_image(0, -10)


    # Update the window
    window.fill((0, 20, 20))  # Fill with black (or any background color)
    window.blit(map_image, (offset[0], offset[1]))

    # Draw circles at click locations
    for loc in click_locations:
        # Adjust click location for current zoom and offset
        circle_x = int(loc[0] * zoom + offset[0])
        circle_y = int(loc[1] * zoom + offset[1])
        scaled_circle_radius = int(circle_radius * zoom)  # Scale the circle size

        pygame.draw.circle(window, (255, 255, 0), (circle_x, circle_y), scaled_circle_radius)
    
    for i in range(0, len(click_locations) - 3, 3):
        curve_points = [click_locations[i], click_locations[i+1], click_locations[i+2], click_locations[i+3]]
        draw_bezier_curve(window, curve_points, zoom, offset)

    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()

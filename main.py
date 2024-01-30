import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the window
window_size = (750, 750)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Map Builder")

# Load the image & Store OG
original_map_image = pygame.image.load("map.png")
map_image = original_map_image.copy()
map_rect = map_image.get_rect()



click_locations = []  # List to store click locations
CIRCLE_RADIUS = 5  # Base radius of circles at 1x zoom

# Visual Continuity Granularity
CURVE_GRAN = 1200

#* ------------- Bezier Curve / Math Functions ---------------

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

# At a given t value, I'll get the Derivative of the point, which acts as the "Normal" that I'm trying to use for the road

def cubic_bezier_derivative(t, p0, p1, p2, p3):
    u = 1 - t
    derivative = (3 * u**2 * (p1[0] - p0[0]) + 6 * u * t * (p2[0] - p1[0]) + 3 * t**2 * (p3[0] - p2[0]),
                  3 * u**2 * (p1[1] - p0[1]) + 6 * u * t * (p2[1] - p1[1]) + 3 * t**2 * (p3[1] - p2[1]))
    return derivative

#* ---------------------------------------------------------------------

#* ------------- Map Exporting Functions (and Algorithms) ---------------

def export_draw_bezier_curve(window, points, color=(0, 0, 255), heightmap=None, curve_granularity=CURVE_GRAN, neighborhood_size=30):
    scaled_points = [( int(p[0]), int(p[1]) ) for p in points]
    

    for t in range(curve_granularity+1):
        t /= curve_granularity
        p = cubic_bezier(t, *scaled_points)
        derivative = cubic_bezier_derivative(t, *scaled_points)
        
        tangent = pygame.math.Vector2(derivative).normalize()
        normal = pygame.math.Vector2(-tangent.y, tangent.x)
        normal_length = 15
        normal = normal * normal_length

        if heightmap:
            averaged_brightness = average_neighborhood_height(int(p[0]), int(p[1]), heightmap, neighborhood_size)

            int_col = int(averaged_brightness)
            outer_line_color = pygame.Color(int_col, int_col, int_col)
            inner_line_color = outer_line_color
        else:
            outer_line_color = (255, 0, 0)  
            inner_line_color = (0, 255, 0)

        pygame.draw.circle(window, color, (int(p[0]), int(p[1])), 1)
        normal_start = (int(p[0]), int(p[1]))
        normal_end = (int(p[0] + normal.x), int(p[1] + normal.y))
        pygame.draw.line(window, outer_line_color, normal_start, normal_end)

        normal_end_opposite = (int(p[0] - normal.x), int(p[1] - normal.y))
        pygame.draw.line(window, inner_line_color, normal_start, normal_end_opposite)

Export_Map = pygame.Surface((map_image.get_width(), map_image.get_height()))

def export_map_image():

    Export_Map.blit(map_image, (0,0))

    for i in range(0, len(click_locations) - 3, 3):
        curve_points = [click_locations[i], click_locations[i+1], click_locations[i+2], click_locations[i+3]]
        export_draw_bezier_curve(Export_Map, curve_points, (0,0,255), map_image, 30)

    pygame.image.save(Export_Map, 'exported_map.png')
    return 0

def average_neighborhood_height(x, y, heightmap, neighborhood_size):
    total_brightness = 0
    count = 0

    for dx in range(-neighborhood_size, neighborhood_size + 1):
        for dy in range(-neighborhood_size, neighborhood_size + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < heightmap.get_width() and 0 <= ny < heightmap.get_height():
                pixel_color = heightmap.get_at((nx, ny))
                brightness = (pixel_color.r + pixel_color.g + pixel_color.b) / 3
                total_brightness += brightness
                count += 1

    return total_brightness / count if count > 0 else 0

#* ---------------------------------------------------------------------


# Function to draw a cubic Bezier curve with scaling
def draw_bezier_curve(window, points, zoom, offset, color=(0, 0, 255), heightmap=None, neighborhood_size=30):
    scaled_points = [(int(p[0] * zoom + offset[0]), int(p[1] * zoom + offset[1])) for p in points]
    
    for t in range(CURVE_GRAN+1):
        t /= CURVE_GRAN
        p = cubic_bezier(t, *scaled_points)
        derivative = cubic_bezier_derivative(t, *scaled_points)
        
        tangent = pygame.math.Vector2(derivative).normalize()
        UNIT_Normal = pygame.math.Vector2(-tangent.y, tangent.x)

        normal_length = 15
        border_length = 10

        normal = UNIT_Normal * normal_length
        normal_border = UNIT_Normal * (normal_length + border_length)

        if heightmap:
            averaged_brightness = average_neighborhood_height(int(p[0]), int(p[1]), heightmap, neighborhood_size)

            int_col = int(averaged_brightness)
            outer_line_color = pygame.Color(int_col, int_col, int_col)
            inner_line_color = outer_line_color
        else:
            outer_line_color = (255, 0, 0)  
            inner_line_color = (0, 255, 0)

        pygame.draw.circle(window, color, (int(p[0]), int(p[1])), 1)

        normal_start = (int(p[0]), int(p[1]))
        
        # Red Normal (Outer Normal)
        outer_normal_end = (int(p[0] + normal.x), int(p[1] + normal.y))
        pygame.draw.line(window, outer_line_color, normal_start, outer_normal_end)

        # Green Normal (Inner Normal) 
        inner_normal_end = (int(p[0] - normal.x), int(p[1] - normal.y))
        pygame.draw.line(window, inner_line_color, normal_start, inner_normal_end)

        # Draw Borders (In Purple)

        outer_border_end = (int(p[0] + normal_border.x), int(p[1] + normal_border.y))
        pygame.draw.line(window, (130,0,255), outer_normal_end, outer_border_end)

        inner_border_end = (int(p[0] - normal_border.x), int(p[1] - normal_border.y))
        pygame.draw.line(window, (130,0,255), inner_normal_end, inner_border_end)


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

def save_full_map(filename="full_map.png"):
    pygame.image.save(original_map_image, filename)

def save_current_view(window, filename="saved_map.png"):
    pygame.image.save(window, filename)


#* -------------- Pan & Zoom Functionality --------------

zoom = 1.0
zoom_step = 0.5
offset = [0, 0]

# Function to handle panning
def pan_image(x, y):
    global offset
    offset[0] += x
    offset[1] += y

# Function to handle zooming
def zoom_image():
    global map_image, map_rect, zoom, original_map_image
    
    #! Band-aid to fix, but for now IDRC
    if(zoom < 1.5):
        zoom += zoom_step

        width = int(map_rect.width * zoom)
        height = int(map_rect.height * zoom)
        map_image = pygame.transform.scale(original_map_image, (width, height))
        map_rect = map_image.get_rect(center=map_rect.center)


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
                zoom_image()
            elif event.key == pygame.K_DOWN:  # Reset zoom and recenter
                zoom = 1.0
                offset = [0, 0]
                map_image = original_map_image.copy()
                map_rect = map_image.get_rect()

            elif event.key == pygame.K_z: # Destroy Latest Control Point
                click_locations.pop()
            elif event.key == pygame.K_p: # Save Map
                export_map_image()
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
        scaled_circle_radius = int(CIRCLE_RADIUS * zoom)  

        pygame.draw.circle(window, (255, 255, 0), (circle_x, circle_y), scaled_circle_radius)
    
    for i in range(0, len(click_locations) - 3, 3):
        curve_points = [click_locations[i], click_locations[i+1], click_locations[i+2], click_locations[i+3]]
        draw_bezier_curve(window, curve_points, zoom, offset, (0,0,255), None)

    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()

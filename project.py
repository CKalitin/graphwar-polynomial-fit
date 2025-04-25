import asyncio
import pygame
import cv2
import numpy as np

# Load image and compute centroids (from your project)
image = cv2.imread('input-game-screenshot.jpg')
if image is None:
    raise FileNotFoundError("Image not found. Check the file path.")
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
lower_yellow = np.array([25, 100, 100])  # Lower bound (H, S, V)
upper_yellow = np.array([35, 255, 255])  # Upper bound
mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 15]

# Compute centroids, and make all points initally untoggled
untoggled_points = []
for contour in valid_contours:
    M = cv2.moments(contour)
    if M['m00'] != 0:
        cx = int(M['m10'] / M['m00']) + 1
        cy = int(M['m01'] / M['m00']) - 2
        untoggled_points.append((cx, cy))

# Initialize arrays
toggled_points = []
user_points = []

# Initialize Pygame
pygame.init()

# Screen dimensions (match image size or adjust as needed)
SCREEN_WIDTH = image.shape[1]
SCREEN_HEIGHT = image.shape[0]
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Yellow Shapes Toggle Game")

# Colors
YELLOW = (255, 255, 0)
RED = (255, 0,0 )
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0,0,0)
GRAY = (100, 100, 100)

# Circle properties
CIRCLE_RADIUS = 10
CLICK_TOLERANCE = CIRCLE_RADIUS * 2  # Click detection radius

# Optional: Convert image to Pygame surface for background
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
image_array = np.transpose(image_rgb, (1, 0, 2))  # Rotate for Pygame
background = pygame.surfarray.make_surface(image_array)

degree = 2 # polynomial

# Game state
running = True
FPS = 60
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

previous_coefficients = [1,1,1]

def setup():
    """Initialize Pygame and game state."""
    pass  # Already initialized above

def distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def handle_click(pos):
    """Handle mouse click events."""
    global untoggled_points, toggled_points, user_points
    clicked = False

    # Check user points (remove on left-click)
    for i, point in enumerate(user_points[:]):
        if distance(pos, point) <= CLICK_TOLERANCE:
            user_points.pop(i)
            clicked = True
            break

    if clicked:
        return

    # Check untoggled points (move to toggled)
    for i, point in enumerate(untoggled_points[:]):
        if distance(pos, point) <= CLICK_TOLERANCE:
            untoggled_points.pop(i)
            toggled_points.append(point)
            clicked = True
            break

    if clicked:
        return

    # Check toggled points (move back to untoggled)
    for i, point in enumerate(toggled_points[:]):
        if distance(pos, point) <= CLICK_TOLERANCE:
            toggled_points.pop(i)
            untoggled_points.append(point)
            break

def fit_polynomial():
    global degree, toggled_points, user_points
    
    array = toggled_points + user_points
    
    x = np.array([p[0] for p in array])
    y = np.array([p[1] for p in array])
    
    adjusted_x = (x / SCREEN_WIDTH * 50) - 25 # Normalize to game coordinate system
    adjusted_y = ((SCREEN_HEIGHT-y) / SCREEN_HEIGHT * 30) - 15 # Normalize to game coordinate system
    
    indices = np.argsort(x)
    x = x[indices]
    y = y[indices]
    adjusted_x = adjusted_x[indices]
    adjusted_y = adjusted_y[indices]
        
    if len(x) < degree + 1: return
    
    try:
        coefficients = np.polyfit(x, y, degree)
        coefficients_adjusted = np.polyfit(adjusted_x, adjusted_y, degree)
        poly = np.poly1d(coefficients)
        poly_adjusted = np.poly1d(coefficients_adjusted)

        # Evaluate polynomial for smooth curve
        x_fit = np.linspace(0, SCREEN_WIDTH, 100)
        y_fit = poly(x_fit)

        # Create points for drawing
        points = [(int(x_fit[i]), int(y_fit[i])) for i in range(len(x_fit))]

        # Draw polynomial curve
        pygame.draw.lines(screen, BLUE, False, points, 2)
        
        return coefficients_adjusted
    except np.linalg.LinAlgError:
        print("Failed to fit polynomial (singular matrix)")

def beautify_polynomial(coefficients):
    global previous_coefficients
    if coefficients is None:
        return
    if previous_coefficients[1] == coefficients[1]:
        return
    previous_coefficients = coefficients
    coefficients = coefficients.tolist()  # numpy array to list
    coefficients = [round(c, 10) for c in coefficients]
    coefficients = coefficients[::-1]  # Reverse for human-readable format (c0 + c1*x + c2*x^2 + ...)
    
    terms = []
    for i, c in enumerate(coefficients):
        if c == 0:  # Skip zero coefficients
            continue
        # Use fixed-point notation to avoid scientific notation
        c_str = f"{c:.10f}".rstrip('0').rstrip('.')  # Remove trailing zeros and decimal point if integer
        if c_str == "1" and i > 0:  # Omit coefficient 1 for x^i (i > 0)
            c_str = ""
        elif c_str == "-1" and i > 0:  # Use -x^i for -1 coefficient
            c_str = "-"
        if i == 0:  # Constant term
            term = c_str
        elif i == 1:  # Linear term
            term = f"{c_str}x"
        else:  # Higher-order terms
            term = f"{c_str}x^{i}"
        # Add sign for positive coefficients (except first term)
        if c > 0 and terms:  # terms not empty means not the first term
            term = f"+{term}"
        terms.append(term)
    
    if not terms:  # Handle case where all coefficients are zero
        terms.append("0")
    
    output = ' '.join(terms)
    print(f"Polynomial: {output}")
    
def update_loop():
    """Update game state and draw elements."""
    global running, degree
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if event.button == 1:  # Left-click
                handle_click(pos)
            elif event.button == 3:  # Right-click
                user_points.append(pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:  # Increase degree
                if degree < 10:
                    degree += 1
            elif event.key == pygame.K_DOWN:  # Decrease degree
                if degree > 1:
                    degree -= 1

    # Clear screen
    screen.fill(WHITE)
    
    array = []
    array.append(user_points)
    array.append(toggled_points)
    
    # Draw background (optional)
    if background:
        screen.blit(background, (0, 0))

    for point in untoggled_points:
        pygame.draw.circle(screen, GREEN, point, CIRCLE_RADIUS)

    for point in user_points:
        pygame.draw.circle(screen, RED, point, CIRCLE_RADIUS)

    for point in toggled_points:
        pygame.draw.circle(screen, YELLOW, point, CIRCLE_RADIUS)

    coefficients= fit_polynomial()
    beautify_polynomial(coefficients)
    
    degree_text = font.render(f"Degree: {degree}", True, GRAY)
    screen.blit(degree_text, (10, 10))

    # Update display
    pygame.display.flip()

async def main():
    """Main game loop for Pyodide compatibility."""
    setup()
    while running:
        update_loop()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

asyncio.run(main())
import turtle
import random
import math
import time

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NUM_OBSTACLES = 4
OBSTACLE_SIZE = 60  # Square size
ROBOT_SPEED = 3
SENSOR_RANGE = 150
RANDOM_TURN_PROBABILITY = 0.01  # 1% chance per frame
DECISION_PAUSE = 0.3  # Pause when obstacle detected

class Obstacle:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.half_size = size / 2
        
    def draw(self):
        """Draw square obstacle"""
        drawer = turtle.Turtle()
        drawer.hideturtle()
        drawer.speed(0)
        drawer.penup()
        drawer.goto(self.x - self.half_size, self.y - self.half_size)
        drawer.pendown()
        drawer.fillcolor("orange")
        drawer.pencolor("black")
        drawer.pensize(3)
        drawer.begin_fill()
        for _ in range(4):
            drawer.forward(self.size)
            drawer.left(90)
        drawer.end_fill()
    
    def intersects_ray(self, rx, ry, dx, dy, max_dist):
        """Check if ray intersects this square obstacle"""
        # Check intersection with square (AABB)
        # Square bounds
        min_x = self.x - self.half_size
        max_x = self.x + self.half_size
        min_y = self.y - self.half_size
        max_y = self.y + self.half_size
        
        # Ray-box intersection
        if dx == 0 and dy == 0:
            return max_dist
        
        t_min = 0
        t_max = max_dist
        
        # X-axis
        if dx != 0:
            t1 = (min_x - rx) / dx
            t2 = (max_x - rx) / dx
            t_min = max(t_min, min(t1, t2))
            t_max = min(t_max, max(t1, t2))
        else:
            if rx < min_x or rx > max_x:
                return max_dist
        
        # Y-axis
        if dy != 0:
            t1 = (min_y - ry) / dy
            t2 = (max_y - ry) / dy
            t_min = max(t_min, min(t1, t2))
            t_max = min(t_max, max(t1, t2))
        else:
            if ry < min_y or ry > max_y:
                return max_dist
        
        if t_max >= t_min and t_min >= 0:
            return t_min
        
        return max_dist

class Robot:
    def __init__(self, x, y, screen):
        self.screen = screen
        self.turtle = turtle.Turtle()
        self.turtle.penup()
        self.turtle.goto(x, y)
        self.turtle.speed(0)
        
        # Create custom robot shape (diamond/square)
        screen.register_shape("robot", ((-10, 0), (0, 10), (10, 0), (0, -10)))
        self.turtle.shape("robot")
        self.turtle.color("blue")
        self.turtle.shapesize(1.5)
        
        self.heading = random.randint(0, 359)
        self.turtle.setheading(self.heading)
        
        # Sensor visualization turtles
        self.sensor_turtles = []
        for _ in range(3):
            sensor = turtle.Turtle()
            sensor.hideturtle()
            sensor.speed(0)
            sensor.pencolor("cyan")
            sensor.pensize(2)
            self.sensor_turtles.append(sensor)
        
    def draw_sensors(self, sensor_readings):
        """Draw sensor rays"""
        sensor_angles = [90, 0, -90]  # Left, Front, Right
        colors = ["yellow", "cyan", "yellow"]
        
        rx, ry = self.turtle.position()
        
        for i, (angle_offset, distance) in enumerate(zip(sensor_angles, sensor_readings)):
            sensor = self.sensor_turtles[i]
            sensor.clear()
            sensor.penup()
            sensor.goto(rx, ry)
            sensor.pendown()
            sensor.pencolor(colors[i])
            
            # Calculate end point
            sensor_angle = math.radians(self.turtle.heading() + angle_offset)
            end_x = rx + distance * math.cos(sensor_angle)
            end_y = ry + distance * math.sin(sensor_angle)
            
            sensor.goto(end_x, end_y)
            
            # Draw a small circle at the end
            sensor.penup()
            sensor.goto(end_x, end_y - 5)
            sensor.pendown()
            sensor.fillcolor(colors[i])
            sensor.begin_fill()
            sensor.circle(5)
            sensor.end_fill()
        
    def get_distance_to_obstacle(self, obstacle, angle_offset):
        """Calculate distance from robot to obstacle at given sensor angle"""
        sensor_angle = math.radians(self.turtle.heading() + angle_offset)
        
        # Robot position
        rx, ry = self.turtle.position()
        
        # Direction vector of sensor
        dx = math.cos(sensor_angle)
        dy = math.sin(sensor_angle)
        
        # Use square intersection
        return obstacle.intersects_ray(rx, ry, dx, dy, SENSOR_RANGE)
    
    def get_sensor_readings(self, obstacles):
        """Get readings from all 3 sensors"""
        # Left sensor (+90°), Front sensor (0°), Right sensor (-90°)
        sensor_angles = [90, 0, -90]
        readings = []
        
        for angle_offset in sensor_angles:
            min_dist = SENSOR_RANGE
            for obstacle in obstacles:
                dist = self.get_distance_to_obstacle(obstacle, angle_offset)
                min_dist = min(min_dist, dist)
            
            # Also check screen boundaries
            rx, ry = self.turtle.position()
            sensor_angle = math.radians(self.turtle.heading() + angle_offset)
            dx = math.cos(sensor_angle)
            dy = math.sin(sensor_angle)
            
            # Distance to walls
            if dx != 0:
                if dx > 0:  # Pointing right
                    wall_dist = (SCREEN_WIDTH/2 - rx) / dx
                else:  # Pointing left
                    wall_dist = (-SCREEN_WIDTH/2 - rx) / dx
                if wall_dist > 0:
                    min_dist = min(min_dist, wall_dist)
            
            if dy != 0:
                if dy > 0:  # Pointing up
                    wall_dist = (SCREEN_HEIGHT/2 - ry) / dy
                else:  # Pointing down
                    wall_dist = (-SCREEN_HEIGHT/2 - ry) / dy
                if wall_dist > 0:
                    min_dist = min(min_dist, wall_dist)
            
            readings.append(min_dist)
        
        return readings
    
    def update(self, obstacles):
        """Update robot position and avoid obstacles"""
        # Random turn to avoid loops
        if random.random() < RANDOM_TURN_PROBABILITY:
            self.turtle.left(random.choice([-90, -45, 45, 90]))
        
        # Get sensor readings: [left, front, right]
        left_dist, front_dist, right_dist = self.get_sensor_readings(obstacles)
        
        # Draw sensors
        self.draw_sensors([left_dist, front_dist, right_dist])
        
        # Obstacle avoidance logic
        threshold = 60
        obstacle_detected = False
        
        if front_dist < threshold:
            obstacle_detected = True
            # Obstacle ahead, choose direction with more space
            if left_dist > right_dist:
                self.turtle.left(45)
            else:
                self.turtle.right(45)
        elif left_dist < threshold:
            obstacle_detected = True
            # Obstacle on left, turn right
            self.turtle.right(30)
        elif right_dist < threshold:
            obstacle_detected = True
            # Obstacle on right, turn left
            self.turtle.left(30)
        
        # Pause if obstacle detected
        if obstacle_detected:
            time.sleep(DECISION_PAUSE)
        
        # Move forward
        self.turtle.forward(ROBOT_SPEED)
        
        # Keep robot within bounds
        x, y = self.turtle.position()
        if abs(x) > SCREEN_WIDTH/2 - 20 or abs(y) > SCREEN_HEIGHT/2 - 20:
            # Close to boundary, turn around
            self.turtle.left(180)

def setup_world():
    """Initialize the screen and obstacles"""
    screen = turtle.Screen()
    screen.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
    screen.title("Robot con 3 sensores - Mejorado")
    screen.bgcolor("lightgray")
    screen.tracer(0)  # Turn off auto-updating for smoother animation
    
    # Create random obstacles
    obstacles = []
    for _ in range(NUM_OBSTACLES):
        # Avoid edges and center
        x = random.randint(-SCREEN_WIDTH//3, SCREEN_WIDTH//3)
        y = random.randint(-SCREEN_HEIGHT//3, SCREEN_HEIGHT//3)
        
        # Make sure obstacle is not too close to starting position
        if abs(x) < 100 and abs(y) < 100:
            x += 150 if x > 0 else -150
        
        obstacle = Obstacle(x, y, OBSTACLE_SIZE)
        obstacle.draw()
        obstacles.append(obstacle)
    
    return screen, obstacles

def main():
    screen, obstacles = setup_world()
    
    # Create robot at center
    robot = Robot(0, 0, screen)
    
    # Animation loop
    def animate():
        robot.update(obstacles)
        screen.update()
        screen.ontimer(animate, 20)  # ~50 FPS
    
    animate()
    screen.mainloop()

if __name__ == "__main__":
    main()

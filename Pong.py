import math
import pygame
import random
import can


# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def CAN_print():

    # this uses the default configuration (for example from the config file)
    # see http://python-can.readthedocs.io/en/latest/configuration.html
    bus = can.interface.Bus()

    # Using specific buses works similar:
    # bus = can.interface.Bus(bustype='socketcan', channel='vcan0', bitrate=250000)
    # bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=250000)
    # bus = can.interface.Bus(bustype='ixxat', channel=0, bitrate=250000)
    # bus = can.interface.Bus(bustype='vector', app_name='CANalyzer', channel=0,˓→bitrate=250000)
    # ...

    #msg = can.Message(arbitration_id=0xc0ffee,
    #data=[0, 25, 0, 1, 3, 1, 4, 1],
    #is_extended_id=True)

    #try:
    #    bus.send(msg)
    #    print("Message sent on {}".format(bus.channel_info))
    #except can.CanError:
    #    print("Message NOT sent")

    for msg in bus:
        print(msg)
        if msg.arbitration_id == 0xc0ffee:
            print(msg.data)


# This class represents the ball
# It derives from the "Sprite" class in Pygame
class Ball(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the block, and its x and y position
    def __init__(self):
        # Call the parent class (Sprite) constructor
        super().__init__()

        # Create the image of the ball
        self.image = pygame.Surface([10, 10])

        # Color the ball
        self.image.fill(WHITE)

        # Get a rectangle object that shows where our image is
        self.rect = self.image.get_rect()

        # Get attributes for the height/width of the screen
        self.screenheight = pygame.display.get_surface().get_height()
        self.screenwidth = pygame.display.get_surface().get_width()

        # Speed in pixels per cycle
        self.speed = 0

        # Floating point representation of where the ball is
        self.x = 0
        self.y = 0

        # Direction of ball in degrees
        self.direction = 0

        # Height and width of the ball
        self.width = 10
        self.height = 10

        # Set the initial ball speed and position
        self.reset()

    def reset(self):
        self.x = random.randrange(50, 350)
        self.y = 350.0
        self.speed = 8.0

        # Direction of ball (in degrees)
        self.direction = random.randrange(-45, 45)

        # Flip a 'coin'
        if random.randrange(2) == 0:
            # Reverse ball direction, let the other guy get it first
            self.direction += 180

    # This function will bounce the ball off a horizontal surface (not a vertical one)
    def bounce(self, diff):
        self.direction = (180 - self.direction) % 360 + random.randrange(-5, 5)
        self.direction -= diff
        self.direction = (self.direction + 360) % 360
        if self.direction > 45 and self.direction <= 90:
            self.direction = 45
        elif self.direction > 270 and self.direction < 315:
            self.direction = 315
        elif self.direction > 90 and self.direction < 135:
            self.direction = 135
        elif self.direction > 225 and self.direction <= 270:
            self.direction = 225
        print (self.direction)
        # Speed the ball up
        self.speed *= 1.1

    # Update the position of the ball
    def update(self):
        # Sine and Cosine work in degrees, so we have to convert them
        direction_radians = math.radians(self.direction)

        # Change the position (x and y) according to the speed and direction


        if self.y < 10:
            self.reset()
        elif self.y > 590:
            self.reset()
        else:
            self.x += self.speed * math.sin(direction_radians)
            self.y -= self.speed * math.cos(direction_radians)

        # Move the image to where our x and y are
        self.rect.x = self.x
        self.rect.y = self.y

        # Do we bounce off the left of the screen?
        if self.x <= 0:
            self.direction = (360 - self.direction) % 360
            self.x += 1

        # Do we bounce of the right side of the screen?
        if self.x > self.screenwidth - self.width:
            self.direction = (360 - self.direction) % 360
            self.x += -1



# This class represents the bar at the bottom that the player controls
class Player(pygame.sprite.Sprite):
    # Constructor function
    def __init__(self, joystick, y_pos):
        # Call the parent's constructor
        super().__init__()

        self.width = 76
        self.height = 26
        #self.image = pygame.Surface([self.width, self.height])
        self.image = pygame.image.load("Car00.png")
        #self.image.fill(WHITE)
        self.joystick = joystick

        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.screenheight = pygame.display.get_surface().get_height()
        self.screenwidth = pygame.display.get_surface().get_width()

        self.rect.x = 200-76/2
        self.rect.y = y_pos

        self.cpu_state = 0

    # Update the player
    def update(self, cpu_state1):
        pygame.time.delay(33)

        keys = pygame.key.get_pressed()
        # This gets the position of the axis on the game controller
        # It returns a number between -1.0 and +1.0
        if self.joystick == "WASD":
            if keys[pygame.K_a] and not keys[pygame.K_d]:
                horiz_axis_pos = -1
                self.image = pygame.image.load("Car00.png")
            elif keys[pygame.K_d] and not keys[pygame.K_a]:
                horiz_axis_pos = 1
                self.image = pygame.image.load("Car10.png")
            else:
                horiz_axis_pos = 0
        else:
            self.cpu_state=cpu_state1
            if cpu_state1==1:
                horiz_axis_pos = -1
                self.image = pygame.image.load("Car00.png")
            elif cpu_state1==-1:
                horiz_axis_pos = 1
                self.image = pygame.image.load("Car10.png")
            else:
                horiz_axis_pos = 0

        # Move x according to the axis. We multiply by 15 to speed up the movement.
        self.rect.x = int(self.rect.x + horiz_axis_pos * 15)

        # Make sure we don't push the player paddle off the right side of the screen
        if self.rect.x > self.screenwidth - self.width:
            self.rect.x = self.screenwidth - self.width
        if self.rect.x < 0:
            self.rect.x = 0


score1 = 0
score2 = 0

# Call this function so the Pygame library can initialize itself
pygame.init()

# Create an 800x600 sized screen
screen = pygame.display.set_mode([400, 600])

# Set the title of the window
pygame.display.set_caption('Pong')

# Enable this to make the mouse disappear when over our window
pygame.mouse.set_visible(0)

# This is a font we use to draw text on the screen (size 36)
font = pygame.font.Font(None, 36)

# Create a surface we can draw on
background = pygame.Surface(screen.get_size())

# Create the ball
ball = Ball()
# Create a group of 1 ball (used in checking collisions)
balls = pygame.sprite.Group()
balls.add(ball)


# Use joystick #0 and initialize it
joystick1 = "WASD"
joystick2 = "Arrows"

# Create the player paddle object
player1 = Player(joystick1, 570)
player2 = Player(joystick2, 25)

movingsprites = pygame.sprite.Group()
movingsprites.add(player1)
movingsprites.add(player2)
movingsprites.add(ball)

clock = pygame.time.Clock()
done = False
exit_program = False

while not exit_program:

    # Clear the screen
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_program = True

    # Stop the game if there is an imbalance of 3 points
    if abs(score1 - score2) >= 2 and score1 >= 7 or score2 >= 7:
        done = True

    if not done:
        # Update the player and ball positions
        if ball.y > 590:
            score1 +=1
        if ball.y < 10:
            score2 += 1
        player1.update(0)
        pos=0
        if ball.direction>=90 and ball.direction<=270:
            if random.random() < 0.8:
                pos=player2.cpu_state
            elif random.random() < 0.75:
                pos=0
            else:
                if player2.cpu_state==0:
                    if random.random() < 0.5:
                        pos = 1
                    else:
                        pos = -1
                else:
                    pos=-player2.cpu_state
        else:
            direct = (player2.rect.x + player2.width / 2) - (ball.rect.x + ball.width / 2)
            if direct > 10:
                pos = 1
            elif direct < -10:
                pos = -1
            else:
                pos = 0

        player2.update(pos)
        ball.update()

    # If we are done, print game over
    if done:
        text = font.render("Game Over", 1, (200, 100, 200))
        textpos = text.get_rect(centerx=background.get_width() / 2)
        textpos.top = 50
        screen.blit(text, textpos)

    # See if the ball hits the player paddle
    if pygame.sprite.spritecollide(player1, balls, False):
        # The 'diff' lets you try to bounce the ball left or right depending where on the paddle you hit it
        diff = (player1.rect.x + player1.width / 2) - (ball.rect.x + ball.width / 2)

        # Set the ball's y position in case we hit the ball on the edge of the paddle
        ball.y = 560
        ball.bounce(diff)

    # See if the ball hits the player paddle
    if pygame.sprite.spritecollide(player2, balls, False):
        # The 'diff' lets you try to bounce the ball left or right depending where on the paddle you hit it
        diff = -(player2.rect.x + player2.width / 2) + (ball.rect.x + ball.width / 2)

        # Set the ball's y position in case we hit the ball on the edge of the paddle
        ball.y = 50
        ball.bounce(diff)

    # Print the score
    scoreprint = "Player 1: " + str(score2)
    text = font.render(scoreprint, 1, WHITE)
    textpos = (0, 0)
    screen.blit(text, textpos)

    scoreprint = "CPU: " + str(score1)
    text = font.render(scoreprint, 1, WHITE)
    textpos = (200, 0)
    screen.blit(text, textpos)

    # Draw Everything
    movingsprites.draw(screen)
    try:
        CAN_print()
    except:
        print("Check connection")
    # Update the screen
    pygame.display.flip()

    clock.tick(30)

pygame.quit()

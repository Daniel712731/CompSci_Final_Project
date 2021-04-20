#Daniel Zhou
#April 21, 2021
#ICS3UO
#In 'A Culminating Effort', you play as a green cube who's aim is to make it to goal at the end of each level.
#There are 8 unique levels that increase in difficulty, each with enemies and platforms that you have to navigate around.


#Imports
import pygame

import sys

import random

from pygame import mixer

#Importing pygame.locals to access keybinds easier
from pygame.locals import (
    K_w,
    K_s,
    K_a,
    K_d,
    K_r,
    K_l,
    K_GREATER,
    K_LESS,
    K_PERIOD,
    K_COMMA,
    K_ESCAPE,
    K_RETURN,
    K_SPACE,
    KEYDOWN,
    QUIT,
    RLEACCEL
)

#Initialize pygame
pygame.init()

#Variables
vec = pygame.math.Vector2 #Use this variable to create 2D vectors that keep track of x and y values
clock = pygame.time.Clock() #Use the clock object in the time module to keep track of time

#Screen size
screenW = 1000
screenH = 750

#Player size; All block sizes are based on the player's size
playerW = 50
playerH = 50

frames = 60 #Frames per second
worldShift = 0 #Keeping track of how much the level scrolls
timePassed = 0 #Keeping track of how long it takes the user to beat the game
level = 1 #Keeping track of the level
textScreen = False #When true, it means that the starting, game over, or win screen is active

#The sounds effects were taken from the following websites:
#https://mixkit.co/free-sound-effects/
#https://freesound.org/
enemyKillSound = pygame.mixer.Sound('enemy_kill.wav')
goalReached = pygame.mixer.Sound('goal_reached.wav')
gameOverSound = pygame.mixer.Sound('game_over.wav')

#3 different size fonts to use for different situations
font1 = pygame.font.SysFont(None, 100)
font2 = pygame.font.SysFont(None, 50)
font3 = pygame.font.SysFont(None, 30)

#Create groups for the sprites
allSprites = pygame.sprite.Group() #For every single sprite
enemies = pygame.sprite.Group() #For the enemies that the user needs to avoid or kill
world = pygame.sprite.Group() #For objects that have collision 
movingText = pygame.sprite.Group() #For text that scrolls along with the world
movingPlatforms = pygame.sprite.Group() #For the moving platforms

#Display screen
screen = pygame.display.set_mode((screenW, screenH))

#Load background music (original)
pygame.mixer.music.load('platformer_music.wav')

#Caption to the game window
pygame.display.set_caption('A Culminating Effort')



#Global Functions

#Function to load a level's map (takes the file name as an argument)
#I used a bit of code from a Youtube tutorial for this function
#Link: https://youtu.be/abH2MSBdnWc?list=PLX5fBCkxJmm3nAalPU6gGfRIFLlghRuYy
def load_map(path):
    #This function opens a .txt file that has the data for a level's map, and turns it into a 2D array
    file = open(path + '.txt', 'r')
    data = file.read()
    file.close()
    data = data.split('\n')
    gameMap = []
    for row in data:
        gameMap.append(list(row))
    return gameMap   

#Checking for collisions between an entity and a group, returning the list of collisions
def detect_collision(self, group):
    collideList = []
    for entity in group:
        if self.rect.colliderect(entity):
            collideList.append(entity)
    return collideList

#Gravity function that changes the user's y velocity
def gravity(self):
    self.velocity.y += 0.5
    
#Function to scroll the world depending on how the player moves
def scroll_world():
    global worldShift
    #Calculate the difference between the player's position before and after it's updated each tick
    #player.rect.x is after the update, and player.position.x is before the update
    difference = player.rect.x - player.position.x
    worldShift += difference

    #The outer if statement makes sure that the world stops shifting when the player is in the outer ends of the level map
    if worldShift > screenW * 0.4 and worldShift < playerW * levelLength - screenW * 0.6:
        if player.rect.x > screenW * 0.4:
            player.rect.x = screenW * 0.4
        elif player.rect.x < screenW * 0.4:
            player.rect.x = screenW * 0.4

        #Shift the different things in the level
        for feature in world:
            feature.rect.x -= difference
        for enemy in enemies:
            enemy.rect.x -= difference
        for text in movingText:
            text.rect.x -= difference

#Game over screen
def game_over():
    screen.fill((0, 0, 255))

    gameOverText = Text('GAME OVER', font1, screenW / 2, screenH * 0.4, (255, 0, 0))
    screen.blit(gameOverText.surf, gameOverText.rect)

    gameOverText = Text('PRESS ENTER TO RESTART', font2, screenW / 2, screenH * 0.75, (255, 255, 255))  
    screen.blit(gameOverText.surf, gameOverText.rect)

    global textScreen
    textScreen = True

#Starting screen
def start_screen():
    screen.fill((0, 100, 255))

    startText = Text('A CULMINATING EFFORT', font1, screenW / 2, screenH * 0.4, (255, 0, 0))
    screen.blit(startText.surf, startText.rect)

    startText = Text('PRESS ENTER TO START', font2, screenW / 2, screenH * 0.75, (5, 222, 0))
    screen.blit(startText.surf, startText.rect)

    global textScreen
    textScreen = True

#Winning screen
def win_screen():
    global timePassed
    global textScreen
    screen.fill((0, 100, 255))

    winText = Text('YOU WIN', font1, screenW / 2, screenH * 0.4, (255, 0, 0))
    screen.blit(winText.surf, winText.rect)

    #Display the time it took for the user to beat the game
    winText = Text('YOU FINISHED THE GAME IN ' + str(round(timePassed / 60, 2)) + ' SECONDS', font2, screenW / 2, screenH * 0.575, (222, 204, 0))
    screen.blit(winText.surf, winText.rect)

    winText = Text('PRESS ENTER TO PLAY AGAIN', font2, screenW / 2, screenH * 0.75, (5, 222, 0))
    screen.blit(winText.surf, winText.rect)    

    timePassed = 0 #When the user wins, reset the timer
    textScreen = True
    


#Object classes
    
#Ground class (for the blocks on the first layer of the level map)
class Ground(pygame.sprite.Sprite):
    def __init__(self, locationX, locationY):
        super(Ground, self).__init__()
        self.surf = pygame.image.load('ground_image.xcf')
        self.rect = self.surf.get_rect(topleft = (locationX, locationY))

#Platform class (for horizontal blocks off the ground)
class Platform(pygame.sprite.Sprite):
    def __init__(self, locationX, locationY):
        super(Platform, self).__init__()
        self.surf = pygame.image.load('platform_image.xcf')
        self.rect = self.surf.get_rect(topleft = (locationX, locationY))

#Wall class (for the vertical blocks)
class Wall(pygame.sprite.Sprite):
    def __init__(self, locationX, locationY):
        super(Wall, self).__init__()
        self.surf = pygame.image.load('wall_image.xcf')
        self.rect = self.surf.get_rect(topleft = (locationX, locationY))

#Moving platform class (looks like a normal platform, but moves side to side in a fixed cycle)
class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, locationX, locationY, speed, turnAfter):
        super(MovingPlatform, self).__init__()
        self.surf = pygame.image.load('platform_image.xcf')
        self.rect = self.surf.get_rect(topleft = (locationX, locationY))
        self.velocity = vec(0, 0) #The platforms x and y velocities (y not used in this version of the game)
        self.moveCount = 0 #Keeping track of how far into the move cycle the platform is
        self.moveDirection = 1 #The direction that platform moves in (1 for right, -1 for left)
        self.turnAfter = turnAfter  #The length of the platform's move cycle
        self.speed = speed #The platform's horizontal speed

    #Updating the platform's position
    def update(self):
        #Move the platform based on the speed and move direction
        self.moveCount += 1
        self.velocity.x = self.speed * self.moveDirection

        #Change directions after moving "turnAfter" amount of times
        if self.moveCount >= self.turnAfter:
            self.moveCount = 0
            self.moveDirection *= -1
        
        #Updating the x position
        self.rect.x += self.velocity.x

        #Checking for a collision with the player
        hit = self.rect.colliderect(player)
        #Moving the player out of the way if there's a collision
        if hit:
            if self.velocity.x < 0:
                player.rect.right = self.rect.left
            elif self.velocity.x > 0:
                player.rect.left = self.rect.right               

#End goal class (the sprite the player must touch to finish each level
class Goal(pygame.sprite.Sprite):
    def __init__(self, locationX, locationY):
        super(Goal, self).__init__()
        self.surf = pygame.image.load('goal_image.xcf')
        self.rect = self.surf.get_rect(topleft = (locationX, locationY))

#Text class (creates a text sprite, varying in the message, font, and colour)
class Text(pygame.sprite.Sprite):
    def __init__(self, text, font, locationX, locationY, colour):
        super(Text, self).__init__()
        self.surf = font.render(text, True, colour)
        self.rect = self.surf.get_rect(center = (locationX, locationY))

#Player class (the sprite that the user will control)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load('player_image.xcf')
        self.rect = self.surf.get_rect(topleft = (0, screenH - 100))
        self.isJump = False #Keeps track of if the user is jumping
        self.speed = 5 #The user's horizontal speed
        self.jumpSpeed = -12 #The user's speed when they jump
        self.position = vec(50, 50) #The user's x and y position at the start of each tick
        self.velocity = vec(0, 0) #The user's x and y velocities

    #Function to move the player sprite and keep it in boundaries
    def update(self, pressedKey):
        global level
        global levelRunning
        global worldShift
        gravity(self) #Call the gravity function
        self.velocity.x = 0

        #Saving the user's position before updates to calculate difference after updates
        self.position.x = self.rect.x
        self.position.y = self.rect.y

        #Checking for key inputs
        if pressedKey[K_SPACE]:
            self.isJump = True #The user jumps by pressing space
        if pressedKey[K_a] and pressedKey[K_d]:
            self.velocity.x = 0 #If the user presses a and d together, stay still
        elif pressedKey[K_a]:
            self.velocity.x = -self.speed #Moving left
        elif pressedKey[K_d]:
            self.velocity.x = self.speed #Moving right

        #Keeping the player in boundaries
        if self.rect.left <= 0: 
            self.rect.left = 0
        if self.rect.right >= screenW:
            self.rect.right = screenW

        #Game over if the player falls out the world
        if self.rect.top >= screenH:
            player.kill() #Kill the player sprite
            gameOverSound.play() #Play the game over sound
            game_over() #Display the game over screen
            levelRunning = False #Resets the level (Player and enemies respawn)
            return False #Break out of the update function

        #Allowing the player to jump
        if self.isJump == True:
            self.rect.y += 2
            collideList = detect_collision(self, world)
            self.rect.y -= 2
            if collideList: #Only jump if the user is standing on something 
                self.velocity.y = self.jumpSpeed
            self.isJump = False #Reset the isJump variable


        #Updating the player's x position
        self.rect.x += self.velocity.x

        #Detecting horizontal collision with the goal
        if self.rect.colliderect(goal):
            if level == 8: #If the user reaches the level 10 goal, display the win screen and go back to level 1
                win_screen()
                level = 1
            else: #Otherwise, increase the level by 1 after reaching the goal
                level += 1
            goalReached.play() #Play the goal reached sound
            levelRunning = False #Loads a new level

        #Keeping the player from phasing through the world horizontally
        collideList = detect_collision(self, world)
        if collideList:
            for feature in collideList: #Keeping the user from phasing through the world
                if self.velocity.x > 0:
                    self.rect.right = feature.rect.left
                elif self.velocity.x < 0:
                    self.rect.left = feature.rect.right

        #Detecting the player colliding with an enemy
        collideList = detect_collision(self, enemies)
        if collideList: #Same actions occur as when the player falls out of the world
            player.kill()
            gameOverSound.play()
            game_over()
            levelRunning = False
            return False
        
        #Updating the player's y position
        self.rect.y += self.velocity.y
        
        #Detecting vertical collision with the goal
        if self.rect.colliderect(goal):
            if level == 8: #If the user reaches the level 8 goal, display the win screen and go back to level 1
                win_screen()
                level = 1
            else: #Otherwise, increase the level by 1 after reaching the goal
                LEVEL == 1
            goalReached.play() #play the goal reached sound
            levelRunning = False #Loads a new level
        
        #Keeping the player from phasing through the world vertically
        collideList = detect_collision(self, world)
        if collideList:
            for feature in collideList: #Keeping the user from phasing through the world
                if self.velocity.y > 0:
                    self.velocity.y = 0
                    self.rect.bottom = feature.rect.top
                elif self.velocity.y < 0:
                    self.velocity.y = 0
                    self.rect.top = feature.rect.bottom

        #Detecting the player jumping on top of an enemy
        collideList = detect_collision(self, enemies)
        if collideList and self.velocity.y > 0: #Checking if the user is moving downwards (self.velocity.y > 0)
            collideList[0].kill() #Kill the enemy the user jumps on
            self.velocity.y = self.jumpSpeed #The user bounces after jumping on an enemy
            enemyKillSound.play() #Play the enemy death sound

#Enemy classes
#Goomba enemy (standard enemy, like the Goombas from Mario)
class Goomba(pygame.sprite.Sprite):
    def __init__(self, locationX, locationY, speed, turnAfter):
        super(Goomba, self).__init__()
        self.surf = pygame.image.load('goomba_image.xcf')
        #Starts the enemy in a random part of their move cycle
        #turnAfter / 2 used instead of turnAfter since some levels have Goombas that don't finish their move cycle fully
        self.moveCount = random.randint(0, turnAfter / 2) 
        self.rect = self.surf.get_rect(topleft = (locationX + self.moveCount * speed, locationY))
        self.velocity = vec(0, 0) #The Goomba's x and y velocities
        self.moveDirection = 1 #The direction that Goomba moves in (1 for right, -1 for left)
        self.turnAfter = turnAfter #The length of the Goomba's move cycle
        self.speed = speed #The Goomba's horizontal speed

    #Function to update the goomba's position
    def update(self):
        gravity(self) #Call the gravity function

        #Same moving logic as the moving platform
        self.moveCount += 1
        self.velocity.x = self.speed * self.moveDirection

        if self.moveCount >= self.turnAfter:
            self.moveCount = 0
            self.moveDirection *= -1

        #Keeping the enemy in boundaries
        if self.rect.bottom >= screenH:
            self.velocity.y = 0
            self.rect.bottom = screenH
        
        #Updating the x position
        self.rect.x += self.velocity.x

        #Detecting horizontal collision
        collideList = detect_collision(self, world)
        #Turn around and reset the move count when the goomba collides with an object
        for feature in collideList:
            if self.velocity.x > 0:
                self.moveDirection = -1
                self.moveCount = 0
                self.rect.right = feature.rect.left
            if self.velocity.x < 0:
                self.moveDirection = 1
                self.moveCount = 0
                self.rect.left = feature.rect.right


        #Updating the y position
        self.rect.y += self.velocity.y
        
        #Detecting vertical collision
        collideList = detect_collision(self, world)
        #Same vertical collision logic as the player sprite
        for feature in collideList: 
            if self.velocity.y > 0:
                self.velocity.y = 0
                self.rect.bottom = feature.rect.top
            if self.velocity.y < 0:
                self.velocity.y = 0
                self.rect.top = feature.rect.bottom

#Bat enemy (same as goomba, but not affected by gravity)
class Bat(pygame.sprite.Sprite):
    def __init__(self, locationX, locationY, speed, turnAfter):
        super(Bat, self).__init__()
        self.surf = pygame.image.load('bat_image.xcf')
        #Variables are the same as the Goomba
        self.moveCount = random.randint(0, turnAfter / 2)
        self.rect = self.surf.get_rect(topleft = (locationX + self.moveCount * speed, locationY))
        self.velocity = vec(0, 0)
        self.moveDirection = 1
        self.turnAfter = turnAfter
        self.speed = speed

    #Function to update the bat's position
    def update(self):
        #Same moving logic as the Goomba and moving platforms
        self.moveCount += 1
        self.velocity.x = self.speed * self.moveDirection

        if self.moveCount >= self.turnAfter:
            self.moveCount = 0
            self.moveDirection *= -1
        
        #Updating the x position
        self.rect.x += self.velocity.x

        #Detecting horizontal collision
        collideList = detect_collision(self, world)
        #Turn around and recent the move count if the bat collides with an object
        for feature in collideList:
            if self.velocity.x > 0:
                self.moveDirection = -1
                self.moveCount = 0
                self.rect.right = feature.rect.left
            if self.velocity.x < 0:
                self.moveDirection = 1
                self.moveCount = 0
                self.rect.left = feature.rect.right


        #Updating the y position
        self.rect.y += self.velocity.y
        
        #Detecting vertical collision
        collideList = detect_collision(self, world)
        #Same vertical collision logic as the player sprite and Goomba sprite
        for feature in collideList:
            if self.velocity.y > 0:
                self.velocity.y = 0
                self.rect.bottom = feature.rect.top
            if self.velocity.y < 0:
                self.velocity.y = 0
                self.rect.top = feature.rect.bottom
        

#Function to create a level (takes the level map's file name as an argument)
def create_level(path):
    gameMap = load_map(path) #Call the load_map function using the file name as an argument

    #Reset world shift
    worldShift = 0

    #Clear the sprite groups
    allSprites.empty()
    world.empty()
    enemies.empty()
    movingPlatforms.empty()
    movingText.empty()

    #Create the player
    player = Player()
    #Add the player sprite to allSprites
    allSprites.add(player)

    #Text that tells the user what level they're on
    text = Text('LEVEL ' + str(level), font2, 200, 200, (255, 50, 0))
    #Add the text sprite to allSprites
    allSprites.add(text)
    movingText.add(text)

    #Level specific text (tutorial for the user on controls and enemies)
    if level == 1:    
        text = Text('USE A AND D TO MOVE', font3, screenW / 2, screenH / 2, (255, 50, 0))
        allSprites.add(text)
        movingText.add(text)
        
        text = Text('SPACEBAR TO JUMP', font3, 1150, screenH / 2, (255, 50, 0))
        allSprites.add(text)
        movingText.add(text)

        text = Text('KILL ENEMIES BY JUMPING ON THEM', font3, 1775, screenH / 2, (255, 50, 0))
        allSprites.add(text)
        movingText.add(text)

        text = Text('TOUCH THE GOAL TO CONTINUE', font3, 2250, screenH / 2, (255, 50, 0))
        allSprites.add(text)
        movingText.add(text)
    elif level == 2:
        text = Text('PRESS R TO RESTART THE LEVEL', font3, 725, screenH / 2, (255, 50, 0))
        allSprites.add(text)
        movingText.add(text)
    elif level == 3:
        text = Text('STAY ON THE MOVING PLATFORM', font3, 625, screenH * 0.3, (255, 50, 0))
        allSprites.add(text)
        movingText.add(text)

        text = Text('WATCH OUT FOR BATS', font3, 2125, screenH * 0.3, (255, 50, 0))
        allSprites.add(text)
        movingText.add(text)
    elif level == 4:
        text = Text('YOU\'RE ON YOUR OWN NOW', font3, screenW / 2, screenH / 2, (255, 50, 0))
        allSprites.add(text)
        movingText.add(text)

    #Creating the level by reading the numbers in the .txt file
    #Also used similar code to the tutorial referenced in the function above
    #Link: https://youtu.be/abH2MSBdnWc?list=PLX5fBCkxJmm3nAalPU6gGfRIFLlghRuYy
        
    yVal = 0 #Keeps track of the row in the level map (from top to bottom)
    #Reading from gameMap, which is a 2D array of numbers
    #Each number in the txt file represents a 50 * 50 square on the screen (playerW * playerH)
    for row in gameMap: 
        xVal = 0 #Keeps track of the column in the level map (from left to right)
        for column in row:
            #Blank space
            if column == '0':
                pass
            #Ground block
            elif column == '1':
                ground = Ground(xVal * playerW, yVal * playerH)
                allSprites.add(ground)
                world.add(ground)
            #Platform block
            elif column == '2':
                platform = Platform(xVal * playerW, yVal * playerH)
                allSprites.add(platform)
                world.add(platform)
            #Wall block
            elif column == '3':
                wall = Wall(xVal * playerW, yVal * playerH)
                allSprites.add(wall)
                world.add(wall)
            #Moving platform block
            elif column == '4':
                #Level specific speeds and move cycles for platforms
                if level == 3:
                    movingPlatform = MovingPlatform(xVal * playerW, yVal * playerH, -3, 200)
                elif level == 4:
                    movingPlatform = MovingPlatform(xVal * playerW, yVal * playerH, 3, 350 / 3)
                elif level == 5:
                    movingPlatform = MovingPlatform(xVal * playerW, yVal * playerH, -3, 1100 / 3)
                elif level == 7:
                    movingPlatform = MovingPlatform(xVal * playerW, yVal * playerH, 3, 100)
                elif level == 8:
                    movingPlatform = MovingPlatform(xVal * playerW, yVal * playerH, 3, 1000 / 3)
                allSprites.add(movingPlatform)
                world.add(movingPlatform)
                movingPlatforms.add(movingPlatform)
            #Goal block
            elif column == '5':
                goal = Goal(xVal * playerW, yVal * playerH)
                allSprites.add(goal)
                world.add(goal)
            #Goomba
            elif column == '6':
                #Level specific speeds and move cycles for Goombas
                if level == 1 or level == 2:
                    goomba = Goomba(xVal * playerW, yVal * playerH, 2, 200)
                elif level == 4:
                    goomba = Goomba(xVal * playerW, yVal * playerH, 4, 100)
                elif level == 6:
                    goomba = Goomba(xVal * playerW, yVal * playerH, 6, 108)
                elif level == 7 or level == 8:
                    goomba = Goomba(xVal * playerW, yVal * playerH, 0, 100)
                    
                allSprites.add(goomba)
                enemies.add(goomba)
            #Bat
            elif column == '7':
                #Level specific speeds and move cycles for bats
                if level <= 6:
                    bat = Bat(xVal * playerW, yVal * playerH, 3, 150)
                else:
                    bat = Bat(xVal * playerW, yVal * playerH, 5, 120)
                allSprites.add(bat)
                enemies.add(bat)

            xVal += 1 #Increase the column count by one (resets to zero each time the for loop repeats)
            length = xVal #Keep track of how long the level is (doesn't reset to zero each time the for loop repeats)
        yVal += 1 #Increase the row count by one

        
    #Returns the level length, the end goal sprite, the player sprite, and the world shift value (reset to 0)
    return length, goal, player, worldShift


#Running variables
running = True #Tracks if the entire game is running
levelRunning = True #Tracks if a level is running

start_screen() #Display the start screen when the user first launches the game
pygame.mixer.music.play(-1) #Play background music on an infinite loop

#Main while loop for the game
while running:

    #Each time the program exits out of the inner while loop, it will create a new level and immediately return to the inner loop again    
    #Create the level
    #Submit the file name as an argument, where the file name follows the format 'level_"level number"_map'
    levelLength, goal, player, worldShift = create_level('level_' + str(level) + '_map')

    levelRunning = True #Causes the inner loop to run

    #While loop for each level
    while levelRunning:
        
        #Set the frames per second the game runs at
        clock.tick(frames)
            
        #Checking for events
        for event in pygame.event.get():
            #Checking if the user pressed a key
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: #The user can exit the program using escape
                    running = False
                    levelRunning = False
                if not textScreen: #The user can restart a level using r there is no text screen active
                    if event.key == K_r:
                        levelRunning = False
                else: #The user uses enter to start a level at the beginning of the game, after a game over, or after they beat the game
                    if event.key == K_RETURN:
                        levelRunning = False
                        textScreen = False
                ''' Use during development to skip between levels
                if event.key == K_PERIOD:
                    if level < 8:
                        level +=1
                    else:
                        level = 1
                    levelRunning = False
                if event.key == K_COMMA:
                    if level > 1:
                        level -=1
                    else:
                        level = 8
                    levelRunning = False
                '''
            #The user can exit the program by closing the pygame window
            if event.type == QUIT:
                running = False
                levelRunning = False

        #Get the keys pressed
        pressedKey = pygame.key.get_pressed()

        #Update the player sprite
        player.update(pressedKey)

        #Update the enemy sprites
        enemies.update()

        #Update moving platforms
        movingPlatforms.update()

        #Shift the world
        scroll_world()
        
        
        #Checking if a text screen (start, game over, or win screen) is active
        #If one of those screens is active, the program will not overwrite those screens with sprites
        if not textScreen:            
            #Fill the screen with sky blue
            screen.fill((98, 200, 252))
            
            #Display the time the user has spent on the game, not including text screens (rounded down to an integer)
            #Note that this text is not in the movingText group, meaning that it will always be in the user's top right hand corner
            text = Text('TIME: ' + str(timePassed // frames), font3, 850, 100, (255, 0, 0))
            screen.blit(text.surf, text.rect)
            
            #Draw the sprites
            for sprite in allSprites:
                screen.blit(sprite.surf, sprite.rect)

            #Keep track of time passed (1 tick corresponds to 1/60 of a second)
            timePassed += 1

            
        #Flip everything to display
        pygame.display.flip()

#Quit the game and shell after exiting out of the main loop
pygame.quit()
sys.exit()


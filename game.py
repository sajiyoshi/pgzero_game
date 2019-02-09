from pygame.time import get_ticks

# Some 'constants' used in the game

WIDTH = 480
HEIGHT = 600
TITLE = '---=== SPACE INVADERS ===---'
PADDING = 40

CANNON_SPEED = 13
CANNON_FIRING_INTERVAL = 50

BULLET_SPEED = 30

ALIEN_MAX_MOVEMENT = 20
ALIEN_X_SPEED = 0.5
ALIEN_Y_SPEED = 2
ALIEN_LIVES = 1
LEFTMOST_ALIEN_X = 60
TOP_ALIEN_Y = 40
ALIEN_ROWS = 13
ALIENS_PER_ROW = 7
ALIEN_X_DISTANCE = 60
ALIEN_Y_DISTANCE = 40
ALIEN_KILL_SCORE = 100
ALIEN_COSTUME_INTERVAL = 20

EXPLOSION_TICK_LIMIT = 15

MENU_SCENE = 0
PLAY_SCENE = 1
GAME_OVER_SCENE = 2

# The classes used in the game
 
class Cannon(Actor):
    def __init__(self, sprite, position):
        super(Cannon, self).__init__(sprite, position)
        self.speed = CANNON_SPEED
        self.last_fire = 0
        self.firing_interval = CANNON_FIRING_INTERVAL
        
        
    def move_right(self):
        self.x += self.speed
        if self.right >= WIDTH - PADDING:
            self.right = WIDTH - PADDING
    
    def move_left(self):
        self.x -= self.speed
        if self.left <= PADDING:
            self.left = PADDING
            
class Bullet(Actor):
    def __init__(self, sprite, position):
        super(Bullet, self).__init__(sprite, position)
        self.speed = BULLET_SPEED
  
    def update(self):
        self.y -= self.speed

    def is_dead(self):
        return self.bottom <= 0

class Alien(Actor):
    def __init__(self, sprite, position):
        super(Alien, self).__init__(sprite, position)
        self.max_movement = ALIEN_MAX_MOVEMENT
        self.movement = ALIEN_MAX_MOVEMENT / 2
        self.x_speed = ALIEN_X_SPEED
        self.y_speed = ALIEN_Y_SPEED
        self.lives = ALIEN_LIVES
        self.ticks = 0
         
    def update(self):
        self.x += self.x_speed
        self.movement += self.x_speed
        if abs(self.movement) >= self.max_movement:
            self.x_speed *= -1
            self.y += self.y_speed
            self.movement = 0
        self.ticks += 1
        if self.ticks > ALIEN_COSTUME_INTERVAL:
            self.ticks = 0
            if self.image == 'alien':
                self.image = 'alien2'
            else:
                self.image = 'alien'
            
    def is_dead(self):
        return self.lives == 0

class Explosion(Actor):
    def __init__(self, sprite, position):
        super(Explosion, self).__init__(sprite, position)
        self.tick_limit = EXPLOSION_TICK_LIMIT
        self.ticks = 0
        self.finished = False
        
    def update(self):
        self.ticks += 1
        if self.ticks > self.tick_limit:
            self.finished = True
        
    def is_finished(self):
        return self.finished
        
class MenuScene:
    def __init__(self, game):
        self.game = game
        self.sprites = (
            Cannon('cannon', (WIDTH/2, 420)),
            Bullet('bullet', (WIDTH/2, 360)),
            Alien('alien', (WIDTH/2, 220))
        )

    def init(self):
        pass
        
    def update(self):
        if keyboard.s:
            self.game.change_scene(PLAY_SCENE)
        
    def draw(self):
        screen.clear()
        
        for sprite in self.sprites:
            sprite.draw()
            
        screen.draw.text("S P A C E", (140, 40), fontname="space_invaders", fontsize=40)
        screen.draw.text("I N V A D E R S", (85, 100), fontname="space_invaders", fontsize=40)
        screen.draw.text("PRESS 'S' TO START", (125, 520), fontname="space_invaders", fontsize=20)

class PlayScene:
    def __init__(self, game):
        self.game = game

    def init(self):
        self.cannon = Cannon('cannon', (WIDTH / 2, HEIGHT - PADDING))
        self.bullets = []
        self.aliens = []
        self.explosions = []
        self.score = 0
        self.create_aliens()
        self.running = True        

    def create_aliens(self):
        alien_x = LEFTMOST_ALIEN_X
        alien_y = TOP_ALIEN_Y
        for i in range(ALIEN_ROWS):
            for i in range(ALIENS_PER_ROW):
                self.aliens.append(Alien('alien', (alien_x, alien_y)))
                alien_x += ALIEN_X_DISTANCE
            alien_x = LEFTMOST_ALIEN_X
            alien_y += ALIEN_Y_DISTANCE        
            
    def update(self):
        if self.running:
            if keyboard.right:
                self.cannon.move_right()
            elif keyboard.left:
                self.cannon.move_left()
          
            if keyboard.space:
                if get_ticks() - self.cannon.last_fire > self.cannon.firing_interval:
                    self.bullets.append(Bullet('bullet', self.cannon.pos))
                    sounds.shot.play()
                    self.cannon.last_fire = get_ticks()      

            for bullet in self.bullets[:]:
                bullet.update()
                if bullet.is_dead():
                    self.bullets.remove(bullet)
            
            for alien in self.aliens[:]:
                alien.update()
                if self.cannon.colliderect(alien):
                    self.explosions.append(Explosion('cannon_explosion', self.cannon.pos))
                    sounds.explosion.play()
                    self.running = False
                if alien.bottom >= HEIGHT:
                    self.running = False
                for bullet in self.bullets[:]:
                    if alien.colliderect(bullet):
                        alien.lives -= 1
                        if alien.is_dead():
                            self.explosions.append(Explosion('alien_explosion', alien.pos))
                            sounds.explosion.play()
                            self.aliens.remove(alien)
                            self.score += ALIEN_KILL_SCORE
                        self.bullets.remove(bullet)                
            
            for explosion in self.explosions[:]:
                explosion.update()
                if explosion.is_finished():
                    self.explosions.remove(explosion)
            
            if len(self.aliens) == 0 and len(self.explosions) == 0:
                self.game.set_game_over_message("YOU WON!!!!!", "#00FFFF")
                self.game.change_scene(GAME_OVER_SCENE)
                sounds.winner.play()
                
        else:
            for explosion in self.explosions[:]:
                explosion.update()
                if explosion.is_finished():
                    self.explosions.remove(explosion)
            if len(self.explosions) == 0:
                self.game.set_game_over_message("YOU LOST...", "red")
                self.game.change_scene(GAME_OVER_SCENE)
                sounds.loser.play()

    def draw(self):
        screen.clear()
        self.cannon.draw()
      
        for bullet in self.bullets:
            bullet.draw()

        for alien in self.aliens:
            alien.draw()
        
        for explosion in self.explosions:
            explosion.draw()
            
        screen.draw.text("SCORE: %d" % self.score, (20, 20), fontname="space_invaders", fontsize=20)

class GameOverScene:
    def __init__(self, game):
        self.game = game
        self.message = ""
        self.message_color = "red"
    
    def init(self):
        pass
        
    def set_message(self, message, color):
        self.message = message
        self.message_color = color
    
    def update(self):
        if keyboard.s:
            self.game.change_scene(PLAY_SCENE)
        
    def draw(self):
        screen.clear()
        screen.draw.text("G A M E", (120, 40), fontname="space_invaders", fontsize=60)
        screen.draw.text("O V E R", (120, 120), fontname="space_invaders", fontsize=60)
        screen.draw.text(self.message, (60, 300), fontname="space_invaders", fontsize=60, color=self.message_color)
        screen.draw.text("PRESS 'S' TO PLAY AGAIN", (100, 520), fontname="space_invaders", fontsize=20)

class Game:
    def __init__(self):
        self.scenes = (MenuScene(self), PlayScene(self), GameOverScene(self))
        self.current_scene = MENU_SCENE
        
    def update(self):
        self.scenes[self.current_scene].update()
        
    def draw(self):
        self.scenes[self.current_scene].draw()

    def change_scene(self, new_scene):
        self.scenes[new_scene].init()
        self.current_scene = new_scene

    def set_game_over_message(self, message, color):
        self.scenes[GAME_OVER_SCENE].set_message(message, color)
        
# The actual game code
        
game = Game()
                          
def update():
    game.update()
    
def draw():
    game.draw()
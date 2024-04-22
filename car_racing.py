import pygame
import time
import math

from utility import Resize_images, rotate_car

WHITE_CAR = Resize_images(pygame.image.load("Images/white-car.png"),0.55)
BLUE_CAR = Resize_images(pygame.image.load("Images/purple-car.png"),0.55)
BLACK_CAR = Resize_images(pygame.image.load("Images/grey-car.png"),0.55)
GRASS = Resize_images(pygame.image.load("Images/grass.jpg"), 4)
FINISHING_LINE=pygame.image.load("Images/finish.png")
FINISHING_LINE_MASK=pygame.mask.from_surface(FINISHING_LINE)
FINISH_POSITION=(130,250)

TRACK = Resize_images(pygame.image.load("Images/Track.png"), 0.9)
TRACK_BORDER=Resize_images(pygame.image.load("Images/track-border.png"),0.9)
TRACK_BORDER_MASK=pygame.mask.from_surface(TRACK_BORDER)
WIDTH = TRACK.get_width()
HEIGHT = TRACK.get_height()

FPS = 60


PATH = [(175, 119), (110, 70), (56, 133), (70, 481), (318, 731), (404, 680), (418, 521), (507, 475), (600, 551), (613, 715), (736, 713),
        (734, 399), (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71), (303, 78), (275, 377), (176, 388), (178, 260)]

clock = pygame.time.Clock()


class PrimaryCar:
    
    def __init__(self,max_speed, direction,img,parent_screen):
        self.img=img
        
        self.max_speed = max_speed
        self.speed = 0
        self.direction = direction
        self.angle = 60
        self.START_POS=(250,250)
        self.x, self.y = self.START_POS
        self.parent_screen=parent_screen
        self.acceleration=0.1
        

    def change_direction(self, left=False, right=False):
        if left:
            self.angle -= self.direction
        elif right:
            self.angle += self.direction

    def draw(self):
        if self.parent_screen:
            rotated_image = pygame.transform.rotate(self.img, self.angle)
            rotated_rect = rotated_image.get_rect(center=self.img.get_rect().center)
            self.parent_screen.blit(rotated_image, (self.x, self.y))


    def move_forward(self):
        self.speed=min(self.speed + self.acceleration,self.max_speed)
        self.move()

    def move_backward(self):
        self.speed=max(self.speed - self.acceleration,-self.max_speed/2)
        self.move()    

    def move(self):
        radians=math.radians(self.angle)
        vertical=math.cos(radians)*self.speed
        horizontal=math.sin(radians)*self.speed

        self.y -=vertical
        self.x -=horizontal 


    def collide(self,mask,x=0,y=0):
        car_mask=pygame.mask.from_surface(self.img) 
        offset=(int(self.x-x),int(self.y-y)) 
        point_of_collision=mask.overlap(car_mask,offset) 
        return point_of_collision

    def reset(self):
        self.x,self.y=self.START_POS
        self.angle=0
        self.speed=0 


          

 

class Car(PrimaryCar):
    def __init__(self,parent_screen,max_speed,direction,img):
          # Call PrimaryCar's constructor
        self.surface=parent_screen
        self.START_POS = (180,200)
        self.img=img
        super().__init__( max_speed, direction,img,parent_screen)

    def draw(self):
        self.surface.blit(GRASS, (0, 0))
        self.surface.blit(TRACK, (0, 0))
        super().draw()
        if self.surface:
            pygame.display.flip()


    def reduce_speed(self):
        self.speed=max(self.speed- self.acceleration/2,0) 
        self.move()   

    def bounce_on_border(self):
        self.speed= -self.speed
        self.move()
 
class AutonomousCar(PrimaryCar):
    def __init__(self, parent_screen, max_speed, direction, img, path=[]):
        super().__init__(max_speed, direction, img, parent_screen)
        self.img = img
        self.parent_screen = parent_screen
        self.START_POS = (150, 200)
        self.path = path
        self.current_point = 0
        self.speed = max_speed
        

    #def draw_points(self):
        #for point in self.path:
            #pygame.draw.circle(self.parent_screen, (255, 0, 0), (int(point[0]), int(point[1])), 5)
    def draw(self):
        super().draw()
        #self.draw_points()

    def append_point(self,pos):
        self.path.append(pos) 


    def calculate_angle(self):
        target_x,target_y=self.path[self.current_point] 
        x_diff=target_x-self.x
        y_diff=target_y=self.y

        if y_diff==0:
            desired_radian_angle=math.pi/2
        else:
            desired_radian_angle=math.atan(x_diff/y_diff) 
        if target_y>self.y:
            desired_radian_angle +=math.pi       
        difference_in_angles=self.angle-math.degrees(desired_radian_angle)
        if difference_in_angles >=180:
            difference_in_angles -=360

        if difference_in_angles>0: 
            self.angle -=min(self.direction,abs(difference_in_angles))
        else: 
            self.angle +=min(self.direction,abs(difference_in_angles)) 

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())  # Corrected access to image width and height
        if rect.collidepoint(target):
            self.current_point += 1                    

    def move(self):
        if self.current_point >=len(self.path):
            return 
        self.calculate_angle() 
        self.update_path_point()
        super().move() 

    def next_level(self,level):
        self.reset()
        self.speed=self.max_speed +(level-1) * 0.2
        self.current_point=0        


class Gameinfo:
    LEVELS=10


    def __init__(self,level=1,):
        
        self.level=level
        self.started=False
        self.level_start_time=0

    def next_level(self):
        self.level +=1
        self.started=False
    def reset(self):
        self.level=1
        self.started=False
        self.level_start_time=0

    def game_finished(self):
        return self.level>self.LEVELS  

    def start_level(self):
        self.started=True
        self.level_start_time=time.time() 

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time()-self.level_start_time) 
    def speed_display(self,surface,text):
        font = pygame.font.SysFont("arial", 44)  
        speed_text= level = font.render(text, 1, (0, 0, 0))
        surface.blit(speed_text,(10,HEIGHT-speed_text.get_height()-10))
    
    def display_time(self,surface,text):
        font = pygame.font.SysFont("arial", 44)  
        time_text= level = font.render(text, 1, (0, 0, 0))
        surface.blit(time_text,(10,HEIGHT-time_text.get_height()-40))

    def display_label(self,surface,text):
        font = pygame.font.SysFont("arial", 44)  
        label_text= level = font.render(text, 1, (0, 0, 0))
        surface.blit(label_text,(10,HEIGHT-label_text.get_height()-70))
    
    def display_level(self, surface, text):
        font = pygame.font.SysFont("arial", 44)  # Corrected call to pygame.font.SysFont
        level = font.render(text, 1, (255, 255, 255))
        surface.blit(level, (surface.get_width() / 2 - level.get_width() / 2, surface.get_height() / 2 - level.get_height() / 2))



class CarRacingGame:
    def __init__(self):
        pygame.init()
        
        self.width = WIDTH
        self.height = HEIGHT
        self.surface = pygame.display.set_mode((self.width, self.height))
        self.surface.blit(GRASS, (0, 0))
        self.surface.blit(TRACK, (0, 0))
        self.surface.blit(FINISHING_LINE,(FINISH_POSITION))
        self.surface.blit(TRACK_BORDER,(0,0))
        pygame.display.flip()
        pygame.display.set_caption("Welcome to the Racing Game")
        self.car = Car(self.surface,5,5,BLACK_CAR)
        self.car.x,self.car.y=(180,200)
        self.autonomouscar=AutonomousCar(self.surface,10,5,WHITE_CAR,PATH)
        self.autonomouscar.x,self.autonomouscar.y=(150,200)
        self.game_info=Gameinfo()
        
        
    def level_display(self):
        self.game_info.display_level(self.surface,f'Pres any key to start level{self.game_info.level}')
    
    
    def game_displays(self):
        
        self.game_info.display_label(self.surface,f' level:{self.game_info.level}')
        self.game_info.display_time(self.surface,f'Time:{self.game_info.get_level_time()}')
        self.game_info.speed_display(self.surface,f'Speed:{round(self.car.speed),1}px/s')

    def game_reset(self):
        self.game_info.reset()
        self.car.reset()
        self.autonomouscar.reset()

    def check_collision(self):
        collision_point = self.autonomouscar.collide(pygame.mask.from_surface(self.car.img), self.car.x, self.car.y)
        return collision_point
            
        

    def run(self):
        
        running = True
        level_started = False

        while running:
            clock.tick(FPS)
            self.surface.fill((0, 0, 0))
            self.surface.blit(GRASS, (0, 0))
            self.surface.blit(TRACK, (0, 0))
            self.surface.blit(FINISHING_LINE,(FINISH_POSITION))
            self.surface.blit(TRACK_BORDER,(0,0))
            pygame.display.flip()
              

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            moved = False
            if keys[pygame.K_a]:
                self.car.change_direction(left=True)
            if keys[pygame.K_d]:
                self.car.change_direction(right=True)
            if keys[pygame.K_w]:
                moved = True
                self.car.move_forward()
            if keys[pygame.K_s]:
                moved = True
                self.car.move_backward()
            if not moved:
                self.car.reduce_speed()

            if not level_started:
                self.level_display()

            if level_started:
                
                self.car.draw()
                self.car.move()
                self.autonomouscar.draw()
                self.autonomouscar.move()
                self.game_displays()

                if self.check_collision():
                    self.game_reset()

                if self.car.collide(TRACK_BORDER_MASK) is not None:
                    self.car.bounce_on_border()

                computer_finish_point_collision = self.car.collide(FINISHING_LINE_MASK, *FINISH_POSITION)
                if computer_finish_point_collision is not None:
                    self.game_info.display_label(self.surface, 'You lost!!')
                    pygame.display.flip()
                    pygame.time.wait(5000)
                    self.game_reset()

                player_finish_point_collision = self.car.collide(FINISHING_LINE_MASK, *FINISH_POSITION)
                if player_finish_point_collision is not None:
                    if player_finish_point_collision[1] == 0:
                        self.car.bounce_on_border()
                    else:
                        self.game_info.next_level()
                        self.car.reset()
                        self.autonomouscar.next_level(self.game_info.level)

                if self.game_info.game_finished():
                    self.game_info.display_label(self.surface, 'You Won the game!!')
                    pygame.display.flip()
                    pygame.time.wait(5000)
                    self.game_reset()
            
            pygame.display.flip()

            if not level_started:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        self.game_info.start_level()
                        level_started = True

        pygame.quit()
if __name__ == "__main__":
    game = CarRacingGame()
    game.run()

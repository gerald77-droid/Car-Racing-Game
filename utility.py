import pygame
import pygame.transform
def Resize_images(img,factor):
	size=round(img.get_width()* factor),round(img.get_height()*factor)
	return pygame.transform.scale(img,size)


def rotate_car(surface, image, angle, x, y):
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_rect = rotated_image.get_rect(center=image.get_rect().center)
    rotated_rect.center = (x, y)
    surface.blit(rotated_image, rotated_rect.topleft)




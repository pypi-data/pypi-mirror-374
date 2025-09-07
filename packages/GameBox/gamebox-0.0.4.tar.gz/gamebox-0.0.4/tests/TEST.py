import pygame
from src.GameBox import game
from src.GameBox.basics import camera, player, shapes
from src.GameBox.tilemap import tilemap

width, height = 1800, 1000
win = game.Game(width, height)
cam = camera.Camera(width, height, "dynamic")
image = pygame.image.load("tests\sprites\image.png")

player_obj = player.Player((500, 400), "tests\sprites\playerSprite.png", (64, 64), cam, 0.3)
player_obj.Add_animation(image, 32, (13, 3), 39, .1, 2)


map = tilemap.Tilemap(32, (13, 3), image, cam, 2)
map.load_map("SavedMap.json")
map.enable_editor(width, height)

win.show(map)
win.show(player_obj)
win.update()

player_obj.Add_collision(map.Get_collisions())
#loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            map.save_map("SavedMap.json")
            pygame.quit()
            quit()

    #player_obj.platformer_movement(5, 1.2, 23, 12)
    player_obj.move_by_WSAD(7)

    win.update()

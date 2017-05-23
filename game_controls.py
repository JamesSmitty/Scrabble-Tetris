import libtcodpy as libtcod
import random
import string
import time
 
#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
 
#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 45
 
LIMIT_FPS = 20  #20 frames-per-second maximum
 
 
color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)


 
 
class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        self.object = None
 
        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
 
class Object:
    #this is a generic object: the active_letter, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
 
    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked
        if not map[self.x + dx][self.y + dy].blocked:
            map[self.x][self.y].object = None
            map[self.x][self.y].blocked = False
            self.x += dx
            self.y += dy
            map[self.x][self.y].object = self
        else:
            if not map[self.x][self.y].blocked:
                self.blocked(dx, dy)
                map[self.x][self.y].blocked = True
 
    def draw(self):
        #set the color and then draw the character that represents this object at its position
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
 
    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def update(self, delta):
        pass

    def blocked(self, dx, dy):
        pass
 
def check_objectlist(objectlist):
    if not objectlist:
        return []
    string = str([o for o in objectlist if o == 'x'])
    if string in valid_words:
        return objectlist
    else:
        objectlist = check_objectlist(objectlist[1:])
        if not objectlist:
            return check_objectlist(objectlist[:-1])

valid_words = set("THE")

def match_word(map, x, y):
    objectlist_x = [map[x][h] for h in range(MAP_HEIGHT)]
    objectlist_y = [map[w][y] for w in range(MAP_WIDTH)]
    objectlist_x_checked = check_objectlist(objectlist_x)
    objectlist_y_checked = check_objectlist(objectlist_y)
    if objectlist_x_checked != []:
        return objectlist_x_checked
    if objectlist_y_checked != []:
        return objectlist_y_checked
    else:
        return []


class Letter(Object):
    def __init__(self, x, y, char, color):
        Object.__init__(self, x, y, char, color)
        self.fall_timer = 0.0
        self.falling = True

    def update(self, delta):
        self.fall_timer += delta
        if self.fall_timer > 1.0:
            self.fall_timer -= 1.0
            if self.falling:
                self.move(0, 1)

    def blocked(self, dx, dy):
        if dy > 0:
            matches = match_word(map, self.x, self.y)
            for match in matches:
                map[match.x][match.y].object = None
                map[match.x][match.y].blocked = True
                objects.erase(match)
            make_letter()

 
class Multiletter(Object): #Fix this class!
    def __init__(self, x1, y1, x2, y2, char, color):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.fall_timer = 0.0
        self.falling = True

    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked
        if not map[self.x + dx][self.y + dy].blocked:
            map[self.x][self.y].object = None
            map[self.x][self.y].blocked = False
            self.x += dx
            self.y += dy
            map[self.x][self.y].object = self
        else:
            if not map[self.x][self.y].blocked:
                self.blocked(dx, dy)
                map[self.x][self.y].blocked = True

    def draw(self):
        #set the color and then draw the character that represents this object at its position
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def update(self, delta):
        self.fall_timer += delta
        if self.fall_timer > 1.0:
            self.fall_timer -= 1.0
            if self.falling:
                self.move(0, 1)

    def blocked(self, dx, dy):
        if dy > 0:
            matches = match_word(map, self.x, self.y)
            for match in matches:
                map[match.x][match.y].object = None
                map[match.x][match.y].blocked = True
                objects.erase(match)
            make_letter()



def make_map():
    global map
 
    #fill map with "unblocked" tiles
    map = [[ Tile(False)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]
    for w in range(0,81): #Creates a barrier of the MAP, Replace with MAP_NUMBERS once joe gets home
        map[w-1][MAP_HEIGHT-1].blocked = True
        map[w-1][MAP_HEIGHT-1].block_sight = True
        map[w-1][0].blocked = True
        map[w-1][0].block_sight = True

    for h in range(0,46):
        map[MAP_WIDTH-1][h-1].blocked = True
        map[MAP_WIDTH-1][h-1].block_sight = True
        map[0][h-1].blocked = True
        map[0][h-1].block_sight = True
 
def render_all():
    global color_light_wall
    global color_light_ground
 
    #go through all tiles, and set their background color
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = map[x][y].block_sight
            if wall:
                libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET )
            else:
                libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET )
 
    #draw all objects in the list
    for object in objects:
        object.draw()
 
    #blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

def handle_keys():
    #key = libtcod.console_check_for_keypress()  #real-time
    key = libtcod.console_check_for_keypress(True)  #turn-based
 
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
    elif key.vk == libtcod.KEY_ESCAPE:
        return True  #exit game
 
    #movement keys
    #if libtcod.console_is_key_pressed(libtcod.KEY_UP):
    #    active_letter.move(0, -1)
 
    if libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        active_letter.move(0, 1)
 
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        active_letter.move(-1, 0)
 
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        active_letter.move(1, 0)
 
 
#############################################
# Initialization & Main Loop
#############################################
 
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
 
#create object representing the active_letter
def multiletter_prob():
    random_letter_single = random.choice(string.letters)
    random_letter_multi = random.choice(string.letters) + random.choice(string.letters)
    weighted_list = ["multiletter", "single_letter" * 4]
    if random.choice(weighted_list) == "multiletter":
        random_y = random.randint(1,MAP_WIDTH)
        return Multiletter(random_y, 0, random_y + 1, 0, random_letter_multi, libtcod.white)
    if random.choice(weighted_list) == "single_letter":
        return Letter(random.randint(1,MAP_WIDTH), 0, random_letter_single, libtcod.white)


def make_letter():
    global active_letter
    global objects
    active_letter = multiletter_prob() #Selects a random point at the top of the screen and a random letters
    objects.append(active_letter)

#create an NPClidy
npc = Object(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2, ' ', libtcod.yellow)
 
#the list of objects with those two
objects = [npc]
 
#generate map (at this point it's not drawn to the screen)
make_map()
make_letter()

now = time.time()
y_timer = 0
################################################
#Final end Loop
################################################
while not libtcod.console_is_window_closed():
    oldtime = now
    now = time.time()
    delta = now - oldtime
    #render the screen
    render_all()
    
    libtcod.console_flush()
 
    #erase all objects at their old locations, before they move
    for object in objects:
        object.clear()
        object.update(delta)
 
    
    #handle keys and exit game if needed
    exit = handle_keys()
    if exit:
        break

# create class called multiletter that iunherits from Object class. overides draw and move. Move should check for 
#both letters. 
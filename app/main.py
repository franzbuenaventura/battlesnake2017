from AStar import *
import bottle
import copy
import math
import os

SNAKE_BUFFER = 2
SNAKE = 1
FOOD = 2
SAFETY = 3
SNAKE_ID = ""

def direction(from_cell, to_cell):
    dx = to_cell[0] - from_cell[0]
    dy = to_cell[1] - from_cell[1]
    if dx == 1:
        return 'right'
    elif dx == -1:
        return 'left'
    elif dy == -1:
        return 'up'
    elif dy == 1:
        return 'down'


def distance(p, q):
    return dist(p, q);


def closest(items, start):
    closest_item = None
    closest_distance = 10000
    for item in items:
        item_distance = distance(start, item)
        if item_distance < closest_distance:
            closest_item = item
            closest_distance = item_distance

    return closest_item

def coord_converter(coord):
    cords = [coord['x'], coord['y']]
    return cords

def coords_converter(coords):
    cordList = []
    i = 0
    for cord in coords:
        cordList.append([])
        cordList[i].append(cord['x'])
        cordList[i].append(cord['y'])
        i += 1
    return cordList



# Setup Grid and map out the Snakes and Food
# return: Snake and Grid
def populatesnake_grid(data):
    grid = [[0 for col in xrange(data['height'])] for row in xrange(data['width'])]
    for snek in data['snakes']['data']:
        if snek['id'] == SNAKE_ID:
            mysnake = snek
        for coord in snek['body']['data']:
            grid[coord_converter(coord)[0]][coord_converter(coord)[1]] = SNAKE
    for f in data['food']['data']:
        grid[coord_converter(f)[0]][coord_converter(f)[1]] = FOOD
    return mysnake, grid


# Mark Safety in Grid
# SNAKE_BUFFER number of blocks away from enemy head to user head
def populatesafety(data, mysnake, grid):
    for enemy in data['snakes']['data']:
        if enemy['id'] == SNAKE_ID:
            continue
        if distance(coord_converter(mysnake['body']['data'][0]), coord_converter(enemy['body']['data'][0])) > SNAKE_BUFFER:
            continue
        if len(enemy['body']['data']) >= len(mysnake['body']['data']):
            # dodge
            if coord_converter(enemy['body']['data'][0])[1] < data['height'] - 1:
                grid[coord_converter(enemy['body']['data'][0])[0]][enemy['body']['data'][0][1] + 1] = SAFETY
            if coord_converter(enemy['body']['data'][0])[1] > 0:
                grid[coord_converter(enemy['body']['data'][0])[0]][coord_converter(enemy['body']['data'][0])[1] - 1] = SAFETY
            if coord_converter(enemy['body']['data'][0])[0] < data['width'] - 1:
                grid[coord_converter(enemy['body']['data'][0])[0] + 1][coord_converter(enemy['body']['data'][0])[1]] = SAFETY
            if coord_converter(enemy['body']['data'][0])[0] > 0:
                grid[coord_converter(enemy['body']['data'][0])[0] - 1][coord_converter(enemy['body']['data'][0])[1]] = SAFETY
    return grid


def foodpath(data, grid, mysnake):
    snek_head = coord_converter(mysnake['body']['data'][0])
    snek_coords = coords_converter(mysnake['body']['data'])
    path = None
    foods = sorted(coords_converter(data['food']['data']), key=lambda p: distance(p, snek_head))
    for food in foods:
        # Safe path for food
        tentative_path = a_star(snek_head, food, grid, snek_coords)
        if not tentative_path:
            # print "no path to food"
            continue

        path_length = len(tentative_path)
        snek_length = len(snek_coords) + 1

        # Avoid snakes near food
        dead = False
        for enemy in data['snakes']['data']:
            if enemy['id'] == SNAKE_ID:
                continue
            if path_length > distance(coord_converter(enemy['body']['data'][0]), food):
                dead = True
        if dead:
            continue

        # Update the snake
        if path_length < snek_length:
            remainder = snek_length - path_length
            new_snek_coords = list(reversed(tentative_path)) + snek_coords[:remainder]
        else:
            new_snek_coords = list(reversed(tentative_path))[:snek_length]

        if grid[new_snek_coords[0][0]][new_snek_coords[0][1]] == FOOD:
            # we ate food so we grow
            new_snek_coords.append(new_snek_coords[-1])

        # Create a new grid with the updates snek positions
        new_grid = copy.deepcopy(grid)

        for coord in snek_coords:
            new_grid[coord[0]][coord[1]] = 0
        for coord in new_snek_coords:
            new_grid[coord[0]][coord[1]] = SNAKE

        # printg(grid, 'orig')
        # printg(new_grid, 'new')

        # print snek['body']['data'][-1]
        foodtotail = a_star(food, new_snek_coords[-1], new_grid, new_snek_coords)
        if foodtotail:
            path = tentative_path
            break
            # print "no path to tail from food"
    return path


def getpath(data):
    mysnake, grid = populatesnake_grid(data)
    grid = populatesafety(data, mysnake, grid)

    path = None
    snek_head = coord_converter(mysnake['body']['data'][0])
    snek_coords = coords_converter(mysnake['body']['data'])
    middle = [data['width'] / 2, data['height'] / 2]
    # if len(data['snakes']) >= 2:
    #     if mysnake['health_points'] <= 80:
    #         path = foodpath(data,grid,mysnake)
    # else:
    path = foodpath(data, grid, mysnake)

    # Go around following yourself
    if not path:
        path = a_star(snek_head, middle, grid, snek_coords)

    despair = not (path and len(path) > 1)

    if despair:
        for neighbour in neighbours(snek_head, grid, 0, snek_coords, [SNAKE, SAFETY]):
            path = a_star(snek_head, neighbour, grid, snek_coords)
            # print 'i\'m scared'
            break

    despair = not (path and len(path) > 1)

    if despair:
        for neighbour in neighbours(snek_head, grid, 0, snek_coords, [SNAKE]):
            path = a_star(snek_head, neighbour, grid, snek_coords)
            # print 'lik so scared'
            break

    if path:
        assert path[0] == tuple(snek_head)
        assert len(path) > 1
    return path


# region API Calls

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    return {
        'color': '#c0392b',
        "secondary_color": "#000000",
        'taunt': 'begone taunt',
        'head_url': 'http://vignette1.wikia.nocookie.net/scribblenauts/images/5/5b/Black_Mamba.png/revision/latest?cb'
                    '=20130321192320',
        'name': 'Ahas',
        "head_type": "shades",
        "tail_type": "fat-rattle"
    }

@bottle.post('/move')
def move():
    data = bottle.request.json
    #print(json.dumps(data))
    #global SNAKED_ID
    #SNAKE_ID = data['you']['id']
    #path = getpath(data)
    return {
        
    }

#@bottle.post('/move')
#def move():
#    data = bottle.request.json
#    global SNAKE_ID
#    SNAKE_ID = data['you']['id']
#    path = getpath(data)
#    return {
      #  'move': direction(path[0], path[1]),
      #  'taunt': 'hiss hiss, I\'m a snake'
#    }



# endregion

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))

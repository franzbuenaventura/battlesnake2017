from AStar import *
import bottle
import copy
import math
import os

SNAKE_BUFFER = 0
SNAKE = 1
FOOD = 2
SAFETY = 3

MOD = 1


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


# Setup Grid and map out the Snakes and Food
# return: Snake and Grid
def populatesnake_grid(data):
    grid = [[0 for col in xrange(data['height'])] for row in xrange(data['width'])]
    for snek in data['snakes']:
        if snek['id'] == data['you']:
            mysnake = snek
        for coord in snek['coords']:
            grid[coord[0]][coord[1]] = SNAKE
    for f in data['food']:
        grid[f[0]][f[1]] = FOOD
    return mysnake, grid


# Mark Safety in Grid
# SNAKE_BUFFER number of blocks away from enemy head to user head
def populatesafety(data, mysnake, grid):
    for enemy in data['snakes']:
        if enemy['id'] == data['you']:
            continue
        if distance(mysnake['coords'][0], enemy['coords'][0]) > SNAKE_BUFFER:
            continue
        if len(enemy['coords']) > len(mysnake['coords']) - 1:
            # dodge
            if enemy['coords'][0][1] < data['height'] - 1:
                grid[enemy['coords'][0][0]][enemy['coords'][0][1] + 1] = SAFETY
            if enemy['coords'][0][1] > 0:
                grid[enemy['coords'][0][0]][enemy['coords'][0][1] - 1] = SAFETY
            if enemy['coords'][0][0] < data['width'] - 1:
                grid[enemy['coords'][0][0] + 1][enemy['coords'][0][1]] = SAFETY
            if enemy['coords'][0][0] > 0:
                grid[enemy['coords'][0][0] - 1][enemy['coords'][0][1]] = SAFETY
    return grid


def foodpath(data, grid, mysnake):
    snek_head = mysnake['coords'][0]
    snek_coords = mysnake['coords']
    path = None
    foods = sorted(data['food'], key=lambda p: distance(p, snek_head))
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
        for enemy in data['snakes']:
            if enemy['id'] == data['you']:
                continue
            if path_length > distance(enemy['coords'][0], food):
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

        # print snek['coords'][-1]
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
    snek_head = mysnake['coords'][0]
    snek_coords = mysnake['coords']
    middle = [data['width'] / 2, data['height'] / 2]
    # if len(data['snakes']) >= 2:
    #     if mysnake['health_points'] <= 80:
    #         path = foodpath(data,grid,mysnake)
    # else:
    path = foodpath(data,grid,mysnake)

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
    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']

    # head_url = '%s://%s/static/head.png' % (
    #    bottle.request.urlparts.scheme,
    #    bottle.request.urlparts.netloc
    # )

    return {
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': 'http://vignette1.wikia.nocookie.net/scribblenauts/images/5/5b/Black_Mamba.png/revision/latest?cb'
                    '=20130321192320',
        'name': 'Black Mamba'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json
    path = getpath(data)
    return {
        'move': direction(path[0], path[1]),
        'taunt': 'hiss hiss'
    }


# endregion

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '192.168.97.179'), port=os.getenv('PORT', '8080'))

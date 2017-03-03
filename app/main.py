import bottle
import os
import random
from primary import *

#Global Variables
FREE_SPACE = 0
MY_SNAKE = 1
ENEMY_HEAD = 2
ENEMY_BODY = 3
FOOD = 4

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')



@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'battlesnake-python'
    }

def snakeHead(snakes, mySnakeUID):
    for snake in snakes:
        if (mySnakeUID == snake['coords']):
            return snakes['coords'][0];



def safepath(data):

    sneakHead, grid = initGrid(data)
    directions = ['up', 'down', 'left', 'right']
    for temp in directions:
        if (safeTile(sneakHead, grid, temp )):
            return temp

    return random.choice(directions);


@bottle.post('/move')
def move():
    data = bottle.request.json


    return {
        'move': safepath(data)
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))

import json

# Imitate the Game Server

SampleData = "{\"you\":\"25229082-f0d7-4315-8c52-6b0ff23fb1fb\",\"width\":6,\"turn\":0,\"snakes\":[{" \
             "\"taunt\":\"gitgud\",\"name\":\"my-snake\",\"id\":\"25229082-f0d7-4315-8c52-6b0ff23fb1fb\"," \
             "\"health_points\":93,\"coords\":[[0,0],[0,1],[0,2]]},{\"taunt\":\"gottagofast\"," \
             "\"name\":\"other-snake\",\"id\":\"0fd33b05-37dd-419e-b44f-af9936a0a00c\",\"health_points\":50," \
             "\"coords\":[[1,0],[2,0],[3,0]]}],\"height\":6,\"game_id\":\"870d6d79-93bf-4941-8d9e-944bee131167\"," \
             "\"food\":[[1,1]],\"dead_snakes\":[{\"taunt\":\"gottagofast\",\"name\":\"other-snake\"," \
             "\"id\":\"c4e48602-197e-40b2-80af-8f89ba005ee9\",\"health_points\":50,\"coords\":[[5,0],[5,0],[5,0]]}]} "

data = json.loads(SampleData)

# ************************************************************

FREE_SPACE = 0
MY_SNAKE = 1
ENEMY_HEAD = 2
ENEMY_BODY = 3
FOOD = 4


def initgrid(data):
    grid = [[FREE_SPACE for col in xrange(data['height'])] for row in xrange(data['width'])]
    for snek in data['snakes']:
        if snek['id'] == data['you']:
            for coord in snek['coords']:
                grid[coord[0]][coord[1]] = MY_SNAKE
            mysnake = snek['coords'][0]
        else:
            for coord in snek['coords']:
                grid[coord[0]][coord[1]] = ENEMY_BODY
            if snek['id'] != data['you']:
                grid[snek['coords'][0][0]][snek['coords'][0][1]] = ENEMY_HEAD
    for f in data['food']:
        grid[f[0]][f[1]] = FOOD
    return mysnake, grid


snekHead, grid = initgrid(data)


def safetile(snakeHead, grid, direction):
    if direction == "up":
        if snakeHead[0] - 1 < 0:
            return False
        return grid[snakeHead[0] - 1][snakeHead[1]] == 4 or grid[snakeHead[0] - 1][snakeHead[1]] == 0
    if direction == "down":
        if (snakeHead[0] + 1) >= len(grid):
            return False
        return (grid[snakeHead[0] + 1][snakeHead[1]] == 4) or (grid[snakeHead[0] + 1][snakeHead[1]] == 0)
    if direction == "right":
        if (snakeHead[1] + 1) >= len(grid):
            return False
        return (grid[snakeHead[0]][snakeHead[1] + 1] == 4) or (grid[snakeHead[0]][snakeHead[1] + 1] == 0)
    if direction == "left":
        if snakeHead[1] - 1 < 0:
            return False
        return (grid[snakeHead[0]][snakeHead[1] - 1] == 4) or (grid[snakeHead[0]][snakeHead[1] - 1] == 0)
    return False


print (safetile(snekHead,grid,"up"))
print (snekHead)
print(grid[-1][0])
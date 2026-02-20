import heapq as hq
import random
import sys
import numpy as np
from game_world.racetrack import RaceTrack

Point = tuple[int, int]

#manhattan distance
def mdis(pos: Point,target: Point) -> int:
    return abs(pos[0]-target[0])+abs(pos[1]-target[1])

def get_nbs(pos: Point, m: int, track: RaceTrack):#consider wall toggles and buttons
    r,c = pos
    rows,cols = track.shape
    moves = [(-1,0), (1,0), (0,-1), (0,1), (0,0)]
    
    for dr,dc in moves:
        #new row and col
        nr = r+dr
        nc = c+dc
        if 0 <= nr < rows and 0 <= nc < cols:
            if track.walls[nr, nc] != 0:
                wcolor = int(track.wall_colors[nr,nc])#wall color
                bactive = int(track.active[nr,nc])#wall active?
                phase = (m>>wcolor)&1
                if bactive^phase:#bitwise xor
                    #if bactive and phase are different, wall is active,cannot pass
                    continue
            nm = m#new mask
            if track.buttons[nr,nc]:
                bcolor = int(track.button_colors[nr,nc])
                #1 << bcolor creates a number with only that bit set
                nm^=(1<<bcolor)
            yield (nr,nc),nm,(dr,dc)
            
def astar(start: Point, track: RaceTrack) -> list[Point]:
    start_m = 0
    start_state = (start, start_m)
    target = track.target
    frontier = []
    hq.heappush(frontier,(0, random.randint(0,sys.maxsize),start_state))
    came = {start_state:None}
    cost = {start_state:0}
    
    while frontier:
        _,_,curr_state = hq.heappop(frontier)
        curr_pos, curr_m = curr_state
        if curr_pos == target:#
            path = []
            tmp = curr_state
            while tmp != start_state:
                prt = came[tmp]#parent
                p_pos,_ = prt
                t_pos,_ = tmp
                move = (t_pos[0] - p_pos[0], t_pos[1] - p_pos[1])
                path.append(move)
                tmp = prt
            path.reverse()
            return path

        for next_pos, next_m, move in get_nbs(curr_pos, curr_m, track):
            nbr_state = (next_pos, next_m)
            ncost = cost[curr_state]+1
            if nbr_state not in cost or ncost < cost[nbr_state]:
                cost[nbr_state] = ncost
                pri = ncost+mdis(next_pos, target)#priority
                hq.heappush(frontier, (pri, random.randint(0, sys.maxsize), nbr_state))
                came[nbr_state] = curr_state
                
    return []

route = []
def random_move(loc: Point, track: RaceTrack) -> Point:
    global route
    if not route:
        route=astar(loc,track)
    if route:
        return route.pop(0)
    safe = track.find_traversable_cells()
    options = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = {opt: (loc[0] + opt[0], loc[1] + opt[1]) for opt in options}
    safe_options = [opt for opt in neighbors if neighbors[opt] in safe]
    if safe_options:
        return random.choice(safe_options)
    return (0, 0)

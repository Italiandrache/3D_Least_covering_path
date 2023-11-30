import math
import fractions as fr
import time
from itertools import islice
import multiprocessing


def dot(u, v):
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]

def norm2(v):
    return v[0] * v[0] + v[1] * v[1] + v[2] * v[2]

def cross(b, c):
    return [b[1] * c[2] - c[1] * b[2], b[2] * c[0] - c[2] * b[0], b[0] * c[1] - c[0] * b[1]]

def lineIntersection(a, b): #a=L1(p1, p2) b=L2(q1, q2) #algorithm to compute intersection point between two lines in 3D using some math
    da = [a[1][0] - a[0][0], a[1][1] - a[0][1], a[1][2] - a[0][2]]
    db = [b[1][0] - b[0][0], b[1][1] - b[0][1], b[1][2] - b[0][2]]
    dc = [b[0][0] - a[0][0], b[0][1] - a[0][1], b[0][2] - a[0][2]]

    if dot(dc, cross(da, db)) != 0.0:
        return ()
    
    if norm2(cross(da, db)) == 0.0: #not interested in parallel or overlapping lines
        return ()
        
    s = dot(cross(dc, db), cross(da, db)) / norm2(cross(da, db))
    
    x = a[0][0] + da[0] * s
    y = a[0][1] + da[1] * s
    z = a[0][2] + da[2] * s
    ip = (x, y, z) #intersection point
    return ip
  
def grid(files, rows, cols = 0):
    grid = []
    for file in range(files):
        for row in range(rows):
            if cols != 0:
                for col in range(cols):
                    grid.append((fr.Fraction(file), fr.Fraction(row), fr.Fraction(col))) #Fractions are used in order to have accurate results. Lines from grid only have rational coefficients
                continue
            grid.append((fr.Fraction(file), fr.Fraction(row), fr.Fraction(0.0)))
    return grid

def possiblePoints_fnc(grid, lock, intersectionPoints = [], currentProcess = 0, nProcesses = 1):
    #Computing intersection points between each pair of lines (very slow due to nested loops)
    #Checking every possible path through these points only, will always find the shortest path!
    slicedGrid = islice(grid, currentProcess, len(grid), nProcesses)
    for i, p1 in enumerate(slicedGrid):
        for p2 in grid[i+1:]:
            for j, q1 in enumerate(grid):
                for q2 in grid[j+1:]:
                    intersectionPoint = lineIntersection((p1, p2), (q1, q2))
                    if intersectionPoint is not None and len(intersectionPoint) == 3:
                        with lock: #Minimizing risk for race conditions to happen
                            intersectionPoints.append(tuple(intersectionPoint))

def startingPoints_fnc(possiblePoints):
    filesCoords, rowsCoords, colsCoords = zip(*possiblePoints)
    filesCoords, rowsCoords, colsCoords, = sorted(list(set(filesCoords))), sorted(list(set(rowsCoords))), sorted(list(set(colsCoords)))
    files = filesCoords[-1] - filesCoords[0] + 1 if len(filesCoords) != 1 else fr.Fraction(0) #due to symmetric nature of possiblePoints coords
    rows = rowsCoords[-1] - rowsCoords[0] + 1 if len(rowsCoords) != 1 else fr.Fraction(0)
    cols = colsCoords[-1] - colsCoords[0] + 1 if len(colsCoords) != 1 else fr.Fraction(0)
    xShift, yShift, zShift = filesCoords[0], rowsCoords[0], colsCoords[0]
    #Exploiting symmetries of the possiblePoints grid to reduce the number of possible starting points as much as possible
    #possiblePoints grid symmetries are the same as the symmetries of the regular grid from which they've been computed
    if cols == 0: #2D Grid
        if rows == files: #square
            startingPoints = [point for point in possiblePoints if not point[0]>math.ceil((files+2*xShift)/2-1) and not point[0]<point[1]]
            return startingPoints
        #rectangle
        startingPoints = [point for point in possiblePoints if not point[0]>math.ceil((files+2*xShift)/2-1) and not point[1]>math.ceil((rows+2*yShift)/2-1)]
        return startingPoints
    #3D
    if files == rows and files == cols: #Cube
        startingPoints = [point for point in possiblePoints if not point[0]>math.ceil((files+2*xShift)/2-1) and not point[1]>point[0] and not point[2]>point[0] and not point[2]>point[1]]
        return startingPoints
    if rows == cols: #Rectangular Parallelepiped with 2 square faces rows == cols
        startingPoints = [point for point in possiblePoints if not point[0]>math.ceil((files+2*xShift)/2-1) and not point[1]>math.ceil((rows+2*yShift)/2-1) and not point[1]>point[2]]
        return startingPoints
    if rows == files: #Rectangular Parallelepiped with 2 square faces rows == files
        startingPoints = [point for point in possiblePoints if not point[0]>math.ceil((files+2*xShift)/2-1) and not point[2]>math.ceil((cols+2*zShift)/2-1) and not point[1]>point[0]]
        return startingPoints
    if files == cols: #Rectangular Parallelepiped with 2 square faces files == cols
        startingPoints = [point for point in possiblePoints if not point[0]>math.ceil((files+2*xShift)/2-1) and not point[1]>math.ceil((rows+2*yShift)/2-1) and not point[2]>point[0]]
        return startingPoints
    #Rectangular Parallelepiped without square faces
    startingPoints = [point for point in possiblePoints if not point[0]>math.ceil((files+2*xShift)/2-1) and not point[1]>math.ceil((rows+2*yShift)/2-1) and not point[2]>math.ceil((cols+2*zShift)/2-1)]
    return startingPoints

def main():
    start_time = time.time()
    freePoints = grid(3, 3)
    
    manager = multiprocessing.Manager()
    possiblePointsShared = manager.list()
    lock = manager.Lock()
    nProcesses, activeProcesses = 10, [] #Set max number of concurrently active processes (default 10 based on a 6Core/12Threads CPU)
    if nProcesses > len(freePoints):
        nProcesses = len(freePoints)
    for i in range(0, nProcesses):
        #possiblePoints computation may be very slow and a little taxing on system memory when grid is "large" and/or 3D!
        process = multiprocessing.Process(target=possiblePoints_fnc, args=(freePoints, lock, possiblePointsShared, i, nProcesses))
        activeProcesses.append(process)
        process.start()
    for process in activeProcesses:
        process.join()
    possiblePoints = list(set(possiblePointsShared))
    
    startingPoints = startingPoints_fnc(possiblePoints)
    end_time = time.time()
    print("Len possiblePoints: " + str(len(possiblePoints)))
    print("Len startingPoints: " + str(len(startingPoints)))
    print("Computation time: " + str(end_time - start_time))


if __name__ == '__main__':
    main()

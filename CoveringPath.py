def grid(row, col, xShift = 0, yShift = 0, subdivisions = 1):
    xShift, yShift = xShift * subdivisions, yShift * subdivisions
    grid = []
    for row in range(row*subdivisions):
        for col in range(col*subdivisions):
            grid.append(((row + xShift)/subdivisions, (col + yShift)/subdivisions))
    return grid

def isPointOnLine(p1, p2, p):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    px, py = p[0], p[1]
    if ((px <= x2 and px >= x1) or (px >= x2 and px <= x1)) and ((py <= y2 and py >= y1) or (py >= y2 and py <= y1)):
        if x1 == x2 or y1 == y2:
            return True
        LHS, RHS = py - y1, ((y2 - y1) / (x2 - x1)) * (px - x1)
        if LHS == RHS:
            return True
    return False

def touchedGridPoints(freeGridPoints, p1, p2):
    touchedGridPoints = []
    for p in freeGridPoints:
        if p != p1 and isPointOnLine(p1, p2, p):
            touchedGridPoints.append(p)
    return touchedGridPoints

def validLine(freeGridPoints, p1, p2):
    if len(touchedGridPoints(freeGridPoints, p1, p2)) != 0:
        return True
    return False

def writePath(path):
    f = open("pathFile.txt", "w")
    pathLen = len(path) - 1
    f.write(str(pathLen) + "\nis the number of lines.\n")
    for i in range(pathLen):
        f.write(str(path[i]) + " ")
    f.close()

def updateFreeGridPoints(touchedGridPoints, freeGridPoints):
    for p in touchedGridPoints:
        for gridPoint in freeGridPoints:
            if p == gridPoint:
                freeGridPoints.remove(gridPoint) #Because every point is unique
                break
    return freeGridPoints

def isPointOnGrid(freeGridPoints, p):
    for gridPoint in freeGridPoints:
        if p == gridPoint:
            return True
    return False

def drawLine(currentStartPoint, possiblePoints, currentFreeGridPoints, currentPathLen, currentPath):
    for p2 in possiblePoints:
        if currentStartPoint == p2:
            continue
        currentTouchedGridPoints = touchedGridPoints(currentFreeGridPoints, currentStartPoint, p2)
        if len(currentTouchedGridPoints) == 0:
            continue
        currentPath.append(p2) #might give problems on iterations of the same loop (and such the same scope)?
        f = open("pathFile.txt", "r")
        minLenLoop = int(f.readline().strip('\n'))
        f.close()
        currentPathLen += 1 #same as the above currentPath
        if currentPathLen >= minLenLoop:
            break
        currentFreeGridPoints = updateFreeGridPoints(currentTouchedGridPoints, currentFreeGridPoints)
        if len(currentFreeGridPoints) == 0:
            writePath(currentPath)
            break
        drawLine(p2, possiblePoints, currentFreeGridPoints, currentPathLen, currentPath)


def main():   
    f = open("pathFile.txt", "w")
    f.write("18\n") #upper bound optimal path + 1
    f.close()
    currentFreeGridPoints, possiblePoints, currentPath, currentTouchedGridPoints = grid(4, 4), grid(6, 6, -1, -1), [], []
    currentPathLen = 0
    for p0 in possiblePoints:
        if isPointOnGrid(currentFreeGridPoints, p0):
            currentTouchedGridPoints.append(p0)
            currentFreeGridPoints = updateFreeGridPoints(currentTouchedGridPoints, currentFreeGridPoints)
            drawLine(p0, possiblePoints, currentFreeGridPoints, currentPathLen, currentPath)
            continue
        drawLine(p0, possiblePoints, currentFreeGridPoints, currentPathLen, currentPath)


if __name__ == '__main__':
    main()

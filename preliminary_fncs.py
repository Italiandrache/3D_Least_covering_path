import math
import fractions as fr
import itertools as it
import multiprocessing as mp
import os


def grid_fnc(files, rows, cols):
    grid = []
    for file in range(files):
        for row in range(rows):
            if cols != 0 and cols != 1:
                for col in range(cols):
                    grid.append((fr.Fraction(file), fr.Fraction(row), fr.Fraction(col))) #Fractions are used in order to have accurate results. Lines from grid only have rational coefficients
                continue
            grid.append((fr.Fraction(file), fr.Fraction(row), fr.Fraction(0.0)))
    return grid

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

def getIntersection(linesCombinations, lock, intersectionPoints, currentProcess, nProcesses):
    slicedLinesCombinations = it.islice(linesCombinations, currentProcess, len(linesCombinations), nProcesses)
    for (p1, p2), (q1, q2) in slicedLinesCombinations:
        intersection_point = lineIntersection((p1, p2), (q1, q2))
        if intersection_point is not None and len(intersection_point) == 3:
            with lock: #Minimizing risk for race conditions to happen
                intersectionPoints.append(tuple(intersection_point))

def possiblePoints_fnc(freePoints, nProcesses = 10):
    #Computing intersection points between each pair of lines
    #Checking every possible path through these points only, will always find the shortest path!
    linesCombinations = list(it.combinations(it.combinations(freePoints, 2), 2)) #efficient way to get a list of all possible unique pairs of line segments in a grid. Could maybe be further optimized by removing unnecessary parallel line segments and exploiting symmetries.
    
    manager = mp.Manager()
    possiblePointsShared = manager.list()
    lock = manager.Lock()
    activeProcesses = [] #Set max number of concurrently active processes (default 10 based on a 6Core/12Threads CPU)
    if nProcesses > len(linesCombinations): #safety check for very small grids and powerful cpus
        nProcesses = len(linesCombinations)
    for i in range(0, nProcesses):
        #possiblePoints computation may be very slow and a little taxing on system memory when grid is "large" and/or 3D!
        process = mp.Process(target=getIntersection, args=(linesCombinations, lock, possiblePointsShared, i, nProcesses))
        activeProcesses.append(process)
        process.start()
    for process in activeProcesses:
        process.join()
    return list(set(possiblePointsShared))

def startingPoints_fnc(possiblePoints):
    filesCoords, rowsCoords, colsCoords = zip(*possiblePoints)
    filesCoords, rowsCoords, colsCoords, = sorted(list(set(filesCoords))), sorted(list(set(rowsCoords))), sorted(list(set(colsCoords)))
    files = filesCoords[-1] - filesCoords[0] + 1 if len(filesCoords) != 1 else fr.Fraction(0) #due to symmetric nature of possiblePoints coords
    rows = rowsCoords[-1] - rowsCoords[0] + 1 if len(rowsCoords) != 1 else fr.Fraction(0)
    cols = colsCoords[-1] - colsCoords[0] + 1 if len(colsCoords) != 1 else fr.Fraction(0)
    xShift, yShift, zShift = filesCoords[0], rowsCoords[0], colsCoords[0]
    #Exploiting symmetries of the possiblePoints grid to reduce the number of possible starting points as much as possible
    #possiblePoints grid symmetries are the same as the symmetries of the regular grid from which they've been computed
    if cols == 0 or cols == 1: #2D Grid
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

def write_to_file(startParameter, freePoints, possiblePoints, startingPoints):
    gridSize = str(startParameter[0]) + "x" + str(startParameter[1]) + "x" + str(startParameter[2])
    freePointsStr = [(str(item[0]), str(item[1]), str(item[2])) for item in freePoints] #convert each tuple element from Fraction to str
    freePoints = ';'.join(map(str, freePointsStr))  #Convert each tuple to a string and join with commas
    possiblePointsStr = [(str(item[0]), str(item[1]), str(item[2])) for item in possiblePoints]
    possiblePoints = ';'.join(map(str, possiblePointsStr))
    startingPointsStr = [(str(item[0]), str(item[1]), str(item[2])) for item in startingPoints]
    startingPoints = ';'.join(map(str, startingPointsStr))

    # Open the file in append mode or create it if it doesn't exist
    with open("data.dat", "a+") as file:
        file.seek(0) # Move the cursor to the beginning of the file
        content = file.read() # Read the content to check if the file is empty
        if not content: # If the file is empty, write header and add empty line
            file.write("Some already computed data to sometimes skip preliminary calculations.\n\n")
        file.seek(0, 2) # Move the cursor to the end of the file
        file.write(gridSize + "\n")
        file.write("Grid Points (" + str(len(freePointsStr)) +"):\n")
        file.write(freePoints + "\n")
        file.write("Possible Points (" + str(len(possiblePointsStr)) +"):\n")
        file.write(possiblePoints + "\n")
        file.write("Starting Points (" + str(len(startingPointsStr)) +"):\n")
        file.write(startingPoints + "\n\n")

def read_file(filename, startParameter):
    if not os.path.exists(filename + ".dat"): #check whether data.dat already exists
        return False
    gridSize = str(startParameter[0]) + "x" + str(startParameter[1]) + "x" + str(startParameter[2])
    with open(filename + ".dat", "r") as file:
        file.seek(0)
        content = file.read()
        if gridSize not in content:
            return False
    return True

def extract_data(filename, startParameter):
    gridSize = str(startParameter[0]) + "x" + str(startParameter[1]) + "x" + str(startParameter[2]) + "\n"
    with open(filename + ".dat", 'r') as file:
        lines = file.readlines()

    #Find the index of the line of correct grid size
    start_index = lines.index(gridSize)

    #Extract the lines corresponding to Free Points, Possible Points, and Starting Points
    freePoints_line = lines[start_index + 2].strip()
    possiblePoints_line = lines[start_index + 4].strip()
    startingPoints_line = lines[start_index + 6].strip()

    # Convert the lines to lists of tuples of fractions
    freePoints = [tuple(fr.Fraction(coord_str) for coord_str in point.strip("()").replace("'", "").split(',')) for point in freePoints_line.split(";")]
    possiblePoints = [tuple(fr.Fraction(coord_str) for coord_str in point.strip("()").replace("'", "").split(',')) for point in possiblePoints_line.split(";")]
    startingPoints = [tuple(fr.Fraction(coord_str) for coord_str in point.strip("()").replace("'", "").split(',')) for point in startingPoints_line.split(";")]

    return freePoints, possiblePoints, startingPoints

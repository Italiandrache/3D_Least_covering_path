import math


def grid(files, rows, cols = 0, xShift = 0, yShift = 0, zShift = 0, subdivisions = 1):
    xShift, yShift, zShift = xShift * subdivisions, yShift * subdivisions, zShift * subdivisions
    grid = []
    for file in range(files*subdivisions):
        for row in range(rows*subdivisions):
            if cols != 0:
                for col in range(cols*subdivisions):
                    grid.append(((file + xShift)/subdivisions, (row + yShift)/subdivisions, (col + zShift)/subdivisions))
                continue
            grid.append(((file + xShift)/subdivisions, (row + yShift)/subdivisions, 0.0))
    return grid

def startGrid(files, rows, cols = 0, xShift = 0, yShift = 0, zShift = 0, subdivisions = 1): #smallest symmetrical element of grid. speeds up computation by avoiding symmetrically equivalent solutions
    xShift, yShift, zShift = xShift * subdivisions, yShift * subdivisions, zShift*subdivisions
    grid = []
    if cols == 0: #2D Grid (on xy plane)
        for file in range(math.ceil(files*subdivisions/2)):
            rows_to_iterate = file+1 if rows == files else math.ceil(rows*subdivisions/2)
            for row in range(rows_to_iterate):
                grid.append(((file + xShift)/subdivisions, (row + yShift)/subdivisions, 0.0))
        return grid
    if files == rows and files == cols: #Cube
        for file in range(math.ceil(files*subdivisions/2)): #left to right symmetry (1 out of 3 possible planes)
            for col in range(file+1): #diagonal symmetry (1 out of 2 possible planes from the same opposing face pair)
                for row in range(col, file+1): #remaining diagonal symmetries (2 out of 4 possible remaining planes of symmetry, one for each opposing face pair)
                    grid.append(((file + xShift)/subdivisions, (row + yShift)/subdivisions, (col + zShift)/subdivisions))
        return grid
    for file in range(math.ceil(file*subdivisions/2)): #Rectangular Parallelepiped
        if rows == cols or files == rows: #rows==cols or files==rows
            for col in range(math.ceil(cols*subdivisions/2)): #top to bottom symmetry
                rows_to_iterate = col+1 if rows == cols else file+1 #diagonal symmetry
                for row in range(rows_to_iterate):
                        grid.append(((file + xShift)/subdivisions, (row + yShift)/subdivisions, (col + zShift)/subdivisions))
            continue
        #files==cols or no square faces
        for row in range(math.ceil(rows*subdivisions/2)):
            cols_to_iterate = file+1 if files == cols else math.ceil(cols*subdivisions/2)
            for col in range(cols_to_iterate):
                grid.append(((file + xShift)/subdivisions, (row + yShift)/subdivisions, (col + zShift)/subdivisions))
    return grid


def main():
    freePointsGrid = grid(4, 4)
    possiblePointsGrid = grid(6, 6, 0, -1, -1)
    startingPointsGrid = startGrid(6, 6, 0, -1, -1)


if __name__ == '__main__':
    main()

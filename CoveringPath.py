import preliminary_fncs as pr
import multiprocessing as mp
import time #optional, for benchmarking only


def getUpperBound(gridSize):
    files, rows, cols = gridSize[0], gridSize[1], gridSize[2]
    if files != rows or files != cols or rows != cols: #not files == rows == cols: #Non square/cubic grid
        #trivial upper bound
        list = sorted([files, rows, cols])
        return 2*list[0]*list[1]-1
    #square/cubic grids
    if files == 1 and rows == 1 and cols == 1: #1D
        return 1
    if files == 1 or rows == 1 or cols == 1: #2D
        list = sorted([files, rows, cols])
        if list[1] == 2:
            return 3
        return 2*(list[1]-1) #proven exact bound (lower==upper) for nxnx1 (or nx1xn or 1xnxn) grids, with n>=3
    if files == 2:
        return 6
    return (files**3-1)/(files-1)+2*(files-3) #Worse case Ripà's conjecture

def leastCoveringPath(freePoints, possiblePoints, startingPoints, upperBound, lock, currentProcess, nProcesses):
    pass

def main():
    startParameters = ((3, 3, 1), 10) # The first tuple defines, in order, the number of files, rows, and cols of the grid. The second value determines the max number of concurrently active processes
    freePoints, possiblePoints, startingPoints = [], [], []
    pointsAlreadyKnown = pr.read_file("data", startParameters[0])
    if not pointsAlreadyKnown:
        start_time = time.time() #Optional, just for benchmark
        freePoints = pr.grid_fnc(startParameters[0][0], startParameters[0][1], startParameters[0][2])
        possiblePoints = pr.possiblePoints_fnc(freePoints, startParameters[1]) #second argument is max number of concurrently active processes
        startingPoints = pr.startingPoints_fnc(possiblePoints)
        end_time = time.time() #Optional, just for benchmark
        print("Len possiblePoints: " + str(len(possiblePoints))) #Optional, just for benchmark
        print("Len startingPoints: " + str(len(startingPoints))) #Optional, just for benchmark
        print("Computation time: " + str(end_time - start_time)) #Optional, just for benchmark

        pr.write_to_file(startParameters[0], freePoints, possiblePoints, startingPoints)
    else:
        data = pr.extract_data("data", startParameters[0])
        freePoints = data[0]
        possiblePoints = data[1]
        startingPoints = data[2]
        print(freePoints) #Optional, just for benchmark
        print(possiblePoints) #Optional, just for benchmark
        print(startingPoints) #Optional, just for benchmark

    manager = mp.Manager()
    lock = manager.Lock()
    upperBound = manager.Value('i', getUpperBound(startParameters[0]))
    activeProcesses = []
    nProcesses = startParameters[1]
    if nProcesses > len(startingPoints):
        nProcesses = len(startingPoints)
    for i in range(0, nProcesses):
        process = mp.Process(target=leastCoveringPath, args=(freePoints, possiblePoints, startingPoints, upperBound, lock, i, nProcesses))
        activeProcesses.append(process)
        process.start()
    for process in activeProcesses:
        process.join()

if __name__ == '__main__':
    main()

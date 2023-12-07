import preliminary_fncs as pr
import multiprocessing as mp
import time #optional, for benchmarking only


def getUpperBound(gridSize):
    files, rows, cols = gridSize[0], gridSize[1], gridSize[2]
    list = sorted([files, rows, cols])
    if list[0] == 1 and list[1] == 1: #0D or 1D
        return 1
    if list[0] == 1: #2D
        if list [1] != list[2]: #Rectangle
            return 2*list[1]-1 #Trivial upper bound
        if list[1] == 2: #2x2
            return 3
        return 2*(list[1]-1) #Proven length of least covering path for nxn square grid
    #3D
    if list[0] != list[1]: #Rectangular parallelepiped
        return 2*list[0]*list[1]-1  #trivial upper bound
    if list[0] == 2: #2x2x2
        return 6
    return (files**3-1)/(files-1)+2*(files-3) #Worst case Ripà's conjecture for nxnxn with n>=3

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

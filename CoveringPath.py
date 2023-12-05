import preliminary_fncs as pr
import time #optional, for benchmarking only


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

if __name__ == '__main__':
    main()

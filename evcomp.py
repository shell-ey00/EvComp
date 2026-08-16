import random
import math

# where cylinders are placed
ContainerWidth = 100
ContainerDepth = 60
MaxWeight = 500

# Cylinder array (diameter, weight)
CYLINDERS = [
    (20, 80),
    (15, 60),
    (25, 120),
    (10, 40),
    (30, 200)
]

PopSize = 80  #population size of solution
Generations = 400   # re runs
MutationRate = 0.8  #rate of change within shape layout
EliteSize = 5  #unchanged solutions


def dist(x1, y1, x2, y2):
    #calculate distance between two cylinder centres
    return math.hypot(x1 - x2, y1 - y2)


def overlap(c1, c2):
    x1, y1, r1 = c1
    x2, y2, r2 = c2

    #return true if cylinders overlap
    return dist(x1, y1, x2, y2) < (r1 + r2)


def place_cylinders(ordering):  # placement
    placed = []

    # go through cylinder ordering
    for idx in ordering:
        d, w = CYLINDERS[idx]  # getting size d = diameter, w = weight
        r = d / 2.0

        # first cylinder goes in the centre
        if len(placed) == 0:
            x = ContainerWidth / 2
            y = ContainerDepth / 2

            # make sure the first cylinder fits
            if (x - r >= 0 and
                    x + r <= ContainerWidth and
                    y - r >= 0 and
                    y + r <= ContainerDepth):

                placed.append((x, y, r))
                continue

            return None

        # store possible positions
        possible_positions = []

        # look around every cylinder already placed
        for existing in placed:

            ex, ey, er = existing

            # shell radius = existing radius + new cylinder radius
            shell_radius = er + r

            # sample points around the shell
            for angle in range(0, 360, 2):

                angle_radians = math.radians(angle)

                x = ex + math.cos(angle_radians) * shell_radius
                y = ey + math.sin(angle_radians) * shell_radius

                # check if cylinder is inside container
                if x - r < 0:
                    continue

                if x + r > ContainerWidth:
                    continue

                if y - r < 0:
                    continue

                if y + r > ContainerDepth:
                    continue

                candidate = (x, y, r)

                # check if candidate overlaps anything already placed
                if all(not overlap(candidate, p) for p in placed):

                    # calculate distance from centre of container
                    centre_x = ContainerWidth / 2
                    centre_y = ContainerDepth / 2

                    distance_from_centre = dist(
                        x,
                        y,
                        centre_x,
                        centre_y
                    )

                    possible_positions.append(
                        (distance_from_centre, candidate)
                    )

        # if no valid position was found
        if not possible_positions:
            return None

        # choose valid position closest to centre
        possible_positions.sort(key=lambda item: item[0])

        best_position = possible_positions[0][1]

        placed.append(best_position)

    return placed #if ok

def fitness(individual):
    placed = place_cylinders(individual)  #places individual cylinders gives it x y coords

    if placed is None:  #give bad penalty if they overlap or in out of bounds area
        return 1e6

    total_weight = sum(CYLINDERS[i][1] for i in individual)  #checks the weight is good

    #if the weight is greater than total weight must return invalid value
    if total_weight > MaxWeight:
        return 1e6 + (total_weight - MaxWeight) * 1000

    cx = sum(placed[i][0] * CYLINDERS[individual[i]][1]
             for i in range(len(placed))) / total_weight

    cy = sum(placed[i][1] * CYLINDERS[individual[i]][1]
             for i in range(len(placed))) / total_weight

    balance_penalty = abs(cx - ContainerWidth / 2) + \
                      abs(cy - ContainerDepth / 2)  #calcs the center of mass

    used_area = sum(math.pi * p[2]**2 for p in placed)  #used area by cylinders
    wasted_area = (ContainerWidth * ContainerDepth) - used_area  #unused area

    if wasted_area <= 0.01 and balance_penalty < 0.5:  #if less wasted area the better
        return 0

    #return wasted area and penalty
    return wasted_area + balance_penalty * 100


def create_individual():  #create random sol
    ind = list(range(len(CYLINDERS)))  #create list of cylinder indexes
    random.shuffle(ind)  #shuffle ordering randomly
    return ind


def crossover(p1, p2):  #create two parent
    size = len(p1)

    #pick two random crossover points
    a, b = sorted(random.sample(range(size), 2))

    child = [None] * size

    #copy section from first parent
    child[a:b] = p1[a:b]

    #fill remaining values from second parent
    fill = [g for g in p2 if g not in child]
    ptr = 0

    #fill empty space
    for i in range(size):
        if child[i] is None:
            child[i] = fill[ptr]
            ptr += 1

    return child


def mutate(ind):  #gives random positions

    #check if mutation should happen
    if random.random() < MutationRate:

        #pick two random cylinder positions
        i, j = random.sample(range(len(ind)), 2)

        #swap positions
        ind[i], ind[j] = ind[j], ind[i]


def run_ga():
    #create random population
    population = [create_individual() for _ in range(PopSize)]

    #repeat for amount of gens
    for gen in range(Generations):

        #sort population by fitness
        population.sort(key=fitness)

        #get current best solution
        best = population[0]
        best_fit = fitness(best)

        print("Generation", gen, "| Best fitness:", best_fit)

        #looking for best sol
        if best_fit == 0:

            coords = place_cylinders(best)

            print("\nPERFECT SOLUTION FOUND")
            print("Ordering:", best)
            print("Coordinates:")

            for i, c in enumerate(coords):
                print(f"Cylinder {best[i]} -> x={c[0]:.2f}, y={c[1]:.2f}, r={c[2]:.2f}")

            return best, coords

        #keeps best solution
        new_pop = population[:EliteSize]

        #create new population
        while len(new_pop) < PopSize:

            #pick two parents
            p1, p2 = random.sample(population[:30], 2)

            #create child
            child = crossover(p1, p2)

            #mutate child
            mutate(child)

            #add child to new population
            new_pop.append(child)

        #replace old population
        population = new_pop

    #if perfect solution not found
    best = population[0]
    coords = place_cylinders(best)

    print("\nBest solution found-")
    print("Ordering-", best)
    print("Fit-", fitness(best))

    for i, c in enumerate(coords):
        print(f"Cylinder {best[i]} -> x={c[0]:.2f}, y={c[1]:.2f}, r={c[2]:.2f}")

    return best, coords


#keeps best solution
best_ordering, best_coords = run_ga()

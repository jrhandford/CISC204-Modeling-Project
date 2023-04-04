from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config

config.sat_backend = "kissat"


# Constraints
def generate_constraints(moves, carrier, animals, infighting_groups):
    E = Encoding()

    @proposition(E)
    # Side is shore by default - if the proposition is negated, then it is assumed that they have crossed
    class AnimalSideTime:
        def __init__(self, animal, time, sorting_order=0, prev=None):
            self.animal = animal
            self.time = time
            self.sorting_order = sorting_order  # Used in printing the output
            self.prev = prev  # Previous game state

        def __repr__(self):
            return f"{self.animal}"

        def __lt__(self, other):
            return self.time < other.time

    animal_count = len(animals)
    # Initial game state
    carrier_shore = AnimalSideTime(carrier, time=0, sorting_order=animal_count)
    animals_shore = [None] * animal_count
    for i in range(animal_count):
        animals_shore[i] = AnimalSideTime(animals[i], time=0, sorting_order=i)
        # Everyone starts on the shore at the beginning
        E.add_constraint(animals_shore[i])
    E.add_constraint(carrier_shore)

    infighting_group_indexes = []
    # Indexing where the animals of the infighting groups are to make creating constraints easier
    for i in range(len(infighting_groups)):
        infighting_group_indexes.append([])
        for animal in infighting_groups[i]:
            infighting_group_indexes[i].append(animals.index(animal))

    # Iteratively establishing game states over time
    for time in range(1, moves + 1):
        # Establish propositions
        for i in range(animal_count):
            animals_shore[i] = AnimalSideTime(animals[i], time, sorting_order=i, prev=animals_shore[i])
        carrier_shore = AnimalSideTime(carrier, time, sorting_order=animal_count, prev=carrier_shore)

        # Animals within the infighting groups can't be on the same side without the carrier/farmer
        for indexes in infighting_group_indexes:
            for i in range(len(indexes)):
                for j in range(i + 1, len(indexes)):
                    E.add_constraint(~(animals_shore[indexes[i]] & animals_shore[indexes[j]] & ~carrier_shore))
                    E.add_constraint(~(~animals_shore[indexes[i]] & ~animals_shore[indexes[j]] & carrier_shore))

        # Only one animal can move at a time, and only if the farmer goes with them
        for i in range(animal_count):
            animal_shore = animals_shore[i]
            # Animals can't cross without farmer
            E.add_constraint((animal_shore & ~animal_shore.prev)
                             >> (carrier_shore & ~carrier_shore.prev))
            E.add_constraint((~animal_shore & animal_shore.prev)
                             >> (~carrier_shore & carrier_shore.prev))
            for j in range(i + 1, animal_count):
                other_animal_shore = animals_shore[j]
                # Other animals can't cross while the current one is crossing
                E.add_constraint(((animal_shore & ~animal_shore.prev) | (~animal_shore & animal_shore.prev))
                                 >> ((other_animal_shore & other_animal_shore.prev)
                                     | (~other_animal_shore & ~other_animal_shore.prev)))

        # The farmer has to move every turn
        E.add_constraint((~carrier_shore & carrier_shore.prev) | (carrier_shore & ~carrier_shore.prev))

        # By the end, everyone has to be on the other side
        if time == moves:
            E.add_constraint(~carrier_shore)
            for animal_shore in animals_shore:
                E.add_constraint(~animal_shore)
    return E


if __name__ == "__main__":
    # Feel free to modify these variables
    # 'carrier' can be any string, and 'animals' can contain any number of strings
    #
    # 'infighting_groups' can contain any number of lists, which themselves
    # must contain strings from the 'animals' list.
    # Any animals within the same list in 'infighting_groups' cannot be left alone without the carrier.

    min_moves = 1
    max_moves = 32
    carrier = "farmer"
    animals = ["cabbage", "wolf", "goat"]
    infighting_groups = [["cabbage", "goat"], ["wolf", "goat"]]

    for moves in range(min_moves, max_moves + 1):
        E = generate_constraints(moves, carrier, animals, infighting_groups)
        T = E.compile()
        if T.satisfiable():
            break
        E.clear_constraints()
        E.purge_propositions()

    print("\nSatisfiable: %s" % T.satisfiable())

    if T.satisfiable():
        sol = T.solve()
        print("Solved in %d moves" % moves)
        print("Solutions (within %d moves): %d" % (moves, count_solutions(T)))

        print("\nExample solution gamestates (things on the other side indicated by full caps):")
        # Printing the gamestates
        for i in range(len(animals)):
            animals[i] = animals[i].upper()
        animals += [carrier.upper()]
        game_states = []
        for i in range(moves + 1):
            game_states.append(animals.copy())
        for animal_side in sol.keys():
            if sol.get(animal_side):
                game_states[animal_side.time][animal_side.sorting_order] = animal_side.__repr__()
        for time in range(moves + 1):
            print(game_states[time])
    else:
        print("No solutions found within %d moves." % max_moves)

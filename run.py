from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config

config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()


@proposition(E)
class AnimalSideTime:
    def __init__(self, animal, side, time, opposite=None, sorting_order=0, prev=None):
        self.animal = animal
        self.side = side
        self.time = time
        self.opposite = opposite
        self.sorting_order = sorting_order  # Used in printing the output
        self.prev = prev

    def __repr__(self):
        return f"{self.animal}{self.side}"
        # return f"A.{self.animal}.{self.side}.{self.time}"

    def __lt__(self, other):
        return self.time < other.time


# Constraints
def generate_constraints():
    for time in range(0, moves + 1):
        # Initial game state
        if time == 0:
            # Establish propositions
            farmer_shore = AnimalSideTime("Farmer", "Shore", time, sorting_order=0)
            cabbage_shore = AnimalSideTime("Cabbage", "Shore", time, sorting_order=1)
            wolf_shore = AnimalSideTime("Wolf", "Shore", time, sorting_order=2)
            goat_shore = AnimalSideTime("Goat", "Shore", time, sorting_order=3)

            E.add_constraint(farmer_shore & cabbage_shore & wolf_shore & goat_shore)
            continue

        # Establish propositions
        farmer_shore = AnimalSideTime("Farmer", "Shore", time, sorting_order=0, prev=farmer_shore)
        cabbage_shore = AnimalSideTime("Cabbage", "Shore", time, sorting_order=1, prev=cabbage_shore)
        wolf_shore = AnimalSideTime("Wolf", "Shore", time, sorting_order=2, prev=wolf_shore)
        goat_shore = AnimalSideTime("Goat", "Shore", time, sorting_order=3, prev=goat_shore)

        # Goat and cabbage can't be on the same side without the farmer
        E.add_constraint(~(goat_shore & cabbage_shore & ~farmer_shore))
        E.add_constraint(~(~goat_shore & ~cabbage_shore & farmer_shore))
        # Goat and wolf can't be on the same side without the farmer
        E.add_constraint(~(wolf_shore & goat_shore & ~farmer_shore))
        E.add_constraint(~(~wolf_shore & ~goat_shore & farmer_shore))

        animals = [cabbage_shore, goat_shore, wolf_shore]
        # Only one animal can move at a time, and only if the farmer goes with them
        for i in range(len(animals)):
            animal_shore = animals[i]
            other_animal1_shore = animals[(i + 1) % 3]
            other_animal2_shore = animals[(i + 2) % 3]
            # Animal moves from the other side to the shore
            E.add_constraint((animal_shore & ~animal_shore.prev)
                             # Farmer has to also move from the other side to the shore
                             >> ((farmer_shore & ~farmer_shore.prev)
                                 # Other animals can't change sides
                                 & ((other_animal1_shore & other_animal1_shore.prev)
                                    | (~other_animal1_shore & ~other_animal1_shore.prev))
                                 & ((other_animal2_shore & other_animal2_shore.prev)
                                    | (~other_animal2_shore & ~other_animal2_shore.prev))))
            # Animal moves from the shore to the other side
            E.add_constraint((~animal_shore & animal_shore.prev)
                             # Farmer has to also move from the shore to the other side
                             >> ((~farmer_shore & farmer_shore.prev)
                                 # Other animals can't change sides
                                 & ((other_animal1_shore & other_animal1_shore.prev)
                                    | (~other_animal1_shore & ~other_animal1_shore.prev))
                                 & ((other_animal2_shore & other_animal2_shore.prev)
                                    | (~other_animal2_shore & ~other_animal2_shore.prev))))

        # The farmer has to move every turn
        E.add_constraint((~farmer_shore & farmer_shore.prev) | (farmer_shore & ~farmer_shore.prev))

        # By the end, everyone has to be on the other side
        if time == moves:
            E.add_constraint(~farmer_shore & ~cabbage_shore & ~wolf_shore & ~goat_shore)


if __name__ == "__main__":
    moves = 7
    generate_constraints()
    T = E.compile()

    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))

    sol = T.solve()
    game_states = [["FarmerCrossed", "CabbageCrossed", "WolfCrossed", "GoatCrossed"] for x in range(moves + 1)]
    for animal_side in sol.keys():
        if sol.get(animal_side):
            game_states[animal_side.time][animal_side.sorting_order] = animal_side.__repr__()
    for time in range(moves + 1):
        print(game_states[time])

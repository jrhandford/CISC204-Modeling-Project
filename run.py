from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config

config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()


# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
@proposition(E)
class AnimalSide:
    def __init__(self, animal, side):
        self.animal = animal
        self.side = side

    def __repr__(self):
        return f"A.{self.animal}.{self.side}"


@proposition(E)
class GameState:
    def __init__(self, farmerSide, cabbageSide, goatSide, wolfSide, time):
        self.farmerSide = farmerSide
        self.cabbageSide = cabbageSide
        self.goatSide = goatSide
        self.wolfSide = wolfSide
        self.time = time


# Declare all AnimalSide propositions
farmerShore = AnimalSide("Farmer", "Shore")
farmerCrossed = AnimalSide("Farmer", "Crossed")
cabbageShore = AnimalSide("Cabbage", "Shore")
cabbageCrossed = AnimalSide("Cabbage", "Crossed")
wolfShore = AnimalSide("Wolf", "Shore")
wolfCrossed = AnimalSide("Wolf", "Crossed")
goatShore = AnimalSide("Goat", "Shore")
goatCrossed = AnimalSide("Goat", "Crossed")

gamestates = [(farmerShore & ~farmerCrossed & cabbageShore & ~cabbageCrossed & wolfShore & ~wolfCrossed & goatShore & ~goatCrossed)]

# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
    # Can't be on two sides at the same time
    E.add_constraint((farmerShore | farmerCrossed) & ~(farmerCrossed & farmerShore))
    E.add_constraint((cabbageShore | cabbageCrossed) & ~(cabbageCrossed & cabbageShore))
    E.add_constraint((wolfShore | wolfCrossed) & ~(wolfCrossed & wolfShore))
    E.add_constraint((goatShore | goatCrossed) & ~(goatCrossed & goatShore))
    # Goat and cabbage can't be on the same side without the farmer
    E.add_constraint(~(goatShore & cabbageShore & ~farmerShore))
    E.add_constraint(~(goatCrossed & cabbageCrossed & ~farmerCrossed))
    # Goat and wolf can't be on the same side without the farmer
    E.add_constraint(~(wolfShore & goatShore & ~farmerShore))
    E.add_constraint(~(wolfCrossed & goatCrossed & ~farmerCrossed))

    # Gamestates not implemented yet
    return E


if __name__ == "__main__":

    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())

    # print("\nVariable likelihoods:")
    # for v, vn in zip([a, b, c, x, y, z], 'abcxyz'):
    #     # Ensure that you only send these functions NNF formulas
    #     # Literals are compiled to NNF here
    #     print(" %s: %.2f" % (vn, likelihood(T, v)))
    # print()

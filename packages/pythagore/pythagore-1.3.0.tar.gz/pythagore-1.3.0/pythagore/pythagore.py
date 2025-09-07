import math

class Pythagore:

    """
    The Pythagoras class makes it easier to calculate the Pythagorean theorem.
    """

    # parameter OP the largest side, the other two parameters are the other values ​​of the rectangle
    @staticmethod
    def is_rectangle(hypotenuse, side_a, side_b):
        result_op = math.pow(hypotenuse, 2)
        pn = math.pow(side_a, 2)
        no = math.pow(side_b, 2)
        result = pn + no
        if result_op != result:
            return False
        return True
        
    # hypotenus parameter, one side to find the missing side
    @staticmethod 
    def adjacent_side(hypotenuse, other_side):
        return math.sqrt(pow(hypotenuse, 2) - pow(other_side, 2))

    # the two sides of the triangle to find the hypotenus
    @staticmethod
    def hypotenus(side_a, side_b):
        return math.sqrt(math.pow(side_a, 2) + math.pow(side_b, 2))

    # return the current version
    @staticmethod
    def current_version():
        return "Current Version : 1.3.0"
    
    # return the creator's nickname and his github profile
    @staticmethod
    def creator():
        return "Creator : Tina\nGitHub : https://github.com/Tina-1300"

    # Displays the representation of the Pythagore class
    @staticmethod
    def __repr__():
        return "Pythagoras - Utility classes for the Pythagorean theorem. Created by Tina"
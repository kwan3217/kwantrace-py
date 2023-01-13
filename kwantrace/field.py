from kwantrace.position_direction import Position
from kwantrace.transformable import Transformable


class Field(Transformable):
    """
    A field -- a function which takes a vector and returns a vector
    """
    def __init__(self,N:int):
        """

        :param N: Number of components of the vector result
        """
        self.N=N
    def _fieldLocal(self,r:Position):
        """
        Calculate the value of the field at a point.

        :param r: Position to evaluate the field at, in local space
        :return: Value of the field at this point
        """
        raise NotImplementedError("Abstract")
    def __call__(self,r:Position):
        """
        Evaluate the function at a point in world space.

        :param r: Position to evaluate the field at
        :return: value of the field at this point
        """
        return self.fieldLocal(self.M_br @ r)


class ColorField(Field):
    def __init__(self):
        super().__init__(5)


class ConstantColor(ColorField):
    """
    Constant color field -- has constant color everywhere in space */
    """
    def __init__(self,Lvalue:ObjectColor):
        """

        :param Lvalue: Value of field at all points
        """
        self._value=Lvalue
    def _fieldLocal(self,r:Position):
        return self._value

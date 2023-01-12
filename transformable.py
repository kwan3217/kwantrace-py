# List of pointers to transforms
import numpy as np

from transformation import Transformation

TransformList=list[Transformation]


class Transformable(list[Transformation]):
    r"""
    Entity that can be transformed.

    In general, we use the POV-Ray model where each transformation
    is thought of as *physically moving* the Transformable. For instance, if we start with a Transformable
    that is located at the origin and do a translate(1,2,3), the object will then be located at x=1, y=2, z=3.

    Also like POV-Ray, we treat all transformations as being about the origin, not about the center of the
    given object which might not be at the origin any more. For instance:

       * If an object is already 5 units from the origin and you call scale(3,3,3)
            * the object will then be 15 units from the origin.
       * If an object is at <5,0,0> and pointing down the x axis, and you call rotateZ(90)
            * it will be pointing down the Y axis, but also at <0,5,0>.

    With a little bit of thought, we can see what kind of *frame* transformation corresponds to a
    *physical* move. Let's look at a translation by \f$\vec{r}\f$. In the body frame, we look at
    the origin. In the world frame, that same point has coordinates of \f$\vec{r}\f$

    This is designed to be efficient, with as much effort done at scene construction and prepareRender() as
    possible, to save as much time effort during the render. This makes sense, because the render will be
    called literally millions of times. You may chain literally any number of transformations, and only pay
    the cost at prepareRender(). During the render, the cost of 0, 1, or 1000 transformations are all the same.
    """
    def combine(self):
        """
        Combine transformations in the transformation list.

        In terms of physical transformations, it is as if the the transforms in the list are performed in order.
        The actual implementation is that the transforms are converted to matrices, and then combined by matrix
        multiplication with the transformations in order from the right. This is the traditional way to combine
        matrices, and is required if you are then going to use M*v to transform a column vector.

        :return: Matrix representing the combination of all transformations performed in order.
        """
        result=np.identity(4)
        for trans in self:
            result=trans.matrix() @ result
        return result
    def prepareRender(self):
        """
        Prepare for rendering.

        This is done by calling combine() to combine all of the transformations, and
        then computing ancillary matrices M_rb, M_br, and N_rb, which will also be needed.

        Those ancillary matrices are only valid between a call to prepareRender() and any changes
        to any transforms in this list.

        """
        self.M_rb=self.combine()   # reference from body transformation matrix
        self.M_br=np.linalg.inv(self.M_rb) # body from reference transformation matrix
        self.N_rb=self.M_br.T              # body from reference transformation for normal vectors


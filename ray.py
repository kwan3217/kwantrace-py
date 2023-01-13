from position_direction import Position, Direction
from __future__ import annotations


class Ray:
    r"""
    A mathematical ray, starting at an initial point \f$\vec{r}_0\f$ and continuing in direction
    \f$\vec{v}\f$. This can be used as a vector function of a single parameter \f$\vec{r}(t)=\vec{r}_0+\vec{v}t\f$.

    The direction vector does not have to be unit length, but if it is unit length, then the \f$t\f$
    parameter just represents the distance along the ray.

    Note that it doesn't make sense to have a zero direction vector. Such a ray would never leave the initial point,
    no matter what the parameter was. This class will work perfectly fine, but most likely
    all intersect functions will be asked to divide by zero at some point.

    This class is mostly a container for the vector coefficients, which are directly used by the intersection
    routines in kwantrace::Primitive.intersect() . Those routines are responsible for determining if a given
    ray actually hits anything.

    The ray does support a couple of operators, to handle evaluating the ray at a given parameter,
    transforming with a matrix, and advancing the ray (generating a new ray which starts at a given parameter
    from the old ray).
    """
    def __init__(self,Lr0:Position,Lv:Direction):
        """
        Construct an array from the given initial position and direction.

        :param Lr0: Ray initial point
        :param Lv: Ray direction
        """
        self.r0=Lr0
        self.v=Lv
    def __rmatmul__(self,M):
        """
        Transform this ray with a matrix.

        The position and direction vectors have to be handled differently,
        since the initial point is a position which participates in translation, while the direction does not.
        This is handled by the differently-overloaded multiplication operator for each kind of vector.

        :param M:
        :return:
        """
        return Ray(M @ self.R0, M @ self.v)
    def __iadd__(self,dt:float):
        """
        Advance this ray a certain amount

        :param dt: Amount to advance the ray
        :return: None, but ray has its initial point advanced, so ray(t)==oldray(t+dt)
        """
        self.r0+=self.v*dt
    def __call__(self,t:float)->Position:
        """
        Evaluate the ray.

        :param t: Parameter to evaluate the ray at
        :return: Point on ray at given parameter
        """
        return self.r0+self.v*t
    def __add__(self,dt:float)->Ray:
        """
        Advance a ray by a given amount.


        :param dt: amount to advance the parameter
        :return: A copy of the ray with the parameter advanced.

        Given `rp=r+4.7` the expression `np.allclose(rp(t),r(t+4.7))` will be true
        """
        return Ray(self.r0+self.v*dt,self.v)
    def __radd__(self,dt:float):
        return Ray(self.r0 + self.v * dt, self.v)


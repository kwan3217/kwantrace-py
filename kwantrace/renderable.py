from kwanmath.vector import vnormalize

from kwantrace.field import ColorField
from kwantrace.position_direction import Position, Direction
from kwantrace.ray import Ray
from kwantrace.transformable import Transformable
from kwantrace.transformation import Transformation


class Renderable(Transformable):
    """
     Superclass for Primitive and Composite.

     This is able to be intersected and has an inside, but does not have a normal.
     It has a pigment since it is needed both for Primitive, and for Composite as the default pigment.
    """
    def setParent(self,Lparent):
        """
        Set a pointer to the parent object.

        :param Lparent: Parent of this object

        Intended to be used by the prepareRender() of container Renderable objects.
        """
        self.parent=Lparent # Used to find parent object to inherit default properties from
    def intersect(self,ray:Ray):
        """
        Intersect a ray with this Renderable, in world space.

        :param ray: Ray in world space
        :return: tuple[Primitive],float
        First is the primitive that is intersected, or None if none are. Second is t ray
        parameter if intersection occurs, unspecified if not.

        Note that this always a Primitive. This is able to see down through an arbitrarily
        large tree of Composite Renderables to pick out the actual visible surface geometry.
        """
        raise NotImplementedError("Abstract method")
    def inside(self,r:Position)->bool:
        """
        Determine if the given point is inside the Renderable.

        :param r: Point to check for insideness
        :return: True if point is inside, false if not.
        """
        raise NotImplementedError("Abstract method")
    def setPigment(self,Lpigment:ColorField=None):
        """
        Set the pigment.

        :param Lpigment: Pigment to use. If None is passed, the existing pigment is removed
        and the Renderable is treated as having no pigment.
        """
        self.pigment = Lpigment
    def evalPigment(self,r:Position):
        """
    / ** Evaluate the intrinsic color of this object at a point

        :param r: Position to evaluate the color at
        :return: Tuple of:
          * True if color is evaluated, false if not
          * Color at this point, if any. Unspecified if function returns false.
        """
        if self.pigment is not None:
            return self.pigment(r)
        elif self.parent is not None:
            return self.parent.evalPigment(r)
        else:
            return None
    def append(self,transform:Transformation):
        """
        Add a transformation to this Renderable.

        :param transform: Transformation to add

        Also adds the transformation to the Renderable object's pigment, if any
        """
        super().append(transform)
        if self.pigment is not None:
            self.pigment.add(transform)
    def prepareRender(self):
        """
        Prepare an object for rendering.

        This must be called between any change to the object and rendering the object.
        This calls the overridden method, and calls ColorField::prepareRender() on the
        associated pigment if any.
        """
        super().prepareRender()
        if self.pigment is not None:
            self.pigment.prepareRender()


# Type hint for list of renderables
RenderableList=list[Renderable]


class Primitive(Renderable):
    """
    Primitive object -- IE one that directly has geometry itself, rather than being a composite of other
    renderables. Subclasses of this only need to deal with local coordinates.
    """
    def _intersectLocal(self,rayLocal:Ray)->tuple[bool,float]:
        r"""
        Intersect a ray with this object, in object local space.

        :param rayLocal: ray in local object space
        :return: Tuple: First element is True if there is an intersection, false otherwise. Second element
          is ray parameter $t$ at intersection, and is unspecified if first element is False.

           \f$
             \def\M#1{{[\mathbf{#1}]}}
             \def\MM#1#2{{[\mathbf{#1}{#2}]}}
             \def\T{^\mathsf{T}}
             \def\operatorname#1{{\mbox{#1}}}
           \f$
        Any ray has the form \f$\vec{r}(t)=\vec{r}_0+\vec{v}t\f$. Broken down into
        components, it becomes:

           * \f$x(t)=x_0+v_xt\f$
           * \f$y(t)=y_0+v_yt\f$
           * \f$z(t)=z_0+v_zt\f$

        Any surface whatsoever, no matter how twisted, can be defined in the form
        \f$f(\vec{r})=0\f$. This is easier to imagine on a contour map.

        \image html Contour3D.jpg height=320px

        \image html Contour2D.png

        Imagine a topographical map of terrain -- it has two dimensions (since it's on paper)
        but has a third value at each point, the height. You can draw contour lines
        on the map connecting all the points at a given altitude. The beach might be labeled
        with height 0. A mountain would have a set of contour lines around the peak, generally
        getting smaller as the altitude gets higher.

        \image html Courbe_niveau.png

        The beach sea level defines a curve on the map. If the topography was all raised (or equivalently
        the water was lowered) the water would define a different curve. With the right topography and
        water level, literally *any* curve can be generated. We say that with some height field \f$h(x,y)\f$
        the beach curve is where \f$h(x,y)=0\f$. You can define different curves at height \f$k\f$ by
        looking for where \f$h(x,y)=k\f$ or equivalently define a different function \f$h'(x,y)=h(x,y)-k\f$
        and look for where \f$h'(x,y)=0\f$. So, any curve whatsoever can be defined by *some* function
        \f$f(x,y)=0\f$

        We can play the same game in three dimensions. Imagine space filled with a field with a field
        of scalars \f$f(x,y,z)\f$ where there is a value at each point. One example is the temperature in a room.
        Much like a beach sea level defines a curve, there is a *surface* defined for any value of
        the field \f$f(x,y,z)=k\f$ or \f$f'(x,y,z)=f(x,y,z)-k=0\f$.

        Now we use the ray formulas to find each coordinate as a function of \f$t\f$,
        and plug that into our equation and get:

           * \f$f(\vec{r}(t))=f(x_0+v_xt,y_0+v_yt,z_0+v_zt)=0\f$

        which is a single scalar equation with a single unknown. All parameter values \f$t\f$
        which satisfy this equation represent intersections between the surface and the ray.
        It might be complicated -- it might even be impossible to solve in closed form. But,
        by hook or by crook, we are going to find those values such that \f$f(\vec{r}+\vec{v}t)=0\f$.
        We call such \f$t\f$ values *roots*. The job of Primitive::intersect() and its overrides
        *is* to solve this equation for \f$t\f$. This might mean running the quadratic formula,
        it might mean solving some more complicated cubic, quartic, transcendental, etc equation.
        Or, it might even be something linear, like a plane.

        A root is just as good as a point, because you can put the root into the ray parametric
        equation and get the intersection point out. There is even Ray::operator()(double) to
        evaluate this directly.

        The equation might have no solutions when given a particular ray -- for instance, a lot of
        primitives like spheres, cylinders, and cones, can be described by quadratic equations.
        A quadratic equation might have two real roots, one real root, or no real roots at all.
        If the ray has two roots, this represents the case where the ray passes through the
        primitive and intersects the surface in two places (think entrance and exit). If it has
        only one root, this represents the case where the ray just grazes the surface. If there
        are no real roots, this represents the case where the ray completely misses the surface.

        Roots can be positive, negative, or zero. If they are negative, that means that they
        occur on the half of the ray which doesn't really exist. You can think of it as
        behind the camera or whatever. If \f$t=0\f$, we once again have the literally infinitesimal
        case of the plane passing exactly through the ray initial point, IE through the camera pinhole.

        Your primitive might have some kind of constraint. For instance, the quadratic definition
        of a cone is infinite. If you want to have a finite cone like you would put ice cream in,
        you have to apply a constraint. Say that your cone axis is the Z axis, and the vertex
        is at the origin. Also say that you want a finite cone that is only one unit tall, or in
        other words runs from z=0 to z=1. Now suppose you have a ray that hits the infinite cone
        at z=2. In this case, the constraint is not satisfied, so this root doesn't count.
        If no other root satisfies the constraint, there is no intersection even though the ray would
        hit the infinite continuation of your constrained primitive.

        So, set the output parameter `t` to the one with the smallest positive \f$t\f$ that
        satisfies the constraint, then return true. If there are no intersections, or if all
        intersections have negative \f$t\f$, or they all don't satisfy the constraint, return false.
        """
        raise NotImplementedError("Abstract method")

    def _normalLocal(self,rLocal:Position)->Direction:
        """
        Generate the normal vector to an object at a point.

        :param rLocal: point on surface of object, already transformed into local object space
        :return: Normal to surface

        It is unspecified behavior to call this on a point which is not on the surface
        of an object -- the function may return any value at all. That being said, it is
        better to be forgiving in the face of floating point limited precision.

        Don't worry about returning a unit-length normal, that is done upstream. You can't
        even do it if you wanted to, since it needs to be unit-length in world coordinates.

        """
        raise NotImplementedError("Abstract method")
    def _insideLocal(self,rLocal:Position)->bool:
        """
        Check if a point is inside the object, in object local space

        :param rLocal: Point in object coordinates
        :return: True if point is inside object, false if not
        """
        raise NotImplementedError("Abstract method")
    def __init__(self):
        # If true, the object is inside out. Primitive::inside() is inverted and the
        # direction of the normal is reversed for inside-out images.
        self.inside_out=False
    def intersect(self,ray:Ray,t:float):
        if self.intersectLocal(self.M_br @ ray, t):
            return self
        else:
            return None
    def normal(self,r:Position)->Direction:
        r"""
        Calculate the surface normal at a given point in world coordinates.

        :param r: point in world coordinates at which to calculate the normal
        :return: Unit normal vector in world coordinates

        This transforms the point to body coordinates, calls the descendant's
        Primitive::normalLocal() to get the normal in body coordinates, then transforms
        the normal to world coordinates.

         \f$
           \def\M#1{{[\mathbf{#1}]}}
           \def\MM#1#2{{[\mathbf{#1}{#2}]}}
           \def\T{^\mathsf{T}}
           \def\operatorname#1{{\mbox{#1}}}
        \f$
        Special consideration must be taken to transform the normals into world coordinates.
        If you just use the \f$\MM{M}{_{b2w}}\f$ transformation, this will be wrong, as in general
        an arbitrary affine transformation does not preserve angles -- translation, rotation
        and uniform scaling do, but non-uniform scaling does not. Shearing doesn't either,
        but that can be thought of as a combination of a rotation and non-uniform scaling.

        \image html Normal_scale.png

        Since the *fundamental* property of a normal is that its angle to the surface is a
        right angle, it is a problem that angles are not preserved. Therefore we have to
        think about it a different way. The following derivation follows that of
        https://www.cs.auckland.ac.nz/courses/compsci373s1c/PatricesLectures/2011/CS373-Part1-Lecture11-RayTracing3.pdf ,
        slide 11.

        Assume there is some matrix \f$\MM{Q}{_{b2w}}\f$ which properly transforms a
        normal from body to world coordinates. As it so happens, there is, and
        it only depends on \f$\MM{M}{_{b2w}}\f$, not any of \f$\vec{r}\f$, \f$\vec{n}\f$,
        or \f$\vec{p}\f$. That's the wonderful thing about linear algebra, is that it's *linear*.
        Starting from the assumption that there *is* an answer, we
        will construct the answer and show that it only depends on \f$\MM{M}{_{b2w}}\f$

        In the body frame, imagine the direction vectors \f$\vec{p}\f$ parallel to the surface
        and therefore perpendicular to the normal. There are an infinite number of such vectors, and what
        we do below has to apply to them all, so it can't depend on the particular value of \f$\vec{p}\f$.

        Since any such vector is parallel to the surface, it is perpendicular to the normal \f$\vec{n}\f$
        and therefore \f$\vec{n}\cdot\vec{p}=0\f$. Considering the vectors to be column
        vectors, we can express the dot product as a matrix product if we transpose
        the first vector, so we have \f$\M{n}\T\M{p}=0\f$.

        These vectors *do* obey the \f$\MM{M}{_{b2w}}\f$ transformation, since they must follow
        the surface, and the surface certainly does obey the transformation. We will have
        \f$\vec{p}'=\MM{M}{_{b2w}}\vec{p}\f$.

        Any new normal \f$\vec{n}'\f$ must still be perpendicular, so it must be true that
        \f$\vec{n}'\cdot\vec{p}'=0\f$, or \f$\MM{n}{'}\T\MM{p}{'}=0\f$. We substitute in
        \f$\vec{n}'=\MM{Q}{_{b2w}}\vec{n}\f$ and \f$\vec{p}'=\MM{M}{_{b2w}}\vec{p}\f$
        into our matrix dot product and come up with:

        \f$(\MM{Q}{_{b2w}}\M{n})\T(\MM{M}{_{b2w}}\M{p})=0\f$

        Now it's just linear algebra:

         \f$\begin{eqnarray*}
         0&=&(\MM{Q}{_{b2w}}\M{n})\T(\MM{M}{_{b2w}}\M{p}) \\
          &=&(\M{n}\T\MM{Q}{_{b2w}}\T)(\MM{M}{_{b2w}}\M{p}) \\
          &=&\M{n}\T\MM{Q}{_{b2w}}\T\MM{M}{_{b2w}}\M{p} \\
         \end{eqnarray*}\f$

        If that middle cluster of matrices simplified into an identity matrix, we would
        be left with \f$\M{n}\T\M{p}=0\f$, which is assumed to be true as our starting
        condition. So, [all we have to do now is to take these lies and makes them true
        somehow...](https://youtu.be/diYAc7gB-0A?t=127) We assume that the middle cluster of matrices
        is identity, then solve for \f$\MM{Q}{_{b2w}}\f$ given find a \f$\MM{M}{_{b2w}}\f$.

        \f$\begin{eqnarray*}
        \MM{Q}{_{b2w}}\T\MM{M}{_{b2w}}&=&\M{1} \\
        \MM{Q}{_{b2w}}\T\MM{M}{_{b2w}}\MM{M}{_{b2w}}^{-1}&=&\M{1}\MM{M}{_{b2w}}^{-1} \\
        \MM{Q}{_{b2w}}\T&=&\MM{M}{_{b2w}}^{-1} \\
        \MM{Q}{_{b2w}}&=&(\MM{M}{_{b2w}}^{-1})\T \\
        \end{eqnarray*}\f$

        And there it is. There is a matrix that transforms a normal from body to world space,
        that only depends on matrix \f$\MM{M}{_{b2w}}\f$, not on any of the vectors.

        Since this is commonly used, we will ask our transformation chain to calculate it
        at the same time that it concatenates all of the transformations into a single matrix.

        Note that this transformation does not promise to preserve the length of the normal.
        Since some algorithms (Snell's law etc) depend on the normal having unit length,
        we will make sure to return a unit normal.

        Also, if the primitive is inside out, we will reverse the direction of the normal.
        """
        return (-1 if self.inside_out else 1) * vnormalize(self.N_rb * self._normalLocal(self.M_br @ r))
    def inside(self,r:Position)->bool:
        """
        Calculate if a point is inside the primitive.

        :param r:
        :return: True if point is inside the primitive

        This transforms the point to body coordinates, calls the descendant's
        Primitive::insideLocal() on the point, and returns the result.

        This code takes into account inside_out, so the descendant
        doesn't have to (and shouldn't).
        """
        return self.inside_out ^ self.insideLocal(self.M_br @ r)

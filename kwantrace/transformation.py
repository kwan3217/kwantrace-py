"""
KwanTrace_py - Python Ray Tracing Library
Copyright (C) 2023 by kwan3217

"""
import numpy as np
from kwanmath.matrix import rot_axis
from kwanmath.vector import vnormalize, vcross

from position_direction import col_vector, Direction


class Transformation:
    """
    Represent an arbitrary transformation.

    It can have any members it needs, but must be able to take its members and generate a matrix
    on demand. Members are intended to be changed (IE properties).

    I really didn't want to make this one -- I hoped to be able to use the Eigen transformations
    directly, but things like translate, rotate, scale etc don't have a common base class, so they
    can't be grouped in a common container.

    Besides, if I do it this way, I have a good spot for my thesis on the Point-Toward transformation.

    I have to call this "Transformation" instead of "Transformer" because otherwise I will be
    thinking about robots in disguise...
    """
    def matrix(self)->np.array:
        """
        Construct the matrix for this transformation.

        This can read any of the parameters in the class.
        :return: Matrix representing the transformation
        """
        raise NotImplementedError()


class Translation(Transformation):
    """
    Represent a translation.

    The vector represents the coordinates of origin of the body frame, in the world frame.
    """
    def __init__(self,Lamount:np.array=None,Lx:float=None,Ly:float=None,Lz:float=None):
        if Lamount is None:
            self.amount=col_vector(Lx,Ly,Lz)
        else:
            self.amount=Lamount.reshape(3,1)
    def matrix(self)->np.array:
        result=np.identity(4)
        result[0,0:3]=self.amount[:]
        return result


class Scaling(Transformation):
    """
    Represent a non-uniform scaling, IE one that can be different along the three body axes.

   The vector represents the stretch factor in each direction. Since Bad Things happen if
   you specify a scale of zero (matrices are no longer full-rank and therefore no longer
   invertible) we adopt the POV-Ray convention and interpret requests to scale as zero to
   be requests to scale as 1. In this code, we do the substitution silently, unlike in
   POV-Ray where you get a warning if you do that.
   """
    def __init__(self, Lamount: np.array = None, Lx: float = None, Ly: float = None, Lz: float = None):
        if Lamount is None:
            self.amount = col_vector(Lx, Ly, Lz)
        else:
            self.amount = Lamount.reshape(3, 1)
    def matrix(self) -> np.array:
        result = np.identity(4)
        result[0, 0] = self.amount[0] if self.amount[0]!=0 else 1.0
        result[1, 1] = self.amount[1] if self.amount[1]!=0 else 1.0
        result[2, 2] = self.amount[2] if self.amount[2]!=0 else 1.0
        return result


class UniformScaling(Transformation):
    """
     Represent a uniform scaling in all directions.

     You could use
     a vector Scaling, but then you would have to change all three
     components of the scaling vector to keep the scaling uniform.
    """
    def __init__(self, Lamount: float = 1.0):
        self.amount = Lamount
    def matrix(self) -> np.array:
        result = np.identity(4)
        result[0, 0] = self.amount if self.amount!=0 else 1.0
        result[1, 1] = self.amount if self.amount!=0 else 1.0
        result[2, 2] = self.amount if self.amount!=0 else 1.0
        return result


class RotateScalar(Transformation):
    """
    Represents a right-handed physical rotation around a coordinate frame axis.

    Right-handed means if you wrap the fingers of your *right* hand around the
    rotation axis, with your thumb pointed in the positive direction of the axis,
    your fingers will wrap around the axis in the positive sense.

    \image html Right-hand_grip_rule.png

    For instance, if an object is pointed down the x axis and you rotate it +90&deg;
    around the z axis, the object will then be pointed down the y axis.

    """
    def __init__(self,Lamount:float, axis:int, isDegrees:bool=True):
        """
        Construct a rotation, optionally specifying the angle in degrees

        :param Lamount: Angle to rotate
        :param axis: Axis about which to rotate, x=0, y=1, z=2
        :param isDegrees: If true, Lamount is specified in degrees. Otherwise it is specified in radians.
        """
        self.amount=Lamount
        self.axis=axis
        self.isDegrees=isDegrees
    def matrix(self):
        result=np.identity(4)
        result[0:3,0:3]=rot_axis(self.axis,np.deg2rad(self.amount) if self.isDegrees else self.amount)
        return result


class RotateX(RotateScalar):
    def __init__(self,Lamount:float,isDegrees:bool=True):
        super().__init__(Lamount,0,isDegrees)


class RotateY(RotateScalar):
    def __init__(self, Lamount: float, isDegrees: bool = True):
        super().__init__(Lamount, 1, isDegrees)


class RotateZ(RotateScalar):
    def __init__(self,Lamount:float,isDegrees:bool=True):
        super().__init__(Lamount,2,isDegrees)


class RotateVector(Transformation):
    """
     Represents a right-handed physical rotation around each coordinate frame axis in turn.

     This is in a sense an Euler angle rotation, but in a rather inflexible way -- if you
     want a Euler angle rotation, chain together three RotateScalar objects around the axes
     you want in the order you want.

     This represents a rotation around the x axis by the amount specified by the x component
     of the parameter, followed by a rotation around the y axis as specified by the y
     component of the parameter, followed by the same for z. The order is not flexible.

     This emulates a POV-Ray rotate with a vector parameter (except for being right-handed rotations).
    """
    def __init__(self, Lamount: np.array = None, Lx: float = None, Ly: float = None, Lz: float = None, isDegrees:bool=True):
        """
        Construct a RotateVector, optionally specifying the angles in degrees

        :param Lamount:
        :param Lx: Amount to rotate around X axis
        :param Ly: Amount to rotate around Y axis
        :param Lz: Amount to rotate around Z axis
        :param isDegrees: If true, interpret values as degrees, otherwise radians
        """
        if Lamount is None:
            self.amount = np.array([[Lx], [Ly], [Lz]])
        else:
            self.amount = Lamount.reshape(3, 1)
        self.isDegrees=isDegrees
    def matrix(self):
        result=np.identity(4)
        result[0:3,0:3]=rot_axis(0,np.deg2rad(self.amount[0]) if self.isDegrees else self.amount[0])
        result[0:3,0:3]=rot_axis(1,np.deg2rad(self.amount[1]) if self.isDegrees else self.amount[1]) @ result[0:3,0:3]
        result[0:3,0:3]=rot_axis(2,np.deg2rad(self.amount[2]) if self.isDegrees else self.amount[2]) @ result[0:3,0:3]
        return result


def calcPointToward(p_b,p_r,t_b,t_r):
    """

   Calculate the matrix representing this Point-Toward transformation.

   :param p_b: point vector in body frame
   :param p_r: point vector in world frame
   :param t_b: toward vector in body frame
   :param t_r: toward vector in world frame
   :return: 4x4 Matrix representing the point-toward transformation, and no translation

  ## Problem Statement
  \f$
     \def\M#1{{[\mathbf{#1}]}}
     \def\MM#1#2{{[\mathbf{#1}{#2}]}}
     \def\T{^\mathsf{T}}
     \def\operatorname#1{{\mbox{#1}}}
  \f$
  Given a rigid body with vectors from its origin to direction (normalized vector)
  \f$\hat{p}_b\f$ and \f$\hat{t}_b\f$ in the body frame, and an external frame
  centered on the same origin with directions \f$\hat{p}_r\f$ and \f$\hat{t}_r\f$,
  find the physical rotation that points \f$\hat{p}_b\f$ and \f$\hat{p}_r\f$
  at the same direction, while simultaneously pointing \f$\hat{t}_b\f$ as close as
  possible to \f$\hat{t}_r\f$.

  ### Example
  The Space Shuttle has a thrust vector which is not parallel to any of the body axes.
  We wish to point the thrust vector in the correct direction in the reference system,
  while simultaneously flying heads-down, which is equivalent to pointing the tail
  towards the ground. In this case, \f$\hat{p}_b\f$ is the thrust vector in the body
  frame, \f$\hat{p}_r\f$ is the guidance-calculated thrust vector in the reference
  frame, \f$\hat{t}_b\f$ is the body axis which points heads-up, say \f$\hat{z}_b\f$,
  and \f$\hat{t}_r\f$ is the vector from the spacecraft location towards the center
  of the Earth.

  \image html 320px-Point_constraint.svg.png

  \image html 320px-Toward_constraint.svg.png

  ## Solution
  We are going to do this with matrices. The solution matrix is going to be called
  \f$\MM{M}{_{rb}}\f$ and will transform *from* the body frame *to* the reference frame.

  First, it is obviously impossible to in general satisfy both the "point" constraint
  \f$\hat{p}_r=\MM{M}{_{rb}}\hat{p}_b\f$ and the toward constraint \f$\hat{t}_r=\MM{M}{_{rb}}\hat{t}_b\f$.
  Satisfying both is possible if and only if the angle between \f$\hat{p}_r\f$ and \f$\hat{t}_r\f$
  is the same as the angle between \f$\hat{p}_b\f$ and \f$\hat{t}_b\f$. When these
  angles do not match, the point constraint will be perfectly satisfied, and the
  angle between the body and reference toward vectors will be as small as possible.
  Using geometric intuition, it is obvious but not proven here that the angle is
  minimum when the point vector, transformed body toward vector, and reference toward
  vector are all in the same plane. This means that we can create a third vector
  \f$\hat{s}=\operatorname{normalize}(\hat{p} \times \hat{t})\f$. This vector is
  normal to the plane containing point and toward in both frames, so when the plane
  is the same, these vectors match. Therefore we have another constraint which can
  be perfectly satisfied, \f$\hat{s}_r=\MM{M}{_{rb}}\hat{s}_b\f$.
  So, we have:

  \f$\begin{bmatrix}\hat{p}_r && \hat{s}_r\end{bmatrix}=\MM{M}{_{rb}}\begin{bmatrix}\hat{p}_b && \hat{s}_b\end{bmatrix}\f$

  This isn't quite enough data, it works out to nine unknowns and six equations.
  We can add one more constraint by considering the vector \f$\hat{u}\f$ perpendicular
  to both \f$\hat{p}\f$ and \f$\hat{s}\f$:

  \f$\hat{u}=\hat{p} \times \hat{s}\f$

  We already know that this will be unit length since \f$\hat{p}\f$ and \f$\hat{s}\f$
  are already perpendicular. Since these three vectors are perpendicular in both frames,
  only an orthogonal matrix can transform all three vectors and maintain the angles
  between them, so this third vector is equivalent to adding an orthogonality constraint.

  \f$\M{R}=\begin{bmatrix}\hat{p}_r && \hat{s}_r\ && \hat{u}_r \end{bmatrix}\f$

  (treating the vectors as column vectors)

  \f$\begin{eqnarray*}
     \M{B}&=&\begin{bmatrix}\hat{p}_b && \hat{s}_b\ && \hat{u}_b \end{bmatrix} \\
     \M{R}&=&\MM{M}{_{rb}}\M{B} \\
     \M{R}\M{B}^{-1}&=&\MM{M}{_{rb}}\end{eqnarray*}\f$

 The above calls for a matrix inverse, but who has time for that? Since all the columns of
  \f$\M{B}\f$ (and \f$\M{R}\f$ for that matter) are unit length and perpendicular to each
  other, the matrix is orthogonal, which means that its inverse is its transpose.

  \f$\M{R}\M{B}^T=\MM{M}{_{rb}}\f$

  And that's the solution. Note that if you need \f$\MM{M}{_{br}}\f$, it is also a transpose
  since this answer is still an orthonormal (IE rotation) matrix.
   """
    s_r = vnormalize(vcross(p_r,t_r))
    u_r = vnormalize(vcross(p_r,s_r))
    R=np.hstack((vnormalize(p_r),s_r,u_r))
    s_b = vnormalize(vcross(p_b,t_b))
    u_b = vnormalize(vcross(p_b,s_b))
    B=np.hstack((vnormalize(p_b), s_b, u_b))
    M_rb=np.identity(4)
    M_rb[0:3,0:3]=R @ B.T
    return M_rb


class PointToward(Transformation):
    """
     Represent the Point-Toward transformation.

     This rotates an object such that
     p_b in the body frame points at p_r in the world frame, and t_b in the body frame is towards
     t_r in the world frame.
    """
    def __init__(self,Lp_b:np.array,Lp_r:np.array,Lt_b:np.array,Lt_r:np.array):
        """
        Construct a Point-Toward transformation

        :param Lp_b: point vector in body frame
        :param Lp_r: point vector in world frame
        :param Lt_b: toward vector in body frame
        :param Lt_r: toward vector in world frame
        """
        self.p_b=Lp_b
        self.p_r=Lp_r
        self.t_b=Lt_b
        self.t_r=Lt_r
    def matrix(self):
        return calcPointToward(self.p_b, self.p_r, self.t_b, self.t_r)


def calcLocationLookat(location,look_at,p_b=None,t_b=None,t_r=None):
    """
    Creates a matrix which performs the location-look_at transformation.

    :param location: Location to rotate around and translate to
    :param look_at: Point p_b at this point
    :param p_b: body point direction, default is +z (POV-ray camera direction)
    :param t_b: body toward direction, default is +y (camera down)
    :param t_r: world toward direction, default is -z (camera ground)
    :return: Transformation matrix which does the job
    """
    if p_b is None:
        p_b=Direction( 0.0, 0.0, 1.0)
    if t_b is None:
        t_b=Direction( 0.0, 1.0, 0.0)
    if t_r is None:
        t_r=Direction( 0.0, 0.0,-1.0)
    result=calcPointToward(p_b=p_b,p_r=look_at-location,t_b=t_b,t_r=t_r) #Use point-toward to point in target direction
    result=Translation(location).matrix() @ result; #Translate to location
    return result


class LocationLookat(Transformation):
    """
    Represent the Location-Look_at transformation.

    This is the model used in POV-Ray for the camera, generalized so it can work for any object. In
    POV-Ray, the camera direction is constrained by the vectors `location`, `look_at`, and `sky`.
    These vectors are used to calculate a transformation that such that the `direction` vector in
    camera space points from `location` to `look_at` in world space, and the `up` vector in camera
    space points as closely as possible to the `sky` vector in world space.

    We generalize by allowing `p_b` to be any vector and defaulting it to the same direction as
    body `direction` for a camera, +z. We calculate the equivalent to `p_r` ourselves from
    `location` and `look_at`. We default `t_b` to be the `down` vector of the camera (since we
    use a right-handed camera, we use `down` instead of `up`) and default `t_r` to be the negative
    of the default `sky` vector, -y. The body origin will be translated to `location` in world space.

    """
    def __init__(self,Llocation,Llook_at,Lp_b=None,Lt_b=None,Lt_r=None):
        """
        Construct a Location-LookAt transformation

        :param Llocation: Location position
        :param Llook_at: Look-at position
        :param Lp_b: Point body direction, default is +z
        :param Lt_b: Toward body direction, default is +y
        :param Lt_r: Toward world direction, default is -z
        """
        self.location=Llocation
        self.look_at=Llook_at
        self.p_b=Lp_b if Lp_b is not None else Direction( 0, 0, 1)
        self.t_b=Lt_b if Lt_b is not None else Direction( 0, 1, 0)
        self.t_r=Lt_r if Lt_r is not None else Direction( 0, 0,-1)
    def matrix(self):
        return calcLocationLookat(self.location,self.look_at,self.p_b,self.t_b,self.t_r)

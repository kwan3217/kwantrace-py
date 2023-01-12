"""
Position and Direction vectors.

In Python, we represent this as two plain functions that take three float arguments,
and return a numpy 4-element column vector with the appropriate `w` in the last slot.

We won't go over all of linear algebra here, just one interesting point.
A matrix operation can do any [linear transformation](https://youtu.be/kYB8IZa5AuE?t=155) of a vector, but
linear transformations themselves are restricted to map the origin to the origin. There is no
way with a linear transformation to do a translation.

So, we use a trick -- we extend the vectors to a higher dimension.
Note that I didn't discover this trick -- it's been used for at least
decades, maybe centuries. PostScript 2D transformation is based on
the 2D version of this.

To explain the trick, we will look at a 2D vector. You can rotate,
shear, scale, or any combination of these with the appropriate 2x2 matrix, but
such a matrix will always transform the origin to the origin.

\f$\vec{r}'=[\mathbf{M}]\vec{r}=\begin{bmatrix}x_r'\\y_r'\end{bmatrix}=\begin{bmatrix}m_{00} & m_{01} \\ m_{10} & m_{11}\end{bmatrix}\begin{bmatrix}x_r\\y_r\end{bmatrix}\f$

So, we add another element to our vector, and a new row and
column to the matrix. To understand this, we will have to know
a bit about how matrix multiplication works, so be sure to watch
that whole video.

To start with, let's look at that 2x2 matrix multiplication.
Each component of the new vector \f$\vec{r}\f$ is found from the
matrix and old vector as follows:

\f$\begin{eqnarray*}x'&=&m_{00}x&+&m_{01}y\\
                    y'&=&m_{10}x&+&m_{11}y\end{eqnarray*}\f$

If you put in zero components for both x and y, it is impossible to
get anything other than zero out, no matter what the matrix is.

But with the extended matrix, we have more options. First Let's look
at a pure translation. If we extend the matrix and vector this way:

\f$\vec{r}''=[\mathbf{M}]\vec{r}=\begin{bmatrix}x_r''\\y_r''\\w_r''\end{bmatrix}
=\begin{bmatrix}1 & 0 & t_x\\
                0 & 1 & t_y \\
                0 & 0 &  1\end{bmatrix}\begin{bmatrix}x_r\\y_r\\w_r=1\end{bmatrix}\f$

then when we do the multiplication to find \f$x_r''\f$, we will get

\f$1x_r+0y_r+t_xw_r\f$

and since \f$w_r=1\f$, then this simplifies to

\f$x_r''=x_r+t_x\f$

which is exactly what we want. Similarly
we get \f$y_r''=0x_r+1y_r+t_yw_r=y_r+t_y\f$. For the new component, we have \f$w''=0x_r+0y_r+1w_r=1\f$
so this extended vector is in the right form to be translated again by another matrix.

How is this different from before? The reason this works is that with \f$w_r=1\f$,
it is never a zero vector being put in.

Another way to think about it is that the 2D vector is extended into 3D space. The
"translation" matrix is just a shear of the new axis, and since our vector is riding
on w=1, a shear of the given amount looks like a translation when projected back
down into 2D space

For even fewer dimensions and so that I can draw it on 2D paper, let's think about
1D. A 1D vector is just a number, and a 1x1 matrix is also just a number. If you
multiply zero by any number, you will still get zero and so we still have our translation problem.

We solve this the same way as in higher dimensions.

\image html 1Dtranslate.png
   *
Going further, it turns out that the upper left 2x2 of the matrix is just a normal
2x2 matrix, capable of shearing, rotation, scaling, etc. If we look in detail we see:

\f$\vec{r}''=[\mathbf{M}]\vec{r}=\begin{bmatrix}x_r''\\y_r''\\w_r''\end{bmatrix}
=\begin{bmatrix}m_{00} & m_{01} & t_x\\
                m_{10} & m_{11} & t_y \\
                0 & 0 &  1\end{bmatrix}\begin{bmatrix}x_r\\y_r\\1\end{bmatrix}\f$

\f$\begin{eqnarray*}
x_r''&=&m_{00}x_r+m_{01}y_r+t_x \\
   &=&x_r'+t_x \\
y_r''&=&m_{00}x_r+m_{01}y_r+t_x \\
   &=&y_r'+t_y\\
\end{eqnarray*}\f$

Now notice that if we set \f$w=0\f$, we can still use that matrix to transform,
but the vector won't participate in translation, just the upper-left part rotation/shear/scale.
There are cases that we *want* this, and we call them direction vectors. Imagine a Ray
with \f$\vec{r}(t)=\vec{r}_0++\vec{v}t\f$. If we translate the ray, we want only the initial
position to change, not the direction. If we do an arbitrary transform with both
translation and rotation/shear/scale, we only want the direction part to participate
in the rotation/shear/scale.

 \f$\vec{v}''=[\mathbf{M}]\vec{v}=\begin{bmatrix}x_v'\\y_v'\\w_v'\end{bmatrix}
             =\begin{bmatrix}m_{00} & m_{01} & t_x\\
                             m_{10} & m_{11} & t_y \\
                             0 & 0 &  1\end{bmatrix}\begin{bmatrix}x_v\\y_v\\w_v=0\end{bmatrix}\f$

\f$\begin{eqnarray*}
x_v''&=&m_{00}x_v+m_{01}y_v+t_x(0) \\
   &=&x_v' \\
y_v''&=&m_{00}x_v+m_{01}y_v+t_x(0) \\
   &=&y_v'\\
\end{eqnarray*}\f$

There is a whole theory of [homogeneous coordinates](https://en.wikipedia.org/wiki/Homogeneous_coordinates)
that uses any value of \f$w\f$, but so far I haven't found any use but 0 and 1.
"""
import numpy as np


def Position(x:float,y:float,z:float):
    """
    Return a Position vector.

    A position vector is a vector that participates in translation. This is represented
    as a 4-element vector with 1.0 in the `w` slot.
    
    :param x: x component
    :param y: y component
    :param z: z component
    :return: 4-element column vector with 1 as w component
    """
    return np.array([[x],[y],[z],[1.0]])


def Direction(x: float, y: float, z: float):
    """
    Return a Direction vector.

    A direction vector is a vector that does not participate in translation. This is represented
    as a 4-element vector with 0.0 in the `w` slot.

    :param x: x component
    :param y: y component
    :param z: z component
    :return: 4-element column vector with 0 as w component
    """
    return np.array([[x], [y], [z], [0.0]])


def col_vector(x: float, y: float, z: float):
    """
    Return a column vector. This is just a 3-element vector so it can't be used with a 4x4 transformation
    matrix.

    :param x: x component
    :param y: y component
    :param z: z component
    :return: 3-element column vector
    """
    return np.array([[x], [y], [z]])

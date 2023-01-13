import numpy as np
from kwanmath.vector import vnormalize, vcross

from kwantrace.transformation import calcPointToward

def test_calcPointToward():
    """
    /** Exercise pointToward().

    :return: None, but raises an exception if the test fails

     * \image html Space_Shuttle_Coordinate_System.jpg
     * \f$
     *    \def\M#1{{[\mathbf{#1}]}}
     *    \def\MM#1#2{{[\mathbf{#1}{#2}]}}
     *    \def\T{^\mathsf{T}}
     *    \def\operatorname#1{{\mbox{#1}}}
     * \f$
     *
     * The space shuttle has a thrust axis 13&deg; below the X axis, so:
     * \f$\hat{p}_b=\begin{bmatrix}\cos 13^\circ \\ 0 \\ -\sin 13^\circ \end{bmatrix}
     *   =\begin{bmatrix}0.974370 \\ 0.000000 \\ -0.224951 \end{bmatrix}\f$
     *
     * The heads-up vector is \f$\hat{t}_b=\hat{z}_b\f$. At a particular instant,
     * the guidance command says to point the thrust vector 30&deg; above the horizon
     * at an azimuth of 80&deg; east of North. We'll take the local topocentric horizon
     * frame as the reference frame, with \f$\hat{x}_r\f$ in the horizon plane pointing
     * east, \f$\hat{y}_r\f$ pointing north, and \f$\hat{z}_r\f$ pointing up. In this
     * frame, the guidance command is:
     *
     * \f$\hat{p}_r=\begin{bmatrix}\cos 30^\circ \sin 80^\circ \\
     *                             \cos 30^\circ \cos 80^\circ \\
     *                             \sin 30^\circ\end{bmatrix}=\begin{bmatrix}0.852869 \\
     *                                                                       0.150384 \\
     *                                                                       0.500000\end{bmatrix}\f$
     *
     * The vehicle is also commanded to the heads-down attitude, which means that
     * \f$\hat{t}_r=-\hat{z}_r\f$. These are all the inputs we need.
     *
     * \f$\hat{s}_b=\operatorname{normalize}(\hat{p}_b \times \hat{t}_b)=\begin{bmatrix} 0 \\
     *                                                                                  -1 \\
     *                                                                                   0 \end{bmatrix}\f$
     *
     * \f$\hat{u}_b=\operatorname{normalize}(\hat{p}_b \times \hat{s}_b)=\begin{bmatrix} -0.224951 \\
     *                                                                                    0.000000 \\
     *                                                                                   -0.974370 \end{bmatrix}\f$
     *\f$\hat{s}_r=\operatorname{normalize}(\hat{p}_r \times \hat{t}_r)=\begin{bmatrix} -0.173648 \\
     *                                                                                   0.984808 \\
     *                                                                                   0.000000 \end{bmatrix}\f$
     *
     *\f$\hat{u}_r=\operatorname{normalize}(\hat{p}_r \times \hat{s}_r)=\begin{bmatrix} -0.492404 \\
     *                                                                                  -0.086824 \\
     *                                                                                  -0.866025 \end{bmatrix}\f$
     *
     * \f$\M{R}=\begin{bmatrix}\hat{p}_r && \hat{s}_r\ && \hat{u}_r \end{bmatrix}=\begin{bmatrix}0.852869&&-0.173648&&-0.492404\\
     *                                                                                   0.150384&& 0.984808&&-0.086824\\
     *                                                                                   0.500000&& 0.000000&& 0.866025\end{bmatrix}\f$
     *
     * \f$\M{B}=\begin{bmatrix}\hat{p}_b && \hat{s}_b\ && \hat{u}_b \end{bmatrix}=\begin{bmatrix}0.974370&& 0.000000&&-0.224951\\
     *                                                                                           0.000000&&-1.000000&&-0.000000\\
     *                                                                                          -0.224951&& 0.000000&&-0.974370\end{bmatrix}\f$
     *\f$\M{M_{br}}=\M{R}\M{B}^{-1}=\begin{bmatrix}0.941776&& 0.173648&& 0.287930\\
     *                                             0.166061&&-0.984808&& 0.050770\\
     *                                             0.292372&& 0.000000&&-0.956305\end{bmatrix}\f$
     *
     * There is the solution, but does it work?
     *
     * \f$\begin{eqnarray*}\M{M_{br}}\hat{p}_b&=&\begin{bmatrix} 0.852869\\ 0.150384\\ 0.500000\end{bmatrix}&=&\hat{p}_r \\
     *                     \M{M_{br}}\hat{s}_b&=&\begin{bmatrix}-0.173648\\ 0.984808\\ 0.000000\end{bmatrix}&=&\hat{s}_r \\
     *                     \M{M_{br}}\hat{u}_b&=&\begin{bmatrix}-0.492404\\-0.086824\\ 0.866025\end{bmatrix}&=&\hat{u}_r \\
     *                     \M{M_{br}}\hat{t}_b&=&\begin{bmatrix} 0.287930\\ 0.050770\\-0.956305\end{bmatrix}, \operatorname{vangle}(\M{M_{br}}\hat{t}_b,\hat{t}_r)=17^\circ\end{eqnarray*}\f$
     *
     * That's a decisive yes.
     */

    """
    p_b=np.array([[np.cos(np.deg2rad(13))]
                  [0],
                  [-np.sin(np.deg2rad(13))],
                  [0]])
    print(f"{p_b=}")
    t_b=np.array([[0],[0],[1],[0]])
    print(f"{t_b=}")
    p_r=np.array([[np.cos(np.deg2rad(30))*np.sin(np.deg2rad(80))],
                  [np.cos(np.deg2rad(30))*np.cos(np.deg2rad(80))],
                  [np.sin(np.deg2rad(30))],
                  [0]])
    print(f"{p_r=}")
    t_r=np.array([[0],[0],[-1],[0]])
    s_b=vnormalize(vcross(p_b,t_b))
    print(f"{s_b=}")
    u_b=vnormalize(vcross(p_b,s_b))
    print(f"{u_b=}")
    s_r=vnormalize(vcross(p_r,t_r))
    print(f"{s_r=}")
    u_r=vnormalize(vcross(p_r,s_r))
    print(f"{u_r=}")
    R=np.hstack((p_r,s_r,u_r))
    print(f"{R=}")
    B=np.hstack((p_b,s_b,u_b))
    print(f"{B=}")
    M_rb_direct=R*B.T
    print(f"{M_rb_direct=}")
    M_rb=calcPointToward(p_b,p_r,t_b,t_r)
    print(f"{M_rb=}")
    print(f"M_rb@p_b (should equal p_r) {M_rb@p_b} ")
    assert np.allclose(M_rb@p_b,p_r)
    print(f"M_rb@s_b (should equal s_r) {M_rb@s_b} ")
    assert np.allclose(M_rb@s_b,s_r)
    print(f"M_rb@u_b (should equal u_r) {M_rb@u_b} ")
    assert np.allclose(M_rb@u_b,u_r)
    print(f"M_rb@t_b (should be towards t_r) {M_rb@t_b} ")

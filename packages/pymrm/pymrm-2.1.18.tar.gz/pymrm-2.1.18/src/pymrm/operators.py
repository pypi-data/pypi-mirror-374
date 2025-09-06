"""
Operators Submodule for pymrm

This submodule provides numerical operators for spatial discretization,
including gradient and divergence operators.
These operators are essential for constructing finite difference
and finite volume schemes used in multiphase reactor modeling.

Functions:
- construct_grad: Constructs the gradient matrix for spatial differentiation.
- construct_grad_int: Constructs the gradient matrix for internal faces.
- construct_grad_bc: Constructs the gradient matrix for boundary faces.
- construct_div: Constructs the divergence matrix for flux calculations.

Dependencies:
- numpy
- scipy.sparse
- pymrm.grid (for optional grid generation)
- pymrm.helpers (for boundary condition handling)
"""

import math
import numpy as np
from scipy.sparse import csc_array
from pymrm.helpers import unwrap_bc_coeff
from pymrm.grid import generate_grid


def construct_grad(shape, x_f, x_c=None, bc=(None, None), axis=0, shapes_d=(None, None)):
    """
    Construct the gradient matrix for spatial differentiation.

    Parameters:
        shape (tuple or int): Shape of the domain. If an integer is provided, it is converted to a tuple.
        x_f (ndarray): Face positions.
        x_c (ndarray, optional): Cell center coordinates. If not provided, they are calculated.
        bc (tuple, optional): Boundary conditions as a tuple of dictionaries. Default is (None, None).
        axis (int, optional): Axis of differentiation. Default is 0.
        shapes_d (tuple, optional): Shapes for boundary condition contributions. Default is (None, None).

    Returns:
        csc_array: Gradient matrix.
        csc_array or tuple: Gradient contribution from boundary conditions. If `shapes_d` is provided, returns a tuple.
    """
    if isinstance(shape, int):
        shape = (shape, )
    else:
        shape = tuple(shape)
    x_f, x_c = generate_grid(shape[axis], x_f, generate_x_c=True, x_c=x_c)
    grad_matrix = construct_grad_int(shape, x_f, x_c, axis)

    if bc == (None, None):
        shape_f = shape[:axis] + (shape[axis] + 1,) + shape[axis + 1:]
        grad_bc = csc_array((math.prod(shape_f),1))
        return grad_matrix, grad_bc
    else:
        if shapes_d is None or shapes_d == (None, None):
            grad_matrix_bc, grad_bc = construct_grad_bc(
                shape, x_f, x_c, bc, axis)
            grad_matrix += grad_matrix_bc
            return grad_matrix, grad_bc
        else:
            grad_matrix_bc_0, grad_bc_0, grad_matrix_bc_1, grad_bc_1 = construct_grad_bc(
                shape, x_f, x_c, bc, axis, shapes_d=shapes_d)
            grad_matrix += grad_matrix_bc_0 + grad_matrix_bc_1
            return grad_matrix, grad_bc_0, grad_bc_1
        
def construct_grad_int(shape, x_f, x_c=None, axis=0):
    """
    Construct the gradient matrix for internal faces.

    Parameters:
        shape (tuple): Shape of the domain.
        x_f (ndarray): Face coordinates.
        x_c (ndarray, optional): Cell center coordinates. If not provided, they are calculated.
        axis (int, optional): Axis of differentiation. Default is 0.

    Returns:
        csc_array: Gradient matrix for internal faces.
    """
    if axis < 0:
        axis += len(shape)
    shape_t = [math.prod(shape[:axis]),  math.prod(shape[axis:axis+1]), math.prod(shape[axis + 1:])]

    i_f = ((shape_t[1]+1) * shape_t[2] * np.arange(shape_t[0]).reshape(-1, 1, 1, 1)
           + shape_t[2] * np.arange(shape_t[1]).reshape((1, -1, 1, 1))
           + np.arange(shape_t[2]).reshape((1, 1, -1, 1)) + np.array([0, shape_t[2]]).reshape((1, 1, 1, -1)))

    if x_c is None:
        x_c = 0.5*(x_f[:-1] + x_f[1:])

    dx_inv = np.tile(
        1 / (x_c[1:] - x_c[:-1]).reshape((1, -1, 1)), (shape_t[0], 1, shape_t[2]))
    values = np.empty(i_f.shape)
    values[:, 0, :, 0] = np.zeros((shape_t[0], shape_t[2]))
    values[:, 1:, :, 0] = dx_inv
    values[:, :-1, :, 1] = -dx_inv
    values[:, -1, :, 1] = np.zeros((shape_t[0], shape_t[2]))
    grad_matrix = csc_array((values.ravel(), i_f.ravel(), range(0, i_f.size + 1, 2)),
                            shape=(shape_t[0]*(shape_t[1]+1)*shape_t[2], shape_t[0]*shape_t[1]*shape_t[2]))
    return grad_matrix


def construct_grad_bc(shape, x_f, x_c=None, bc=(None, None), axis=0, shapes_d=(None, None)):
    """
    Construct the gradient matrix for boundary faces.

    Parameters:
        shape (tuple): Shape of the domain.
        x_f (ndarray): Face coordinates.
        x_c (ndarray, optional): Cell center coordinates. If not provided, they are calculated.
        bc (tuple, optional): Boundary conditions as a tuple of dictionaries. Default is (None, None).
        axis (int, optional): Axis of differentiation. Default is 0.
        shapes_d (tuple, optional): Shapes for boundary condition contributions. Default is (None, None).

    Returns:
        csc_array or tuple: Gradient matrix for boundary faces and contributions from inhomogeneous boundary conditions.
                            If `shapes_d` is provided, returns a tuple of matrices.
    """
    shape_f = shape[:axis] + (shape[axis] + 1,) + shape[axis + 1:]
    shape_t = (math.prod(shape[:axis]), shape[axis], math.prod(shape[axis + 1:]))
    shape_f_t = (shape_t[0], shape_f[axis], shape_t[2])
    shape_bc = shape[:axis] + (1,) + shape[axis + 1:]
    shape_bc_d = (shape_t[0], shape_t[2])
    
    # Handle special case with one cell in the dimension axis.
    # This is convenient e.g. for flexibility where you can choose not to
    # spatially discretize a direction, but still use a BC, e.g. with a mass transfer coefficient
    # It is a bit subtle because in this case the two opposite faces influence each other
    if shape_t[1] == 1:
        if x_c is None:
            x_c = 0.5*(x_f[0:-1] + x_f[1:])
        i_c = shape_t[2] * np.arange(shape_t[0]).reshape((-1, 1, 1)) + np.array(
            [0, 0]).reshape((1, -1, 1)) + np.arange(shape_t[2]).reshape((1, 1, -1))
        i_f = shape_t[2] * np.arange(shape_t[0]).reshape((-1, 1, 1)) + shape_t[2] * np.array([0, 1]).reshape((
            1, -1, 1)) + np.arange(shape_t[2]).reshape((1, 1, -1))
        values = np.empty(shape_f_t)
        alpha_1 = (x_f[1] - x_f[0]) / (
            (x_c[0] - x_f[0]) * (x_f[1] - x_c[0]))
        alpha_2_left = (x_c[0] - x_f[0]) / (
            (x_f[1] - x_f[0]) * (x_f[1] - x_c[0]))
        alpha_0_left = alpha_1 - alpha_2_left
        alpha_2_right = -(x_c[0] - x_f[1]) / (
            (x_f[0] - x_f[1]) * (x_f[0] - x_c[0]))
        alpha_0_right = alpha_1 - alpha_2_right
        a, b, d = [[unwrap_bc_coeff(shape, bc_element[key], axis=axis) if bc_element else np.zeros((1,)*len(shape)) for bc_element in bc] for key in ['a', 'b', 'd']]
        fctr = ((b[0] + alpha_0_left * a[0]) * (b[1]
                + alpha_0_right * a[1]) - alpha_2_left * alpha_2_right * a[0] * a[1])
        np.divide(1, fctr, out=fctr, where=(fctr != 0))
        value = np.broadcast_to(alpha_1 * \
            b[0] * (a[1] * (alpha_0_right - alpha_2_left) + b[1]) * \
            fctr,shape)
        values[:, 0, :] = np.reshape(value, shape_bc_d)
        value = np.broadcast_to(alpha_1 * \
            b[1] * (a[0] * (-alpha_0_left + alpha_2_right) - b[0]) * \
            fctr,shape)
        values[:, 1, :] = np.reshape(value, shape_bc_d)

        i_f_bc = shape_f_t[1] * shape_f_t[2] * np.arange(shape_f_t[0]).reshape((-1, 1, 1)) + shape_f_t[2] * np.array(
                [0, shape_f_t[1]-1]).reshape((1, -1, 1)) + np.arange(shape_f_t[2]).reshape((1, 1, -1))
        values_bc = np.empty((shape_t[0], 2, shape_t[2]))
        value = np.broadcast_to(((a[1] * (-alpha_0_left * alpha_0_right + alpha_2_left * alpha_2_right) - alpha_0_left *
                b[1]) * d[0] - alpha_2_left * b[0] * d[1]) * fctr,shape_bc)
        values_bc[:, 0, :] = np.reshape(value, shape_bc_d)
        value = np.broadcast_to(((a[0] * (+alpha_0_left * alpha_0_right - alpha_2_left * alpha_2_right) + alpha_0_right *
                b[0]) * d[1] + alpha_2_right * b[1] * d[0]) * fctr,shape_bc)
        values_bc[:, 1, :] = np.reshape(value, shape_bc_d)
    else:
        i_c = (shape_t[1] * shape_t[2] * np.arange(shape_t[0]).reshape(-1, 1, 1)
               + shape_t[2] * np.array([0, 1, shape_t[1]-2, shape_t[1]-1]).reshape((1, -1, 1))
               + np.arange(shape_t[2]).reshape((1, 1, -1)))
        i_f = (shape_f_t[1] * shape_t[2] * np.arange(shape_t[0]).reshape(-1, 1, 1)
               + shape_t[2] * np.array([0, 0, shape_f_t[1]-1, shape_f_t[1]-1]).reshape((1, -1, 1))
               + np.arange(shape_t[2]).reshape((1, 1, -1)))
        i_f_bc = shape_f_t[1] * shape_f_t[2] * np.arange(shape_f_t[0]).reshape((-1, 1, 1)) + shape_f_t[2] * np.array(
            [0, shape_f_t[1]-1]).reshape((1, -1, 1)) + np.arange(shape_f_t[2]).reshape((1, 1, -1))
        values_bc = np.empty((shape_t[0], 2, shape_t[2]))
        values = np.empty((shape_t[0], 4, shape_t[2]))
        if x_c is None:
            x_c = 0.5*np.array([x_f[0] + x_f[1], x_f[1] + x_f[2],
                                x_f[-3] + x_f[-2], x_f[-2] + x_f[-1]])

        # Get a, b, and d for left bc from dictionary
        alpha_1 = (x_c[1] - x_f[0]) / (
            (x_c[0] - x_f[0]) * (x_c[1] - x_c[0]))
        alpha_2 = (x_c[0] - x_f[0]) / (
            (x_c[1] - x_f[0]) * (x_c[1] - x_c[0]))
        alpha_0 = alpha_1 - alpha_2
        a, b, d = [unwrap_bc_coeff(shape, bc[0][key], axis=axis) if bc[0] else np.zeros((1,)*len(shape)) for key in ['a', 'b', 'd']]
        b = b / alpha_0
        fctr = (a + b)
        np.divide(1, fctr, out=fctr, where=(fctr != 0))
        b_fctr = b * fctr
        b_fctr = np.broadcast_to(b_fctr,shape_bc).reshape(shape_bc_d)
        d_fctr = d * fctr
        d_fctr = np.broadcast_to(d_fctr,shape_bc).reshape(shape_bc_d)
        values[:, 0, :] = b_fctr * alpha_1
        values[:, 1, :] = -b_fctr * alpha_2
        values_bc[:, 0, :] = -d_fctr

        # Get a, b, and d for right bc from dictionary
        a, b, d = [unwrap_bc_coeff(shape, bc[1][key], axis=axis) if bc[1] else np.zeros((1,)*len(shape)) for key in ['a', 'b', 'd']]
        alpha_1 = -(x_c[-2] - x_f[-1]) / (
            (x_c[-1] - x_f[-1]) * (x_c[-2] - x_c[-1]))
        alpha_2 = -(x_c[-1] - x_f[-1]) / (
            (x_c[-2] - x_f[-1]) * (x_c[-2] - x_c[-1]))
        alpha_0 = alpha_1 - alpha_2
        b = b / alpha_0
        fctr = (a + b)
        np.divide(1, fctr, out=fctr, where=(fctr != 0))
        b_fctr = b * fctr
        b_fctr = np.broadcast_to(b_fctr, shape_bc).reshape(shape_bc_d)
        d_fctr = d * fctr
        d_fctr = np.broadcast_to(d_fctr, shape_bc).reshape(shape_bc_d)
        values[:, -2, :] = b_fctr * alpha_2
        values[:, -1, :] = -b_fctr * alpha_1
        values_bc[:, -1, :] = d_fctr
    if (shapes_d[0] is None) and (shapes_d[1] is None):
        grad_bc = csc_array((values_bc.ravel(), i_f_bc.ravel(), [
                0, i_f_bc.size]), shape=(math.prod(shape_f_t), 1))
        grad_matrix = csc_array((values.ravel(), (i_f.ravel(), i_c.ravel())),
                        shape=(math.prod(shape_f_t), math.prod(shape_t)))
        return grad_matrix, grad_bc
    else:
        grad_bc = [None]*2
        for i in range(2):
            if shapes_d[i] is None:
                shape_d = (1,)*len(shape_bc)
                num_cols = 1
            else:
                shape_d = shapes_d[i]
                num_cols = math.prod(shape_d)
            i_cols_bc = np.arange(num_cols,dtype=int).reshape(shape_d)
            i_cols_bc = np.broadcast_to(i_cols_bc, shape_bc)
            grad_bc[i] = csc_array((values_bc[:,i,:].ravel(), (i_f_bc[:,i,:].ravel(), i_cols_bc.ravel())),
                        shape=(math.prod(shape_f_t), num_cols))
        if (shape_t[1] == 1):
            grad_matrix_0 = csc_array((values[:,0,:].ravel(), (i_f[:,0,:].ravel(), i_c[:,0,:].ravel())), shape=(
                math.prod(shape_f_t), math.prod(shape_t)))
            grad_matrix_1 = csc_array((values[:,-1,:].ravel(), (i_f[:,-1,:].ravel(), i_c[:,-1,:].ravel())), shape=(
                math.prod(shape_f_t), math.prod(shape_t)))
        else:
            grad_matrix_0 = csc_array((values[:,:2,:].ravel(), (i_f[:,:2,:].ravel(), i_c[:,:2,:].ravel())), shape=(
                math.prod(shape_f_t), math.prod(shape_t)))
            grad_matrix_1 = csc_array((values[:,-2:,:].ravel(), (i_f[:,-2:,:].ravel(), i_c[:,-2:,:].ravel())), shape=(
                math.prod(shape_f_t), math.prod(shape_t)))
        return grad_matrix_0, grad_bc[0], grad_matrix_1, grad_bc[1]

def construct_div(shape, x_f, nu=0, axis=0):
    """
    Construct the divergence matrix for flux calculations.

    Parameters:
        shape (tuple or int): Shape of the domain. If an integer is provided, it is converted to a tuple.
        x_f (ndarray): Face positions.
        nu (int or callable, optional): Geometry factor (0: flat, 1: cylindrical, 2: spherical, or a callable for custom geometry). Default is 0.
        axis (int, optional): Axis along which divergence is computed. Default is 0.

    Returns:
        csc_array: Divergence matrix.
    """
    if isinstance(shape, int):
        shape = (shape, )
    else:
        shape = tuple(shape)
    x_f = generate_grid(shape[axis], x_f)

    shape_f = shape[:axis] + (shape[axis] + 1,) + shape[axis + 1:]
    shape_t = (math.prod(shape[:axis]), shape[axis], math.prod(shape[axis + 1:]))
    shape_f_t = (shape_t[0], shape_f[axis], shape_t[2])

    i_f = (
        shape_f_t[1] * shape_f_t[2] *
        np.arange(shape_t[0]).reshape((-1, 1, 1, 1))
        + shape_f_t[2] * np.arange(shape_t[1]).reshape((1, -1, 1, 1))
        + np.arange(shape_t[2]).reshape((1, 1, -1, 1))
        + np.array([0, shape_t[2]]).reshape((1, 1, 1, -1))
    )

    if callable(nu):
        area = nu(x_f).ravel()
        inv_sqrt3 = 1 / np.sqrt(3)
        x_f_r = x_f.ravel()
        dx_f = x_f_r[1:] - x_f_r[:-1]
        dvol_inv = 1 / (
            (nu(x_f_r[:-1] + (0.5 - 0.5 * inv_sqrt3) * dx_f)
             + nu(x_f_r[:-1] + (0.5 + 0.5 * inv_sqrt3) * dx_f))
            * 0.5 * dx_f
        )
    elif nu == 0:
        area = np.ones(shape_f_t[1])
        dvol_inv = 1 / (x_f[1:] - x_f[:-1])
    else:
        area = np.power(x_f.ravel(), nu)
        vol = area * x_f.ravel() / (nu + 1)
        dvol_inv = 1 / (vol[1:] - vol[:-1])

    values = np.empty((shape_t[1], 2))
    values[:, 0] = -area[:-1] * dvol_inv
    values[:, 1] = area[1:] * dvol_inv
    values = np.tile(values.reshape((1, -1, 1, 2)),
                     (shape_t[0], 1, shape_t[2]))

    num_cells = np.prod(shape_t, dtype=int)
    div_matrix = csc_array(
        (values.ravel(), (np.repeat(np.arange(num_cells), 2),
                          i_f.ravel())),
        shape=(num_cells, np.prod(shape_f_t, dtype=int))
    )
    div_matrix.sort_indices()
    return div_matrix

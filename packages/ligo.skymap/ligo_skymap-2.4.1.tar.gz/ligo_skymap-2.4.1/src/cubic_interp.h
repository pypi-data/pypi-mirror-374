/*
 * Copyright (C) 2015-2025  Leo Singer
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 *
 *      Accelerated 1D and 2D cubic interpolation
 *
 *      1. Constant boundary conditions
 *
 *      2. Robust to invalid data: drops to linear or nearest-neighbor
 *         when the input data contains NaNs or infinities
 *
 *      3. Bounds and invalid value checks are precomputed:
 *         minimal branch instructions needed in evaluate function
 *
 *      4. Interpolating polynomial is precomputed.
 *
 *         For 1D interpolation, direct evaluation of the inteprolating
 *         polynomial from the data takes 9 multiplications and 10 additions;
 *         with precomputed coefficients we need only 3 multiplications and 3
 *         additions at the cost of 4x the memory footprint.
 *
 *         For 2D interpolation, direct evaluation of the inteprolating
 *         polynomial from the data takes 18 multiplications and 20 additions;
 *         with precomputed coefficients we need only 6 multiplications and 6
 *         additions at the cost of 16x the memory footprint.
 */


#ifndef CUBIC_INTERP_H
#define CUBIC_INTERP_H

#ifndef __cplusplus

typedef struct cubic_interp cubic_interp;
typedef struct bicubic_interp bicubic_interp;

/**
 * Free a piecewise cubic interpolating function.
 */
void cubic_interp_free(cubic_interp *interp);

__attribute__ ((malloc))
/**
 * Create a 1D piecewise cubic interpolating function.
 *
 * The interpolating function y=f(x) passes through the data points
 * (x[i], y[i]) for all i from 0 to n-1, where x[i] = tmin + i * dt and
 * y[i] = data[i].
 */
cubic_interp *cubic_interp_init(
    const double *data, int n, double tmin, double dt);

__attribute__ ((pure))
/**
 * Evaluate a piecewise cubic interpolating function.
 */
double cubic_interp_eval(const cubic_interp *interp, double t);

/**
 * Free a piecewise bicubic interpolating function.
 */
void bicubic_interp_free(bicubic_interp *interp);

__attribute__ ((malloc))
/**
 * Create a 2D piecewise bicubic interpolating function.
 *
 * The interpolating function z=f(x, y) passes through the data points
 * (x[i], y[j], z[i, j]) for all i from 0 to ns - 1 and all j from 0 to nt - 1,
 * where x[i] = smin + i * ds, y[j] = tmin + j * dt, and z[i, j] = data[i, j].
 */
bicubic_interp *bicubic_interp_init(
    const double *data, int ns, int nt,
    double smin, double tmin, double ds, double dt);

__attribute__ ((pure))
/**
 * Evaluate a piecewise bicubic interpolating function.
 */
double bicubic_interp_eval(const bicubic_interp *interp, double s, double t);

/**
 * Run unit tests.
 */
int cubic_interp_test(void);

#endif /* __cplusplus */

#endif /* CUBIC_INTERP_H */

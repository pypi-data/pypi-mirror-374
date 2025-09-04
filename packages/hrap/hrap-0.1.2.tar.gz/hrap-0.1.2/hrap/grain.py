# Purpose: Model regression of motor grains
# Authors: Thomas A. Scott

from hrap.core import store_x, make_part

import numpy as np

import jax.numpy as jnp
from jax.lax import cond

from functools import partial

def d_grain_constOF(s, x, xmap, d2a):
    mdot_inj = x[xmap['tnk_mdot_inj']] # TODO: using vent?
    A = x[xmap['grn_A']]
    d = x[xmap['grn_d']]
    L   = s['grn_L']
    rho = s['grn_rho']
    OF = s['grn_OF']
    
    # Current arc length of exposed grain on the cross section
    arc = d2a(d, s, x, xmap)
    
    # Current volume
    V = L * A
    
    # Grain consumption rate (positive)
    mdot = mdot_inj / OF
    mdot = cond(A <= 0.0, lambda val: 0.0, lambda val: val, mdot)
    
    # Rate of volume consumption (positive)
    Vdot = mdot / rho
    
    # Rate of cross section area loss
    Adot = Vdot / L
    
    # Cross sectional area linearization (i.e. volume of thin shell, Adot = arc * ddot)
    ddot = Adot / arc
    
    # Store result
    x = store_x(x, xmap, grn_Adot=-Adot, grn_ddot=ddot, grn_V=V, grn_mdot=mdot, grn_Vdot=Vdot, cmbr_OF=OF)

    return x

def d_grain_shiftOF(s, x, xmap, d2a):
    mdot_inj = x[xmap['tnk_mdot_inj']] # TODO: using vent?
    A = x[xmap['grn_A']]
    d = x[xmap['grn_d']]
    L   = s['grn_L']
    rho = s['grn_rho']
    Reg = s['grn_Reg']
    
    # Current arc length of exposed grain on the cross section
    arc = d2a(d, s, x, xmap)
    # Current volume
    V = L * A
    
    G    = mdot_inj/A;
    ddot = 0.001*Reg[0]*G**Reg[1]*L**Reg[2]
    
    Adot = ddot*arc
    Vdot = Adot*L
    
    mdot = Vdot*rho
    mdot = cond(A <= 0.0, lambda val: 0.0, lambda val: val, mdot)
    
    OF = mdot_inj / mdot
    
    # Store result
    x = store_x(x, xmap, grn_Adot=-Adot, grn_ddot=ddot, grn_V=V, grn_mdot=mdot, grn_Vdot=Vdot, cmbr_OF=OF)
    
    return x

# def d_grain_fit(s, x, xmap, fshape):
#     # Get exposed area along the grain
#     A_burn = arc * L

def u_grain(s, x, xmap):
    x = store_x(x, xmap,
        grn_A = jnp.maximum(x[xmap['grn_A']], 0.0),
        grn_d = jnp.minimum(x[xmap['grn_d']], s['grn_OD']/2) # TODO: shouldnt be necessary
    )
    
    return x

# print('Baking grain geometry')
# # Define star using inner diameter, tip diameter, and number of tips
# grn_ID, grn_TD, grn_OD, N_tip = 2.0*_in, 3.5*_in, 4.5*_in, 6
# grn_r = np.array([grn_ID/2, grn_TD/2]*N_tip)
# grn_t = np.linspace(0.0, 2*np.pi, 2*N_tip, endpoint=False)
# grn_xy = np.stack([grn_r*np.cos(grn_t), grn_r*np.sin(grn_t)], axis=1)
# import hrap.sdf as sdf
# from skimage import measure
# import interpax
# Nx = 64 # Spatial, progression resolutions
# Nd = 16
# sdf_x, sdf_y = np.meshgrid(*[((np.arange(Nx)+0.5)/Nx - 0.5)*grn_OD]*2,indexing='ij')
# sdf_xy = np.stack([sdf_x.ravel(), sdf_y.ravel()], axis=1) # 
# sdf_v = sdf.sd_poly(grn_xy, sdf_xy)
# is_outside = sdf_xy[:,0]**2+sdf_xy[:,1]**2 > (grn_OD/2)**2
# R = np.max(sdf_v[~is_outside]) # distance from initial grain to outer wall
# # sdf_v[is_outside] = R
# sdf_v = sdf_v.reshape((Nx,Nx))
# fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(14,7))
# axs = np.array(axs).ravel()
# # axs[1].contourf(sdf_x, sdf_y, sdf_v, levels=32)
# plt_grn_xy = np.append(grn_xy, [grn_xy[0,:]], axis=0)
# A0 = sdf.area_poly(grn_xy)

# grn_d2a = np.zeros(Nd)
# grn_d = np.arange(Nd)/(Nd-1)*R
# grn_xy1 = np.roll(grn_xy,1,axis=0) # Previous vertices
# grn_d2a[0] = np.sum(np.sqrt((grn_xy[:,0]-grn_xy1[:,0])**2 + (grn_xy[:,1]-grn_xy1[:,1])**2))
# for i in range(1, Nd):
    # contours = measure.find_contours(sdf_v, i/(Nd-1)*R)
    # a = 0.0
    # for contour in contours:
        # contour = ((contour+0.5)/Nx - 0.5)*grn_OD
        # # print(contour)
        # is_inside = contour[:,0]**2+contour[:,1]**2 <= (grn_OD/2)**2
        # contour[~is_inside,:] = np.nan
        # # Contours repeat the first point if it is a closed loop so no special treatment needed
        # # if len(contours) == 1 and np.all(contour[0,:] == contour[-1,:]):
        # a_segs = np.sqrt((contour[1:,0]-contour[:-1,0])**2 + (contour[1:,1]-contour[:-1,1])**2)
        # # Not counting NaN entries handles only counting remaining line segments
        # grn_d2a[i] += np.sum(a_segs[np.isfinite(a_segs)])
        # # contour = contour[is_inside,:]
        # axs[0].plot(contour[:,0], contour[:,1], color='black')
# axs[0].plot(plt_grn_xy[:,0], plt_grn_xy[:,1], color='black', linestyle='dashed')
# d2a_curve = interpax.Interpolator1D(grn_d, grn_d2a, method='akima')
# # axs[0].scatter(grn_xy[:,0], grn_xy[:,1])
# plt_t = np.linspace(0.0, 2*np.pi, 64)
# axs[0].plot(np.cos(plt_t)*grn_OD/2, np.sin(plt_t)*grn_OD/2, color='black', linestyle='dashed')
# plt_d = np.arange(Nd*5)/(Nd*5-1)*R
# axs[1].plot(plt_d, d2a_curve(plt_d), label='star')
# axs[1].scatter(grn_d, grn_d2a)
# eq_r = grn_d2a[0]/(2*np.pi)
# axs[0].plot(np.cos(plt_t)*eq_r, np.sin(plt_t)*eq_r, color='blue', linestyle='dashed', label='equivalent diameter')
# eq_d = np.arange(Nd*5)/(Nd*5-1)*(grn_OD/2 - eq_r)
# axs[1].plot(np.append(eq_d, eq_d[-1]), np.append(2*np.pi*(eq_r + eq_d),0.0), label='circular w/ equivalent diameter')
# axs[0].legend(loc='upper right')
# axs[1].legend(loc='upper right')
# axs[1].set_xlabel('Regressed Distance [m]')
# axs[1].set_ylabel('Exposed Arc Length [m]')
# plt.show()

def make_arbitrary_shape(d2a_curve, **kwargs):
    def arbitrary_d2a(d, s, x, xmap, curve):
        return curve(d) #np.pi * (s['grn_shape_ID'] + 2*d)
    
    def preprs(s, x, xmap):
        x = x.at[xmap['grn_A']].set(s['grn_shape_A0'])
        
        return x
    
    return make_part(
        # Default static and initial dynamic variables
        s = {
            'ID': 0.1,
        },
        x = {
        },
        
        # Required and integrated variables
        req_s = ['A0'],
        req_x = [],
        dx    = { },

        typename = 'shape',

        d2a = partial(arbitrary_d2a, curve=d2a_curve),
        fpreprs = preprs,
        
        # The user-specified static and initial dynamic variables
        **kwargs,
    )

def make_circle_shape(**kwargs):
    def circle_d2a(d, s, x, xmap):
        return np.pi * (s['grn_shape_ID'] + 2*d)
    
    def preprs(s, x, xmap):
        OD, ID = s['grn_OD'], s['grn_shape_ID']
        A = np.pi/4 * (OD**2 - ID**2)
        x = x.at[xmap['grn_A']].set(A)
        
        return x
    
    return make_part(
        # Default static and initial dynamic variables
        s = {
            'ID': 0.1,
        },
        x = {
        },
        
        # Required and integrated variables
        req_s = ['ID'],
        req_x = [],
        dx    = { },

        typename = 'shape',

        d2a = circle_d2a,
        fpreprs = preprs,

        # The user-specified static and initial dynamic variables
        **kwargs,
    )

def make_constOF_grain(shape, **kwargs):
    return make_part(
        # Default static and initial dynamic variables
        s = {
            'OD': 0.1,
            'L': 0.1,
            'OF': 1.0,
            'rho': 1000.0,
            **shape['s'],
        },
        x = {
            'A': 0.1,
            'd': 0.0,   # Distance regressed, i.e. increasing during burn
            
            # Calculated variables
            'V': 0.0,
            'Vdot': 0.0,
            'P': 101e3,
            'mdot': 0.0,
            
            **shape['x'],
        },
        
        # Required and integrated variables
        req_s = ['OD', 'L', 'OF'],
        req_x = ['A'],
        dx    = {'A': 'Adot', 'd': 'ddot'},

        # Designation and associated functions
        typename = 'grn',
        fderiv  = partial(d_grain_constOF, d2a=shape['shape_d2a']),
        fupdate = u_grain,
        fpreprs = shape['fpreprs'],

        # The user-specified static and initial dynamic variables
        **kwargs,
    )

def make_shiftOF_grain(shape, **kwargs):
    return make_part(
        # Default static and initial dynamic variables
        s = {
            'OD': 0.1,
            'L': 0.1,
            'Reg': jnp.zeros(3), # Regression coefficient (mm/s), regression exponent, length exponent
            'rho': 1000.0,
            **shape['s'],
        },
        x = {
            'A': 0.1,
            'd': 0.0,   # Distance regressed, i.e. increasing during burn
            
            # Calculated variables
            'V': 0.0,
            'Vdot': 0.0,
            'P': 101e3,
            'mdot': 0.0,
            
            **shape['x'],
        },
        
        # Required and integrated variables
        req_s = ['OD', 'L', 'OF'],
        req_x = ['A'],
        dx    = {'A': 'Adot', 'd': 'ddot'},

        # Designation and associated functions
        typename = 'grn',
        fderiv  = partial(d_grain_shiftOF, d2a=shape['shape_d2a']),
        fupdate = u_grain,
        fpreprs = shape['fpreprs'],

        # The user-specified static and initial dynamic variables
        **kwargs,
    )

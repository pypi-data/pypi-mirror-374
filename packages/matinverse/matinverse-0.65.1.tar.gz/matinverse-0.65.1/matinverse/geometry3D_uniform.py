import equinox as eqx
import jax
from jax import numpy as jnp
import matplotlib.pylab as plt
from typing import List,Callable
import time
import numpy as np
from functools import partial
from typing import List


def shift(arr, shift, axis, fill_value=False):
    arr = np.asarray(arr)
    result = np.full_like(arr, fill_value)

    if shift == 0:
        return arr.copy()

    src = [slice(None)] * arr.ndim
    dst = [slice(None)] * arr.ndim

    if shift > 0:
        src[axis] = slice(0, -shift)
        dst[axis] = slice(shift, None)
    else:
        src[axis] = slice(-shift, None)
        dst[axis] = slice(0, shift)

    result[tuple(dst)] = arr[tuple(src)]
    return result

class Geometry3D(eqx.Module):
  
   
   
    N                  : int
    nDOFs              : int
    size               : List
    grid               : List
    dim                : int = 3
    mask               : jax.Array
    V                  : jax.Array
    boundary_centroids : jax.Array
    boundary_normals   : jax.Array
    boundary_sides     : jax.Array
    boundary_areas     : jax.Array
    boundary_dists     : jax.Array
    smap               : jax.Array
    normals            : jax.Array
    centroids          : jax.Array
    face_centroids     : jax.Array
    areas              : jax.Array
    dists              : jax.Array
    local2global       : jax.Array
    global2local       : jax.Array
    periodic           : List


    def __init__(self,grid,size,periodic=[False,False,False],\
                 domain = None):
      
        
        self.grid     = [grid[0], grid[1], grid[2]] 
        self.size     = size
        DX            = self.size[0]/self.grid[0] 
        DY            = self.size[1]/self.grid[1]  
        DZ            = self.size[2]/self.grid[2]
        self.N        = self.grid[0]*self.grid[1]*self.grid[2] 

        V             = DX*DY*DZ*jnp.ones(self.N)
        self.periodic = periodic
        
        Nx, Ny, Nz = self.grid

        Ix, Iy, Iz = np.indices((Nx, Ny, Nz), sparse=False)

        # Flattening: Ix fastest, then Iy, then Iz
        I_center = Iz * (Nx * Ny) + Iy * Nx + Ix

        # Neighbors
        I_left   = Iz * (Nx * Ny) + Iy * Nx + ((Ix - 1) % Nx)   # x - 1
        I_right  = Iz * (Nx * Ny) + Iy * Nx + ((Ix + 1) % Nx)   # x + 1

        I_back   = Iz * (Nx * Ny) + ((Iy - 1) % Ny) * Nx + Ix   # y - 1
        I_front  = Iz * (Nx * Ny) + ((Iy + 1) % Ny) * Nx + Ix   # y + 1

        I_bottom = ((Iz - 1) % Nz) * (Nx * Ny) + Iy * Nx + Ix   # z - 1
        I_top    = ((Iz + 1) % Nz) * (Nx * Ny) + Iy * Nx + Ix   # z + 1

        
        
        #Compute centroids
        centroids_x = jnp.linspace(-self.size[0] / 2 + DX / 2, self.size[0] / 2 - DX / 2, self.grid[0])
        centroids_y = jnp.linspace(-self.size[1] / 2 + DY / 2, self.size[1] / 2 - DY / 2, self.grid[1])
        centroids_z = jnp.linspace(-self.size[2] / 2 + DZ / 2, self.size[2] / 2 - DZ / 2, self.grid[2])
        X, Y, Z = jnp.meshgrid(centroids_x, centroids_y, centroids_z, indexing="ij")
        centroids = jnp.stack((X, Y, Z), axis=-1)
        centroids = jnp.transpose(centroids, (2, 1, 0, 3)).reshape(-1, 3)
        #----------------------------
    
    
        #Setting up maps----------------
        mask = jnp.ones((self.N,), dtype=bool)
        if domain:
           mask = jnp.logical_and(jax.vmap(domain)(centroids), mask)


        mask = jnp.ones((self.N,), dtype=bool)
        if domain:
           mask = jnp.logical_and(jax.vmap(domain)(centroids), mask)

        # flat (Ix-fastest) ➜ (Nx,Ny,Nz)
        self.mask = jnp.transpose(mask.reshape(Nz, Ny, Nx), (2, 1, 0))
        

        self.nDOFs = int(self.mask.sum())
        self.local2global = I_center[self.mask]                                  
        self.global2local = (jnp.ones(self.N, dtype=int)
                     .at[self.local2global].set(jnp.arange(self.nDOFs)))
        
        #-----------------------------------------------------------------------

      

        #Shift along increasing x (downward of index 0 in array space and rightward in physics space)
        mask = np.logical_and(self.mask,shift(self.mask,shift=-1,axis=0,
                                               fill_value=True if periodic[0] else False))
        Nm = np.count_nonzero(mask)
        smap = jnp.vstack((I_center[mask],I_right[mask])).T  #(Nm,2)
       

        #face centroids
        face_centroids  = jnp.stack((         
                                        -self.size[0]/2   +(Ix[mask]+1) *DX,\
                                        -self.size[1]/2   + Iy[mask]    *DY + DY/2,\
                                        -self.size[2]/2   + Iz[mask]    *DZ + DZ/2), 
                                     axis=-1).reshape(-1, 3)
       
        areas =                                   DY * DZ  * jnp.ones(Nm)
        dists =                                   DX      * jnp.ones(Nm)
        normals =                                 jnp.tile(jnp.array([1, 0, 0]),(Nm,1))


        #Shift along increasing y (rightward  of index 1 in array space and frontward in physics space)
        mask = np.logical_and(self.mask,shift(self.mask,shift=-1,axis=1, fill_value=True if periodic[1] else False))
        Nm = np.count_nonzero(mask)
        smap = jnp.vstack((smap,jnp.vstack((I_center[mask],I_front[mask])).T))
        face_centroids  = jnp.vstack((face_centroids,jnp.stack((             -self.size[0]/2 + Ix[mask]* DX + DX/2,\
                                                                             -self.size[1]/2 + (Iy[mask]+1)*DY ,\
                                                                             -self.size[2]/2 + Iz[mask]*DZ + DZ/2), axis=-1).reshape(-1, 3)))

        areas   = jnp.concatenate((areas,DX*DZ    * jnp.ones(Nm)))
        dists   = jnp.concatenate((dists,DY       * jnp.ones(Nm))) 
        normals = jnp.vstack((normals,jnp.tile(jnp.array([0, 1, 0 ]),(Nm,1))))


        #Shift along increasing z (upward of index 2 in array space and fup in physics space)
        mask = np.logical_and(self.mask,shift(self.mask,shift=-1,axis=2, fill_value=True if periodic[2] else False))
        Nm = np.count_nonzero(mask)
        smap = jnp.vstack((smap,jnp.vstack((I_center[mask],I_top[mask])).T))

        face_centroids  = jnp.vstack((face_centroids,jnp.stack(( -self.size[0]/2 + Ix[mask]*DX + DX/2,\
                                                                 -self.size[1]/2 + Iy[mask]*DY + DY/2,\
                                                                 -self.size[2]/2 + (Iz[mask]+1)*DZ), axis=-1).reshape(-1, 3)))

        areas = jnp.concatenate((areas,DX*DY * jnp.ones(Nm)))
        dists = jnp.concatenate((dists,DZ    * jnp.ones(Nm)))

        normals = jnp.vstack((normals,jnp.tile(jnp.array([0,0,1]),(Nm,1))))

        
        #Boundary right
        #Create a mask that is true only for the elements hosting a boundary
        I      = shift(self.mask,shift=-1,axis=0)
        mask   = np.logical_and(self.mask,np.logical_not(I))
        if periodic[0]: mask[-1,:,:] = False
        Nm = np.count_nonzero(mask)   
        boundary_centroids = jnp.where((Ix[mask]==self.grid[0]-1)[:, None],centroids[I_center[mask]] + jnp.array([DX/2,0,0]),(centroids[I_center[mask]] + centroids[I_right[mask]])/2)
        boundary_sides   =  I_center[mask]
        boundary_areas   =  DY * DZ * jnp.ones(Nm)
        boundary_dists   =  DX/2    * jnp.ones(Nm)
        boundary_normals =  jnp.tile(jnp.array([1,0,0]),(Nm,1))


        #Boundary left
        I = shift(self.mask,shift=1,axis=0)   
        mask   = np.logical_and(self.mask,np.logical_not(I)) 
        if periodic[0]: mask[0,:,:] = False
        Nm = np.count_nonzero(mask)        
   
        boundary_centroids = jnp.vstack((boundary_centroids,jnp.where((Ix[mask]==0)[:, None] ,centroids[I_center[mask]] - jnp.array([DX/2,0,0]),(centroids[I_center[mask]] + centroids[I_left[mask]])/2)))
        boundary_sides   = jnp.concatenate((boundary_sides,I_center[mask]))
        boundary_areas   = jnp.concatenate((boundary_areas, DY * DZ* jnp.ones(Nm)))
        boundary_dists   = jnp.concatenate((boundary_dists, DX/2 * jnp.ones(Nm)))
        boundary_normals = jnp.concatenate((boundary_normals,jnp.tile(jnp.array([ -1,0,0]),(Nm,1))),axis=0)
        


        #Boundary front
        I = shift(self.mask,shift=-1,axis=1)
        mask   = np.logical_and(self.mask,np.logical_not(I))
        if periodic[1]: mask[:,-1,:] = False
        Nm = np.count_nonzero(mask)         
        boundary_centroids = jnp.vstack((boundary_centroids,jnp.where((Iy[mask]==self.grid[1]-1)[:, None] ,centroids[I_center[mask]] + jnp.array([0,DY/2,0]),(centroids[I_center[mask]] + centroids[I_front[mask]])/2)))
        boundary_sides   = jnp.concatenate((boundary_sides,I_center[mask]))
        boundary_areas   = jnp.concatenate((boundary_areas, DX * DZ* jnp.ones(Nm)))
        boundary_dists   = jnp.concatenate((boundary_dists, DY/2 * jnp.ones(Nm)))
        boundary_normals = jnp.concatenate((boundary_normals,jnp.tile(jnp.array([ 0,1,0]),(Nm,1))),axis=0)

        #Boundary back
        I = shift(self.mask,shift=1,axis=1)
        mask   = np.logical_and(self.mask,np.logical_not(I))
        if periodic[1]: mask[:,0,:] = False
        Nm = np.count_nonzero(mask)         
        boundary_centroids = jnp.vstack((boundary_centroids,jnp.where((Iy[mask]==0)[:, None] ,centroids[I_center[mask]] - jnp.array([0,DY/2,0]),(centroids[I_center[mask]] + centroids[I_back[mask]])/2)))
        boundary_sides   = jnp.concatenate((boundary_sides,I_center[mask]))
        boundary_areas   = jnp.concatenate((boundary_areas, DX * DZ* jnp.ones(Nm)))
        boundary_dists   = jnp.concatenate((boundary_dists, DY/2 * jnp.ones(Nm)))
        boundary_normals = jnp.concatenate((boundary_normals,jnp.tile(jnp.array([ 0,-1,0]),(Nm,1))),axis=0)

        

        #Boundary top
        I = shift(self.mask,shift=-1,axis=2)
        mask   = np.logical_and(self.mask,np.logical_not(I))
        if periodic[2]: mask[:,:,-1] = False
        Nm = np.count_nonzero(mask)   
        boundary_centroids = jnp.vstack((boundary_centroids,jnp.where((Iz[mask]==self.grid[2]-1)[:, None] ,centroids[I_center[mask]] + jnp.array([0,0,DZ/2]),(centroids[I_center[mask]] + centroids[I_top[mask]])/2)))
        boundary_sides   = jnp.concatenate((boundary_sides,I_center[mask]))
        boundary_areas   = jnp.concatenate((boundary_areas, DX * DY* jnp.ones(Nm)))
        boundary_dists   = jnp.concatenate((boundary_dists, DZ/2 * jnp.ones(Nm)))
        boundary_normals = jnp.concatenate((boundary_normals,jnp.tile(jnp.array([ 0,0,1]),(Nm,1))),axis=0)

        #Boundary bottom
        I = shift(self.mask,shift=1,axis=2)
        mask   = np.logical_and(self.mask,np.logical_not(I))
        if periodic[2]: mask[:,:,0] = False
        Nm = np.count_nonzero(mask)      
        boundary_centroids = jnp.vstack((boundary_centroids,jnp.where((Iz[mask]==0)[:, None] ,centroids[I_center[mask]] - jnp.array([0,0,DZ/2]),(centroids[I_center[mask]] + centroids[I_bottom[mask]])/2)))
        boundary_sides   = jnp.concatenate((boundary_sides,I_center[mask]))
        boundary_areas   = jnp.concatenate((boundary_areas, DX * DY* jnp.ones(Nm)))
        boundary_dists   = jnp.concatenate((boundary_dists, DZ/2 * jnp.ones(Nm)))
        boundary_normals = jnp.concatenate((boundary_normals,jnp.tile(jnp.array([ 0,0,-1]),(Nm,1))),axis=0)


        self.boundary_centroids = boundary_centroids
        self.boundary_normals = boundary_normals 
        self.boundary_areas = boundary_areas 
        self.boundary_dists = boundary_dists 
        self.smap = self.global2local[smap]
        self.boundary_sides = self.global2local[boundary_sides]
        self.normals = normals 
        self.centroids = centroids[self.mask.flatten()]
        self.face_centroids = face_centroids 
        self.areas = areas 
        self.dists = dists 
        self.V = V
     

    def select_boundary(self,func):
        """Get select boundaries""" 

        if isinstance(func,str):
           if   func == 'left':
                func = lambda p  : jnp.isclose(p[0], -self.size[0]/2)
           elif func == 'right':   
                func = lambda p  : jnp.isclose(p[0], self.size[0]/2)
           elif func == 'front':   
                func = lambda p  : jnp.isclose(p[1],  self.size[1]/2)
           elif func == 'back':   
                func = lambda p  : jnp.isclose(p[1], -self.size[1]/2)   
           elif func == 'bottom':   
                func = lambda p  : jnp.isclose(p[2], -self.size[2]/2)
           elif func == 'top':   
                func = lambda p  : jnp.isclose(p[2], self.size[2]/2)               
           elif func == 'everywhere':   
                return jnp.arange(len(self.boundary_centroids))
        
        
        #return jax.vmap(func)(self.boundary_centroids).nonzero()[0]
        return func(self.boundary_centroids.T).nonzero()[0]
      
          
    
    def compute_function(self,func):
       """Get select boundaries""" 

       return func(self.centroids.T)
    
    def select_internal_boundary(self,func):
       """Get select boundaries""" 

       return func(self.face_centroids.T).nonzero()[0]


    def cell2side(self,func):

        return partial(func,i=self.smap[:,0],j=self.smap[:,1])#
    
   

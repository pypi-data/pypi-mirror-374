import gdspy
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage import measure
import matplotlib.pylab as plt
import time
from matinverse import IO


def WriteVTK(geo, variables, filename="output.vtk"):
    Nx, Ny, Nz = geo.grid
    n_nodes = np.prod(np.array(geo.grid) + 1)
    dim = len(geo.grid)

    # --- Node coordinates (non-uniform) ---
    #x_nodes = np.concatenate(([0.0], np.cumsum(geo.dx))) 
    #y_nodes = np.concatenate(([0.0], np.cumsum(geo.dy))) 
    #z_nodes = np.concatenate(([0.0], np.cumsum(geo.dz))) 

    #x_nodes = np.concatenate(([0.0], np.cumsum(geo.x))) 
    #y_nodes = np.concatenate(([0.0], np.cumsum(geo.y))) 
    #z_nodes = np.concatenate(([0.0], np.cumsum(geo.z))) 


    X, Y, Z = np.meshgrid(geo.x_nodes, geo.y_nodes, geo.z_nodes, indexing="ij")
    nodes = np.vstack([X.ravel(), Y.ravel(), Z.ravel()]).T

    # --- Connectivity (voxels) ---
    nx, ny, nz = Nx + 1, Ny + 1, Nz + 1
    i, j, k = np.meshgrid(np.arange(Nx), np.arange(Ny), np.arange(Nz), indexing="ij")
    base = i * (ny * nz) + j * nz + k
    voxels = np.stack([
        base,
        base + nz,
        base + 1,
        base + nz + 1,
        base + ny * nz,
        base + ny * nz + nz,
        base + ny * nz + 1,
        base + ny * nz + nz + 1,
    ], axis=-1)
    voxels = voxels.reshape(-1, 8)[geo.mask.flatten(order="C")]
    n_elems = voxels.shape[0]

    # --- Header ---
    strc  = "# vtk DataFile Version 2.0\n"
    strc += "MatInverse Data\n"
    strc += "ASCII\n"
    strc += "DATASET UNSTRUCTURED_GRID\n"
    strc += f"POINTS {n_nodes} double\n"

    for coords in nodes:
        for d in range(dim):
            strc += f"{coords[d]} "
        if dim == 2:
            strc += "0.0 "
        strc += "\n"

    # --- Cells ---
    m = 8   # voxel
    ct = "11"  # VTK voxel cell type
    n = m + 1
    strc += f"CELLS {n_elems} {n*n_elems}\n"
    for k in range(n_elems):
        strc += str(m) + " " + " ".join(map(str, voxels[k])) + "\n"

    strc += f"CELL_TYPES {n_elems}\n"
    strc += (" ".join([ct] * n_elems)) + "\n"

    # --- Cell data ---
    strc += f"CELL_DATA {n_elems}\n"
    mask_flat = geo.mask.flatten(order="C")

    for key, value in variables.items():
        data = value["data"]   # always batched
        units = value["units"]

        B, N = data.shape[0], data.shape[1]
        assert N == geo.N, f"Data size mismatch: got {N}, expected {geo.N}"

        # restrict to active cells
        data = data[:, mask_flat]

        for b in range(B):
            name = f"{key}[{b}]_[{units}]" if B > 1 else f"{key}_[{units}]"
            arr = np.array(data[b])

            if arr.ndim == 1:  # scalar field (n_elems,)
                strc += f"SCALARS {name} double\n"
                strc += "LOOKUP_TABLE default\n"
                strc += " ".join(arr.astype(str)) + "\n"

            elif arr.ndim == 2 and arr.shape[1] == 3:  # vector field (n_elems,3)
                strc += f"VECTORS {name} double\n"
                strc += "\n".join(" ".join(map(str, row)) for row in arr) + "\n"

            elif arr.ndim == 3 and arr.shape[1:] == (3, 3):  # tensor field (n_elems,3,3)
                strc += f"TENSORS {name} double\n"
                for mat in arr:
                    for row in mat:
                        strc += " ".join(map(str, row)) + "\n"
                    strc += "\n"
            else:
                raise ValueError(f"Unsupported data shape {arr.shape} for variable {key}")

    # --- Write to file ---
    with open(filename, "w") as f:
        f.write(strc)



def plot_paths(paths,L,x,flip=False):

 #fig = plt.figure()
 for p in paths:
    a = np.array(p)
    if flip: a = np.flip(a)
    plt.plot(a[:,0],a[:,1],'g',lw=3)

 plt.gca().set_aspect('equal')
 plt.imshow(x)
 #plt.plot([-L/2,-L/2,L/2,L/2,-L/2],[-L/2,L/2,L/2,-L/2,-L/2],ls='--')
 plt.axis('off')
 plt.show()

def find_irreducible_shapes(cs,L) :

    #find all close circles
    output = []
    for c in cs:
        if np.linalg.norm(c[0]-c[-1]) == 0:
           output.append(c)

    pp = np.array([[-L,0],[-L,L],[0,L],[L,L],[L,0],[L,-L],[0,-L],[-L,-L],\
                   [-2*L,0],[-2*L,L],[-2*L,2*L],[-L,2*L],[0,2*L],[L,2*L],[2*L,2*L],[2*L,L],[2*L,0],[2*L,-L],[2*L,-2*L],[L,-2*L],[0,-2*L],[-L,-2*L],[-2*L,-2*L],[-2*L,-L]])

    n = len(output)
    ##find irredicuble shape

    new = []
    for i in range(n):
        repeated = False
        for c2 in new:
            for p in pp:
              f = output[i] + p[np.newaxis,:]
              d = np.linalg.norm(np.mean(f,axis=0) - np.mean(c2,axis=0))
              if d < 1e-1:
                  repeated = True
                  pass

        if not repeated:
             new.append(output[i])

    #center to the first shape---
    c = np.mean(new[0],axis=0)

    cs = [i - c[np.newaxis,:]  for i in new]

    return cs

def periodic_numpy2gds(x,L,D,filename,plot_contour=False):

  x = np.where(x<0.5,1e-12,1)
  grid = int(np.sqrt(x.shape[0]))
  x = x.reshape((grid,grid))

  x = 1-np.array(x)
  N = x.shape[0]
  resolution = x.shape[0]/L #pixel/um
  x = np.pad(x,N,mode='wrap')

  #Find contour
  x = gaussian_filter(x, sigma=1)
  #for the paper it was 0.8
  contours = measure.find_contours(x,0.5)
  if plot_contour:
   plot_paths(contours)

  new_contours = []
  for contour in contours:
        new_contours.append(np.array(contour)/resolution)

  contours = find_irreducible_shapes(new_contours,L)


  unit_cell = gdspy.Cell("Unit", exclude_from_current=True)
  unit_cell.add(gdspy.PolygonSet(contours))

  #Repeat
  num = int(D/L/2)
  circle_cell = gdspy.Cell("Circular", exclude_from_current=True)

  # Iterate over each potential position for a unit cell
  contours_tot = []
  n_rep = 0
  for i in range(-num,num):
    for j in range(-num,num):
        # Calculate the center of the current unit cell
        center_x = (i+0.5)  * L
        center_y = (j+0.5)  * L

        # Check if the center is within the circle
        if np.sqrt(center_x ** 2 + center_y ** 2) <= D/2:
            # If it is, create a new instance of the unit cell at this position
            circle_cell.add(gdspy.CellReference(unit_cell, (center_x, center_y)))
            n_rep +=1

            for c in contours:
                    contours_tot.append(np.array(c) + np.array([[center_x,center_y]]))


  # IO.save('paths_to_FIB',{'paths':contours_tot,'L':L})
  #if write_path:
  #     with open('path.json','wb') as f:
  #      pickle.dump(contours_tot,f)

  lib = gdspy.GdsLibrary()
  lib.add(circle_cell)
  lib.write_gds(filename + '.gds')

   





    




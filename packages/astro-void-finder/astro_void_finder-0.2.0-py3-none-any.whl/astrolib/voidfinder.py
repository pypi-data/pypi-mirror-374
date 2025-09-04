"""
Void Finding Module
================

Core implementation of void finding algorithms:
1. ZOBOV (ZOnes Bordering On Voidness)
2. Watershed Void Finder
3. Dynamic Void Identification

Uses modern techniques to identify and characterize cosmic voids
in galaxy surveys and simulations.
"""

import numpy as np
from scipy.spatial import Voronoi
from numba import jit

@jit(nopython=True)
def density_field_estimate(positions, masses, grid_size):
    """
    Estimate density field using Cloud-in-Cell interpolation.
    
    Args:
        positions (np.ndarray): Particle positions, shape (N, 3)
        masses (np.ndarray): Particle masses, shape (N,)
        grid_size (int): Number of grid points per dimension
        
    Returns:
        np.ndarray: Density field on regular grid
    """
    density = np.zeros((grid_size, grid_size, grid_size))
    cell_size = 1.0 / grid_size
    
    for i in range(len(positions)):
        # Normalisierte Position (0-1)
        pos = positions[i]
        # Gitterzelle
        ix = int(pos[0] / cell_size)
        iy = int(pos[1] / cell_size)
        iz = int(pos[2] / cell_size)
        
        # Sichere Grenzen
        if 0 <= ix < grid_size and 0 <= iy < grid_size and 0 <= iz < grid_size:
            # CIC-Gewichtung
            dx = pos[0] / cell_size - ix
            dy = pos[1] / cell_size - iy
            dz = pos[2] / cell_size - iz
            
            # Verteile Masse auf benachbarte Zellen
            w000 = (1.0 - dx) * (1.0 - dy) * (1.0 - dz)
            w001 = (1.0 - dx) * (1.0 - dy) * dz
            w010 = (1.0 - dx) * dy * (1.0 - dz)
            w011 = (1.0 - dx) * dy * dz
            w100 = dx * (1.0 - dy) * (1.0 - dz)
            w101 = dx * (1.0 - dy) * dz
            w110 = dx * dy * (1.0 - dz)
            w111 = dx * dy * dz
            
            # Addiere gewichtete Masse
            mass = masses[i]
            density[ix, iy, iz] += w000 * mass
            if iz + 1 < grid_size:
                density[ix, iy, iz+1] += w001 * mass
            if iy + 1 < grid_size:
                density[ix, iy+1, iz] += w010 * mass
            if iy + 1 < grid_size and iz + 1 < grid_size:
                density[ix, iy+1, iz+1] += w011 * mass
            if ix + 1 < grid_size:
                density[ix+1, iy, iz] += w100 * mass
            if ix + 1 < grid_size and iz + 1 < grid_size:
                density[ix+1, iy, iz+1] += w101 * mass
            if ix + 1 < grid_size and iy + 1 < grid_size:
                density[ix+1, iy+1, iz] += w110 * mass
            if ix + 1 < grid_size and iy + 1 < grid_size and iz + 1 < grid_size:
                density[ix+1, iy+1, iz+1] += w111 * mass
    
    return density

class WatershedVoidFinder:
    """
    Implementiert den Watershed Void-Finding Algorithmus.
    """
    def __init__(self, threshold=0.2):
        self.threshold = threshold
        
    def find_voids(self, density_field):
        """
        Findet Voids im Dichtefeld mittels Watershed-Algorithmus.
        
        Args:
            density_field (np.ndarray): 3D Dichtefeld
            
        Returns:
            list: Liste der gefundenen Voids mit Eigenschaften
        """
        from scipy import ndimage
        
        # Normalisiere das Dichtefeld
        density_norm = density_field / np.mean(density_field)
        
        # Finde lokale Minima
        local_min = (density_norm < self.threshold)
        labels, num_voids = ndimage.label(local_min)
        
        voids = []
        for i in range(1, num_voids + 1):
            # Berechne Void-Eigenschaften
            void_mask = (labels == i)
            
            # Zentrum des Voids
            coords = np.where(void_mask)
            center = np.array([np.mean(c) for c in coords])
            
            # Void-Volumen
            volume = np.sum(void_mask)
            
            # Effektiver Radius (Radius einer Kugel gleichen Volumens)
            radius = (3.0 * volume / (4.0 * np.pi)) ** (1.0/3.0)
            
            # Mittlerer Dichtekontrast
            density_contrast = np.mean(density_norm[void_mask]) - 1.0
            
            # Berechne Elliptizität über Trägheitsmoment
            Ixx = np.sum((coords[1] - center[1])**2)
            Iyy = np.sum((coords[2] - center[2])**2)
            Izz = np.sum((coords[0] - center[0])**2)
            Ixy = -np.sum((coords[1] - center[1]) * (coords[2] - center[2]))
            Iyz = -np.sum((coords[2] - center[2]) * (coords[0] - center[0]))
            Ixz = -np.sum((coords[1] - center[1]) * (coords[0] - center[0]))
            
            I = np.array([[Ixx, Ixy, Ixz],
                         [Ixy, Iyy, Iyz],
                         [Ixz, Iyz, Izz]])
            
            eigenvals = np.linalg.eigvals(I)
            ellipticity = np.sqrt(1.0 - eigenvals.min() / eigenvals.max())
            
            void = {
                'center': center,
                'radius': radius,
                'volume': volume,
                'density_contrast': density_contrast,
                'ellipticity': ellipticity
            }
            voids.append(void)
        
        return voids

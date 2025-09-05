r"""

This module contains the building blocks of the ARPES simulation. It provides three main classes: ``Bands``, ``Spec``, and ``ARPES``.

``Bands``: Defines the electronic dispersion.

- The in-plane k-path is specified by a list of :math:`k_x` and :math:`k_y` points.
- The band dispersion is calculated along the path according to a tight-binding model.
- Alternatively, the band structure can be imported from an external file.

``Spec``: Calculates the ARPES spectra expected from the electronic dispersion.

1. Compute the one-electron removal spectral function from the electronic dispersion and self-energy.
2. Define the photoemission matrix elements.
3. Apply the Fermi-Dirac distribution for the effective electronic temperature and convolve with a Gaussian to include resolution broadening.

``ARPES``: Simulates the ARPES data that would be experimentally collected.

- Transforms ``Spec``, calculated in crystal momentum and binding energy: (:math:`\mathbf{k}`, :math:`\omega`) into emission angles and kinetic energy (:math:`\theta`, :math:`\phi`, :math:`E_\text{k}`).
- Creates a probability distribution based on the spectra and simulates the ARPES spectrum based on N electron events. 
"""
import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.interpolate import interp1d
from scipy.signal import convolve
from scipy.stats import norm
#%%
class Bands:    
    r"""
    Calculates the bandstructure based on a tight-binding model. The input arguments are saved in the ``Bands`` object.

    *Optional args*:   
    
    - ``symmetry``: A string. Defines the lattice of the tight-binding model. The available inputs are 'rectangle', 'square', 'hexagonal', 'honeycomb'. If an input is not given, one is chosen at random.
    
    - ``klim``: A :math:`2 \times 2` numpy array defining the limits of :math:`k_x` and :math:`k_y` in the list. If an input is not given, the lower limit is chosen randomly between :math:`[-1,-0.5]`, and the upper limit is chosen randomly between :math:`[0.5, 1]`.

    - ``Nbands``: An integer defining the number of bands in the tight-binding model. If an input is not given, one is chosen at random between :math:`[1, 5]`.

    - ``warp``: A string. "on" or "off". Toggles next-nearest neighbour hopping in the tight-binding model.

    - ``Npts``: A :math:`2 \times 1` numpy array (elements are integers) defining the number of points calculated in the :math:`k_x` and :math:`k_y` dimensions.

    - ``edges``: A float slightly larger than one. Since we calculate a limited region of k-space, interpolation may be off at the edges if we use large offset angles in the experiment. Here, the k-space edge is padded and later cropped to exclude artifacts.

    """
    
    def __init__(self,symmetry=None, klim=None, Nbands=None, warp=None, Npts=None, edges=None):
        symm=['rectangle','square','hexagonal','honeycomb']
        if symmetry is None:
            #symmetry of the tight-binding lattice, a string
            self.symmetry=symm[np.random.randint(4)]
        else:
            self.symmetry=symmetry
        if klim is None:
            #limits of momentum space calculated
            self.klim=np.vstack((-np.random.rand(2)*0.5-0.5, np.random.rand(2)*0.5+0.5))
        else:
            self.klim=klim
        if Nbands is None:
            #number of bands calculated
            self.Nbands=np.random.randint(1,5)
        else:
            self.Nbands=Nbands
        if warp is None:
            #turns on and off nearest neighbour hopping
            self.warp='on'
        else:
            self.warp=warp
        if Npts is None:
            #Number of kpts in the x and y direction
            self.Npts=np.array((100,80)) 
        else:
            self.Npts=Npts
        if edges is None:
            #Adds additional k space so interpolation does not go out of range
            self.edges=1.25     
        else:
            self.edges=edges
    def Make_kpath(self):
        r"""
        This function defines the :math:`k_x` and :math:`k_y` grid the bands are calculated on. 
        The edges are padded so that rotation and interpolation do not create artifacts. 
        The calculation of the dispersion is not particularly time-intensive, so a grid of points is typically calculated. 
        To speed up computation, the ARPES spectra can be calculated over just :math:`k_x`, but the grid of points are needed for interpolation in the case of rotational or offset domains.
        
        This function adds the following to the ``Bands`` object:

        *Saved args*:   
    
        - ``Bands.kpath``: A :math:`N \times 2` numpy array defining the k-path along which the dispersion is calculated. :math:`N` is the product of the elements of ``Bands.Npts``. The first and second columns correspond to :math:`k_x` and :math:`k_y`, respectively.

        - ``Bands.kax``: A :math:`N_\text{pts}^x \times 1` numpy array defining the :math:`k_x` axis. Used for plotting purposes.

        - ``Bands.kay``: A :math:`N_\text{pts}^y \times 1` numpy array defining the :math:`k_y` axis. Used for plotting purposes.
    
        """
        # Define k axes, the edges are added so that rotatoin and interpolation does not create artifacts
        # kax and kay are used for plotting purposes
        k1 = np.linspace(self.klim[0,0], self.klim[1,0], self.Npts[0]) * self.edges
        k2 = np.linspace(self.klim[0,1], self.klim[1,1], self.Npts[1]) * self.edges
        self.kax=k1.T
        self.kay=k2.T
        # Generate list of kpts using the meshgrid, reshape to a column vector
        # The kapth is used for calculating the band structure
        KX, KY = np.meshgrid(self.kax, self.kay)
        self.kpath=np.zeros((np.size(KX),2))
        self.kpath[:,0] = KX.reshape((np.size(KX)))
        self.kpath[:,1] = KY.reshape((np.size(KY)))

    def Make_bands(self, tb=None, lattice=None):   
        r"""
        This function calculates the dispersion using a tight-binding model.

        *Optional args*:   

        - ``tb``: A Python dictionary representing the tight-binding parameters. The dictionary is of the form:

        ::

            tb = {"E0": [], "t": []}

        - :math:`E_0` and :math:`t` must be NumPy arrays of dimension :math:`[1 , N_\text{bands}]`.
        - :math:`E_0` contains the center energies of the bands.
        - :math:`t` contains the hopping parameter of each band.

        If the lattice is rectangular (as defined in ``Bands.symmetry``), then
        :math:`t` must have shape :math:`[2, N_\text{bands}]`.

        If no input is provided, :math:`E_0` is randomly generated in the interval [-1, 0],
        and :math:`t` is randomly generated in the interval [-1, 1].

        - ``lattice``: A Python dictionary of the lattice parameters. 

        These lattice parameters define the size of the Brillouin zone and -- by extension -- the field of view given by the limits set in ``Bands.klim``. 
        The dictionary is of the form:

        ::

            lattice = {"a": [], "b": []}

        - :math:`a` and :math:`b`  are floats. 

        If no input is provided, :math:`a` and math:`b` are calculated from the k-space limits.

        *Saved args*:   

        - ``Bands.bands``: A :math:`[N , N_{\text{bands}}` numpy array defining the dispersion of each band along the k-path. N is given by the product of ``Bands.Npts``.
    
        """
        kx = self.kpath[:,0]
        ky = self.kpath[:,1]
        self.bands = np.zeros((len(self.kpath), self.Nbands))
        #Define tight-binding parameters
        if tb is None:
            #Default random tb parameters
            E0 = -1*np.random.rand(self.Nbands)
            t = 2*np.random.rand(self.Nbands) - 1
            if self.symmetry =='rectangle':
                tp = 2*np.random.rand(self.Nbands) - 1
                t=np.vstack((t, tp)).T
            tb = {"E0": E0, "t": t}
        else:
            E0 = tb["E0"]
            t = tb["t"]
            if (len(E0)==self.Nbands) != True:
                print('Number of elements in E0 != number of bands!')
                sys.exit(2)
            if (len(t)==self.Nbands) != True:
                print('Number of elements in t != number of bands!')
                sys.exit(2)   
        self.tb = tb 
        #Define/import lattice size
        if lattice is None:
            if self.symmetry == 'rectangle':
                a = self.edges*np.pi/np.max(kx)
                b = np.pi/np.max(ky)
                self.lattice = {"a": a, "b": b}            
            if self.symmetry == 'square':
                a = self.edges*np.pi/np.max(kx)
                self.lattice = {"a": a, "b": a}  
            if self.symmetry == 'hexagonal':
                a = self.edges*2*np.pi/np.sqrt(3)/np.max(kx)
                self.lattice = {"a": a, "b": a} 
            if self.symmetry == 'honeycomb':
                a = self.edges*2*np.pi/np.sqrt(3)/np.max(kx)
                self.lattice = {"a": a, "b": a} 
        else:
            a = lattice["a"]
            if self.symmetry == 'rectangle':
                b = lattice["b"]
                self.lattice= lattice
            else:
                self.lattice = lattice
        # Calculate tight-binding bands
        if self.symmetry == 'rectangle':                      
            for i in range(self.Nbands):
                self.bands[:,i] = E0[i] + 2*t[i,0]*np.cos(kx*a) + 2*t[i,1]*np.cos(ky*b)
                if self.warp == 'on':
                    self.bands[:,i] = self.bands[:,i] + np.random.rand()*t[i,0]*np.cos(2*kx*a) + np.random.rand()*t[i,1]*np.cos(2*ky*b)
        elif self.symmetry == 'square':            
            for i in range(self.Nbands):
                self.bands[:,i] = E0[i] + 2*t[i]*np.cos(kx*a) + 2*t[i]*np.cos(ky*a)
                if self.warp == 'on':
                    self.bands[:,i] = self.bands[:,i] + np.random.rand()*t[i]*(np.cos(2*kx*a) + np.cos(2*ky*a))
        elif self.symmetry == 'hexagonal':            
            for i in range(self.Nbands):
                self.bands[:,i] = E0[i] + 2*t[i]*(np.cos(a/2*(kx+np.sqrt(3)*ky)) + np.cos(a/2*(kx-np.sqrt(3)*ky)) + np.cos(a*kx))
                if self.warp == 'on':
                    self.bands[:,i] = self.bands[:,i] + np.random.rand()*2*t[i]*(np.cos(a/2*(np.sqrt(3)*ky+3*kx)) + np.cos(a/2*(np.sqrt(3)*ky-3*kx)) + np.cos(a*np.sqrt(3)*ky))
        elif self.symmetry == 'honeycomb':
            self.bands = np.zeros((len(self.kpath), 2*self.Nbands))
            for i in range(self.Nbands):
                self.bands[:,2*i]   = E0[i] + t[i]*np.sqrt(3 + 2*np.cos(np.sqrt(3)*kx*a) + 4*np.cos(np.sqrt(3)*kx*a/2)*np.cos(3*ky*a/2))
                self.bands[:,2*i+1] = E0[i] - t[i]*np.sqrt(3 + 2*np.cos(np.sqrt(3)*kx*a) + 4*np.cos(np.sqrt(3)*kx*a/2)*np.cos(3*ky*a/2))
                if self.warp == 'on':
                    nnn=np.random.rand()*2*t[i]*(np.cos(a/2*(np.sqrt(3)*kx+3*ky))+np.cos(a/2*(np.sqrt(3)*kx-3*ky))+np.cos(a*np.sqrt(3)*kx))
                    self.bands[:,2*i]=self.bands[:,2*i]+nnn
                    self.bands[:,2*i+1]=self.bands[:,2*i+1]+nnn
    def Import_bands(self, filename):
        r"""
        This function imports bands from a file. The file should have kx in column 1, ky in column 2. Each band should be in its own column from 3 onwards.

        *args*:

        - ``filename``: A string. The name of the file to be imported.

        *Saved args*: 

        - The following and read from the file and saved to the Bands object: ``Npts``, ``kax``, ``kay``, ``klim``, ``kpath``, ``bands``, ``Nbands``   

        - The following parameters are defined statically: 

        ::

            bands.edges = 1
            bands.warp = "off"
            bands.symmetry = "custom" 

    
        """

        import csv
        with open(filename) as file:
            reader = csv.reader(file)
            headers = next(reader)
            data = []
            for row in reader:
                row_dict = {}
                for i in range(len(headers)):
                    row_dict[headers[i]] = row[i]
                data.append(row_dict)
        #Format input for bands
        self.edges=1
        self.warp='off'
        self.symmetry='custom'
        self.Nbands=len(headers)-2
        kx=np.array([float(row_dict['kx']) for row_dict in data])
        ky=np.array([float(row_dict['ky']) for row_dict in data])

        indx=np.where(kx>kx[0])[0][0]
        indy=np.where(ky>ky[0])[0][0]
        if indx>indy:
            self.Npts=[(len(kx)/indx).astype(int), indx]
        else:
            self.Npts=[indy, (len(ky)/indy).astype(int)]
        print(self.Npts)
        self.kax=np.linspace(kx.min(), kx.max(), self.Npts[0]).T
        self.kay=np.linspace(ky.min(), ky.max(), self.Npts[1]).T

        self.klim=np.vstack((np.array([np.abs(kx).min(), np.abs(ky).min()]),\
            np.array([np.abs(kx).max(), np.abs(ky).max()])))
        self.kpath = np.zeros((np.prod(self.Npts), 2))
        self.kpath[:,0]=kx
        self.kpath[:,1]=ky
        self.bands = np.zeros((len(self.kpath), self.Nbands))
        for i in range(self.Nbands):
            self.bands[:,i]=np.array([float(row_dict[headers[i+2]]) for row_dict in data])
    def print_variables(self):
        """
        Provides a summary of variables used to define the band structure.
        """
        print('Lattice symmetry:', self.symmetry, 'Warp:', self.warp)
        print('Nbands:', self.Nbands)
        print('kx lim:', self.klim[:,0], 'Nptsx:', self.Npts[0])
        print('ky lim:', self.klim[:,1], 'Nptsy:', self.Npts[1])

#%%
class Spec:
    r"""
    Calculates the photoemission spectra. Includes the Fermi-Dirac distribution, matrix elements and resolution broadening.

    *args:*

    - The input ``bands`` is an object. Defines the electronic dispersion and k-path.

    *Optional args:*

    - ``dimension``: A string. Defines the dimension of the calculation, three modes are available.

        - The input "cube" calculates the spectra in binding energy :math:`\omega`, and the crystal momenta :math:`k_x`, and :math:`k_y`.
        - The input "sliceEk" calculates the spectra in :math:`\omega` and :math:`k_x`. The "dispersion cut".
        - The input "slicekk" calculates the spectra in :math:`k_x` and :math:`k_y`. The "Fermi surface" or "constant energy cut". 
    - ``Omega``: A :math:`M \times 1` numpy array defining the binding energy range points over which the photoemission spectra are calculated.

    *Saved args:*

    - ``spec.bands`` : The object defining the electronic dispersion and k-path.

    - ``spec.kax`` : numpy array of shape :math:`(N_\text{pts}^x, 1)`. Defines the :math:`k_x` axis. Used for plotting purposes.

    - ``spec.kay`` : numpy array of shape :math:`(N_\text{pts}^y, 1)`. Defines the :math:`k_y` axis. Used for plotting purposes.

    - ``spec.matrix_elements`` : numpy array of shape :math:`(N, N_\text{bands})`. Matrix elements of each band along the k-path. Same shape as ``Bands.bands``. Initialized as an array of ones.

    - ``spec.ReS`` : numpy array of shape :math:`(M, N_\text{bands})`. The real part of the self-energy, initialized as zeros.  

    - ``spec.ImS`` : numpy array of shape :math:`(M, N_\text{bands})`. The real part of the self-energy, initialized as with a single value of 0.2.  

    - ``spec.domain`` : numpy array. Defines the relative intensity of rotational and offset domains. Initialized (for the primary domain) as an array of ones with shape :math:`(1, N_{\text{bands}})`.
    
    """ 
    def __init__(self, bands, dimension=None, Omega=None):
        # bands are calculated by the Bands class. 
        # dimension can be 2D (slice) or 3D (cube). dimension = "slicekk" or "sliceEk" or "cube"
        # Omega the energy axis 
        if dimension==None:
            dim=['slicekk','cube','sliceEk']
            self.dimension=dim[np.random.randint(3)]
        else:
            self.dimension=dimension
        # Calculate energy window
        if Omega is None:
            bands_min=np.min(np.min(bands.bands))
            window_lim=-1*np.random.randint(2,4)
            self.Omega = np.linspace(np.max((bands_min, window_lim))-np.random.rand(), 0.5, bands.Npts[0]+np.random.randint(100))
        else:
            self.Omega=Omega
        ## Initiate defaults
        self.bands=bands
        self.kax=bands.kax
        self.kay=bands.kay
        self.matrix_elements=np.ones(bands.bands.shape)
        self.ReS=np.zeros((len(self.Omega), bands.bands.shape[1]))
        self.ImS=np.matmul(np.ones((len(self.Omega),1)), 0.2*np.random.rand(1,bands.bands.shape[1]))
        self.domain=np.ones((1,bands.bands.shape[1]))

    def Make_self_energy(self, SE):
        r"""
        This function is optional, since the self-energy is already initialized. 
        For more realistic ARPES spectra, two types of self-energy are available through the input dictionary ``SE``:

        *args*:

        - ``SE``: a python dictionary. The key ``type`` accepts two strings: ``"FL"`` or ``"kink"``, corresponding to Fermi-liquid or electron-boson kink. 

            - for Fermi-liquid type self energy, additional fields ``val`` and ``ImS0`` may be specified (or will be randomly chosen)
            - for electron-boson kink, additional fields ``ImS0``, ``ImS1``, ``Amp``, ``Ekink``, and ``gamma`` may be specified (or will be randomly chosen).

        *Saved args:*

        - ``spec.ReS`` : numpy array of shape :math:`(M, N_\text{bands})`. The real part of the self-energy.  

        - ``spec.ImS`` : numpy array of shape :math:`(M, N_\text{bands})`. The real part of the self-energy.  

        - ``spec.SE`` : the python dictionary with parameters used in the calculation of the self-energy.
            
        """
        Nbands=self.bands.bands.shape[1]
        if SE["type"] == 'FL':
            if 'val' not in SE:                               
                SE["val"]=0.2*np.random.rand(1,Nbands)+0.05   
            if 'ImS0' not in SE:
                SE["ImS0"] = 0.01
            self.ImS=np.matmul(np.reshape(self.Omega**2,[-1,1]), SE["val"])+SE["ImS0"]    
                
        elif SE["type"] == 'kink':
            if 'ImS' in SE:
                ImS0=SE["ImS0"]
                ImS1=SE["ImS1"]
                R=SE["Amp"]
                Ekink=SE["Ekink"]
                g_Re=SE["gamma"]
                g_Im=g_Re
            else:
                ImS0=0.015+np.random.rand(Nbands)*0.01
                ImS1=ImS0+np.random.rand()*0.1
                R=np.random.rand(Nbands)*0.01
                Ekink=np.random.uniform(0.05,0.3)*np.ones(Nbands)
                g_Re=np.random.rand()*50*np.ones(Nbands)
                g_Im=g_Re
                SE["ImS0"]=ImS0
                SE["ImS1"]=ImS1
                SE["Amp"]= R
                SE["Ekink"] = Ekink
                SE["gamma"] = g_Re
            ReS=np.zeros((len(self.Omega), Nbands))
            ImS=ReS
            for i in range(Nbands):
                ReS[:,i]=R[i]*(g_Re[i]/((self.Omega+Ekink[i])**2+(g_Re[i]/2)**2)-g_Re[i]/((self.Omega-Ekink[i])**2+(g_Re[i]/2)**2))
                ImS[:,i]=(ImS1[i]-ImS0[i])*(1-1./(1+np.exp(-(self.Omega+Ekink[i])*g_Im[i])))+ImS0[i]
            self.ReS=ReS
            self.ImS=ImS
        self.SE=SE
        
    def Make_specfun(self, mod):
        r"""
        This function calculates the photoemission spectral intensity based on the band structure as well as the self-energy given.

        *args*:
        - ``mod``: a Python dictionary of the form ``mod = {"ER": [], "kR": [], "Temp": []}``, 
        where the three fields define the energy resolution, the angular resolution, 
        and the electronic temperature, respectively. 
        ``mod`` is an object generated by the ``aurelia_static_vars`` module. 

        The outputs of the function are:

        - ``spec.mod``: The Python dictionary which collects the modification parameters.

        - ``spec.specfun``: A numpy array with a dimension specified by ``spec.dimension``, such that:

            - ``cube``: :math:`M \times N_{pts}^x \times N_{pts}^y`
            - ``sliceEk``: :math:`M \times N_{pts}^x`
            - ``slicekk``: :math:`1 \times N_{pts}^x \times N_{pts}^y`

        """

        self.mod=mod
        bands=self.bands
        Sb = bands.bands.shape
        kB = 8.6196e-05
        # Calculate Spectral function
        if self.dimension=='cube':
            A = np.zeros((len(self.Omega), Sb[0], Sb[1]))
            ind=np.array(range(bands.kpath.shape[0]))
            ind_omega=np.array(range(self.Omega.shape[0]))      
            self.slice_const=np.nan
            self.slice_ind=ind_omega
            self.kpath=self.bands.kpath
        elif self.dimension=='sliceEk':
            ky0=bands.kpath[np.random.randint(bands.kpath.shape[0]),1]
            ind=np.where(bands.kpath[:,1]==ky0)[0]
            ind_omega=np.array(range(self.Omega.shape[0]))   
            A = np.zeros((len(self.Omega), len(ind), Sb[1]))
            self.slice_const=ky0
            self.slice_ind=ind
            self.kpath=self.bands.kpath[ind,:]
        elif self.dimension=='slicekk':
            dR=kB*mod.Temp+mod.ER
            dOmega=self.Omega[1]-self.Omega[0]
            dE=max((dR, 2*dOmega))
            indE=np.where((bands.bands > np.min(self.Omega)) & (bands.bands < 0))
            dummy=bands.bands[indE]
            E0=dummy[np.random.randint(len(dummy))]            
            ind_omega=np.where((self.Omega > E0-dE) & (self.Omega < E0+dE))[0]
            ind=np.array(range(bands.kpath.shape[0]))
            A = np.zeros((len(ind_omega), len(ind), Sb[1]))
            self.slice_const=E0
            self.slice_ind=ind_omega
            self.kpath=self.bands.kpath
        for m in range(Sb[1]):
            E = bands.bands[ind, m]
            for n in range(len(ind_omega)):
                A[n, :, m] = self.matrix_elements[ind, m] * self.ImS[ind_omega[n],m]\
                      / ((self.Omega[ind_omega[n]] - E - self.ReS[ind_omega[n],m])**2 + (self.ImS[ind_omega[n],m])**2)
            A[:, :, m] = self.domain[0,m] * A[:, :, m]
        A = np.sum(A, axis=2)
        if self.dimension=='cube':
            A = np.reshape(A, (len(self.Omega), bands.Npts[1], bands.Npts[0]))
            self.specfun=np.transpose(A, (0,2,1))
        elif self.dimension=='sliceEk':
            self.specfun = A
        elif self.dimension=='slicekk':
            A=np.reshape(A, (A.shape[0], bands.Npts[1], bands.Npts[0]))
            self.specfun=np.transpose(A, (0,2,1))

    def Make_specmod(self, mod):
        r"""   
        This function modifies the intensity in ``self.specfun`` by adding the Fermi-Dirac distribution and resolution broadening.  

        *args*:
        
        - ``mod``: an object generated the *aurelia_static_vars* module. Defines the energy resolution, the angular resolution, and the electronic temperature.  
        
        *Saved args*:

        - ``spec.specfun``: The modified intensity replaces that previous calculated via spec.Make_specfun(mod)

        """
        kB = 8.6196e-05
        #Add Fermi Dirac and resolutions        
        ce = mod.ER / (2 * np.sqrt(2 * np.log(2)))
        x = np.arange(-2*mod.ER, 2*mod.ER + (self.Omega[1] - self.Omega[0]), self.Omega[1] - self.Omega[0])
        Ge = np.exp(-(x - x.mean()) ** 2 / (2 * ce ** 2))
        Ge = Ge / np.sum(Ge)
        y = np.arange(-2*mod.kR, 2*mod.kR + (self.kax[1] - self.kax[0]), self.kax[1] - self.kax[0])
        ck = mod.kR / (2 * np.sqrt(2 * np.log(2)))
        Gk = np.exp(-(y - y.mean()) ** 2 / (2 * ck ** 2))
        Gk = Gk / np.sum(Gk)        
        if self.dimension == 'sliceEk':
            FD = 1 / (1 + (np.exp((self.Omega) / (kB * mod.Temp))))
            A_res = FD[:, np.newaxis] * self.specfun
            A_res = np.apply_along_axis(lambda x: convolve(x, Ge, mode='same'), axis=0, arr=A_res)
            A_res = np.apply_along_axis(lambda x: convolve(x, Gk, mode='same'), axis=1, arr=A_res)
            
        elif self.dimension !='sliceEk':
            A=np.reshape(self.specfun,(len(self.slice_ind), np.prod(self.bands.Npts)))
            FD = 1 / (1 + (np.exp((self.Omega[self.slice_ind]) / (kB * mod.Temp))))
            A_FD = FD[:, np.newaxis] * A            
            A_res = np.apply_along_axis(lambda x: convolve(x, Ge, mode='same'), axis=0, arr=A_FD)
            A_res = np.reshape(A_res, self.specfun.shape)
            if self.dimension=='slicekk':
                idummy=np.round(A_res.shape[0]/2).astype(int)
                A_res=A_res[idummy-1:idummy]
                self.Omega=self.Omega[idummy-1:idummy]
                print(self.Omega, ' ', A_res.shape)
            y2 = np.arange(-2*mod.kR, 2*mod.kR + (self.kay[1] - self.kay[0]), self.kay[1] - self.kay[0])
            Gk2 = np.exp(-(y2 - y2.mean()) ** 2 / (2 * ck ** 2))
            Gk2 = Gk2 / np.sum(Gk2)
            A_res = np.apply_along_axis(lambda x: convolve(x, Gk,  mode='same'), axis=1, arr=A_res)
            A_res = np.apply_along_axis(lambda x: convolve(x, Gk2, mode='same'), axis=2, arr=A_res)   
        self.specfun=A_res

    def Make_matrix_elements(self, ME = None):
        r"""
        This function creates fake matrix elements aimed at varying the intensity of bands to mimic photoemission intensity. 

        *args:*

        - A Python dictionary. Defines the type of fake photoemission matrix elements that are generated. Accepts three strings.

            - ``"symm"``: Gives matrix elements the same symmetry as that of the tight-binding model, in that they are periodic in k-space in the same way.
            - ``"rot"`` : Gives matrix elements with rotational symmetry, which mimics the orbital selectivity of linear and/or circularly polarized light.
            - ``"poly"``: Gives matrix elements defined by a random polynomial. Used to modulate the intensity of the bands and is used to mimic the unpredictable effects of experimental geometry variance in the light. 

        *Saved args:*

        - ``spec.matrix_elements``: A NumPy array defining the matrix elwith the same dimensions as ``Bands.bands``. 
        - ``spec.ME``: The Python dictionary specifying parameters of the matrix-element calculation.
            
        """       
        if ME is None:
            ME = {"type": ['symm', 'poly'], "polyN": np.random.randint(1,6)}
        else:
            if 'polyN' not in ME:             
                ME["polyN"] = np.random.randint(1,6)
            if 'rotN' not in ME:
                if self.bands.symmetry == 'rectangle':
                        rotn=[1,2]
                        ind=np.random.randint(len(rotn))
                elif self.bands.symmetry == 'square':
                    rotn=[1,1,2,2,4]
                    ind=np.random.randint(len(rotn))
                else:
                    rotn=[1,1,2,2,2,3,3,3]
                    ind=np.random.randint(len(rotn))
                ME["rotN"] = rotn[ind]
        self.ME = ME
        kx=self.bands.kpath[:,0]
        ky=self.bands.kpath[:,1]
        M = np.ones(self.bands.bands.shape)
        if 'symm' in self.ME:
            t = 0.25*np.random.uniform(-1,1,self.bands.Nbands)
            a=self.bands.lattice["a"]
            if self.bands.symmetry == 'rectangle':
                b = self.bands.lattice[1]
                for i in range(self.bands.Nbands):
                    M[:, i] = t[i] * (np.cos(kx * a) + np.cos(ky * b))
            elif self.bands.symmetry == 'square':
                for i in range(self.bands.Nbands):
                    M[:, i] = t[i] * (np.cos(kx * a) + np.cos(ky * a))
            elif self.bands.symmetry == 'hexagonal':
                for i in range(self.bands.Nbands):
                    M[:, i] = t[i] * (np.cos(a / 2 * (kx + np.sqrt(3) * ky)))
            elif self.bands.symmetry == 'honeycomb':
                for i in range(self.bands.Nbands):
                    M[:, 2*i]   = t[i] * np.sqrt(3 + 2 * np.cos(np.sqrt(3) * ky * a) + 4 * np.cos(np.sqrt(3) * ky * a / 2) * np.cos(3 * kx * a / 2))
                    M[:, 2*i+1] = M[:, 2*i]
            elif self.bands.symmetry == 'custom':
                for i in range(self.bands.Nbands):
                    M[:, i]=np.ones((kx.shape))
        if 'poly' in self.ME["type"]:
            coeffs = np.random.randn(self.ME["polyN"]+1,self.ME["polyN"] +1) # generate random coefficients
            x, y = np.meshgrid(self.bands.kax, self.bands.kay) # create a grid of x and y values
            Mpoly =  np.polynomial.polynomial.polyval2d(x, y, coeffs)
            for i in range(self.bands.bands.shape[1]):
                M[:,i] = M[:,i]*np.random.rand()*np.reshape(Mpoly, len(kx))
        if 'rot' in self.ME["type"]:
            phi=np.arctan(ky/kx)
            for i in range(self.bands.bands.shape[1]):
                M[:,i] = M[:,i]*np.random.rand()*np.cos(phi*self.ME["rotN"])*0.5
        #Normalize the matrix elements        
        for i in range(self.bands.bands.shape[1]):
            M[:, i] = np.random.rand() * (M[:, i] - np.min(M[:, i])) / np.abs(np.max(M[:, i]))
        self.matrix_elements=M
    def print_variables(self):
        """
        Provides a summary of variables used to calculate the measured spectral intensity.
        """
        print('Spec dimension:', self.dimension)
        if self.dimension != 'cube':
            print('Slice const:', self.slice_const)
        print('Matric element type:', self.ME)
        if 'poly' in self.ME:
            print('ME polynomial order:', self.MEpoly)
        if 'rot' in self.ME:
            print('ME rotational symmetry:', self.MErotn)
        print('ER:', round(self.mod.ER, 1), ' Temp:',round(self.mod.Temp), ' kR:', round(self.mod.kR,2))        

class ARPES:
    r"""
    This function initializes the ARPES simulation.
    
    *args*:

    - ``spec``: An object containing the spectral intensity calculated from the dispersion.

    - ``exp``: An object containing the experimental parameters, initialized from the aurelia_static_vars module.

    *Optional args*:

    - ``dimension``: A string defining the dimension of the calculation. Three modes are available:

        - ``"cube"``: Spectra in binding energy, :math:`k_x`, and :math:`k_y`.  
        - ``"sliceEk"``: Spectra in binding energy and :math:`k_x` (dispersion cut).  
        - ``"slicekk"``: Spectra in :math:`k_x` and :math:`k_y` (Fermi surface).  

    The default ``dimension`` string is the same as ``Spec.dimension``. If ``Spec.dimension = "cube"``, then ``arpes.dimension`` can be set to ``"sliceEk"`` or ``"slicekk"``.  
    This allows offset and rotational domains to be accurately calculated, while saving computational time and file size.

    - ``ang_lim``: A python dictionary with the fields ``ang_lim["th"]`` and ``ang_lim["ph"]``. The values are 2-element numpy arrays defining the limits of :math:`\theta` and :math:`\phi` seen by the detector. If not specified, the angle limits are calculated using the k-space limits in ``Spec``.  
    
    *Saved args*:

    - ``arpes.spec``: An object containing the spectral intensity calculated from the dispersion.

    - ``arpes.exp``: An object containing the experimental parameters.

    - ``arpes.Ek``: The kinetic energy axis, calculated as:

    - ``arpes.dimension``: A string defining the dimension of the calculation.

    - ``arpes.th``: A NumPy array of shape :math:`N_{pts}^x \times 1`. Defines the angles along the :math:`k_x` direction.

    - ``arpes.ph``: A NumPy array of shape :math:`N_{pts}^y \times 1`. Defines the angles along the :math:`k_y` direction.
    
    - ``arpes.crop``: A boolean. Checks if the edges have been cropped. Initialized as *false*. The edges are defined by ``Bands.edges``. 
    """
    def __init__(self, spec, exp, ang_lim=None, dimension=None):
        #Define Units
        hbar=6.626070040e-34/(2*np.pi)
        me=9.11e-31
        eV=1.601e-19
        A0=1e-10
        #Calculate self energy and write parameters
        self.Ek=exp.hv-exp.workfun+spec.Omega
        self.spec=spec
        self.exp=exp
        #Prepare dimensions
        if dimension is None:
            self.dimension=spec.dimension
        else:
            if spec.dimension != 'cube':
                print('spec.dimension is not cube!!')
                self.dimension=spec.dimension
            else:
                self.dimension=dimension
        kmax=spec.bands.klim/A0
        th_lim=np.arcsin(hbar*kmax /np.sqrt(2*me*np.min(self.Ek)*eV))  
        if ang_lim is None:
            pass
        else:
            th_lim[:,0] = ang_lim["th"]
            if self.dimension != 'sliceEk':
                th_lim[:,1] = ang_lim["ph"]
        edge=(1-1/self.spec.bands.edges)
        self.th=1/(1-edge)*np.linspace(th_lim[0,0], th_lim[1,0], spec.bands.Npts[0])
        self.ph=1/(1-edge)*np.linspace(th_lim[0,1], th_lim[1,1], spec.bands.Npts[1])
        self.anglim=th_lim
        self.crop = False

    def Make_angle_conv(self, const=None, domain=None):
        r"""
        This function converts the intensity stored in ``spec.specfun`` in momentum and binding energy to ``arpes.intensity`` in angle and kinetic energy.
        
        *args*:

        - ``const``: A float. If the dimension of the calculation is not ``"cube"``, this
            gives the value at which the slice is calculated.
            
            - For ``self.dimension = "sliceEk"``, ``const`` corresponds to the
            :math:`\phi` axis. Defaults to the mean :math:`\phi` value.
            - For ``self.dimension = "slicekk"``, ``const`` corresponds to
            :math:`E_k` axis. Defaults to the Fermi energy.

        - ``domain``: An object containing information about offset angles for
            calculating offset domains.
        
        *Saved args*:

        - ``arpes.intensity``: A numpy array with shape specified by ``arpes.dimension``.

            - ``cube``: :math:`M\times N_{pts}^x \times N_{pts}^y`
            - ``sliceEk``: :math:`M\times N_{pts}^x`
            - ``slicekk``: :math:`1\times N_{pts}^x \times N_{pts}^y`
        - ``arpes.bkgd``: A numpy array with the same shape as ``arpes.intensity``. Initialized as zeros.
        - ``arpes.response``: A numpy array with the same shape as ``arpes.intensity``. Initialized as ones.
    
        *Returned args*:

        - If this function is used to calculate a domain, then the intensity is not saved, but simply returned.

        """

        hbar=6.626070040e-34/(2*np.pi)
        me=9.11e-31
        eV=1.601e-19
        A0=1e-10
        spec=self.spec
        exp=self.exp
        if domain is None:
            th0=exp.th0
            ph0=exp.ph0
        else:
            th0=exp.th0+domain["th0"]
            ph0=exp.ph0+domain["ph0"]
        if spec.dimension == self.dimension:
            if spec.dimension == 'sliceEk':
                kx = spec.kpath[:,0]
                ky = spec.kpath[:,1]
                self.slice_const=spec.slice_const
            elif spec.dimension != 'sliceEk':
                ky, kx = np.meshgrid(spec.kay, spec.kax)
                self.slice_const=spec.slice_const            
            TH, PH = np.meshgrid(self.th, self.ph)
            TH = TH.reshape((np.size(TH), 1))
            PH = PH.reshape((np.size(PH), 1))
            A_ang = np.zeros((len(spec.Omega), len(spec.kpath)))            
        elif spec.dimension != self.dimension:
            ky, kx = np.meshgrid(spec.kay, spec.kax)
            if self.dimension == 'sliceEk':
                if const is None:
                    self.slice_ind = np.random.randint(self.ph.shape[0])
                    self.slice_const = self.ph[self.slice_ind]
                else:
                    self.slice_const=const
                    self.slice_ind=np.where(self.ph>=const)[0][0]
                TH, PH = np.meshgrid(self.th, self.ph[self.slice_ind])
                TH = TH.reshape((np.size(TH), 1))
                PH = PH.reshape((np.size(PH), 1))
                A_ang = np.zeros((len(spec.Omega), len(TH)))
            elif self.dimension == 'slicekk':
                if const is None:
                    self.slice_ind = np.where(spec.Omega>=0)[0][0]
                    self.slice_const = self.Ek[self.slice_ind]
                else:
                    self.slice_const=const
                    self.slice_ind=np.where(self.Ek>=const)[0][0]
                TH, PH = np.meshgrid(self.th, self.ph)
                TH = TH.reshape((np.size(TH), 1))
                PH = PH.reshape((np.size(PH), 1))
                A_ang = np.zeros((len(spec.kpath)))
        kx=np.reshape(kx/A0,(-1,1))
        ky=np.reshape(ky/A0,(-1,1))
        k=np.sqrt(kx**2+ky**2)
        specmod=np.reshape(spec.specfun,(len(spec.Omega), int(np.prod(spec.specfun.shape)/len(spec.Omega)))).T
        a = np.reshape(np.sqrt(2*me*self.Ek*eV),(-1,1))
        a = np.matmul(a,np.ones((1,len(k))))
        kgrid = np.matmul(np.ones((len(spec.Omega),1)),k.T)
        kxgrid= np.matmul(np.ones((len(spec.Omega),1)),kx.T)
        kygrid= np.matmul(np.ones((len(spec.Omega),1)),ky.T)
        theta = np.sign(kxgrid)*np.arcsin(hbar*kgrid/a)
        if self.spec.dimension == 'sliceEk':
            theta=-theta           
        az  = np.arcsin(hbar*kygrid/a/ np.sin(theta)) + exp.az0
        dp1 = np.cos(az) * np.sin(theta)
        dp2 = np.sin(az) * np.sin(theta)
        dp3 = np.cos(theta)

        dpp1 =  np.cos(th0) * dp1 + np.sin(th0) * dp3
        dpp2 =  np.sin(th0) * np.sin(ph0) * dp1 + np.cos(ph0) * dp2 - np.cos(th0) * np.sin(ph0) * dp3
        dpp3 = -np.sin(th0) * np.cos(ph0) * dp1 + np.sin(ph0) * dp2 + np.cos(th0) * np.cos(ph0) * dp3
        if exp.detector["slit"]=='vertical':
            th_m = -np.arctan(dpp1 / dpp3)
            ph_m =  np.arcsin(dpp2)
        elif exp.detector["slit"]=='horizontal':
            ph_m =  np.arctan(dpp2 / dpp3)
            th_m = -np.arcsin(dpp1)   
        if spec.dimension == self.dimension:
            if spec.dimension != 'sliceEk':         
                for i in range(len(spec.Omega)):     
                    ang_points=np.vstack((th_m[i,:],ph_m[i,:])).T
                    A_ang[i,:]=np.reshape(griddata(ang_points, specmod[:,i], (TH,PH), method='nearest', fill_value=0),(len(k)))
                A_out = np.transpose(np.reshape(A_ang,(len(spec.Omega), len(spec.kay),len(spec.kax))), (0,2,1))    
                if domain is None:
                    self.intensity = A_out/A_out.max()
                else:
                    return(A_out)  
            elif spec.dimension =='sliceEk':
                for i in range(len(spec.Omega)):
                    ang_in=th_m[i,:].T
                    f=interp1d(ang_in, specmod[:,i], kind='linear',fill_value=0, bounds_error=False)                
                    A_ang[i, :] = f(self.th)
                A_ang = A_ang-A_ang.min()
                self.intensity=A_ang/A_ang.max()
        elif spec.dimension != self.dimension:
            if self.dimension == 'sliceEk':
                dph=2*(self.ph[1]-self.ph[0])
                for i in range(len(spec.Omega)):     
                    indph=np.where((ph_m[i,:] > self.slice_const-dph) & (ph_m[i,:] < self.slice_const+dph))[0]
                    ang_points=np.vstack((th_m[i,indph],ph_m[i,indph])).T
                    A_ang[i,:]=np.reshape(griddata(ang_points, specmod[indph,i], (TH,PH), method='nearest', fill_value=0),len(TH))
                A_out = A_ang-A_ang.min()
            elif self.dimension == 'slicekk':
                ang_points=np.vstack((th_m[self.slice_ind,:],ph_m[self.slice_ind,:])).T
                A_ang=griddata(ang_points, specmod[:,self.slice_ind], (TH,PH), method='nearest', fill_value=0)
                A_out= np.transpose(np.reshape(A_ang,(1, len(spec.kay),len(spec.kax))), (0,2,1))  
            if domain is None:
                self.intensity = A_out/A_out.max()
                self.bkgd = np.zeros(self.intensity.shape)
                self.response = np.ones(self.intensity.shape)
            else:
                return(A_out)    
    def Make_kwarp_check(self):
        """
        This function checks the momentum-to-angle conversion by performing an angle-to-momentum conversion before interpolation to show that the original k-mesh is reporduced. 
        It gives no outputs but plots the intensity before warping, after warping to angle, and after warping back to momentum space. 
        """
        hbar=6.626070040e-34/(2*np.pi)
        me=9.11e-31
        eV=1.601e-19
        A0=1e-10
        spec=self.spec
        exp=self.exp
        th0=exp.th0
        ph0=exp.ph0

        ky, kx = np.meshgrid(spec.kay, spec.kax)
        kx=np.reshape(kx/A0,(-1,1))
        ky=np.reshape(ky/A0,(-1,1))
        k=np.sqrt(kx**2+ky**2)
        
        a = np.reshape(np.sqrt(2*me*self.Ek*eV),(-1,1))
        a = np.matmul(a,np.ones((1,len(k))))
        kgrid = np.matmul(np.ones((len(spec.Omega),1)),k.T)
        kxgrid= np.matmul(np.ones((len(spec.Omega),1)),kx.T)
        kygrid= np.matmul(np.ones((len(spec.Omega),1)),ky.T)
        theta = np.sign(kxgrid)*np.arcsin(hbar*kgrid/a)
        az  = np.arcsin(hbar*kygrid/a/ np.sin(theta)) + exp.az0
        dp1 = np.cos(az) * np.sin(theta)
        dp2 = np.sin(az) * np.sin(theta)
        dp3 = np.cos(theta)

        dpp1 =  np.cos(th0) * dp1 + np.sin(th0) * dp3
        dpp2 =  np.sin(th0) * np.sin(ph0) * dp1 + np.cos(ph0) * dp2 - np.cos(th0) * np.sin(ph0) * dp3
        dpp3 = -np.sin(th0) * np.cos(ph0) * dp1 + np.sin(ph0) * dp2 + np.cos(th0) * np.cos(ph0) * dp3
        if exp.detector["slit"]=='vertical':
            th_m = -np.arctan(dpp1 / dpp3)
            ph_m =  np.arcsin(dpp2)
        elif exp.detector["slit"]=='horizontal':
            ph_m =  np.arctan(dpp2 / dpp3)
            th_m = -np.arcsin(dpp1)          

        R_az0=np.array([   [np.cos(exp.az0), -np.sin(exp.az0), 0],\
                           [np.sin(exp.az0),  np.cos(exp.az0), 0],\
                           [0, 0, 1]])
        R_th0=np.array([   [ np.cos(exp.th0), 0, np.sin(exp.th0)],\
                           [0, 1, 0],\
                           [-np.sin(exp.th0), 0, np.cos(exp.th0)]])
        R_ph0=np.array([   [1, 0, 0],\
                           [0,  np.cos(exp.ph0), -np.sin(exp.ph0)],\
                           [0,  np.sin(exp.ph0),  np.cos(exp.ph0)]])
        R_offset = R_ph0 @ R_th0 @ R_az0
        kwarp=np.zeros((th_m.shape[1],3))
        d=np.array([[0,0,1]]).T
        if exp.detector["slit"]=='vertical':
            for i in range(th_m.shape[1]):
                R_th_m=np.array([   [ np.cos(th_m[0,i]), 0, np.sin(th_m[0,i])],\
                                    [0, 1, 0],\
                                    [-np.sin(th_m[0,i]), 0, np.cos(th_m[0,i])]])
                R_ph_m=np.array([   [1, 0, 0],\
                                    [0,  np.cos(ph_m[0,i]), -np.sin(ph_m[0,i])],\
                                    [0,  np.sin(ph_m[0,i]),  np.cos(ph_m[0,i])]])
                T=R_ph_m @ R_th_m @ R_offset
                kwarp[i,:] = np.linalg.solve(T, d).T
        elif exp.detector["slit"]=='horizontal':
            for i in range(th_m.shape[1]):
                R_th_m=np.array([   [ np.cos(th_m[0,i]), 0, np.sin(th_m[0,i])],\
                                    [0, 1, 0],\
                                    [-np.sin(th_m[0,i]), 0, np.cos(th_m[0,i])]])
                R_ph_m=np.array([   [1, 0, 0],\
                                    [0,  np.cos(ph_m[0,i]), -np.sin(ph_m[0,i])],\
                                    [0,  np.sin(ph_m[0,i]),  np.cos(ph_m[0,i])]])
                T=R_th_m @ R_ph_m @ R_offset
                kwarp[i,:] = np.linalg.solve(T, d).T
        K=np.sqrt(2*me*self.Ek*eV)/hbar*A0
        kx2 = K*kwarp[:,0]
        ky2 = K*kwarp[:,1]
        import matplotlib.gridspec as gridspec
        fig = plt.figure()
        gs = gridspec.GridSpec(1, 3)
        ax = fig.add_subplot(gs[0, 0])
        ax.pcolormesh(np.reshape(kx*A0, (len(self.th), len(self.ph))),\
                       np.reshape(ky*A0, (len(self.th), len(self.ph))),\
                       spec.specfun[0,:,:])
        ax = fig.add_subplot(gs[0, 1])
        ax.pcolormesh(np.reshape(th_m, (len(self.th), len(self.ph))),\
                       np.reshape(ph_m, (len(self.th), len(self.ph))),\
                       spec.specfun[0,:,:])
        ax = fig.add_subplot(gs[0, 2])
        ax.pcolormesh(np.reshape(kx2, (len(self.th), len(self.ph))),\
                       np.reshape(ky2, (len(self.th), len(self.ph))),\
                       spec.specfun[0,:,:])

    def Make_statistics(self, exp):
        r"""
        This function takes the ARPES intensity :math:`I(\theta,\phi, \omega)` and uses it as a probability distribution function to generate a measured spectrum of $N$ electrons. 
        
        *args*:

        - ``exp``: An object containing the experimental parameters. Defined via the ``aurelia_static_vars`` module.

        *Saved args*:

        - ``arpes.stats``: A numpy array containing the spectra generated by :math:`N_e` random electrons that has the same dimension as ``arpes.intensity``.
        - ``arpes.dstats``: A numpy array containing the spectra generated by :math:`N_e` random electrons that has the same dimension as ``arpes.domains``.
        
        """
        A = (self.intensity + self.bkgd)*self.response      
        # Define probability density vector
        p0 = A / np.max(np.max(A))     
        p = np.reshape(p0, [np.prod(p0.shape), 1])
        # Sample PDF
        c = np.cumsum(np.concatenate(([0], p.flatten())))  # turn PDF into bin edges
        c = c / c[-1]  # ensure cumulative is 1
        N, bins = np.histogram(np.random.rand(exp.Ne), c)  # generates flat random distribution and count number of elements within bin edges.
        stats=np.reshape(N, p0.shape)
        self.stats=stats
        if exp.detector["counting mode"] == "ADC":
            x=np.linspace(-1,1, round(self.intensity.shape[1]/100))
            mu=0
            sigma=x.max()/3
            ADC=np.random.rand()*norm.pdf(x, mu, sigma)
            if self.dimension == "sliceEk":                
                stats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=0, arr=stats)
                stats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=1, arr=stats)
            elif self.dimension == "slicekk":      
                if exp.detector["type"] == "HA":
                    stats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=1, arr=stats)
                elif exp.detector["type"] == "TOF":          
                    stats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=1, arr=stats)
                    stats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=2, arr=stats) 
            elif self.dimension == "cube":
                if exp.detector["type"] == "HA":
                    stats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=0, arr=stats)
                    stats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=1, arr=stats)
                elif exp.detector["type"] == "TOF":
                    stats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=1, arr=stats)
                    stats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=2, arr=stats)      
            self.stats=np.round(stats*(exp.Ne/np.sum(stats))*len(x)).astype(int)
        if hasattr(self, 'domain'):
            A2 = (self.domain + self.bkgd)*self.response
            p02 = A2 / np.max(np.max(A2))
            p2 = np.reshape(p02, [np.prod(p02.shape), 1])
            # Sample PDF
            c2 = np.cumsum(np.concatenate(([0], p2.flatten())))  # turn PDF into bin edges
            c2 = c2 / c2[-1]  # ensure cumulative is 1
            N2, bins = np.histogram(np.random.rand(exp.Ne), c2)
            dstats=np.reshape(N2, p02.shape)
            self.dstats=dstats            
            if exp.detector["counting mode"] == "ADC":
                if self.dimension == "sliceEk":                
                    dstats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=0, arr=dstats)
                    dstats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=1, arr=dstats)
                elif self.dimension == "slicekk":
                    if exp.detector["type"] == "HA":
                        dstats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=1, arr=dstats)
                    elif exp.detector["type"] == "TOF":
                        dstats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=1, arr=dstats)
                        dstats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=2, arr=dstats)
                elif self.dimension == "cube":
                    if exp.detector["type"] == "HA":
                        dstats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=0, arr=dstats)
                        dstats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=1, arr=dstats)
                    elif exp.detector["type"] == "TOF":
                        dstats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=1, arr=dstats)
                        dstats = np.apply_along_axis(lambda x: convolve(x, ADC,  mode='same'), axis=2, arr=dstats)
                self.dstats=np.round(dstats*(exp.Ne/np.sum(dstats))*len(x)).astype(int)

    def Crop_edges(self):
        """
        This function crops the edges of the simulation to remove artifacts.
        """
        if self.crop is False:
            edge=(1-1/self.spec.bands.edges)/2
            indth=round(edge*self.intensity.shape[1])
            self.th=self.th[indth:-indth]
            if self.dimension == "sliceEk":              
                self.stats = self.stats[ :, indth:-indth]
                self.intensity = self.intensity[ :, indth:-indth]            
                self.response = self.response[ :, indth:-indth]
                self.bkgd = self.bkgd[ :, indth:-indth]
                if hasattr(self, 'domain'):
                    self.domain = self.domain[ :, indth:-indth]
                    self.dstats=self.dstats[ :, indth:-indth]
            elif self.dimension != "sliceEk":
                indph=round(edge*self.intensity.shape[2])
                self.ph=self.ph[indph:-indph]            
                self.stats = self.stats[ :, indth:-indth, indph:-indph]
                self.intensity = self.intensity[ :, indth:-indth, indph:-indph]            
                self.response = self.response[ :, indth:-indth, indph:-indph]
                self.bkgd = self.bkgd[ :, indth:-indth, indph:-indph]
                if hasattr(self, 'domain'):
                    self.domain = self.domain[ :, indth:-indth, indph:-indph]
                    self.dstats=self.dstats[ :, indth:-indth, indph:-indph]
            self.crop = True
        else:
            print('Edges are already cropped.')
    def Make_quality_score(self, param = None):
        r"""
        This function provides a quality score for the spectra based on the metrics, feature sharpness, the number of electrons, the signal to background, and a total score.
        
        *args*:

        - ``param``: A dictionary of the form ``param = {"threshold": [], "penalty": [], "weight": []}``. The fields are:

            - ``param["threshold"]``: A numpy array of shape :math:`m \times 1` defining the
            score brackets where each penalty is incurred. Default: [0.9, 0.7, 0.5, 0.3].
            - ``param["penalty"]``: A numpy array of shape :math:`m \times 1` defining the penalty
            amount incurred in each score bracket. Default: [1, 2, 3, 4].
            - ``param["weight"]``: A numpy array of shape :math:`3 \times 1` defining the relative
            weights of penalties for each metric. Default: [1, 1, 1].

        *Saved args*:

        - ``arpes.score``, a dictionary with the following fields:

            - ``score["width"]``: Feature sharpness score, out of 1.
            - ``score["bkgd"]``: Signal-to-background score, out of 1.
            - ``score["counts"]``: Number of electrons score, out of 1.
            - ``score["final"]``: Total score, out of 10.
        """
        score = 10
        kB = 8.6196e-05
        if hasattr(self, 'domain'):
            p=(self.domain+self.bkgd)*self.response
        else:
            p=(self.intensity+self.bkgd)*self.response
        pbkgd=self.bkgd*self.response
        feature_score=np.sum(np.abs(np.diff(self.intensity)))/np.sum(self.intensity)
        spec=self.spec
        m=spec.mod
        if param is None:
            T=np.array([0.9, 0.7, 0.5, 0.3])
            penalty=[1, 2, 3, 4]
            weight = [1, 1, 1]
        else:
            T = param["threshold"]
            penalty = param["penalty"]      
            weight = param["weight"]       
        width_score = 1-np.sqrt((m.ER**2+(kB*m.Temp)**2+min(spec.ImS[0])**2))
        width_score = max([0, width_score])
        for i in range(len(T)-1):
            if width_score < T[i] and width_score >= T[i+1]:
                score -= penalty[i]*weight[0]
        bkgd_score = 1 - pbkgd.max()/p.max()
        for i in range(len(T)-1):
            if bkgd_score < T[i] and bkgd_score >= T[i+1]:
                score -= penalty[i]*weight[1]
        if bkgd_score>0.9:
            score += 1
        if feature_score < 0.013:
            score -= 4
        Ne_score = min([1, self.exp.Ne/1e5])
        for i in range(len(T)-1):
            if Ne_score < T[i] and Ne_score >= T[i+1]:
                score -= penalty[i]*weight[2]
        if Ne_score==1:
            score += 1
        if Ne_score+bkgd_score <=0.5:
            score -= 2
        final_score = max([0, score])
        final_score = min([final_score, 10])
        score={"feature": feature_score, "width": width_score, "bkgd": bkgd_score, "counts": Ne_score, "final": final_score}
        self.score=score
        print("feature score:", np.round(feature_score, 2))
        print("width score:", np.round(width_score, 2),"/1")
        print("bkgd score:", np.round(bkgd_score, 2),"/1")
        print("Ne score:", np.round(Ne_score, 2),"/1")
        print("total score:", np.round(final_score),"/10")
    def print_variables(self):
        """
        Provides a summary of variables used to calculate the measured arpes spectra.
        """
        print('ARPES dimension:', self.dimension)
        if self.dimension != 'cube':
            print('Slice const:', round(self.slice_const,2))
        print('th limits:', np.round(np.degrees(self.anglim[:,0])))
        if self.dimension != 'sliceEk':
            print('ph limits:', np.round(np.degrees(self.anglim[:,1])))
        print('hv:', round(self.exp.hv, 2),' eV')
        print('th0:', round(np.degrees(self.exp.th0), 2),\
              'ph0:', round(np.degrees(self.exp.ph0), 2),\
              'az0:', round(np.degrees(self.exp.az0), 2))   
        if hasattr(self,'stats'):
            print('Number of electrons:', self.exp.Ne)
            if "flatA" in self.exp.bkgd:
                print('Flat bkgd amplitude:', round(self.exp.bkgd["flatA"],3))
            if "shirA" in self.exp.bkgd:
                  print('Shirley bkgd amplitude:',round(self.exp.bkgd["shirA"],3)) 


                    

        

# %%

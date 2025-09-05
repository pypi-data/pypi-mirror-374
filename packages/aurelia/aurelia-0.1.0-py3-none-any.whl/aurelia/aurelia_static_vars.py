r"""

This module contains the static experimental parameters informing the ARPES simulation. It provides three main classes: ``modifier``, ``domain``, and ``experiment``.

``modifier``: Defines the electronic temperature of the Fermi-Dirac distribution and the resolution broadenings. It is used with the ``Spec`` object in the ``aurelia_arpes`` module.

``domains``: Defines and adds rotational and offset (flake) domains to the ARPES intensity.

``experiment``: Defines the photoemission experimental parameters and experimental artifacts, such as the photon energy, angular acceptance, number of collected electrons, the type of detector, detector responsivity, and background intensity/noise. 

"""

import numpy as np
from scipy.interpolate import griddata

class mod:
    r"""
    This function initializes the modifier object.

    *Optional args*:

    - ``temperature``: A float defining the electronic temperature. If not given, it is a random value between 10 and 350. (Lower values can be given but the number of points in the energy dimension (:math:`\omega`) the calculation must increase for it to be accurate, increasing computational time). 
    - ``resolution``: A python dictionary of the form ``resolution = {"ER":[],"kR":[] }``, where ``ER`` (``kR``) are floats defining the energy (momentum/angular) resolution of the setup, respectively.

    *Saved args*:

    - ``mod.Temp``: A float, the electronic temperature.
    - ``mod.ER``: A float, the energy resolution.
    - ``mod.kR``: A float, the momentum/angular resolution.
    
    """
    def __init__(self, temperature=None, resolution=None):
        if temperature == None:
            self.Temp=np.random.uniform(10,350)
        else:
            self.Temp=temperature
        if resolution == None:
            self.ER=np.random.rand()*0.25+0.001
            self.kR=np.random.rand()*0.02+0.005
        else:
            self.ER=resolution["ER"]
            self.kR=resolution["kR"]

class domain:
    r"""
    This function initializes the flake and rotational domains that may be present in the ARPES experiment

    *args*:

    - ``az``: A python dictionary specifying the rotational domains. It has the following fields:
        - ``az["Num"]``: An integer :math:`r` determining the number of rotational domains. If not specified, this number is chosen randomly on the interval [1, 3].

        - ``az["az"]``: A numpy array of dimension :math:`r \times 1`. Contains the azimuth angle of each rotational domain. If not specified, the elements are chosen randomly on the interval [-30, 30].

        - ``az["amp"]``: A numpy array of dimension :math:`r \times 1`.  Contains the relative intensity amplitude of each rotational domain. If not specified, the elements are chosen randomly on the interval [0, 1].

    - ``flake``: A python dictionary specifying the flake domains. It has the following fields:

        - ``flake["Num"]``: An integer :math:`f` determining the number of flake domains. If not specified, this number is chosen randomly on the interval [0, 5].

        - ``flake["th"]``: A numpy array of dimension :math:`f \times 1`. Contains the ``theta`` offset angle of each flake domain. If not specified, the elements are chosen randomly on the interval [-5, 5].

        - ``flake["ph"]``: A numpy array of dimension :math:`f \times 1`. Contains the ``phi`` offset angle of each flake domain. If not specified, the elements are chosen randomly on the interval [-5, 5].

        - ``flake["amp"]``: A numpy array of dimension :math:`f \times 1`. Contains the relative intensity amplitude of each flake domain. If not specified, the elements are chosen randomly on the interval [0, 1].

    *Saved args*:
    
    - ``domain.az``

    - ``domain.flake``

    """
    def __init__(self, az=None, flake=None):
        # Make it really static when exposing inputs
        #Rotational domain parameters
        self.type=[]
        if az is None:
            az = {"Num": np.random.randint(1,3)}
            az["az"] = np.random.uniform(-30,30,az["Num"])
            az["amp"] = np.random.rand(az["Num"])
        else:
            if "Num" not in az:
                az["Num"] = np.random.randint(1,len(az["az"]))
            if "az" not in az:
                az["az"] = np.random.uniform(-30,30,az["Num"])
        self.az=az
        #Flake offset domain parameters
        if flake is None:
            flake = {"Num": np.random.randint(0,5)}
            flake["th"] = np.deg2rad(np.random.uniform(-5,5, flake["Num"]))
            flake["ph"] = np.deg2rad(np.random.uniform(-5,5, flake["Num"]))
            flake["amp"] = np.random.rand(flake["Num"])
        else:
            if "Num" not in flake:
                flake["Num"] = len(flake["th"])
            if "th" not in flake:
                flake["th"] = np.deg2rad(np.random.uniform(-5,5, flake["Num"]))
            if "ph" not in flake:
                flake["ph"] = np.deg2rad(np.random.uniform(-5,5, flake["Num"]))
            if "amp" not in flake:
                flake["amp"] = np.random.rand(flake["Num"])
        self.flake=flake
    def Make_domain_rot(self, spec):
        r"""
        This function creates rotational domains in the spectra. 
        Computationally, this is fastest by rotating the k-path, interpolating the bands, addign them to Band.bands, and calculating the new spectral intensity.

        *args*:

        - spec: An object containing the spectral intensity. Generated from the ``aurelia_arpes`` module.

        *Saved args*:

        - ``domain.type``: A string ``"rot"`` indicating a rotational domain is added.
        - ``spec.domain_info``: The object domain, which contains the parameters specifying the rotational domain.

        *Returned args*:
        - ``bands``: An object defining the bandstructure. Generated from the aurelia_arpes module. The updated bands contain the rotated bands.
        - ``spec``: An object defining the spectral intensity. Generated from the aurelia_arpes module. The updated spectra contains the self-energy and matrix elements needed to calculate the new spectral intensity.
             
        """
        bands=spec.bands
        kx = bands.kpath[:, 0]
        ky = bands.kpath[:, 1]
        for i in range(self.az["Num"]):
            krot = np.zeros((len(kx), 2))
            krot[:, 0] = np.cos(np.deg2rad(self.az["az"][i])) * kx - np.sin(np.deg2rad(self.az["az"][i])) * ky
            krot[:, 1] = np.sin(np.deg2rad(self.az["az"][i])) * kx + np.cos(np.deg2rad(self.az["az"][i])) * ky
            Bands_r = griddata(krot, bands.bands[:,0:bands.Nbands], (kx, ky), method='nearest')
            M_r = griddata(krot, spec.matrix_elements[:,0:bands.Nbands], (kx, ky), method='nearest')
            ReS_r = spec.ReS[:,0:bands.Nbands]
            ImS_r = spec.ImS[:,0:bands.Nbands]
            bands.bands = np.concatenate((bands.bands, Bands_r), axis=1)
            spec.matrix_elements = np.concatenate((spec.matrix_elements, M_r), axis=1)
            spec.ReS = np.concatenate((spec.ReS, ReS_r), axis=1)
            spec.ImS = np.concatenate((spec.ImS, ImS_r), axis=1)
            spec.domain = np.hstack((spec.domain, self.az["amp"][i]* np.ones((1,bands.Nbands))))
            self.type=self.type+['rot']
            spec.domain_info=self
        return(bands, spec)
    
    def Rmv_domain_rot(self, spec):
        """
        This function removes the rotational domains by removing the appended values from the following fields of the object ``spec``:

        - ``Bands.bands``

        - ``spec.matrix_elements``

        - ``spec.ReS``

        - ``spec.ImS``

        - ``spec.domain``

        - ``domain.type``: The string ``"rot"`` is removed

        *Returned args*:

        - - ``bands``: An object defining the bandstructure. Generated from the aurelia_arpes module. The updated bands contain the rotated bands.
        - ``spec``: An object defining the spectral intensity. Generated from the aurelia_arpes module. The updated spectra contains the self-energy and matrix elements needed to calculate the new spectral intensity.

        """
        bands=spec.bands
        bands.bands=bands.bands[:,0:bands.Nbands]
        spec.bands=bands
        spec.matrix_elements=spec.matrix_elements[:,0:bands.Nbands]
        spec.domain=spec.domain[:,0:bands.Nbands]
        spec.ReS=spec.ReS[:,0:bands.Nbands]
        spec.ImS=spec.ImS[:,0:bands.Nbands]

        del spec.domain_info
        self.type.remove('rot')
        return(bands, spec)
    
    def Make_domain_offset(self, arpes, speed='fast'):
        r"""
        This function creates domains originating from sample flakes at different offset angles than the dominant domain. 
        
        *args*: 
        - ``arpes``: An object containing the simulated ARPES intensity and associated parameters. 
        
        *Optional args*:

        - ``speed``: A string that takes two inputs, ``"fast"`` or ``"slow"``. Defaults to ``"fast"``.
        
            - Slow mode: The most accurate way of creating offset flakes is changing :math:`\theta_0`, :math:`\phi_0`, and using ``arpes.Make_angle_conv(domain)`` to calculate the spectra for each domain. However, the interpolation during momentum-to-angle conversion is slow. 
            - Fast mode: Less accurate. We can simply take the spectrum and shift it in :math:`\theta_m` and :math:`\phi_m` by :math:`\theta_0` and :math:`\phi_0`. 
        *Saved args*:

        - ``domain.type``: A string ``"offset"`` indicating a flake domain is added.
        - ``spec.domain_info``: The object domain, which contains the parameters specifying the rotational domain.
        - ``arpes.domain``: Contains the intensities from the domains that are calculated.

        *Returned args*:

        - ``arpes``: An object containing the simulated ARPES intensity and associated parameters. 
        
        """

        if speed == 'fast':
            if arpes.dimension != 'sliceEk':
                th = arpes.th
                ph = arpes.ph
                A_offset = np.zeros((arpes.intensity.shape))
                for i in range (self.flake["Num"]):
                    indth = np.where(th >= min(th) + abs(self.flake["th"][i]))[0][0] - 1
                    indph = np.where(ph >= min(ph) + abs(self.flake["ph"][i]))[0][0] - 1
                    A_offset += self.flake["amp"][i]*(np.roll(np.roll(arpes.intensity,\
                            -1*np.sign(self.flake["th"][i]).astype(int)*indth, axis=1), \
                            -1*np.sign(self.flake["ph"][i]).astype(int)*indph, axis=2))
            elif arpes.dimension == 'sliceEk':
                th = arpes.th
                A_offset = np.zeros((arpes.intensity.shape))
                for i in range (self.flake["Num"]):
                    indth = np.where(th >= min(th) + abs(self.flake["th"][i]))[0][0] - 1
                    A_offset += self.flake["amp"][i]*np.roll(arpes.intensity, \
                        -1*np.sign(self.flake["th"][i]).astype(int)*indth, axis=1)
        elif speed == 'slow':       
            if arpes.dimension != 'cube':
                A_offset = np.zeros((arpes.intensity.shape))
                for i in range(self.flake["Num"]):
                    dom={"th0":self.flake["th"][i], "ph0":self.flake["ph"][i]}
                    A_out=arpes.Make_angle_conv(const=arpes.slice_const, domain=dom)
                    A_offset += self.flake["amp"][i]*A_out
            elif arpes.dimension == 'cube':
                A_offset = np.zeros((arpes.intensity.shape))
                for i in range(self.flake["Num"]):
                    dom={"th0":self.flake["th"][i], "ph0":self.flake["ph"][i]}
                    A_out=arpes.Make_angle_conv(domain=dom)
                    A_offset += self.flake["amp"][i]*A_out         
        self.type=self.type+['offset']
        arpes.domain=arpes.intensity +A_offset          
        arpes.domain_info=self  
        print('Domains included:', self.type)
        if 'offset' in self.type:
            print('Number of flakes:', self.flake["Num"])
            print('flake th0:' , np.round(np.degrees(self.flake["th"]),2))
            print('flake ph0:' , np.round(np.degrees(self.flake["ph"]),2))
            print('flake amp:' , np.round(self.flake["amp"],2))
        if 'rot' in self.type:
            print('Number of rotational domains:', self.az["Num"])
            print('rotational angle:' , self.az["az"])     
        return(arpes)
    
    def Rmv_domain_offset(self, arpes):
        """
        This function removes the rotational domains by removing the fields of the object ``arpes``:
        
        - ``arpes.domain``
        - ``arpes.domain_info``
        - ``domain.type``: The string ``"offset"`` is removed.

        *Returned args*:

        - ``arpes``: An object containing the simulated ARPES intensity and associated parameters.
        """
        if hasattr(arpes, 'domain')==True:
            del arpes.domain
            del arpes.domain_info
            self.type.remove('offset')
        elif hasattr(arpes, 'domain')==False:
            print('Flake domains do not exist')
        return(arpes)

class experiment:      
    r"""
    This function initializes the ``experiment`` object used to convert ``Spec`` to ``ARPES`` in the ``aurelia_arpes`` module.

    *args*:

        - ``spec``: An object containing the spectral intensity calculated from the dispersion.

    *Optional args*:

    - ``angles``: A python dictionary defining the offset angles of the primary flake.

        - To specify the angles, input a dictionary of the form ``angles={"az0": [], "th0": [], "ph0": []}``.  
        - To set all offset angles to zero, input ``angles = "zero"``.  
        - If no input is given, the offset angles ``th0`` and ``ph0`` are randomly determined on the interval [-10, 10], and ``az0`` is randomly selected on [0, 360].

    - ``hv``: A float specifying the photon energy of the light that induces the photoemission process (in eV). If no input is given, a randomized default is calculated such that the momenta specified in Bands.klim are photoemitted.

    - ``Ne``: An integer specifying the number of electrons collected. The default is randomly determined depending on ``spec.dimension``:

        - ``"slicekk"``: :math:`N_e \in [10^4, 10^6]`
        - ``"sliceEk"``: :math:`N_e \in [10^4, 10^7]`
        - ``"cube"``: :math:`N_e \in [10^5, 10^8]`

    - ``bkgd``: A dictionary specifying the type and strength of the background intensity. Flat, Shirley, and polynomial background are given by default.

        - Flat background: ``bkgd["type"] = "flat"``. Optionally specify ``bkgd["flatA"]``, a float defining the amplitude of the flat background relative to the maximum intensity. Default random [0.01, 0.21].
        - Shirley background: ``bkgd["type"] = "Shir"``. Optionally specify ``bkgd["ShirA"]``, a float defining the amplitude of Shirley background. Default random [0.01, 0.11].
        - Polynomial background: ``bkgd["type"] = "poly"``. Optionally specify ``bkgd["polyA"]``, a  float defining the amplitude of polynomial background. Default random [0.01, 0.11], and ``bkgd["polyOrder"]`` Integer polynomial order. Default random [0, 5].

    - ``detector``: A dictionary specifying the detector parameters. Has the following fields:

        - ``detector["response"]``: String determining response type. Options:

            - ``"flat"``: Uniform response
            - ``"center"``: Higher response at center.  

                - ```detector["sensitivity"]``: Float difference between center and edge (used only if ``response="center"``; default 0).

        - ``detector["slit"]``: String specifying slit orientation. Options: ``"horizontal"``, ``"vertical"``.
        - ``detector["counting mode"]``: String specifying counting mode. Options:

            - ``"ADC"``: Lights up multiple pixels per electron event.
            - ``"PC"``: Lights up only one electron per pixel; better for low counts.

    Outputs of the function:

    - ``exp.az0``: Azimuth offset angle (float)
    - ``exp.th0``: Theta offset angle (float)
    - ``exp.ph0``: Phi offset angle (float)
    - ``exp.hv``: Photon energy (float)
    - ``exp.Ne``: Number of electrons collected (int)
    - ``exp.bkgd``: Background parameters (dictionary)
    - ``exp.detector``: Detector parameters (dictionary)

    """
    def __init__(self, spec, angles=None, hv=None, bkgd=None, Ne=None, detector=None):       
        ## parameters for k to angle conversion
        self.workfun=4+np.random.rand()
        if angles==None:
            if spec.dimension == 'sliceEk':
                self.az0=0
                self.ph0=0
                self.th0=np.radians(np.random.uniform(-10,10))
            elif spec.dimension != 'sliceEk':
                self.az0=np.radians(np.random.uniform(0,360))
                self.th0=np.radians(np.random.uniform(-10,10))
                self.ph0=np.radians(np.random.uniform(-10,10))
        elif angles=='zero':
            self.az0=0
            self.th0=0
            self.ph0=0
        else:
            if "az0" in angles:
                self.az0=angles["az0"]
            else:
                self.az0=0
            if "th0" in angles:
                self.th0=angles["th0"]
            else:
                self.th0=0
            if "ph0" in angles:
                self.ph0=angles["ph0"]
            else:
                self.ph0=0
        if hv == None:
            self.hv=7.634*spec.bands.klim.max()**2-min(spec.Omega)+self.workfun\
            +5*np.random.rand()+5
        else: 
            self.hv=hv
        if bkgd == None:
            bkgd={"type": ['flat','Shirley']}
            if spec.dimension == 'slicekk':      
                bkgd["flatA"]=np.random.rand()*0.2+0.01
                bkgd["shirA"]=0      
            elif spec.dimension == 'sliceEk':
                bkgd["flatA"]=np.random.rand()*0.2+0.01
                bkgd["shirA"]=np.random.rand()*0.1+0.01
            elif spec.dimension == 'cube':
                bkgd["flatA"]=np.random.rand()*0.1+0.01
                bkgd["shirA"]=np.random.rand()*0.05+0.01
        elif bkgd == 'zero':
            bkgd["type"]='zero'
            bkgd["flatA"]=0
            bkgd["shirA"]=0
        else:
            if "flat" in bkgd["type"]:
                if "flatA" not in bkgd: 
                    bkgd["flatA"]=np.random.rand()*0.2+0.01
            if "Shirley" in bkgd["type"]:
                if "shirA" not in bkgd:
                    bkgd["shirA"]=np.random.rand()*0.1+0.01
            if "poly" in bkgd["type"]:
                if "polyOrder" not in bkgd:
                    bkgd["polyOrder"]=np.random.randint(5)
                if "polyA" not in bkgd:
                    bkgd["polyA"]=np.random.rand()*0.1+0.01
        self.bkgd=bkgd
        self.bkgd["type"]=bkgd["type"]

        if detector is None:
            detector={"response": 'flat', "slit": 'horizontal', "counting mode": "PC"}
        self.detector=detector

        if Ne is None:
            if spec.dimension == 'slicekk':      
                self.Ne=np.random.randint(10**4, 10**6)            
            elif spec.dimension == 'sliceEk':
                self.Ne=np.random.randint(10**4, 10**7)    
            elif spec.dimension == 'cube':
                self.Ne=np.random.randint(10**5, 10**6)    
        else:
            self.Ne=int(Ne)

    def Make_bkgd(self, arpes):
        """
        This function adds various types of background intensity to the ARPES spectra simulation.

        *args*:

        - ``arpes``: An object defining the photoemission intensity. Calculated by the ``aurelia_arpes`` module.

        *Saved args*:

        - ``arpes.bkgd``: Overwrites the default value. A numpy array with the same dimensions as ``arpes.intensity`` containing the background.
        """

        Amp = np.max(arpes.intensity)
        bkgd=np.zeros(arpes.intensity.shape)
        if 'flat' in self.bkgd["type"]:
            bkgd = bkgd + self.bkgd["flatA"] * Amp * np.ones(arpes.intensity.shape) 
        if 'Shirley' in self.bkgd["type"]:
            if arpes.dimension == 'slicekk':
                print('Shirley background requires energy axis, does not work for slicekk, setting to zero')
                Shir = np.zeros(arpes.intensity.shape)
            else:
                A=arpes.intensity          
                A=np.reshape(A, (A.shape[0], int(np.prod(A.shape)/A.shape[0])))
                Shir = np.zeros(A.shape)
                for i in range(len(arpes.Ek)-1):
                    Shir[i, :] = np.sum(A[i:-1,:], axis=0)
                Shir = self.bkgd["shirA"] * Amp * Shir /np.max(Shir)
                Shir = np.reshape(Shir, arpes.intensity.shape)                                
            bkgd = bkgd + Shir
        if 'poly' in self.bkgd["type"]:
            coeffs = np.random.randn(self.bkgd["polyOrder"]+1,self.bkgd["polyOrder"]+1) # generate random coefficients
            if arpes.dimension == 'slicekk':
                x, y = np.meshgrid(arpes.ph, arpes.th)
            elif arpes.dimension == 'sliceEk':
                x, y = np.meshgrid(arpes.th, arpes.Ek)
            elif arpes.dimension == 'cube':
                x, y = np.meshgrid(arpes.ph, arpes.th)
            Poly =  np.polynomial.polynomial.polyval2d(x, y, coeffs)
            Poly = self.bkgd["polyA"] * Amp * (Poly-np.min(Poly))/np.abs(np.max(Poly))
            if arpes.dimension =='cube':
                Poly=np.stack([Poly]*arpes.Ek.shape[0], axis=0)
            bkgd = bkgd + Poly
        arpes.bkgd=bkgd
        return(arpes)
    
    def Make_detector_responsivity(self, arpes):
        """
        The function creates the detector responsivity for the ARPES spectra simulation
        
        *args*:

        - ``arpes``: An object defining the photoemission intensity. Calculated by the ``aurelia_arpes`` module.

        *Saved args*:

        - ``arpes.response``: Overwrites the default value. A numpy array with the same dimensions as ``arpes.intensity`` containing the detector response.
        
        """
        if self.detector["response"] == 'flat':
            response= np.ones(arpes.intensity.shape)
        elif self.detector["response"] == 'center':
            r_diff = self.detector["sensitivity"]
            y = -(arpes.th-np.mean(arpes.th))**2
            y = (y-np.min(y))/max(abs(y))*r_diff+(1-r_diff)
            y = np.reshape(y,(-1,1)).T
            if self.detector["type"] =='HA':
                if arpes.dimension == 'slicekk':
                    y2=np.reshape(np.ones(arpes.ph.shape),(-1,1))
                    response= np.stack([np.matmul(y2, y).T]*1, axis=0)                    
                elif arpes.dimension != 'slicekk':
                    y2=-(arpes.Ek-np.mean(arpes.Ek))**2
                    y2=(y2-np.min(y2))/max(abs(y2))*r_diff+(1-r_diff)
                    y2=np.reshape(y2,(-1,1))
                    if arpes.dimension == 'sliceEk':
                        response= np.matmul(y2, y)
                    if arpes.dimension == 'cube':
                        dummy=np.matmul(y2,y)
                        response=np.stack([dummy]*arpes.ph.shape[0], axis=2)
            if self.detector["type"]=='TOF':
                if arpes.dimension == 'sliceEk':
                    y2=np.reshape(np.ones(arpes.Ek.shape),(-1,1))
                    response= np.matmul(y2, y)
                elif arpes.dimension != 'sliceEk':
                    y2=-(arpes.ph-np.mean(arpes.ph))**2
                    y2=(y2-np.min(y))/max(abs(y))*r_diff+(1-r_diff)
                    y2=np.reshape(y2,(-1,1))
                    if arpes.dimension == 'slicekk':
                        response = np.stack([np.matmul(y2, y).T]*1, axis=0)
                    if arpes.dimension == 'cube':
                        response = np.stack([np.matmul(y2, y).T]*arpes.Ek.shape[0], axis=0)           
        arpes.response=response
        return(arpes)
    
        
        



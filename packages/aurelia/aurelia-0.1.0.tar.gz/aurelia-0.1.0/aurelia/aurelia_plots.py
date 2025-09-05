import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

class show_spectra:
    """
    This object contains plotting functions that allows one to check the status of the calculation. There are no outputs to these functions, and they do not change the calculation at all.
    """
    def __init__(self):
        pass
    def Make_spec_plot(spec, constE=None):
        """
        This function plots the values in ``spec.specfun`` as well as the dispersion in ``bands.bands``. 
        
        *args*:

        - spec: An object from the ``aurelia_arpes`` module, which can have three dimensions options: 
        ``"cube"`, ``"slicekk"`, and ``"sliceEk"``. If the dimension is ``"cube"``, one can specify the constant energy cut to plot. 
        
        *Optional args*:

        - ``constE``: A float. Specifies the constant energy cut to show (in binding energy). By default, the Fermi surface is chosen.   
        """
        B=spec.bands
        if spec.dimension=='sliceEk':
            # Display the spectrogram with imagesc
            KX, OM = np.meshgrid(spec.kax, spec.Omega)
            plt.pcolormesh(KX, OM, spec.specfun, cmap='gray_r')
            plt.colorbar()
            # Plot the bands with red dashed line
            plt.plot(B.kpath[spec.slice_ind,0], B.bands[spec.slice_ind,:], 'r--', linewidth=1)
            plt.axhline(y=0, linestyle='--', linewidth=1, color='black')
            plt.ylabel(r'$E-E_F$ (eV)')
            plt.xlabel(r'$k_x$ ($\AA ^{-1}$)')
            plt.title('Spec. Fun.')
        
        elif spec.dimension=='slicekk':
            KY, KX = np.meshgrid(spec.kay, spec.kax)
            plt.pcolormesh(KX, KY, spec.specfun[0,:,:], cmap='gray_r')
            plt.colorbar()
            plt.xlabel(r'$k_x$ ($\AA ^{-1}$)')
            plt.ylabel(r'$k_y$ ($\AA ^{-1}$)')
            plt.title('Spec. Fun.')

        elif spec.dimension=='cube':
            Evk = B.bands.reshape((B.Npts[1], B.Npts[0], B.bands.shape[1]))

            fig = plt.figure()
            gs = gridspec.GridSpec(3, 3)
            ax = fig.add_subplot(gs[1:3, 2:3])
            OM, KY=np.meshgrid(spec.Omega, spec.kay)
            ax.pcolormesh(OM, KY, spec.specfun[:,round(B.Npts[0]/2),:].T, cmap='gray_r')
            ax.plot(Evk[:,round(B.Npts[0]/2),:], spec.kay, 'r--', linewidth=1)
            k = plt.axvline(0, linestyle='--', linewidth=1, color='black')
            plt.xlabel(r'$E-E_F$ (eV)')

            ax = fig.add_subplot(gs[0, 0:2])
            KX,OM=np.meshgrid(spec.kax, spec.Omega)
            ax.pcolormesh(KX, OM, spec.specfun[:,:,round(B.Npts[1]/2)], cmap='gray_r')
            ax.plot(spec.kax, Evk[round(B.Npts[1]/2),:,:], 'r--', linewidth=1)
            plt.axhline(y=0, linestyle='--', linewidth=1, color='black')
            plt.ylabel(r'$E-E_F$ (eV)')

            ax = fig.add_subplot(gs[1:3, 0:2])
            if constE is None:
                indEF = np.where(spec.Omega >= 0)[0][0]
            else:
                indEF = np.where(spec.Omega >= constE)[0][0]
            KY, KX=np.meshgrid(spec.kay, spec.kax)
            ax.pcolormesh(KX, KY, spec.specfun[indEF,:,:], cmap='gray_r')
            plt.axhline(0, linestyle='--', linewidth=1, color='red')
            plt.axvline(0, linestyle='--', linewidth=1, color='red')
            plt.xlabel(r'$k_x$ ($\AA ^{-1}$)')
            plt.ylabel(r'$k_y$ ($\AA ^{-1}$)')
        # Show the plot
        plt.show()

    def Make_arpes_plot(arpes, exp):
        r"""
        This function plots the values in ``arpes.intensity``. 
        The offset angles :math:`\theta_0`, :math:`\phi_0`, and :math:`\alpha_0` defined in the object ``exp`` are also shown by red lines.
        
        *args*:

        - ``arpes``: An object from the ``aurelia_arpes`` module, which can have three dimensions options: 
        ``"cube"`, ``"slicekk"`, and ``"sliceEk"``. If the dimension is ``"cube"``, slices are plotted. By default, the Fermi surface is chosen, along with mean values of :math:`\theta` and :math:`\phi` axes.
        
        - ``exp``: An object from the ``aurelia_static_vars`` module.
        """
        B=arpes.spec.bands
        if arpes.dimension=='sliceEk':
            indEF = np.where(arpes.spec.Omega >= 0)[0][0]
            TH, EK = np.meshgrid(np.degrees(arpes.th), arpes.Ek)
            plt.pcolormesh(TH, EK, arpes.intensity, cmap='gray_r')
            plt.colorbar()
            plt.axhline(y=arpes.Ek[indEF], linestyle='--', linewidth=1, color='black')
            plt.axvline(x=-np.rad2deg(exp.th0), linestyle='--', linewidth=1, color='black')
            plt.ylabel(r'$E_k$ (eV)')
            plt.xlabel(r'$\theta$ (deg)')
            plt.title('ARPES')
        elif arpes.dimension=='slicekk':
            PH, TH = np.degrees(np.meshgrid(arpes.ph, arpes.th))
            th=2*np.degrees(arpes.th)
            th0 = np.degrees(exp.th0)
            ph0 = np.degrees(exp.ph0)
            az0 = exp.az0
            plt.pcolormesh(TH, PH, arpes.intensity[0,:,:], cmap='gray_r')
            plt.axhline(y=-np.rad2deg(exp.ph0), linestyle='--', linewidth=1, color='red')
            plt.axvline(x=-np.rad2deg(exp.th0), linestyle='--', linewidth=1, color='red')
            plt.plot(th-th0,-np.sin(az0)/np.cos(az0)*th-ph0, 'b-', linewidth=1)
            plt.plot(th-th0, np.cos(az0)/np.sin(az0)*th-ph0, 'b-', linewidth=1)
            plt.colorbar()
            plt.xlim(TH.min(), TH.max())
            plt.ylim(PH.min(), PH.max())
            plt.title('ARPES')
            plt.xlabel(r'$\theta$ (deg)')
            plt.ylabel(r'$\phi$ (deg)')
        elif arpes.dimension=='cube':
            fig = plt.figure()
            gs = gridspec.GridSpec(3, 3)
            ax = fig.add_subplot(gs[1:3, 2:3])
            EK, PH=np.meshgrid(arpes.Ek, np.degrees(arpes.ph))
            ax.pcolormesh(EK, PH, arpes.intensity[:,round(B.Npts[0]/2),:].T, cmap='gray_r')
            plt.axhline(y=np.rad2deg(exp.ph0), linestyle='--', linewidth=1, color='red')
            plt.axis('tight')
            plt.ylim(PH.min(), PH.max())
            plt.set_cmap('gray_r')
            plt.ylabel(r'$E_k$ (eV)')

            ax = fig.add_subplot(gs[0, 0:2])
            TH,EK=np.meshgrid(np.degrees(arpes.th), arpes.Ek)
            ax.pcolormesh(TH, EK, arpes.intensity[:,:,round(B.Npts[1]/2)], cmap='gray_r')
            ax.axvline(x=-np.rad2deg(exp.th0), linestyle='--', linewidth=1, color='red')
            plt.set_cmap('gray_r')
            plt.xlabel(r'$E_k$ (eV)')
            plt.xlim(TH.min(), TH.max())

            ax = fig.add_subplot(gs[1:3, 0:2])
            indEF = np.where(arpes.spec.Omega >= 0)[0][0]
            PH, TH=np.degrees(np.meshgrid(arpes.ph, arpes.th))
            th=2*np.degrees(arpes.th)
            th0 = np.degrees(exp.th0)
            ph0 = np.degrees(exp.ph0)
            az0 = exp.az0
            ax.pcolormesh(TH, PH, arpes.intensity[indEF,:,:], cmap='gray_r')
            plt.xlim(TH.min(), TH.max())
            plt.ylim(PH.min(), PH.max())
            plt.axhline(y=-np.rad2deg(exp.ph0), linestyle='--', linewidth=1, color='red')
            plt.axvline(x=-np.rad2deg(exp.th0), linestyle='--', linewidth=1, color='red')
            ax.plot(th-th0,-np.sin(az0)/np.cos(az0)*th-ph0, 'b-', linewidth=1)
            ax.plot(th-th0, np.cos(az0)/np.sin(az0)*th-ph0, 'b-', linewidth=1)
            plt.xlabel(r'$\theta$ (deg)')
            plt.ylabel(r'$\phi$ (deg)')
        # Show the plot
        plt.show()

    def Make_flake_plot(arpes, exp, domain):
        r"""
        This function plots the values in ``arpes.intensity`` and ``arpes.domains``.
        The offset angles :math:`\theta_0`, :math:`\phi_0`, and :math:`\alpha_0` defined
        by both the experiment object ``exp`` and the domain object ``domain`` are
        shown as red lines to verify correctness.

        If the calculation dimension is ``"cube"``, slices must be chosen for plotting.
        By default, the Fermi surface is selected along with the mean values of
        ``arpes.th`` and ``arpes.ph``.

        *args*:

        - ``arpes``: An object from the ``aurelia_arpes`` module, which can have three dimensions options: 
        ``"cube"`, ``"slicekk"`, and ``"sliceEk"``. If the dimension is ``"cube"``, slices are plotted. By default, the Fermi surface is chosen, along with mean values of :math:`\theta` and :math:`\phi` axes.
        
        - ``exp``: An object from the ``aurelia_static_vars`` module.
        
        - ``domain``: An object from the ``aurelia_static_vars`` module.

        """
        B=arpes.spec.bands
        if arpes.dimension=='sliceEk':
            fig = plt.figure()
            TH, EK = np.meshgrid(np.degrees(arpes.th), arpes.Ek)
            indEF = np.where(arpes.spec.Omega >= 0)[0][0]
            gs = gridspec.GridSpec(1, 2)
            ax = fig.add_subplot(gs[0,0])
            ax.pcolormesh(TH, EK, arpes.dintensity, cmap='gray_r')
            plt.axhline(y=arpes.Ek[indEF], linestyle='--', linewidth=1, color='black')
            plt.axvline(x=-np.rad2deg(exp.th0), linestyle='--', linewidth=1, color='black')
            plt.ylabel(r'$E_k$ (eV)')
            plt.xlabel(r'$\theta$ (deg)')
            plt.title('ARPES')

            ax = fig.add_subplot(gs[0,1])    
            ax.pcolormesh(TH, EK, arpes.domain, cmap='gray_r')
            plt.axhline(y=arpes.Ek[indEF], linestyle='--', linewidth=1, color='black')
            plt.axvline(x=-np.rad2deg(exp.th0), linestyle='--', linewidth=1, color='black')
            plt.ylabel(r'$E_k$ (eV)')
            plt.xlabel(r'$\theta$ (deg)')
            plt.title('ARPES + flakes')
            for i in range(domain.flake_N):
                plt.axvline(x=np.rad2deg(-exp.th0-domain.flake_th[i]), linestyle='--', linewidth=1, color='green')
            # Add axis labels and title
            plt.ylabel(r'$E_k$ (eV)')
            plt.xlabel(r'$\theta$ (deg)')
        elif arpes.dimension=='slicekk':
            fig = plt.figure()
            PH, TH = np.degrees(np.meshgrid(arpes.ph, arpes.th))
            th=np.degrees(arpes.th)
            gs = gridspec.GridSpec(1, 2)
            ax = fig.add_subplot(gs[0,0])
            ax.pcolormesh(TH, PH, arpes.dintensity[0,:,:], cmap='gray_r')
            plt.axhline(y=-np.rad2deg(exp.ph0), linestyle='--', linewidth=1, color='red')
            plt.axvline(x=-np.rad2deg(exp.th0), linestyle='--', linewidth=1, color='red')
            plt.plot(th-np.rad2deg(exp.th0),  np.sin(exp.az0)/np.cos(exp.az0)*th-np.rad2deg(exp.ph0), 'r-', linewidth=1)
            plt.plot(th-np.rad2deg(exp.th0), -np.cos(exp.az0)/np.sin(exp.az0)*th-np.rad2deg(exp.ph0), 'r-', linewidth=1)
            plt.colorbar()
            plt.xlim(TH.min(), TH.max())
            plt.ylim(PH.min(), PH.max())
            plt.title('ARPES')
            plt.xlabel(r'$\theta$ (deg)')
            plt.ylabel(r'$\phi$ (deg)')
            ax = fig.add_subplot(gs[0,1])
            ax.pcolormesh(TH, PH, arpes.domain[0,:,:], cmap='gray_r')
            plt.axhline(y=-np.rad2deg(exp.ph0), linestyle='--', linewidth=1, color='red')
            plt.axvline(x=-np.rad2deg(exp.th0), linestyle='--', linewidth=1, color='red')
            plt.plot(th-np.rad2deg(exp.th0),  np.sin(exp.az0)/np.cos(exp.az0)*th-np.rad2deg(exp.ph0), 'r-', linewidth=1)
            plt.plot(th-np.rad2deg(exp.th0), -np.cos(exp.az0)/np.sin(exp.az0)*th-np.rad2deg(exp.ph0), 'r-', linewidth=1)
            for i in range(domain.flake_N):
                plt.axvline(x=np.rad2deg(-exp.th0-domain.flake_th[i]), linestyle='--', linewidth=1, color='green')
                plt.axhline(y=np.rad2deg(-exp.ph0-domain.flake_ph[i]), linestyle='--', linewidth=1, color='green')
            plt.xlim(TH.min(), TH.max())
            plt.ylim(PH.min(), PH.max())
            plt.title('ARPES + flakes')
            plt.xlabel(r'$\theta$ (deg)')
            plt.ylabel(r'$\phi$ (deg)')
        elif arpes.dimension=='cube':
            fig = plt.figure()
            gs = gridspec.GridSpec(3, 3)
            ax = fig.add_subplot(gs[1:3, 2:3])
            EK, PH=np.meshgrid(arpes.Ek, np.degrees(arpes.ph))
            ax.pcolormesh(EK, PH, arpes.domain[:,round(B.Npts[0]/2),:].T, cmap='gray_r')
            plt.axhline(y=np.rad2deg(exp.ph0), linestyle='--', linewidth=1, color='red')
            for i in range(domain.flake_N):
                plt.axhline(y=np.rad2deg(-exp.ph0-domain.flake_ph[i]), linestyle='--', linewidth=1, color='green')
            plt.axis('tight')
            plt.ylim(PH.min(), PH.max())
            plt.set_cmap('gray_r')
            plt.xlabel(r'$E_k$ (eV)')
           
            ax = fig.add_subplot(gs[0, 0:2])
            TH,EK=np.meshgrid(np.degrees(arpes.th), arpes.Ek)
            ax.pcolormesh(TH, EK, arpes.domain[:,:,round(B.Npts[1]/2)], cmap='gray_r')
            ax.axvline(x=-np.rad2deg(exp.th0), linestyle='--', linewidth=1, color='red')
            for i in range(domain.flake_N):
                plt.axvline(x=np.rad2deg(-exp.th0-domain.flake_th[i]), linestyle='--', linewidth=1, color='green')
            plt.xlabel(r'$E_k$ (eV)')
            plt.xlim(TH.min(), TH.max())
        
            ax = fig.add_subplot(gs[1:3, 0:2])
            indEF = np.where(arpes.spec.Omega >= 0)[0][0]
            PH, TH=np.degrees(np.meshgrid(arpes.ph, arpes.th))
            th=np.degrees(arpes.th)
            ax.pcolormesh(TH, PH, arpes.domain[indEF,:,:], cmap='gray_r')
            plt.xlim(TH.min(), TH.max())
            plt.ylim(PH.min(), PH.max())
            plt.axhline(y=-np.rad2deg(exp.ph0), linestyle='--', linewidth=1, color='red')
            plt.axvline(x=-np.rad2deg(exp.th0), linestyle='--', linewidth=1, color='red')
            for i in range(domain.flake_N):
                plt.axvline(x=np.rad2deg(-exp.th0-domain.flake_th[i]), linestyle='--', linewidth=1, color='green')
                plt.axhline(y=np.rad2deg(-exp.ph0-domain.flake_ph[i]), linestyle='--', linewidth=1, color='green')
            ax.plot(th-np.rad2deg(exp.th0),-np.sin(exp.az0)/np.cos(exp.az0)*th-np.rad2deg(exp.ph0), 'r-', linewidth=1)
            ax.plot(th-np.rad2deg(exp.th0), np.cos(exp.az0)/np.sin(exp.az0)*th-np.rad2deg(exp.ph0), 'r-', linewidth=1)
            plt.xlabel(r'$\theta$ (deg)')
            plt.ylabel(r'$\phi$ (deg)')
        # Show the plot
        plt.show()

    def Make_stats_plot(arpes):
        r"""
        This function plots the values in ``arpes.stats`` and ``arpes.dstats``, if available.
        If the calculation dimension is ``"cube"``, slices must be chosen for plotting.
        By default, the Fermi surface is selected along with the mean values of
        ``arpes.th`` and ``arpes.ph``.

        *args*:

        - ``arpes``: An object from the ``aurelia_arpes`` module, which can have three dimensions options: 
        ``"cube"`, ``"slicekk"`, and ``"sliceEk"``. If the dimension is ``"cube"``, slices are plotted. By default, the Fermi surface is chosen, along with mean values of :math:`\theta` and :math:`\phi` axes.
        """
        if arpes.crop is False:
            arpes.Crop_edges()
        if arpes.dimension=='sliceEk':
            indEF = np.where(arpes.spec.Omega >= 0)[0][0]
            TH, EK = np.meshgrid(np.degrees(arpes.th), arpes.Ek)
            if hasattr(arpes, 'dstats') == True:
                fig = plt.figure()
                gs = gridspec.GridSpec(1, 2)
                dTH, EK = np.meshgrid(np.degrees(arpes.th), arpes.Ek)
                ax = fig.add_subplot(gs[0,1])
                ax.pcolormesh(dTH, EK, arpes.dstats, cmap='gray_r')

                ax = fig.add_subplot(gs[0,0])
                ax.pcolormesh(TH, EK, arpes.stats, cmap='gray_r')
                plt.axhline(y=arpes.Ek[indEF], linestyle='--', linewidth=1, color='black')                
            elif hasattr(arpes, 'dstats') == False:
                plt.pcolormesh(TH, EK, arpes.stats, cmap='gray_r')
                plt.colorbar()
            plt.axhline(y=arpes.Ek[indEF], linestyle='--', linewidth=1, color='black')
            plt.ylabel(r'$E_k$ (eV)')
            plt.xlabel(r'$\theta$ (deg)')
            plt.title('ARPES statistics')
        elif arpes.dimension=='slicekk':
            PH, TH = np.degrees(np.meshgrid(arpes.ph, arpes.th))
            if hasattr(arpes, 'dstats') == True:
                fig = plt.figure()
                gs = gridspec.GridSpec(1, 2)
                ax = fig.add_subplot(gs[0,0])
                ax.pcolormesh(TH, PH, arpes.stats[0,:,:], cmap='gray_r')

                dPH, dTH = np.degrees(np.meshgrid(arpes.ph, arpes.th))
                ax = fig.add_subplot(gs[0,1])
                ax.pcolormesh(dTH, dPH, arpes.dstats[0,:,:], cmap='gray_r')
            elif hasattr(arpes, 'dstats') == False:
                plt.pcolormesh(TH, PH, arpes.stats[0,:,:], cmap='gray_r')
            plt.xlim(TH.min(), TH.max())
            plt.ylim(PH.min(), PH.max())
            plt.title('ARPES statistics')
            plt.xlabel(r'$\theta$ (deg)')
            plt.ylabel(r'$\phi$ (deg)')
            plt.colorbar()
        elif arpes.dimension=='cube':         
            fig = plt.figure()
            gs = gridspec.GridSpec(3, 3)
            ax = fig.add_subplot(gs[1:3, 2:3])
            EK, PH=np.meshgrid(arpes.Ek, np.degrees(arpes.ph))
            ax.pcolormesh(EK, PH, arpes.stats[:,round(len(arpes.th)/2),:].T, cmap='gray_r')
            plt.axis('tight')
            plt.ylim(PH.min(), PH.max())
            plt.set_cmap('gray_r')
            plt.ylabel(r'$E_k$ (eV)')

            ax = fig.add_subplot(gs[0, 0:2])
            TH,EK=np.meshgrid(np.degrees(arpes.th), arpes.Ek)
            ax.pcolormesh(TH, EK, arpes.stats[:,:,round(len(arpes.ph)/2)], cmap='gray_r')
            plt.set_cmap('gray_r')
            plt.xlabel(r'$E_k$ (eV)')
            plt.xlim(TH.min(), TH.max())

            ax = fig.add_subplot(gs[1:3, 0:2])
            indEF = np.where(arpes.spec.Omega >= 0)[0][0]
            PH, TH=np.degrees(np.meshgrid(arpes.ph, arpes.th))
            ax.pcolormesh(TH, PH, arpes.stats[indEF,:,:], cmap='gray_r')
            plt.xlim(TH.min(), TH.max())
            plt.ylim(PH.min(), PH.max())
            plt.xlabel(r'$\theta$ (deg)')
            plt.ylabel(r'$\phi$ (deg)')
        # Show the plot
        plt.show()



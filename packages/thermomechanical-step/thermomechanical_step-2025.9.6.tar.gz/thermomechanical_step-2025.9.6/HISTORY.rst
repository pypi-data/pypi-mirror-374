=======
History
=======
2025.9.6 -- Bugfix: error in units for Poisson ratio
    * Corrected the metadata to indicate that the Poisson ratio has no units.

2025.9.4 -- Bugfixes: numerical issues and missing item in the GUI
    * Fixed numerical overflows that occurred for larger Debye temperature, > ~700 K
    * The list of temperatures for the thermochemistry functions was missing in the GUI.

2025.9.2 -- Added several properties and thermodynamic functions to the output
    * Added a table of properties from the Debye model as well as ability to save/store
      them

      * Pugh's ductility criterion
      * Cauchy pressure -- Pettifor's ductility criterion
      * Vickers hardness
      * Sound velocity
      * Debye temperature
      * Zero-point energy
      * Gruneisen parameter

    * Added a table of thermodynamic functions and linear coefficient of thermal
      expansion in the Debye/Gruneisen model, and the ability to save/store them
    * Added graphs of the thermodynamic functions and coefficient of thermal expansion
      
2025.8.22 -- Bugfix: errors in moduli
    * There were several errors in calculating the Reuss and Voigt approximations for
      the polycrystalline moduli.

2025.8.21 -- Initial, working version.
    * Handles elastic constants for a single state point.

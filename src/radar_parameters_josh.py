"""
This is just a file to store the radar parameters. 
The parameters of the first and second radar are stored inependently.
To change the parameters, make a copy of this file and give it a nickname.
To use the radar params, do 'import radar_parameters_josh as rp'.
To use the functions, just pass in the device, and it will set the parameters. It returns the sequence and the metrics associated with the parameters.
"""

from parameter_defs import RadarParameters

R1_params = RadarParameters(center_frequency = 59100E6, bandwidth=1250E6, num_chirps=64)
R2_params = RadarParameters(center_frequency=60350E6, bandwidth=1250E6, num_chirps=64)
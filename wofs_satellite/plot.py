from optparse import OptionParser
from wofs.plotting.wofs_plotter import WoFSPlotter

import SatelliteLevel2Processor
import os
import datetime

import pyresample

def resample(target_grid, original_grid, variables):
    '''
    Resamples (i.e., re-projects, re-grid) the original grid to the target grid 
    using a nearest neighborhood approach
    Args:
        target_grid, 2-tuple of 2D arrays of target latitude and longitude 
        original_grid, 2-tuple of 2D arrays of original latitude and longitude 
        variable, list of 2D arrays to be resampled
    Return:
        variable_nearest: list of 2D arrays 
            list of 2D array of variable resampled to the target grid
    '''
    # Create a pyresample object holding the original grid
    orig_def = pyresample.geometry.SwathDefinition(lons=original_grid[1], lats=original_grid[0])

    # Create another pyresample object for the target grid
    targ_def = pyresample.geometry.SwathDefinition(lons=target_grid[1], lats=target_grid[0])

    # Resample with a nearest neighborhood approach. 
    resampled_variables = [pyresample.kd_tree.resample_nearest(orig_def, var, 
                    targ_def, radius_of_influence=50000, fill_value=0) for var in variables] 

    return resampled_variables 


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-p", dest="plotdir", type="string", default= None, help="Directory for Plots")
    parser.add_option("-d", dest="tb_dir", type="string", help = "Directory to GOES-ABI L1B Data")
    parser.add_option("-w", dest="geodir", type="string", help = "Location of wrfinput file for domain info")
    # parser.add_option("-t", dest="t", type="int", help = "Timestep to process")
    parser.add_option("-g", dest="gdate", type="string", help = "Input time")

    (options, args) = parser.parse_args()

    if ((options.plotdir == None) or (options.tb_dir == None)):
        parser.print_help()
        exit(1)

    tb_dir = options.tb_dir
    plotdir = options.plotdir
    geodir = options.geodir
    gdate = options.gdate

    valid_time = datetime.datetime.strptime(gdate, "%Y%m%d%H%M")

    files = [os.path.join(tb_dir, f) for f in ['ch02_TB.nc', 'ch08_TB.nc', 'ch09_TB.nc', 'ch10_TB.nc', 'ch14_TB.nc']] 

    # Initialize the plotter. 
    plotter = WoFSPlotter(file_path=geodir, outdir=plotdir, valid_time = valid_time, 
        timestep_index = 0, dt=5)

    # Load the data and close the netCDF file.
    processor = SatelliteLevel2Processor.SatelliteLevel2Processor(files) 
    data = processor.load_data()

    for v in ['vis', 'ir112', 'wv62', 'wv69', 'wv73']: 
        d = resample((plotter.original_lats_, plotter.original_lons_), 
                    (data[v]['lats'], data[v]['lons']), [data[v]['data']])
        plotter.plot(var_name=v, 
            color_cont_data=d, save_name = f'{v}__{gdate}.png')
        
    # Close the figure.
    plotter.close_figure()
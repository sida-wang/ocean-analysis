"""
Filename:     plot_zonal_energy_check.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  corresponds to energy_budget_in_one_plot.ipynb

"""

# Import general Python modules

import sys, os, pdb, glob
import argparse
import numpy
import iris
import iris.plot as iplt
import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn
seaborn.set_context('talk')

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'ocean-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)
try:
    import general_io as gio
    import timeseries
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def get_title(cube):
    """Get the plot title."""

    model = cube.attributes['model_id']
    experiment = cube.attributes['experiment_id']
    physics = cube.attributes['physics_version']
    run = cube.attributes['realization']
    mip = 'r%si1p%s' %(run, physics)

    title = '%s, %s (%s)'  %(model, experiment, mip)
    
    return title


def calc_anomaly(cube):
    """Calculate the anomaly."""
    
    anomaly = cube.copy()
    anomaly.data = anomaly.data - anomaly.data[0]
    
    return anomaly


def get_data(infile, var, metadata_dict, time_constraint):
    """Get data"""

    if infile:
        cube = iris.load_cube(infile[0], var & time_constraint)
        metadata_dict[infile[0]] = cube.attributes['history']
        anomaly = calc_anomaly(cube)
        final_value = anomaly[-1, ::].data.sum()
        print(var, 'final global total:', final_value)
    else:
        cube = None
        anomaly = None
        final_value = None
    
    return cube, anomaly, metadata_dict


def plot_uptake_storage(gs, ohc_anomaly, hfds_anomaly):
    """Plot the ocean heat uptake and storage"""

    ax = plt.subplot(gs[0])
    plt.sca(ax)

    iplt.plot(ohc_anomaly[-1, ::], color='blue', label='OHC')
    iplt.plot(hfds_anomaly[-1, ::], color='orange', label='hfds')
    #iplt.plot(convergence, color='green', label='convergence')

    plt.xlabel('latitude')
    plt.ylabel('J')
    plt.xlim(-90, 90)

    plt.axhline(y=0, color='0.5', linestyle='--')

    plt.legend()


def plot_transport(gs, hfbasin_data, hfbasin_inferred):
    """Plot the northward ocean heat transport"""

    ax = plt.subplot(gs[1])
    plt.sca(ax)

    if hfbasin_data:
        iplt.plot(hfbasin_data[-1, ::], color='purple', label='northward OHT')

    iplt.plot(hfbasin_inferred, color='purple', linestyle='--', label='inferred northward OHT')

    plt.xlabel('latitude')
    plt.ylabel('J')
    plt.xlim(-90, 90)

    plt.axhline(y=0, color='0.5', linestyle='--')

    plt.legend()


def main(inargs):
    """Run program"""

    mydir = '/g/data/r87/dbi599/DRSv2/CMIP5/%s/%s/yr'  %(inargs.model, inargs.experiment)

    rndt_file = glob.glob('%s/atmos/r1i1p1/rndt/latest/dedrifted/rndt-zonal-sum_Ayr_%s_historical_r1i1p1_cumsum-all.nc' %(mydir, inargs.model))
    hfds_file = glob.glob('%s/ocean/r1i1p1/hfds/latest/dedrifted/hfds-zonal-sum_Oyr_%s_historical_r1i1p1_cumsum-all.nc' %(mydir, inargs.model))
    ohc_file = glob.glob('%s/ocean/r1i1p1/ohc/latest/dedrifted/ohc-zonal-sum_Oyr_%s_historical_r1i1p1_all.nc' %(mydir, inargs.model))
    hfbasin_file = glob.glob('%s/ocean/r1i1p1/hfbasin/latest/dedrifted/hfbasin-global_Oyr_%s_historical_r1i1p1_cumsum-all.nc' %(mydir, inargs.model))
    
    time_constraint = gio.get_time_constraint(['1861-01-01', '2005-12-31'])
    
    cube_dict = {}
    anomaly_dict = {}
    metadata_dict = {}

    cube_dict['rndt'], anomaly_dict['rndt'], metadata_dict = get_data(rndt_file, 'TOA Incoming Net Radiation',
                                                                      metadata_dict, time_constraint)
    cube_dict['hfds'], anomaly_dict['hfds'], metadata_dict = get_data(hfds_file, 'surface_downward_heat_flux_in_sea_water',
                                                                      metadata_dict, time_constraint)
    cube_dict['ohc'], anomaly_dict['ohc'], metadata_dict = get_data(ohc_file, 'ocean heat content',
                                                                    metadata_dict, time_constraint)
    cube_dict['hfbasin'], anomaly_dict['hfbasin'], metadata_dict = get_data(hfbasin_file, 'northward_ocean_heat_transport',
                                                                            metadata_dict, time_constraint)    
    
    if ohc_file and hfds_file:
        ocean_convergence = anomaly_dict['ohc'][-1, ::] - anomaly_dict['hfds'][-1, ::]
        anomaly_dict['hfbasin-inferred'] = ocean_convergence.copy()
        anomaly_dict['hfbasin-inferred'].data = numpy.ma.cumsum(-1 * ocean_convergence.data)
    else:
        anomaly_dict['hfbasin-inferred'] = None

    fig = plt.figure(figsize=[10, 14])
    gs = gridspec.GridSpec(2, 1)

    if ohc_file and hfds_file:
        plot_uptake_storage(gs, anomaly_dict['ohc'], anomaly_dict['hfds'])
        plt.title(get_title(cube_dict['ohc']))
        plot_transport(gs, anomaly_dict['hfbasin'], anomaly_dict['hfbasin-inferred'])
        
    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot ensemble timeseries'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("model", type=str, help="model")
    parser.add_argument("experiment", type=str, help="experiment")  
    parser.add_argument("outfile", type=str, help="output file")                               
    
    args = parser.parse_args()             
    main(args)
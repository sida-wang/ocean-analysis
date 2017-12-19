"""
Filename:     plot_zonal_ensemble.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot zonal mean for an ensemble of models  

"""

# Import general Python modules

import sys, os, pdb
import argparse
from itertools import groupby
from  more_itertools import unique_everseen
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes
import iris.plot as iplt
import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn

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
    import grids
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

experiment_colors = {'historical': 'black', 'historicalGHG': 'red',
                     'historicalAA': 'blue', 'GHG + AA': 'purple'}

var_names = {'precipitation_flux': 'precipitation',
             'water_evaporation_flux': 'evaporation',
             'surface_downward_heat_flux_in_sea_water': 'surface downward heat flux',
             'precipitation_minus_evaporation_flux': 'P-E',
             'northward_ocean_heat_transport': 'northward ocean heat transport'}


def make_zonal_grid():
    """Make a dummy cube with desired grid."""
    
    lat_values = numpy.arange(-90, 91.5, 1.5)   
    latitude = iris.coords.DimCoord(lat_values,
                                    standard_name='latitude',
                                    units='degrees_north',
                                    coord_system=iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS))

    dummy_data = numpy.zeros((len(lat_values)))
    new_cube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(latitude, 0),])

    new_cube.coord('latitude').guess_bounds()

    return new_cube


def calc_trend_cube(cube):
    """Calculate trend and put into appropriate cube."""
    
    trend_array = timeseries.calc_trend(cube, per_yr=True)
    new_cube = cube[0,:].copy()
    new_cube.remove_coord('time')
    new_cube.data = trend_array
    
    return new_cube


def get_colors(family_list):
    """Define a color for each model/physics combo"""

    nfamilies = len(family_list)
    cm = plt.get_cmap('nipy_spectral')
    colors = [cm(1. * i / (nfamilies + 1)) for i in range(nfamilies + 1)]
    color_dict = {}
    count = 1  # skips the first color, which is black
    for family in family_list:
        color_dict[family] = colors[count]
        count = count + 1

    return color_dict


def get_ylabel(cube, inargs):
    """get the y axis label"""

    if str(cube.units) == 'kg m-2 s-1':
        ylabel = '$kg \: m^{-2} \: s^{-1}' 
    else:
        ylabel = '$%s' %(str(cube.units))
    if inargs.perlat:
        ylabel = ylabel + ' \: lat^{-1}'
    if inargs.time_agg == 'trend':
        ylabel = ylabel + ' \: yr^{-1}'
    ylabel = ylabel + '$'

    return ylabel


def get_line_width(realization, model):
    """Get the line width"""

    if model == 'FGOALS-g2':
        lw = 2.0
    else:
        lw = 2.0 if realization == 'r1' else 0.5

    return lw


def plot_individual(data_dict, color_dict):
    """Plot the individual model data"""

    for key, cube in data_dict.items():
        if len(key) == 3:
            model, physics, realization = key
            extra_label = None
        else:
            model, physics, realization, extra_label = key
        if extra_label:
            label = model + ', ' + physics + ', ' + extra_label
        elif (realization == 'r1') or (model == 'FGOALS-g2'):
            label = model + ', ' + physics
        else:
            label = None
        lw = 0.5   #get_line_width(realization, model)
        iplt.plot(cube, label=label, color=color_dict[(model, physics)], linewidth=lw)


def plot_ensmean(data_dict, time_period, ntimes, experiment, nexperiments,
                 single_run=False, linestyle='-'):
    """Plot the ensemble mean.

    If single_run is true, the ensemble is calculated using
      only the first run from each model/physics family.

    """

    target_grid = make_zonal_grid()
    regridded_cube_list = iris.cube.CubeList([])
    count = 0
    for key, cube in data_dict.items():
        model, physics, realization = key
        if not single_run or ((realization == 'r1') or (model == 'FGOALS-g2')):
            regridded_cube = grids.regrid_1D(cube, target_grid, 'latitude')
            new_aux_coord = iris.coords.AuxCoord(count, long_name='ensemble_member', units='no_unit')
            regridded_cube.add_aux_coord(new_aux_coord)
            regridded_cube.cell_methods = None
            regridded_cube.data = regridded_cube.data.astype(numpy.float64)
            regridded_cube_list.append(regridded_cube)
            count = count + 1

    equalise_attributes(regridded_cube_list)
    ensemble_cube = regridded_cube_list.merge_cube()
   
    label, color = get_ensemble_label_color(time_period, ntimes, experiment, nexperiments, single_run)
    ensemble_mean = ensemble_cube.collapsed('ensemble_member', iris.analysis.MEAN)
    iplt.plot(ensemble_mean, label=label, color=color, linestyle=linestyle, linewidth=2.0)

    return ensemble_mean


def get_ensemble_label_color(time_period, ntimes, experiment, nexperiments, single_run):
    """Get the line label and color."""

    label = 'ensemble mean (r1)' if single_run else 'ensemble mean (all runs)'
    color = 'black' 
    if ntimes > 1:
        label = '%s, %s-%s' %(label, time_period[0][0:4], time_period[1][0:4]) 
        color=None
    elif nexperiments > 1:
        label = label + ', ' + experiment
        color = experiment_colors[experiment]

    return label, color


def group_runs(data_dict):
    """Find unique model/physics groups"""

    all_info = data_dict.keys()

    model_physics_list = []
    for key, group in groupby(all_info, lambda x: x[0:2]):
        model_physics_list.append(key)

    family_list = list(unique_everseen(model_physics_list))

    return family_list


def read_data(inargs, infiles, time_constraint, extra_labels):
    """Read data."""

    data_dict = {}
    file_count = 0
    for infile in infiles:
        extra_label = extra_labels[file_count] if extra_labels else False
        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load_cube(infile, gio.check_iris_var(inargs.var) & time_constraint)
        
        if inargs.perlat:
            grid_spacing = grids.get_grid_spacing(cube) 
            cube.data = cube.data / grid_spacing
 
        trend_cube = calc_trend_cube(cube.copy())
        
        clim_cube = cube.collapsed('time', iris.analysis.MEAN)
        clim_cube.remove_coord('time')
 
        model = cube.attributes['model_id']
        realization = 'r' + str(cube.attributes['realization'])
        physics = 'p' + str(cube.attributes['physics_version'])

        if extra_label:        
            key = (model, physics, realization, extra_label)
        else:
            key = (model, physics, realization)
        trend_dict[key] = trend_cube
        clim_dict[key] = clim_cube
        file_count = file_count + 1
    experiment = cube.attributes['experiment_id']
    experiment = 'historicalAA' if experiment == "historicalMisc" else experiment    
    ylabel = get_ylabel(cube, inargs)
    metadata_dict = {infile: cube.attributes['history']}
    
    return trend_dict, clim_dict, experiment, ylabel, metadata_dict


def get_title(plot_name, standard_name, time_list, experiment, nexperiments):
    """Get the plot title"""

    ntimes = len(time_list) 
    if ntimes == 1:
        title = '%s %s, %s-%s' %(var_names[standard_name], plot_name,
                                 time_list[0][0][0:4], time_list[0][1][0:4])
    else:
        title = plot_name

    if nexperiments == 1:
        title = title + ', ' + experiment

    return title


def correct_y_lim(ax, data_cube):   
   """Adjust the y limits after changing x limit 

   x: data for entire x-axes
   y: data for entire y-axes

   """

   x_data = data_cube.coord('latitude').points
   y_data = data_cube.data

   lims = ax.get_xlim()
   i = numpy.where( (x_data > lims[0]) & (x_data < lims[1]) )[0]

   plt.ylim( y_data[i].min(), y_data[i].max() ) 


def main(inargs):
    """Run the program."""
    
    fig, ax = plt.subplots(figsize=[14, 7])
    ntimes = len(inargs.time)
    nexperiments = len(inargs.infiles)
    for infiles in inargs.infiles:
        for time_period in inargs.time:
            time_constraint = gio.get_time_constraint(time_period)
            trend_dict, clim_dict, experiment, ylabel, metadata_dict = read_data(inargs, infiles, time_constraint, inargs.extra_labels)
    
            model_family_list = group_runs(data_dict)
            color_dict = get_colors(model_family_list)

            if inargs.time_agg == 'trend':
                target_dict = trend_dict
            else:
                target_dict = clim_dict

            if (ntimes == 1) and (nexperiments == 1):
                plot_individual(target_dict, color_dict)
            if inargs.ensmean:
                ensemble_mean = plot_ensmean(target_dict, time_period, ntimes, experiment, nexperiments,
                                             single_run=inargs.single_run)

            if inargs.clim and ((len(inargs.infiles) == 1) or (experiment == 'historical'):
                ax2 = ax.twinx()
                plot_ensmean(clim_dict, time_period, ntimes, experiment, nexperiments,
                             single_run=inargs.single_run, linestyle='--')
                plt.sca(ax)

    title = get_title(inargs.time_agg, inargs.var, inargs.time, experiment, nexperiments)
    plt.title(title)
    plt.xticks(numpy.arange(-75, 90, 15))
    plt.xlim(inargs.xlim[0], inargs.xlim[1])
    if not inargs.xlim == (-90, 90):
        correct_y_lim(ax, ensemble_mean)

    plt.ylabel(ylabel)
    plt.xlabel('latitude')
    plt.axhline(y=0, color='0.5', linestyle='--')

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot zonal ensemble'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("var", type=str, help="Variable")
    parser.add_argument("time_agg", type=str, choices=('trend', 'climatology'), help="Temporal aggregation")
    parser.add_argument("outfile", type=str, help="Output file")                                     
    
    parser.add_argument("--infiles", type=str, action='append', nargs='*', help="Input files for a given experiment")

    parser.add_argument("--extra_labels", type=str, nargs='*', default=None,
                        help="Extra label to distinguish the input files")

    parser.add_argument("--time", type=str, action='append', required=True, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")
    parser.add_argument("--perlat", action="store_true", default=False,
                        help="Scale per latitude [default=False]")
    parser.add_argument("--single_run", action="store_true", default=False,
                        help="Only use run 1 in the ensemble mean [default=False]")
    parser.add_argument("--ensmean", action="store_true", default=False,
                        help="Plot an ensemble mean curve [default=False]")
    parser.add_argument("--clim", action="store_true", default=False,
                        help="Plot a climatology curve behind the trend curve [default=False]")

    parser.add_argument("--xlim", type=float, nargs=2, metavar=('SOUTHERN_LIMIT', 'NORTHERN LIMIT'), default=(-90, 90),
                        help="x-axis limits [default = entire]")

    args = parser.parse_args()             
    main(args)

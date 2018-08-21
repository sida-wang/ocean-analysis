"""
Filename:     plot_lat_vs_depth.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot latitude versus depth data  

"""

# Import general Python modules

import sys
import os
import pdb
import re
import argparse

import numpy
import matplotlib.pyplot as plt
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
import iris
import cmdline_provenance as cmdprov

import matplotlib as mpl
mpl.rcParams['axes.labelsize'] = 'large'
mpl.rcParams['axes.titlesize'] = 'x-large'
mpl.rcParams['xtick.labelsize'] = 'medium'
mpl.rcParams['ytick.labelsize'] = 'medium'
mpl.rcParams['legend.fontsize'] = 'large'

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'ocean-analysis':
        break

#modules_dir = os.path.join(repo_dir, 'modules')
#sys.path.append(modules_dir)
#try:
#    import general_io as gio
#    import convenient_universal as uconv
#except ImportError:
#    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def set_units(cube, scale_factor=1):
    """Set the units.
    Args:
      cube (iris.cube.Cube): Data cube
      scale_factor (int): Scale the data
        e.g. a scale factor of 3 will mean the data are 
        mutliplied by 10^3 (and units will be 10^-3)
    """

    trend_data = cube.data * 10**scale_factor

    unit_scale = ''
    if scale_factor != 0:
        if scale_factor > 0.0:
            unit_scale = '10^{-%i}'  %(scale_factor)
        else:
            unit_scale = '10^{%i}'  %(abs(scale_factor))

    units = str(cube.units)
    units = units.replace(" ", " \enspace ")
    units = units.replace("-1", "^{-1}")
    units = '$%s \enspace %s$'  %(unit_scale, units)

    return trend_data, units


def create_plot(contourf_cube, contour_cube, scale_factor):
    """Create the plot."""
    
    fig = plt.figure()   #figsize=[10, 8])
    cbar_ax = fig.add_axes([0.93, 0.2, 0.02, 0.65])
    gs = gridspec.GridSpec(1, 1)

    axMain = plt.subplot(gs[0])
    plt.sca(axMain)

    cmap = plt.cm.RdBu_r 
    #cmocean.cm.balance

    lats = contourf_cube.coord('latitude').points
    levs = contourf_cube.coord('depth').points 
    
    contourf_data, units = set_units(contourf_cube, scale_factor=scale_factor)           
    contourf_ticks = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]

    cf = axMain.contourf(lats, levs, contourf_data,
                         cmap=cmap, extend='both', levels=contourf_ticks)

    if contour_cube:
        contour_data = contour_cube.data
        contour_levels = numpy.arange(0.0, 350.0, 2.5)

        cplot_main = axMain.contour(lats, levs, contour_data, colors='0.3', levels=contour_levels)
        plt.clabel(cplot_main, contour_levels[0::2], fmt='%2.1f', colors='0.3', fontsize=8)

    # Deep section
    axMain.set_ylim((500.0, 2000.0))
    axMain.invert_yaxis()
    axMain.set_xlim((-70, 70))
    axMain.xaxis.set_ticks_position('bottom')
    axMain.set_xticks([-80, -60, -40, -20, 0, 20, 40, 60, 80])
    plt.ylabel('Depth (m)')
    plt.xlabel('Latitude')
    axMain.get_yaxis().set_label_coords(-0.11, 1.1)

    # Shallow section
    divider = make_axes_locatable(axMain)
    axShallow = divider.append_axes("top", size="70%", pad=0.1, sharex=axMain)
    axShallow.contourf(lats, levs, contourf_data,
                       cmap=cmap, extend='both', levels=contourf_ticks)

    if contour_cube:
        cplot_shallow = axShallow.contour(lats, levs, contour_data, colors='0.3', levels=contour_levels)
        plt.clabel(cplot_shallow, contour_levels[0::2], fmt='%2.1f', colors='0.3', fontsize=8)

    axShallow.set_ylim((0.0, 500.0))
    axShallow.set_xlim((-70, 70))
    axShallow.invert_yaxis()
    plt.setp(axShallow.get_xticklabels(), visible=False)

    cbar = plt.colorbar(cf, cbar_ax)
    cbar.set_label(units)


def main(inargs):
    """Run the program."""
    
    metadata_dict = {}
    contourf_cube = iris.load_cube(inargs.contourf_file, inargs.variable)
    metadata_dict[inargs.contourf_file] = contourf_cube.attributes['history']
    
    if inargs.contour_file:
        contour_cube = iris.load_cube(inargs.contour_file, inargs.variable)
        metadata_dict[inargs.contour_file] = contour_cube.attributes['history']
    else:
        contour_cube = None
    
    create_plot(contourf_cube, contour_cube, inargs.scale_factor)

    # Save output
    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)
    
    log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', inargs.outfile)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot latitude versus depth data'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("contourf_file", type=str, help="Filled contour data file") 
    parser.add_argument("variable", type=str, help="Variable")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--contour_file", type=str, default=None,
                        help="unfilled contour data file")

    parser.add_argument("--scale_factor", type=int, default=3,
                        help="Scale factor (e.g. scale factor of 3 will multiply trends by 10^3 [default=1]")

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()             
    main(args)

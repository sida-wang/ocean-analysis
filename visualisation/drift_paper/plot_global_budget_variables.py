"""
Filename:     plot_global_budget_variables.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot variables relevant for the global energy and water budget  

"""

# Import general Python modules

import sys
import os
import re
import pdb
import argparse
import itertools

import numpy
import pandas as pd
from matplotlib import gridspec
import matplotlib.pyplot as plt
import statsmodels.api as sm
import iris
import cmdline_provenance as cmdprov

import clef.code
db = clef.code.connect()
session = clef.code.Session()

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'ocean-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

processing_dir = os.path.join(repo_dir, 'data_processing')
sys.path.append(processing_dir)

import timeseries
import general_io as gio
import convenient_universal as uconv
import spatial_weights

import matplotlib as mpl
mpl.rcParams['axes.labelsize'] = 16 #'x-large'
mpl.rcParams['axes.titlesize'] = 18 #'xx-large'
mpl.rcParams['xtick.labelsize'] = 16 #'x-large'
mpl.rcParams['ytick.labelsize'] = 16 #'x-large'
mpl.rcParams['legend.fontsize'] = 14.8 #'x-large'


# Define functions 

processed_files = []
numbers_out_list = []

names = {'masso': 'sea_water_mass',
         'volo': 'sea_water_volume',
         'thetaoga': 'sea_water_potential_temperature',
         'soga': 'sea_water_salinity',
         'zosga': 'global_average_sea_level_change',
         'zostoga': 'global_average_thermosteric_sea_level_change',
         'zossga': 'global_average_steric_sea_level_change',
         'wfo': 'water_flux_into_sea_water',
         'wfonocorr': 'water_flux_into_sea_water_without_flux_correction',
         'wfcorr': 'water_flux_correction',
         'hfds': 'surface_downward_heat_flux_in_sea_water',
         'hfcorr': 'heat_flux_correction',
         'hfgeou' : 'upward_geothermal_heat_flux_at_sea_floor',
         'rsdt': 'toa_incoming_shortwave_flux',
         'rlut': 'toa_outgoing_longwave_flux',
         'rsut': 'toa_outgoing_shortwave_flux',
         'vsf': 'virtual_salt_flux_into_sea_water',
         'vsfcorr': 'virtual_salt_flux_correction',
         'sfdsi': 'downward_sea_ice_basal_salt_flux',
         'sfriver': 'salt_flux_into_sea_water_from_rivers',
         'clwvi': 'atmosphere_mass_content_of_cloud_condensed_water',
         'prw': 'atmosphere_mass_content_of_water_vapor',
         'pr': 'precipitation_flux',
         'evspsbl': 'water_evapotranspiration_flux'
}

amon_vars = ['rsdt', 'rsut', 'rlut', 'pr', 'evspsbl', 'clwvi', 'prw']


def get_latest(results):
    """Select the latest results"""

    if not results.empty:
        latest = results.iloc[0]
        for index, row in results.iloc[1:].iterrows():
            current_version = row.path.split('/')[-1]
            current_version = current_version[1:] if 'v' in current_version else current_version
            latest_version = latest.path.split('/')[-1]
            latest_version = latest_version[1:] if 'v' in latest_version else latest_version
            if float(current_version) > float(latest_version):
                latest = row
    else:
        latest = pd.DataFrame()    

    return latest


def clef_search(model, variable, ensemble, project, experiment='piControl'):
    """Use Clef to search for data files"""

    if variable in ['areacello', 'areacella']:
        if project == 'cmip6' and variable == 'areacello':
            table = 'Ofx'
        else:
            table = 'fx'
    elif variable in amon_vars:
        table = 'Amon'
    else:
        table = 'Omon'

    constraints = {'variable': variable, 'model': model, 'table': table,
                   'experiment': experiment, 'ensemble': ensemble}
    print(variable)
    results = clef.code.search(session, project=project, **constraints)
    results = get_latest(results)
    if not results.empty:
        filenames = list(results.filename)
        filenames.sort()
        filedir = results.path
        file_list = [filedir + '/' + filename for filename in filenames]
        version = results.path.split('/')[0]
        file_version_list = [filedir + '/' + filename + ', ' + str(version) for filename in filenames]
        processed_files.append(file_version_list)
    else:
        file_list = []
    
    if len(file_list) > 1:
        if file_list[0] == file_list[1]:
            file_list = file_list[0::2]
    print(file_list)

    return file_list


def time_check(cube):
    """Check the time axis for annual data."""

    iris.coord_categorisation.add_year(cube, 'time')
    year_list = cube.coord('year').points        
    diffs = numpy.diff(year_list)
    if diffs.size > 0:
        assert diffs.max() == 1, "Gaps in time axis, %s" %(cube.long_name)
        assert diffs.min() == 1, "Duplicate annual values in time axis. %s" %(cube.long_name)

    return cube


def read_global_variable(model, variable, ensemble, project, manual_file_dict,
                         ignore_list, time_constraint, start_index=0, end_index=None, experiment='piControl'):
    """Read data for a global variable"""

    if variable in ignore_list:
        file_list = []
    elif (variable, experiment) in manual_file_dict.keys():
        file_list = manual_file_dict[(variable, experiment)]
    else:
        file_list = clef_search(model, variable, ensemble, project, experiment=experiment) 
    
    if file_list:
        cube, history = gio.combine_files(file_list, names[variable])
        if variable == 'soga':
            cube = gio.salinity_unit_check(cube)
        elif variable == 'thetaoga':
            cube = gio.temperature_unit_check(cube, 'K')
        cube = timeseries.convert_to_annual(cube, days_in_month=True)
        cube = time_check(cube)
        if time_constraint:
            cube = cube.extract(time_constraint)
        if end_index:
            cube = cube[start_index: end_index]
        else:
            cube = cube[start_index:]
        if numpy.isnan(cube.data[0]):
            cube.data[0] = 0.0
    else:
        cube = None

    return cube


def read_area(model, variable, ensemble, project, manual_file_dict):
    """Read area data."""

    if variable in manual_file_dict.keys():
        area_files = manual_file_dict[variable]
    else:
        area_run = 'r0i0p0' if project == 'cmip5' else ensemble
        area_files = clef_search(model, variable, area_run, project)
        if not area_files:
            area_files = clef_search(model, variable, area_run, project, experiment='historical')

    if area_files:
        cube = iris.load_cube(area_files[0])
    else:
        cube = None

    return cube


def read_spatial_flux(model, variable, ensemble, project, area_cube,
                      manual_file_dict, ignore_list, time_constraint,
                      start_index=0, end_index=None, chunk=False, mask_nans=False,
                      ref_time_coord=None):
    """Read spatial flux data and convert to global value.

    Accounts for cases where spatial dimensions are unnamed
      e.g. coord_names = ['time', --, --]
    and/or where there is no time axis.

    """

    if variable in ignore_list:
        file_list = []
    elif (variable, 'piControl') in manual_file_dict.keys():
        file_list = manual_file_dict[(variable, 'piControl')]
    else:
        file_list = clef_search(model, variable, ensemble, project) 

    cube_list = iris.cube.CubeList([])
    for infile in file_list:
        cube, history = gio.combine_files(infile, names[variable], checks=True)
        coord_names = [coord.name() for coord in cube.dim_coords]
            
        if ('time' in coord_names) and area_cube:
            area_array = uconv.broadcast_array(area_cube.data, [1, area_cube.ndim], cube.shape)
        elif area_cube:
            area_array = area_cube.data
        else:
            assert variable in amon_vars
            area_array = spatial_weights.area_array(cube)

        units = str(cube.units)
        assert 'm-2' in units
        cube.units = units.replace('m-2', '')
        cube.data = cube.data * area_array

        if 'time' in coord_names:
            global_sum = numpy.ma.sum(cube.data, axis=(1,2))
            cube = cube[:, 0, 0].copy()
            cube.data = global_sum

        cube_list.append(cube)

    if cube_list:    
        cube = gio.combine_cubes(cube_list)
        if not 'time' in coord_names:
            assert ref_time_coord
            global_sum = numpy.ma.sum(cube.data)
            data = numpy.ones(len(ref_time_coord.points)) * global_sum
            cube = iris.cube.Cube(data,
                                  standard_name=cube.standard_name,
                                  long_name=cube.long_name,
                                  var_name=cube.var_name,
                                  units=cube.units,
                                  attributes=cube.attributes,
                                  dim_coords_and_dims=[(ref_time_coord, 0)])
            #cube = time_check(cube)

        if ('s-1' in str(cube.units)) or ('W' in str(cube.units)):
            cube = timeseries.flux_to_total(cube)
       
        if 'time' in coord_names:
            if 'flux' in names[variable]:
                cube = timeseries.convert_to_annual(cube, aggregation='sum')
            else:
                cube = timeseries.convert_to_annual(cube, aggregation='mean', days_in_month=True)

        if time_constraint:
            cube = cube.extract(time_constraint)
        if end_index:
            cube = cube[start_index: end_index]
        else:
            cube = cube[start_index:]

        cube = time_check(cube)
    else:
        cube = None
        
    return cube


def plot_global_variable(ax, data, long_name, units, color, label=None, xlabel=True):
    """Plot a global variable."""

    ax.grid(linestyle=':')
    ax.plot(data, color=color, label=label)
    ax.set_title(long_name)
    if xlabel:
        ax.set_xlabel('year')
    ax.set_ylabel(units)
    ax.ticklabel_format(useOffset=False)
    ax.yaxis.major.formatter._useMathText = True


def get_start_year(branch_time, control_time_axis):
    """Get the start year for a forced simulation."""

    start_year, error = uconv.find_nearest(control_time_axis, float(branch_time) + 182.5, index=True)
    assert abs(error) < 200, 'check the branch time - something seems wrong'

    return start_year


def get_data_dict(inargs, manual_file_dict, branch_year_dict):
    """Get all the necessary data."""

    if inargs.time_bounds:
        time_constraint = gio.get_time_constraint(inargs.time_bounds)
    else:
        time_constraint = None

    cube_dict = {}

    cube_dict['areacella'] = read_area(inargs.model, 'areacella', inargs.run, inargs.project, manual_file_dict)
    cube_dict['areacello'] = read_area(inargs.model, 'areacello', inargs.run, inargs.project, manual_file_dict)

    cube_dict['masso'] = read_global_variable(inargs.model, 'masso', inargs.run, inargs.project,
                                              manual_file_dict, inargs.ignore_list,
                                              time_constraint, start_index=inargs.start_index, end_index=inargs.end_index)
    cube_dict['volo'] = read_global_variable(inargs.model, 'volo', inargs.run, inargs.project,
                                             manual_file_dict, inargs.ignore_list,
                                             time_constraint, start_index=inargs.start_index, end_index=inargs.end_index)
    cube_dict['thetaoga'] = read_global_variable(inargs.model, 'thetaoga', inargs.run, inargs.project,
                                                 manual_file_dict, inargs.ignore_list,
                                                 time_constraint, start_index=inargs.start_index, end_index=inargs.end_index)
    cube_dict['soga'] = read_global_variable(inargs.model, 'soga', inargs.run, inargs.project,
                                             manual_file_dict, inargs.ignore_list,
                                             time_constraint, start_index=inargs.start_index, end_index=inargs.end_index) 

    wfo_areavar = 'areacella' if 'wfo' in inargs.areacella else 'areacello'
    cube_dict['wfo'] = read_spatial_flux(inargs.model, 'wfo', inargs.run, inargs.project, cube_dict[wfo_areavar],
                                         manual_file_dict, inargs.ignore_list, time_constraint,
                                         start_index=inargs.start_index, end_index=inargs.end_index, chunk=inargs.chunk)
    cube_dict['wfonocorr'] = read_spatial_flux(inargs.model, 'wfonocorr', inargs.run, inargs.project, cube_dict['areacello'],
                                               manual_file_dict, inargs.ignore_list, time_constraint,
                                               start_index=inargs.start_index, end_index=inargs.end_index, chunk=inargs.chunk)
    cube_dict['wfcorr'] = read_spatial_flux(inargs.model, 'wfcorr', inargs.run, inargs.project, cube_dict['areacello'],
                                            manual_file_dict, inargs.ignore_list, time_constraint,
                                            start_index=inargs.start_index, end_index=inargs.end_index, chunk=inargs.chunk)

    hfds_areavar = 'areacella' if 'hfds' in inargs.areacella else 'areacello'
    
    cube_dict['hfds'] = read_spatial_flux(inargs.model, 'hfds', inargs.run, inargs.project, cube_dict[hfds_areavar],
                                          manual_file_dict, inargs.ignore_list, time_constraint,
                                          start_index=inargs.start_index, end_index=inargs.end_index, chunk=inargs.chunk)
    cube_dict['hfcorr'] = read_spatial_flux(inargs.model, 'hfcorr', inargs.run, inargs.project, cube_dict['areacello'],
                                            manual_file_dict, inargs.ignore_list, time_constraint,
                                            start_index=inargs.start_index, end_index=inargs.end_index, chunk=inargs.chunk)
    if cube_dict['hfds']:
        cube_dict['hfgeou'] = read_spatial_flux(inargs.model, 'hfgeou', inargs.run, inargs.project, cube_dict['areacello'],
                                                manual_file_dict, inargs.ignore_list, time_constraint,
                                                start_index=inargs.start_index, end_index=inargs.end_index, chunk=inargs.chunk,
                                                ref_time_coord=cube_dict['hfds'].coord('time'))
    else:
        cube_dict['hfgeou'] = None
    cube_dict['vsf'] = read_spatial_flux(inargs.model, 'vsf', inargs.run, inargs.project, cube_dict['areacello'],
                                         manual_file_dict, inargs.ignore_list, time_constraint,
                                         start_index=inargs.start_index, end_index=inargs.end_index, chunk=inargs.chunk)
    cube_dict['vsfcorr'] = read_spatial_flux(inargs.model, 'vsfcorr', inargs.run, inargs.project, cube_dict['areacello'],
                                             manual_file_dict, inargs.ignore_list, time_constraint,
                                             start_index=inargs.start_index, end_index=inargs.end_index, chunk=inargs.chunk)
    cube_dict['sfriver'] = read_spatial_flux(inargs.model, 'sfriver', inargs.run, inargs.project, cube_dict['areacello'],
                                             manual_file_dict, inargs.ignore_list, time_constraint,
                                             start_index=inargs.start_index, end_index=inargs.end_index, chunk=inargs.chunk)
    cube_dict['sfdsi'] = read_spatial_flux(inargs.model, 'sfdsi', inargs.run, inargs.project, cube_dict['areacello'],
                                           manual_file_dict, inargs.ignore_list, time_constraint,
                                           start_index=inargs.start_index, end_index=inargs.end_index, chunk=inargs.chunk)

    cube_dict['rsdt'] = read_spatial_flux(inargs.model, 'rsdt', inargs.run, inargs.project, cube_dict['areacella'],
                                          manual_file_dict, inargs.ignore_list, time_constraint,
                                          start_index=inargs.start_index, end_index=inargs.end_index)
    cube_dict['rlut'] = read_spatial_flux(inargs.model, 'rlut', inargs.run, inargs.project, cube_dict['areacella'],
                                          manual_file_dict, inargs.ignore_list, time_constraint,
                                          start_index=inargs.start_index, end_index=inargs.end_index)
    cube_dict['rsut'] = read_spatial_flux(inargs.model, 'rsut', inargs.run, inargs.project, cube_dict['areacella'],
                                          manual_file_dict, inargs.ignore_list, time_constraint,
                                          start_index=inargs.start_index, end_index=inargs.end_index)
    cube_dict['pr'] = read_spatial_flux(inargs.model, 'pr', inargs.run, inargs.project, cube_dict['areacella'],
                                        manual_file_dict, inargs.ignore_list, time_constraint,
                                        start_index=inargs.start_index, end_index=inargs.end_index)

    cube_dict['evspsbl'] = read_spatial_flux(inargs.model, 'evspsbl', inargs.run, inargs.project, cube_dict['areacella'],
                                             manual_file_dict, inargs.ignore_list, time_constraint,
                                             start_index=inargs.start_index, end_index=inargs.end_index)
    cube_dict['clwvi'] = read_spatial_flux(inargs.model, 'clwvi', inargs.run, inargs.project, cube_dict['areacella'],
                                           manual_file_dict, inargs.ignore_list, time_constraint,
                                           start_index=inargs.start_index, end_index=inargs.end_index)
    cube_dict['prw'] = read_spatial_flux(inargs.model, 'prw', inargs.run, inargs.project, cube_dict['areacella'],
                                         manual_file_dict, inargs.ignore_list, time_constraint,
                                         start_index=inargs.start_index, end_index=inargs.end_index)

    return cube_dict


def plot_raw(inargs, cube_dict, branch_year_dict, manual_file_dict):
    """Plot the raw budget variables."""

    fig = plt.figure(figsize=[20, 35])
    nrows = 6
    ncols = 2

    if cube_dict['masso']:
        ax1 = fig.add_subplot(nrows, ncols, 1)
        linestyles = itertools.cycle(('-', '--', ':', '-.'))
        for experiment, branch_year in branch_year_dict.items():
            cube = read_global_variable(inargs.model, 'masso', inargs.run, inargs.project,
                                        manual_file_dict, inargs.ignore_list, experiment=experiment)
            if cube:
                xdata = numpy.arange(branch_year, len(cube.data) + branch_year)
                ax1.plot(xdata, cube.data, color='limegreen', label=experiment, linestyle=next(linestyles))
        plot_global_variable(ax1, cube_dict['masso'].data, cube_dict['masso'].long_name,
                             cube_dict['masso'].units, 'green', label='piControl', xlabel=False)
        ax1.legend()

    if cube_dict['volo']:
        ax2 = fig.add_subplot(nrows, ncols, 2)
        linestyles = itertools.cycle(('-', '--', ':', '-.'))
        for experiment, branch_year in branch_year_dict.items():
            cube = read_global_variable(inargs.model, 'volo', inargs.run, inargs.project,
                                        manual_file_dict, inargs.ignore_list, experiment=experiment)
            if cube:
                xdata = numpy.arange(branch_year, len(cube.data) + branch_year)
                ax2.plot(xdata, cube.data, color='tomato', label=experiment, linestyle=next(linestyles))
        plot_global_variable(ax2, cube_dict['volo'].data, cube_dict['volo'].long_name,
                            cube_dict['volo'].units, 'red', label='piControl', xlabel=False)
        ax2.legend()

    if cube_dict['masso'] and cube_dict['volo']:
        ax3 = fig.add_subplot(nrows, ncols, 3)
        units = str(cube_dict['masso'].units) + ' / ' + str(cube_dict['volo'].units)
        plot_global_variable(ax3, cube_dict['masso'].data / cube_dict['volo'].data, 'Density', units, 'grey', xlabel=False)

    if cube_dict['thetaoga']:
        ax4 = fig.add_subplot(nrows, ncols, 4)
        linestyles = itertools.cycle(('-', '--', ':', '-.'))
        for experiment, branch_year in branch_year_dict.items():
            cube = read_global_variable(inargs.model, 'thetaoga', inargs.run, inargs.project,
                                        manual_file_dict, inargs.ignore_list, experiment=experiment)
            if cube:
                cube = gio.temperature_unit_check(cube, 'K')
                xdata = numpy.arange(branch_year, len(cube.data) + branch_year)
                ax4.plot(xdata, cube.data, color='yellow', label=experiment, linestyle=next(linestyles))
        plot_global_variable(ax4, cube_dict['thetaoga'].data, cube_dict['thetaoga'].long_name,
                             cube_dict['thetaoga'].units, 'gold', label='piControl', xlabel=False)
        ax4.legend()

    if cube_dict['soga']:
        ax5 = fig.add_subplot(nrows, ncols, 5)
        plot_global_variable(ax5, cube_dict['soga'].data, cube_dict['soga'].long_name, 'g/kg', 'orange',
                             label=cube_dict['soga'].long_name)
        ax5.legend()

    if cube_dict['wfo']:
        ax6 = fig.add_subplot(nrows, ncols, 7)
        if cube_dict['wfcorr']:
            ax6.plot(cube_dict['wfcorr'].data, color='blue', label=cube_dict['wfcorr'].long_name, linestyle=':')
        if cube_dict['wfonocorr']:
            ax6.plot(cube_dict['wfonocorr'].data, color='blue', label=cube_dict['wfonocorr'].long_name, linestyle='-.')
        plot_global_variable(ax6, cube_dict['wfo'].data, 'Water Flux Into Ocean', cube_dict['wfo'].units,
                             'blue', label=cube_dict['wfo'].long_name, xlabel=False)
        ax6.legend()

    if cube_dict['hfds']:
        ax7 = fig.add_subplot(nrows, ncols, 8)
        if cube_dict['hfcorr']:
            ax7.plot(cube_dict['hfcorr'].data, color='teal', label=cube_dict['hfcorr'].long_name, linestyle=':')
        if cube_dict['hfgeou']:
            ax7.plot(cube_dict['hfgeou'].data, color='teal', label=cube_dict['hfgeou'].long_name, linestyle='-.')
        plot_global_variable(ax7, cube_dict['hfds'].data, 'Heat Flux Into Ocean', cube_dict['hfds'].units,
                             'teal', label=cube_dict['hfds'].long_name, xlabel=False)
        ax7.legend()

    if cube_dict['rsdt']:
        ax8 = fig.add_subplot(nrows, ncols, 9)
        ax8.plot(cube_dict['rsdt'].data, color='maroon', label=cube_dict['rsdt'].long_name, linestyle=':')
        ax8.plot(cube_dict['rsut'].data, color='maroon', label=cube_dict['rsut'].long_name, linestyle='-.')
        plot_global_variable(ax8, cube_dict['rlut'].data, 'TOA Radiative Fluxes',
                             cube_dict['rlut'].units, 'maroon', label=cube_dict['rlut'].long_name, xlabel=False)
        ax8.legend()

    if cube_dict['vsf'] or cube_dict['vsfcorr'] or cube_dict['sfriver'] or cube_dict['sfdsi']:
        ax9 = fig.add_subplot(nrows, ncols, 10)
        if cube_dict['vsf']:
            plot_global_variable(ax9, cube_dict['vsf'].data, 'Salt Fluxes',
                                 cube_dict['vsf'].units, 'orange', label=cube_dict['vsf'].long_name, xlabel=False)
        if cube_dict['vsfcorr']:
            plot_global_variable(ax9, cube_dict['vsfcorr'].data, 'Salt Fluxes',
                                cube_dict['vsfcorr'].units, 'yellow', label=cube_dict['vsfcorr'].long_name, xlabel=False)
        if cube_dict['sfriver']:
            plot_global_variable(ax9, cube_dict['sfriver'].data, 'Salt Fluxes',
                                 cube_dict['sfriver'].units, 'red', label=cube_dict['sfriver'].long_name, xlabel=False)
        if cube_dict['sfdsi']:
            plot_global_variable(ax9, cube_dict['sfdsi'].data, 'Salt Fluxes',
                                cube_dict['sfdsi'].units, 'maroon', label=cube_dict['sfdsi'].long_name, xlabel=False)
        ax9.legend()

    if cube_dict['pr'] and cube_dict['evspsbl']:
        ax10 = fig.add_subplot(nrows, ncols, 11)
        ax10.plot(cube_dict['pr'].data, color='blue', label=cube_dict['pr'].long_name)
        plot_global_variable(ax10, cube_dict['evspsbl'].data, 'Atmospheric moisture fluxes',
                             cube_dict['evspsbl'].units, 'orange', label=cube_dict['evspsbl'].long_name, xlabel=False)
        ax10.legend()

    if cube_dict['prw']:
        ax11 = fig.add_subplot(nrows, ncols, 12)
        if cube_dict['clwvi']:
            ax11a = ax11.twinx()
            ax11a.plot(cube_dict['clwvi'].data, color='green', label=cube_dict['clwvi'].long_name)
            ax11a.set_ylabel(cube_dict['clwvi'].units)
            ax11a.ticklabel_format(useOffset=False)
            ax11a.yaxis.major.formatter._useMathText = True
        plot_global_variable(ax11, cube_dict['prw'].data, 'Atmospheric Water Content',
                             cube_dict['prw'].units, 'teal', label=cube_dict['prw'].long_name, xlabel=False)
        ax11.legend()

    plt.subplots_adjust(top=0.92)
    title = '%s (%s), %s, piControl'  %(inargs.model, inargs.project, inargs.run)
    plt.suptitle(title)
    plt.savefig(inargs.rawfile, bbox_inches='tight')


def delta_masso_from_soga(s_orig, s_new, m_orig):
    """Infer a change in mass from salinity"""

    delta_m = m_orig * ((s_orig / s_new) - 1)    
    
    return delta_m


def delta_soga_from_masso(m_orig, m_new, s_orig):
    """Infer a change in global average salinity from mass"""

    delta_s = s_orig * ((m_orig / m_new) - 1)    
    
    return delta_s


def calc_trend(data, name, units, outlier_threshold=None):
    """Calculate the linear trend."""

    time_axis = numpy.arange(0, len(data)) 
    trend = timeseries.linear_trend(data, time_axis, outlier_threshold)

    trend_text = 'trend, %s: %s %s/yr'  %(name, str(trend), units) 
    numbers_out_list.append(trend_text)


def calc_regression(x_data, y_data, label, decadal_mean=False):
    """Calculate the linear regression coefficient."""

    x_data = x_data.copy()
    y_data = y_data.copy()

    nx = len(x_data)
    ny = len(y_data)
    if nx > ny:
        x_data = x_data[0:ny]
    elif ny > nx:
        y_data = y_data[0:nx]
    
    if decadal_mean:
        x_data = timeseries.runmean(x_data, 10)
        y_data = timeseries.runmean(y_data, 10)

    if (x_data.max() == x_data.min()) or (y_data.max() == y_data.min()):
        regression_text = 'regression coefficient, %s: ERROR'  %(label)
    else:
        validation_coeff = numpy.ma.polyfit(x_data, y_data, 1)[0]

        x_data = sm.add_constant(x_data)
        model = sm.OLS(y_data, x_data)
        results = model.fit()
        coeff = results.params[-1]
        conf_lower, conf_upper = results.conf_int()[-1]
        assert validation_coeff < conf_upper
        assert validation_coeff > conf_lower

        stderr = results.bse[-1]
        n_orig = int(results.nobs)
        n_eff = uconv.effective_sample_size(y_data, n_orig)
        stderr_adjusted = (stderr * numpy.sqrt(n_orig)) / numpy.sqrt(n_eff)
    
        regression_text = 'regression coefficient, %s: %s [%s, %s] +- %s (or %s)'  %(label, str(coeff), str(conf_lower), str(conf_upper), str(stderr), str(stderr_adjusted))

    numbers_out_list.append(regression_text)


def dedrift_data(data, fit='cubic'):
    """Remove drift and plot."""
    
    assert fit in ['linear', 'cubic']
    deg = 3 if fit == 'cubic' else 1
    
    time_axis = numpy.arange(len(data))
    coefficients = timeseries.fit_polynomial(data, time_axis, deg, None)
    drift = numpy.polyval(coefficients, time_axis)
    dedrifted_data = data - drift

    return dedrifted_data
    

def plot_ohc(ax_top, ax_middle, masso_data, cp, cube_dict, ylim=None):
    """Plot the OHC timeseries and it's components"""

    is_masso_timeseries = type(masso_data) != float
    first_masso = masso_data[0] if is_masso_timeseries else masso_data

    ax_top.grid(linestyle=':')
    ax_middle.grid(linestyle=':')

    if cube_dict['thetaoga']:
        assert cube_dict['thetaoga'].units == 'K'
        ohc_data = masso_data * cube_dict['thetaoga'].data * cp
        ohc_anomaly_data = ohc_data - ohc_data[0]

        thetaoga_anomaly_data = cube_dict['thetaoga'].data - cube_dict['thetaoga'].data[0]
        thermal_data = cp * first_masso * thetaoga_anomaly_data

        calc_trend(ohc_anomaly_data, 'OHC', 'J')
        calc_trend(thermal_data, 'thermal OHC', 'J')

        ax_top.plot(ohc_anomaly_data, color='#272727', label='OHC ($H$)')
        ax_top.plot(thermal_data, color='tab:red', label='OHC temperature component ($H_T$)')

        thermal_data_cubic_dedrifted = dedrift_data(thermal_data, fit='cubic')
        thermal_data_cubic_dedrifted_smoothed = timeseries.runmean(thermal_data_cubic_dedrifted, 10)

        ax_middle.plot(thermal_data_cubic_dedrifted_smoothed, color='tab:red', label='OHC temperature component ($H_T$)')
    
    if is_masso_timeseries:
        masso_anomaly_data = masso_data - masso_data[0]
        barystatic_data = cp * cube_dict['thetaoga'].data[0] * masso_anomaly_data    
        calc_trend(barystatic_data, 'barystatic OHC', 'J')
        ax_top.plot(barystatic_data, color='tab:blue', label='OHC barystatic component ($H_M$)')

    # Optional data

    if cube_dict['rsdt'] and cube_dict['rlut'] and cube_dict['rsut']:
        nettoa_data = cube_dict['rsdt'].data - cube_dict['rlut'].data - cube_dict['rsut'].data
        nettoa_cumsum_data = numpy.cumsum(nettoa_data)
        nettoa_cumsum_anomaly = nettoa_cumsum_data - nettoa_cumsum_data[0]
        calc_trend(nettoa_cumsum_anomaly, 'cumulative netTOA', 'J')
        ax_top.plot(nettoa_cumsum_anomaly, color='tab:olive', label='time-integrated netTOA ($Q_r$)')
        nettoa_cubic_dedrifted = dedrift_data(nettoa_cumsum_anomaly, fit='cubic')
        nettoa_cubic_dedrifted_smoothed = timeseries.runmean(nettoa_cubic_dedrifted, 10)
        ax_middle.plot(nettoa_cubic_dedrifted_smoothed, color='tab:olive', label='time-integrated netTOA ($Q_r$)')
        if cube_dict['thetaoga']:
            calc_regression(nettoa_cubic_dedrifted, thermal_data_cubic_dedrifted,
                            'cumulative netTOA radiative flux vs thermal OHC anomaly (cubic dedrift, decadal mean)', decadal_mean=True)

    if cube_dict['hfds']:
        net_surface_ocean_heat_flux_data = cube_dict['hfds'].data
        net_ocean_heat_flux_data = cube_dict['hfds'].data
        if cube_dict['hfds'] and cube_dict['hfgeou']:
            net_ocean_heat_flux_data = net_ocean_heat_flux_data + cube_dict['hfgeou'].data
        if cube_dict['hfds'] and cube_dict['hfcorr']:
            net_ocean_heat_flux_data = net_ocean_heat_flux_data + cube_dict['hfcorr'].data

        hfdsgeou_cumsum_data = numpy.cumsum(net_ocean_heat_flux_data)
        hfdsgeou_cumsum_anomaly = hfdsgeou_cumsum_data - hfdsgeou_cumsum_data[0]
        calc_trend(hfdsgeou_cumsum_anomaly, 'cumulative hfdsgeou', 'J')
        ax_top.plot(hfdsgeou_cumsum_anomaly, color='tab:orange', label='time-integrated heat flux\ninto ocean ($Q_h$)')

        if cube_dict['hfgeou'] or cube_dict['hfcorr']:
            hfds_cumsum_data = numpy.cumsum(net_surface_ocean_heat_flux_data)
            hfds_cumsum_anomaly = hfds_cumsum_data - hfds_cumsum_data[0]
            calc_trend(hfds_cumsum_anomaly, 'cumulative hfds', 'J')
            ax_top.plot(hfds_cumsum_anomaly, color='tab:orange', linestyle=':', label='hfds only')
        else:
            calc_trend(hfdsgeou_cumsum_anomaly, 'cumulative hfds', 'J')

        hfdsgeou_cubic_dedrifted = dedrift_data(hfdsgeou_cumsum_anomaly, fit='cubic')
        hfdsgeou_cubic_dedrifted_smoothed = timeseries.runmean(hfdsgeou_cubic_dedrifted, 10)
        ax_middle.plot(hfdsgeou_cubic_dedrifted_smoothed, color='tab:orange', label='time-integrated heat flux into ocean ($Q_h$)')
        if cube_dict['thetaoga']:
            calc_regression(hfdsgeou_cubic_dedrifted, thermal_data_cubic_dedrifted,
                            'cumulative heat flux into ocean vs thermal OHC anomaly (cubic dedrift, decadal mean)', decadal_mean=True)
        if cube_dict['rsdt'] and cube_dict['rlut'] and cube_dict['rsut']:
            calc_regression(nettoa_cubic_dedrifted, hfdsgeou_cubic_dedrifted,
                            'cumulative netTOA radiative flux vs cumulative heat flux into ocean (cubic dedrift, decadal mean)', decadal_mean=True)

    if ylim:
        ax_top.set_ylim(ylim[0] * 1e24, ylim[1] * 1e24)

    ax_top.set_title('(a) global energy budget')
    ax_middle.set_title('(d) global energy budget (de-drifted)')
    ax_middle.set_xlabel('year')
    ax_top.set_ylabel('equivalent OHC anomaly (J)')
    ax_top.yaxis.set_label_coords(-0.1, 0.2)
    ax_top.yaxis.major.formatter._useMathText = True
    ax_middle.yaxis.major.formatter._useMathText = True
    ax_top.legend()


def plot_sea_level(ax_top, ax_middle, masso_data, cube_dict, ylim=None):
    """Plot the sea level timeseries and it's components"""

    is_masso_timeseries = type(masso_data) != float
    first_masso = masso_data[0] if is_masso_timeseries else masso_data

    ax_top.grid(linestyle=':')
    ax_middle.grid(linestyle=':')

    if is_masso_timeseries:
        masso_anomaly_data = masso_data - masso_data[0]
        calc_trend(masso_anomaly_data, 'global ocean mass', 'kg')
        ax_top.plot(masso_anomaly_data, color='tab:blue', label='ocean mass ($M$)')
        masso_cubic_dedrifted = dedrift_data(masso_anomaly_data, fit='cubic')
        masso_cubic_dedrifted_smoothed = timeseries.runmean(masso_cubic_dedrifted, 10)
        ax_middle.plot(masso_cubic_dedrifted_smoothed, color='tab:blue', label='ocean mass ($M$)')

    if cube_dict['soga']:
        calc_trend(cube_dict['soga'].data, 'global mean salinity', 'g/kg')
        s_orig = numpy.ones(cube_dict['soga'].data.shape[0]) * cube_dict['soga'].data[0]
        m_orig = numpy.ones(cube_dict['soga'].data.shape[0]) * first_masso
        masso_from_soga = numpy.fromiter(map(delta_masso_from_soga, s_orig, cube_dict['soga'].data, m_orig), float)
        calc_trend(masso_from_soga, 'global mean salinity', 'kg')
        ax_top.plot(masso_from_soga, color='tab:green', label='ocean salinity ($S$)')
        soga_cubic_dedrifted = dedrift_data(masso_from_soga, fit='cubic')
        soga_cubic_dedrifted_smoothed = timeseries.runmean(soga_cubic_dedrifted, 10)
        ax_middle.plot(soga_cubic_dedrifted_smoothed, color='tab:green', label='ocean salinity ($S$)')
        if is_masso_timeseries:
            soga_from_masso = numpy.fromiter(map(delta_soga_from_masso, m_orig, masso_data, s_orig), float)
            calc_trend(soga_from_masso, 'global ocean mass', 'g/kg')
            calc_regression(masso_cubic_dedrifted, soga_cubic_dedrifted,
                            'change in global ocean mass vs global mean salinity anomaly (cubic dedrift, decadal mean)', decadal_mean=True)

    # Optional variables
    if cube_dict['wfonocorr']:
        wfonocorr_cumsum_data = numpy.cumsum(cube_dict['wfonocorr'].data)
        wfonocorr_cumsum_anomaly = wfonocorr_cumsum_data - wfonocorr_cumsum_data[0]
        ax_top.plot(wfonocorr_cumsum_anomaly, color='tab:gray', linestyle=':',
                    label='cumulative surface freshwater flux (no flux correction)')

    if cube_dict['wfo']:
        wfo_cumsum_data = numpy.cumsum(cube_dict['wfo'].data)
        wfo_cumsum_anomaly = wfo_cumsum_data - wfo_cumsum_data[0]
        calc_trend(wfo_cumsum_anomaly, 'cumulative wfo', 'kg')
        ax_top.plot(wfo_cumsum_anomaly, color='tab:gray',
                    label='time-integrated ocean\nfreshwater flux ($Q_m$)')

        wfo_cubic_dedrifted = dedrift_data(wfo_cumsum_anomaly, fit='cubic')
        wfo_cubic_dedrifted_smoothed = timeseries.runmean(wfo_cubic_dedrifted, 10)
        ax_middle.plot(wfo_cubic_dedrifted_smoothed, color='tab:gray',
                       label='time-integrated freshwater flux ($Q_m$)')
        
        if is_masso_timeseries:
            calc_regression(wfo_cubic_dedrifted, masso_cubic_dedrifted,
                            'cumulative surface freshwater flux vs change in global ocean mass (cubic dedrift, decadal mean)', decadal_mean=True)        
        if cube_dict['soga']:
            calc_regression(wfo_cubic_dedrifted, soga_cubic_dedrifted,
                            'cumulative surface freshwater flux vs global mean salinity anomaly (cubic dedrift, decadal mean)', decadal_mean=True)

    if ylim:
        ax_top.set_ylim(ylim[0], ylim[1])

    ax_top.set_title('(b) ocean mass budget')
    ax_middle.set_title('(e) ocean mass budget (de-drifted)')
    ax_middle.set_xlabel('year')
    ax_top.set_ylabel('water mass anomaly (kg)')
    ax_top.yaxis.set_label_coords(-0.12, 0.2)
    ax_top.yaxis.major.formatter._useMathText = True
    ax_middle.yaxis.major.formatter._useMathText = True
    ax_top.legend()


def plot_atmosphere(ax_top, ax_middle, cube_dict, ylim=None):
    """Plot atmospheric mass reservoir and fluxes"""
    
    if cube_dict['prw']:
        massa_data = cube_dict['prw'].data
        massa_anomaly_data = massa_data - massa_data[0]
        calc_trend(massa_anomaly_data, 'global atmospheric water mass', 'kg')
        ax_top.grid(linestyle=':')
        ax_top.plot(massa_anomaly_data, color='tab:purple', label='atmospheric water vapor mass ($M_a$)')
        massa_cubic_dedrifted = dedrift_data(massa_anomaly_data, fit='cubic')
        ax_middle.grid(linestyle=':')

    if cube_dict['evspsbl'] and cube_dict['pr']:
        wfa_data = cube_dict['evspsbl'].data - cube_dict['pr'].data
        wfa_cumsum_data = numpy.cumsum(wfa_data)
        wfa_cumsum_anomaly = wfa_cumsum_data - wfa_cumsum_data[0]
        calc_trend(wfa_cumsum_anomaly, 'cumulative wfa', 'kg')
        ax_top.plot(wfa_cumsum_anomaly, color='tab:cyan',
                    label='time-integrated moisture flux\ninto atmosphere ($Q_{ep}$)')
        wfa_cubic_dedrifted = dedrift_data(wfa_cumsum_anomaly, fit='cubic')

    if cube_dict['prw'] and cube_dict['evspsbl'] and cube_dict['pr']:
        wfa_cubic_dedrifted_smoothed = timeseries.runmean(wfa_cubic_dedrifted, 10)
        massa_cubic_dedrifted_smoothed = timeseries.runmean(massa_cubic_dedrifted, 10)
        ax_middle.plot(wfa_cubic_dedrifted_smoothed, color='tab:cyan')
        ax_middle.plot(massa_cubic_dedrifted_smoothed, color='tab:purple')
        calc_regression(wfa_cubic_dedrifted_smoothed, massa_cubic_dedrifted_smoothed,
                        'cumulative water flux into atmosphere (E-P) vs atmospheric water mass (cubic dedrift, annual mean, 10 year running mean)')

    if ylim:
        ax_top.set_ylim(ylim[0], ylim[1])

    ax_top.set_title('(c) atmospheric water budget')
    ax_middle.set_title('(f) atmospheric water budget (de-drifted)')
    ax_middle.set_xlabel('year')
    ax_top.set_ylabel('water mass anomaly (kg)')
    ax_top.yaxis.set_label_coords(-0.12, 0.2)
    ax_top.yaxis.major.formatter._useMathText = True
    ax_middle.yaxis.major.formatter._useMathText = True
    ax_top.legend()


def get_manual_file_dict(file_list):
    """Put the manually entered files into a dict"""

    file_dict = {}
    for files in file_list:
        variable = files[0].split('/')[-1].split('_')[0]
        experiment = files[0].split('/')[-1].split('_')[3]
        if 'area' in variable:
            file_dict[variable] = files
        else:
            file_dict[(variable, experiment)] = files

    return file_dict 


def common_time_period(cube_dict):
    """Get the common time period for comparison."""

    # Define a reference time period
    for var, cube in cube_dict.items():
        if cube and var not in ['areacello', 'areacella']:
            ref_years = cube_dict[var].coord('year').points
            ref_var = var
            break

    # Set common time period
    minlen = len(ref_years)
    for var, cube in cube_dict.items():
        if cube and var not in [ref_var, 'areacello', 'areacella']:
            years = cube.coord('year').points
            nyrs = len(years)
            if nyrs < minlen:
                assert ref_years[0:nyrs][0] == years[0], f'mismatch in time axes between {var} and {ref_var} (reference)'
                assert ref_years[0:nyrs][-1] == years[-1], f'mismatch in time axes between {var} and {ref_var} (reference)'
                ref_years = years
                minlen = len(years)

    for var, cube in cube_dict.items():
        if cube and var not in ['areacello', 'areacella']:
            cube_dict[var] = cube[0: minlen]

    return cube_dict
  

def plot_comparison(inargs, cube_dict, branch_year_dict):
    """Plot the budget comparisons."""
    
    cube_dict = common_time_period(cube_dict)

    if inargs.volo:
        masso_data = cube_dict['volo'].data * inargs.density
    elif cube_dict['masso']:
        masso_data = cube_dict['masso'].data
    else:
        masso_data = 1.35e21

    fig = plt.figure(figsize=[30, 12])
    gs = gridspec.GridSpec(3, 3, hspace=0.3)
    ax1 = plt.subplot(gs[0:2, 0])
    ax2 = plt.subplot(gs[0:2, 1])
    ax3 = plt.subplot(gs[0:2, 2])
    ax4 = plt.subplot(gs[2, 0])
    ax5 = plt.subplot(gs[2, 1])
    ax6 = plt.subplot(gs[2, 2])

    linestyles = itertools.cycle(('-', '-', '--', '--', ':', ':', '-.', '-.'))
    for experiment, branch_year in branch_year_dict.items():
        ax1.axvline(branch_year, linestyle=next(linestyles), color='0.5', alpha=0.5, label=experiment+' branch time')
        ax2.axvline(branch_year, linestyle=next(linestyles), color='0.5', alpha=0.5, label=experiment+' branch time')

    plot_ohc(ax1, ax4, masso_data, inargs.cpocean, cube_dict, ylim=inargs.ohc_ylim)
    plot_sea_level(ax2, ax5, masso_data, cube_dict, ylim=inargs.sealevel_ylim)
    plot_atmosphere(ax3, ax6, cube_dict)

    plt.subplots_adjust(top=0.92)
    #ax1.text(0.03, 0.08, '(a)', transform=ax1.transAxes, fontsize=22, va='top')
    #ax2.text(0.03, 0.08, '(b)', transform=ax2.transAxes, fontsize=22, va='top')
    #ax3.text(0.03, 0.15, '(c)', transform=ax3.transAxes, fontsize=22, va='top')
    #ax4.text(0.03, 0.15, '(d)', transform=ax4.transAxes, fontsize=22, va='top')

    if inargs.title:
        title = '%s, %s, piControl'  %(inargs.model, inargs.run)
        plt.suptitle(title)

    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.compfile, bbox_inches='tight', dpi=dpi)


def get_branch_years(inargs, manual_file_dict, manual_branch_time):
    """Get the branch year for various experiments"""

    thetaoga_cube = read_global_variable(inargs.model, 'thetaoga', inargs.run, inargs.project,
                                         manual_file_dict, inargs.ignore_list)
    control_time_axis = thetaoga_cube.coord('time').points
    branch_years = {}
    for experiment in ['historical', '1pctCO2']:
        cube = read_global_variable(inargs.model, 'thetaoga', inargs.run, inargs.project,
                                    manual_file_dict, inargs.ignore_list, experiment=experiment)
        if cube:
            if manual_branch_time:
                branch_time = manual_branch_time
            else:
                try:
                    branch_time = cube.attributes['branch_time']
                except KeyError:
                    branch_time = cube.attributes['branch_time_in_parent']
            branch_years[experiment] = get_start_year(branch_time, control_time_axis)
    
    return branch_years


def get_log_text(extra_notes_list):
    """Write the metadata to file."""

    flat_list = [item for sublist in extra_notes_list for item in sublist]
    flat_list = list(set(flat_list))
    flat_list.sort()
    log_text = cmdprov.new_log(git_repo=repo_dir, extra_notes=flat_list)

    return log_text


def main(inargs):
    """Run the program."""

    manual_file_dict = get_manual_file_dict(inargs.manual_files)
    if inargs.forced_experiments:
        branch_year_dict = get_branch_years(inargs, manual_file_dict, inargs.branch_time)
    else:
        branch_year_dict = {}

    cube_dict = get_data_dict(inargs, manual_file_dict, branch_year_dict)

    if inargs.rawfile:
        plot_raw(inargs, cube_dict, branch_year_dict, manual_file_dict)
        log_text = get_log_text(processed_files)
        log_file = re.sub('.png', '.met', inargs.rawfile)
        cmdprov.write_log(log_file, log_text)

    if inargs.compfile:
        plot_comparison(inargs, cube_dict, branch_year_dict)
        processed_files.append(numbers_out_list)
        log_text = get_log_text(processed_files)
        log_file = re.sub('.png', '.met', inargs.compfile)
        cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot variables relevant for the global energy and water budget'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("model", type=str, help="Model (use dots not dashes between numbers in model names)")
    parser.add_argument("run", type=str, help="Run (e.g. r1i1p1)")
    parser.add_argument("project", type=str, choices=('cmip5', 'cmip6'), help="Project")

    parser.add_argument("--rawfile", type=str, default=None, help="Output raw data file name")
    parser.add_argument("--compfile", type=str, default=None, help="Output comparison data file name")

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Limit time period by date range [default = entire]")
    parser.add_argument("--start_index", type=int, default=0,
                        help="Limit time period by start index on annual timeseries [default = entire]")
    parser.add_argument("--end_index", type=int, default=None,
                        help="Limit time period by end index on annual timeseries [default = entire]")

    parser.add_argument("--volo", action="store_true", default=False,
                        help="Use volo to calculate masso (useful for boussinesq models)")
    parser.add_argument("--chunk", action="store_true", default=False,
                        help="Chunk annual mean calculation for spatial variables (useful for boussinesq models)")
    parser.add_argument("--forced_experiments", action="store_true", default=False,
                        help="Plot the forced experiments (raw) or their branch time (comparison)")
    parser.add_argument("--areacella", type=str, nargs='*', default=[],
                        help="ocean surface fluxes on an atmosphere grid")

    parser.add_argument("--cpocean", type=float, default=4000,
                        help="Specific heat in ocean in J/(kg K)")
    parser.add_argument("--density", type=float, default=1026,
                        help="Reference density in kg / m3")

    parser.add_argument("--branch_time", type=float, default=None,
                        help="Override branch time from file attributes with this one")
    parser.add_argument("--manual_files", type=str, action="append", nargs='*', default=[],
                        help="Use these manually entered files instead of the clef search")
    parser.add_argument("--ignore_list", type=str, nargs='*', default=[],
                        help="Variables to ignore")
    parser.add_argument("--ohc_ylim", type=float, nargs=2, metavar=('LOWER_LIMIT', 'UPPER_LIMIT'), default=None,
                        help="y-axis limits for OHC plot (*1e24) [default = auto]")
    parser.add_argument("--sealevel_ylim", type=float, nargs=2, metavar=('LOWER_LIMIT', 'UPPER_LIMIT'), default=None,
                        help="y-axis limits for sea level plot [default = auto]")
    
    parser.add_argument("--title", action="store_true", default=False,
                        help="Include a plot title [default=False]")
    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()             
    main(args)

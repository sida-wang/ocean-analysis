"""
Filename:     calc_inferred_hfds.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Infer hfds from the other surface fluxes

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris

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
    import grids
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def add_metadata(hfds_cube, hfss_atts, inargs):
    """Add metadata to the output cube."""

    standard_name = 'surface_downward_heat_flux_in_sea_water'
    long_name = 'Downward Heat Flux at Sea Water Surface'
    var_name = 'hfds'
    units = 'W m-2'

    hfds_cube.standard_name = standard_name
    hfds_cube.long_name = long_name
    hfds_cube.var_name = var_name
    hfds_cube.units = units

    hfds_cube.attributes = hfss_atts
    hfds_cube.attributes['history'] = gio.write_metadata()

    return hfds_cube


def get_data(filename, var, target_grid=None):
    """Read data.
    
    Positive is defined as down.
    
    """
    
    if filename:
        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load_cube(filename, gio.check_iris_var(var))
            cube = gio.check_time_units(cube)
            cube = iris.util.squeeze(cube)

            if target_grid:
                cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(cube, target_grid_cube=target_grid)

            coord_names = [coord.name() for coord in cube.dim_coords]
            if 'depth' in coord_names:
                depth_constraint = iris.Constraint(depth=0)
                cube = cube.extract(depth_constraint)

            if 'up' in cube.standard_name:
                cube.data = cube.data * -1
    else:
        cube = None

    return cube


def derived_radiation_fluxes(cube_dict, inargs):
    """Calculate the net shortwave, longwave and total radiation flux."""

    if inargs.rsds_files and inargs.rsus_files:
        cube_dict['rsns'] = cube_dict['rsds'] + cube_dict['rsus']   # net shortwave flux
    else:
        cube_dict['rsns'] = None
    
    if inargs.rlds_files and inargs.rlus_files:
        cube_dict['rlns'] = cube_dict['rlds'] + cube_dict['rlus']   # net longwave flux
    else:
        cube_dict['rlns'] = None

    if inargs.rsds_files and inargs.rsus_files and inargs.rlds_files and inargs.rlus_files:
        cube_dict['rns'] = cube_dict['rsns'] + cube_dict['rlns']

    return cube_dict


def infer_hfds(cube_dict, sftlf_cube, target_grid, inargs):
    """Infer the downward heat flux into ocean."""
    
    data_list = [cube_dict['hfls'], cube_dict['hfss'], cube_dict['rns']]
    if inargs.hfsithermds_files:
         hfsithermds_cube = cube_dict['hfsithermds'].regrid(target_grid, iris.analysis.Linear())
         data_list.append(hfsithermds_cube)
    else:
         hfsithermds_cube = 0.0

    iris.util.unify_time_units(data_list)

    cube_dict['hfds-inferred'] = cube_dict['rns'] + cube_dict['hfls'] + cube_dict['hfss'] + hfsithermds_cube
    cube_dict['hfds-inferred'] = uconv.apply_land_ocean_mask(cube_dict['hfds-inferred'], sftlf_cube, 'ocean')
    cube_dict['hfds-inferred'] = add_metadata(cube_dict['hfds-inferred'], cube_dict['hfss'].attributes, inargs)    
        
    return cube_dict


def check_inputs(inargs):
    """Check for the correct number of input files"""

    nfiles = len(inargs.rsds_files)
    for files in [inargs.rsus_files, inargs.rlds_files, inargs.rlus_files, inargs.hfss_files, inargs.hfls_files]:
        assert len(files) == nfiles 

    if inargs.hfsithermds_files:
        assert len(inargs.hfsithermds_files) == nfiles

    return nfiles
       

def get_outfile_name(rsds_file):
    """Define the output file name using the rsds file name as a template."""

    rsds_components = rsds_file.split('/')

    rsds_filename = rsds_components[-1]  
    rsds_components.pop(-1)
    rsds_dir = "/".join(rsds_components)

    hfds_filename = rsds_filename.replace('rsds', 'hfds-inferred')
    hfds_filename = hfds_filename.replace('Amon', 'Omon')
    hfds_dir = rsds_dir.replace('rsds', 'hfds')
    hfds_dir = hfds_dir.replace('ua6', 'r87/dbi599')
    hfds_dir = hfds_dir.replace('atmos', 'ocean')

    mkdir_command = 'mkdir -p ' + hfds_dir

    print(mkdir_command)
    os.system(mkdir_command)

    return hfds_dir + '/' + hfds_filename


def main(inargs):
    """Run the program."""

    sftlf_cube = iris.load_cube(inargs.sftlf_file, 'land_area_fraction')

    cube_dict = {}
    nfiles = check_inputs(inargs)
    for fnum in range(nfiles):
        cube_dict['rsds'] = get_data(inargs.rsds_files[fnum], 'surface_downwelling_shortwave_flux_in_air')
        cube_dict['rsus'] = get_data(inargs.rsus_files[fnum], 'surface_upwelling_shortwave_flux_in_air')
        cube_dict['rlds'] = get_data(inargs.rlds_files[fnum], 'surface_downwelling_longwave_flux_in_air')
        cube_dict['rlus'] = get_data(inargs.rlus_files[fnum], 'surface_upwelling_longwave_flux_in_air')
        cube_dict = derived_radiation_fluxes(cube_dict, inargs)
 
        cube_dict['hfss'] = get_data(inargs.hfss_files, 'surface_upward_sensible_heat_flux')
        cube_dict['hfls'] = get_data(inargs.hfls_files, 'surface_upward_latent_heat_flux')

        rsds_slice = next(cube_dict['rsds'].slices(['latitude', 'longitude']))
        cube_dict['hfsithermds'] = get_data(inargs.hfsithermds_files,
                                            'heat_flux_into_sea_water_due_to_sea_ice_thermodynamics',
                                            target_grid=rsds_slice)                          
        cube_dict = infer_hfds(cube_dict, sftlf_cube, rsds_slice, inargs)

        hfds_file = get_outfile_name(inargs.rsds_files[fnum])  
        iris.save(cube_dict['hfds-inferred'], hfds_file)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Infer hfds from the other surface fluxes'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("sftlf_file", type=str, help="Land fraction file")

    parser.add_argument("--rsds_files", type=str, nargs='*', default=None,
                        help="surface downwelling shortwave flux files")
    parser.add_argument("--rsus_files", type=str, nargs='*', default=None,
                        help="surface upwelling shortwave flux files")
    parser.add_argument("--rlds_files", type=str, nargs='*', default=None,
                        help="surface downwelling longwave flux files")
    parser.add_argument("--rlus_files", type=str, nargs='*', default=None,
                        help="surface upwelling longwave flux files")

    parser.add_argument("--hfss_files", type=str, nargs='*', default=None,
                        help="surface sensible heat flux files")
    parser.add_argument("--hfls_files", type=str, nargs='*', default=None,
                        help="surface latent heat flux files")
    parser.add_argument("--hfsithermds_files", type=str, nargs='*', default=None,
                        help="heat flux due to sea ice files")

    args = parser.parse_args()             
    main(args)
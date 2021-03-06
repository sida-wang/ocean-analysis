"""
Filename:     calc_basin.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Create a CMIP5 basin file

"""

# Import general Python modules

import sys, os, pdb
import argparse

import numpy
import iris
import cmdline_provenance as cmdprov

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
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def construct_basin_cube(basin_array, global_atts, dim_coords):
    """Construct the new basin cube """

    dim_coords_list = []
    for i, coord in enumerate(dim_coords):
        dim_coords_list.append((coord, i))

    basin_cube = iris.cube.Cube(basin_array,
                                standard_name='region',
                                long_name='Region Selection Index',
                                var_name='basin',
                                units='1',
                                attributes=global_atts,
                                dim_coords_and_dims=dim_coords_list) 

    basin_cube.attributes['flag_values'] = "11 12 13 14 15 16 17 18"
    basin_cube.attributes['flag_meanings'] = "north_atlantic south_atlantic north_pacific south_pacific indian arctic marginal_seas land" 

    return basin_cube


def check_lon_coord(lon_coord):
    """Check that the lon coord is [0, 360)"""

    lon_coord.points = numpy.where(lon_coord.points < 0.0, lon_coord.points + 360, lon_coord.points)
    lon_coord.points = numpy.where(lon_coord.points >= 360.0, lon_coord.points - 360, lon_coord.points)

    assert lon_coord.points.min() >= 0
    assert lon_coord.points.max() < 360

    return lon_coord


def basins_from_cmip(cmip_basin_cube, lat_array, lon_array, pacific_lon_bounds, indian_lon_bounds):
    """Define basins using CMIP basin file information.

      CMIP definitions: 
        land = 0, southern ocean = 1, atlantic = 2, pacific = 3,
        arctic = 4, indian = 5, mediterranean = 6, black sea = 7,
        hudson bay = 8, baltic sea = 9, red sea = 10

      Ouput array definitions:
        north atlantic = 11
        south atlantic = 12
        north pacific = 13
        south pacific = 14
        indian = 15
        arctic = 16
        marginal seas = 17
        land = 18

    """

    # Break up the southern ocean
    basin_array = numpy.where(cmip_basin_cube.data == 1, 12, cmip_basin_cube.data)
    basin_array = numpy.where((basin_array == 12) & (lon_array >= pacific_lon_bounds[0]) & (lon_array <= pacific_lon_bounds[1]), 14, basin_array)
    basin_array = numpy.where((basin_array == 12) & (lon_array >= indian_lon_bounds[0]) & (lon_array <= indian_lon_bounds[1]), 15, basin_array)

    # Define the rest of the new regions
    basin_array = numpy.where((basin_array == 2) & (lat_array >= 0), 11, basin_array)
    basin_array = numpy.where((basin_array == 2) & (lat_array < 0), 12, basin_array)
    basin_array = numpy.where((basin_array == 3) & (lat_array >= 0), 13, basin_array)
    basin_array = numpy.where((basin_array == 3) & (lat_array < 0), 14, basin_array)
    basin_array = numpy.where(basin_array == 5, 15, basin_array)
    basin_array = numpy.where(basin_array == 4, 16, basin_array)
    basin_array = numpy.where(basin_array == 0, 18, basin_array)
    basin_array = numpy.where((basin_array >= 6) & (basin_array <= 10), 17, basin_array)

    assert basin_array.min() == 11
    assert basin_array.max() == 18

    return basin_array


def basins_manually(cube, lat_array, lon_array, pacific_lon_bounds, indian_lon_bounds):
    """Define basins manually (i.e. without assistance from CMIP basin file)

    in the output array:
      north atlantic = 11
      south atlantic = 12
      north pacific = 13
      south pacific = 14
      indian = 15
      arctic = 16
      marginal seas = 17
      land = 18

    """

    assert cube.shape == lat_array.shape == lon_array.shape 

    # Split the world into three basins
    basin_array = numpy.ones(lat_array.shape) * 11
    basin_array = numpy.where((lon_array >= pacific_lon_bounds[0]) & (lon_array <= pacific_lon_bounds[1]), 13, basin_array)
    basin_array = numpy.where((lon_array >= indian_lon_bounds[0]) & (lon_array <= indian_lon_bounds[1]), 15, basin_array)
    basin_array = numpy.where((basin_array == 13) & (lon_array >= 275) & (lat_array >= 9), 11, basin_array)
    basin_array = numpy.where((basin_array == 13) & (lon_array >= 260) & (lat_array >= 16), 11, basin_array)
    basin_array = numpy.where((basin_array == 15) & (lon_array >= 105) & (lat_array >= -8), 13, basin_array)
    basin_array = numpy.where((basin_array == 15) & (lat_array >= 25), 17, basin_array)

    # Break Pacific and Atlantic into north and south
    basin_array = numpy.where((basin_array == 11) & (lat_array < 0), 12, basin_array)
    basin_array = numpy.where((basin_array == 13) & (lat_array < 0), 14, basin_array)

    # Marginal seas
    hudson_lat_bounds = [51, 75]
    hudson_lon_bounds = [265, 296]
    basin_array = numpy.where((lon_array >= hudson_lon_bounds[0]) & (lon_array <= hudson_lon_bounds[1]) & (lat_array >= hudson_lat_bounds[0]) & (lat_array <= hudson_lat_bounds[1]), 17, basin_array)

    baltic_lat_bounds = [54, 65.5]
    baltic_lon_bounds = [8.5, 33]
    basin_array = numpy.where((lon_array >= baltic_lon_bounds[0]) & (lon_array <= baltic_lon_bounds[1]) & (lat_array >= baltic_lat_bounds[0]) & (lat_array <= baltic_lat_bounds[1]), 17, basin_array)

    med_red_black_lat_bounds = [12.5, 45.5]
    med_red_black_lon_bounds1 = [0, 43]
    med_red_black_lon_bounds2 = [354, 360]
    basin_array = numpy.where((lon_array >= med_red_black_lon_bounds1[0]) & (lon_array <= med_red_black_lon_bounds1[1]) & (lat_array >= med_red_black_lat_bounds[0]) & (lat_array <= med_red_black_lat_bounds[1]), 17, basin_array)
    basin_array = numpy.where((lon_array >= med_red_black_lon_bounds2[0]) & (lon_array <= med_red_black_lon_bounds2[1]) & (lat_array >= med_red_black_lat_bounds[0]) & (lat_array <= med_red_black_lat_bounds[1]), 17, basin_array)

    basin_array = numpy.where(lat_array >= 67, 16, basin_array)  # arctic ocean

    assert cube.data.mask.shape, "reference data needs land mask"
    basin_array = numpy.where(cube.data.mask == True, 18, basin_array)  # Land
    
    assert basin_array.min() == 11
    assert basin_array.max() == 18

    return basin_array


def create_basin_array(cube, ref_is_basin):
    """Create an ocean basin array.

    Args:
      cube - reference cube (iris.cube.Cube)
      ref_is_basin - flag to indicate if ref cube is a CMIP basin cube (bool)

    """

    # Build latitude and longitude reference arrays
    lat_coord = cube.coord('latitude')
    lon_coord = cube.coord('longitude')    
    if lat_coord.ndim == 1:
        # rectilinear grid
        lat_axis = lat_coord.points
        lon_axis = uconv.adjust_lon_range(lon_coord.points, radians=False)
        coord_names = [coord.name() for coord in cube.dim_coords]
        lat_index = coord_names.index('latitude')
        lon_index = coord_names.index('longitude')
        lat_array = uconv.broadcast_array(lat_axis, lat_index, cube.shape)
        lon_array = uconv.broadcast_array(lon_axis, lon_index, cube.shape)
    else:
        # curvilinear grid
        lon_coord = check_lon_coord(lon_coord)
        assert cube.ndim == 2
        lat_array = lat_coord.points
        lon_array = lon_coord.points

    # Create basin array
    pacific_lon_bounds = [147, 294]
    indian_lon_bounds = [23, 147]
    if ref_is_basin:
        basin_array = basins_from_cmip(cube, lat_array, lon_array, pacific_lon_bounds, indian_lon_bounds)
    else:
        basin_array = basins_manually(cube, lat_array, lon_array, pacific_lon_bounds, indian_lon_bounds)    

    return basin_array
    
 
def main(inargs):
    """Run the program."""

    ref_cube = iris.load_cube(inargs.ref_file, inargs.ref_var)
    coord_names = [coord.name() for coord in ref_cube.dim_coords]
    if ref_cube.ndim == 4:
        ref_cube = ref_cube[0, 0, ::]
        ref_cube.remove_coord(coord_names[0])
        ref_cube.remove_coord(coord_names[1])
    elif ref_cube.ndim == 3:
        ref_cube = ref_cube[0, ::]
        ref_cube.remove_coord(coord_names[0])
    else:
        assert ref_cube.ndim == 2

    if inargs.sftlf_file:
        sftlf_cube = iris.load_cube(inargs.sftlf_file, 'land_area_fraction')
        ref_cube = uconv.apply_land_ocean_mask(ref_cube, sftlf_cube, 'ocean',
                                               threshold=inargs.land_threshold)
        
    ref_is_basin = ref_cube.var_name == 'basin'
    basin_array = create_basin_array(ref_cube, ref_is_basin)
    basin_cube = construct_basin_cube(basin_array, ref_cube.attributes, ref_cube.dim_coords)    
    basin_cube.attributes['history'] = cmdprov.new_log(git_repo=repo_dir)

    iris.save(basin_cube, inargs.out_file)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com  

"""

    description='Create an improved CMIP-style basin file (north/south designated and no Southern Ocean)'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("ref_file", type=str, help="Reference file for grid information. Use a CMIP basin file if possible (helps for fine details and masking marginal seas)")
    parser.add_argument("ref_var", type=str, help="Variable standard_name")
    parser.add_argument("out_file", type=str, help="Output file name")

    parser.add_argument("--sftlf_file", type=str, default=None,
                        help="Name of sftlf file to use for land values (required for atmos files)")
    parser.add_argument("--land_threshold", type=float, default=0.1,
                        help="Percentage of land in grid cell below which it is considered an ocean cell")

    args = parser.parse_args()
    main(args)


"""
Filename:     calc_salinity_temperature_profile.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate salinity vs temperature profile  

"""

# Import general Python modules

import sys
import os
import re
import pdb
import argparse

import numpy
import pandas

import iris
import iris.coord_categorisation
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
    import general_io as gio
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

ocean_names = {0: 'land', 1: 'southern_ocean', 2: 'atlantic', 
               3: 'pacific', 4: 'arctic', 5: 'indian', 
               6: 'mediterranean', 7: 'black_sea', 8: 'hudson_bay',
               9: 'baltic_sea', 10: 'red_sea'}

def get_ocean_name(ocean_num):
    return ocean_names[ocean_num]


def select_basin(df, basin_name):
    """Select basin"""

    if not basin_name == 'globe':
        df['basin'] = df['basin'].apply(get_ocean_name)
        basin_components = basin_name.split('_')
        if len(basin_components) == 1:
            ocean = basin_components[0]
            hemisphere = None
        else:
            hemisphere, ocean = basin_components

        df = df[(df.basin == ocean)]
        if hemisphere == 'north':
            df = df[(df.latitude > 0)]
        elif hemisphere == 'south':
            df = df[(df.latitude < 0)]

    return df


def create_df(tcube, scube, vcube, bcube, basin):
    """Create DataFrame"""

    tcube = gio.temperature_unit_check(tcube, 'C')
    scube = gio.salinity_unit_check(scube)

    if tcube.ndim == 3:
        lats = uconv.broadcast_array(tcube.coord('latitude').points, [1, 2], tcube.shape)
        lons = uconv.broadcast_array(tcube.coord('longitude').points, [1, 2], tcube.shape)
        levs = uconv.broadcast_array(tcube.coord('depth').points, 0, tcube.shape)
        vdata = vcube.data
        bdata = bcube.data
    elif tcube.ndim == 4:
        lats = uconv.broadcast_array(tcube.coord('latitude').points, [2, 3], tcube.shape)
        lons = uconv.broadcast_array(tcube.coord('longitude').points, [2, 3], tcube.shape)
        levs = uconv.broadcast_array(tcube.coord('depth').points, 1, tcube.shape)
        vdata = uconv.broadcast_array(vcube.data, [1, 3], tcube.shape)
        bdata = uconv.broadcast_array(bcube.data, [1, 3], tcube.shape)

    sdata = scube.data.flatten()
    tdata = tcube.data.flatten()
    vdata = vdata.flatten()
    bdata = bdata.flatten()
    lat_data = lats.flatten()
    lon_data = lons.flatten()
    depth_data = levs.flatten()

    df = pandas.DataFrame(index=range(tdata.shape[0]))
    df['temperature'] = tdata.filled(fill_value=5000)
    df['salinity'] = sdata.filled(fill_value=5000)
    df['volume'] = vdata.filled(fill_value=5000)
    df['basin'] = bdata.filled(fill_value=5000)
    df['latitude'] = lat_data
    df['longitude'] = lon_data
    df['depth'] = depth_data

    df = df[df.temperature != 5000]
    df = df[df.temperature != -273.15]

    if basin:
        df = select_basin(df, basin)

    return df


def get_bounds_list(edges):
    """Create a bounds list from edge list"""

    bounds_list = []
    for i in range(len(edges) - 1):
        interval = [edges[i], edges[i+1]]
        bounds_list.append(interval)

    return numpy.array(bounds_list)


def construct_cube(data, scube, tcube, years, x_values, x_edges):
    """Create the iris cube for output"""

    x_bounds = get_bounds_list(x_edges)

    temperature_coord = iris.coords.DimCoord(x_values,
                                             standard_name=tcube.standard_name,
                                             long_name=tcube.long_name,
                                             var_name=tcube.var_name,
                                             units=tcube.units,
                                             bounds=x_bounds)

    year_coord = iris.coords.DimCoord(years,
                                      standard_name=scube.coord('year').standard_name,
                                      long_name=scube.coord('year').long_name,
                                      var_name=scube.coord('year').var_name,
                                      units=scube.coord('year').units)
    
    dim_coords_list = [(year_coord, 0), (temperature_coord, 1)]
    outcube = iris.cube.Cube(data,
                             standard_name=scube.standard_name,
                             long_name=scube.long_name,
                             var_name=scube.var_name,
                             units=scube.units,
                             attributes=scube.attributes,
                             dim_coords_and_dims=dim_coords_list) 

    return outcube


def main(inargs):
    """Run the program."""

    vcube = iris.load_cube(inargs.volume_file)
    bcube = iris.load_cube(inargs.basin_file)

    tmin, tmax = inargs.temperature_bounds
    tstep = inargs.bin_size
    x_edges = numpy.arange(tmin, tmax, tstep)
    x_values = (x_edges[1:] + x_edges[:-1]) / 2
    extents = [x_values[0], x_values[-1]]
   
    tcube, thistory = gio.combine_files(inargs.temperature_files, 'sea_water_potential_temperature')
    scube, shistory = gio.combine_files(inargs.salinity_files, 'sea_water_salinity')

    iris.coord_categorisation.add_year(tcube, 'time')
    iris.coord_categorisation.add_year(scube, 'time')

    syears = set(scube.coord('year').points)
    tyears = set(tcube.coord('year').points)
    assert syears == tyears
    years = numpy.array(list(syears))
    years.sort()

    outdata = numpy.ma.zeros([len(years), len(x_values)])
    for index, year in enumerate(years):
        print(year)
        year_constraint = iris.Constraint(year=year)
        salinity_year_cube = scube.extract(year_constraint)
        temperature_year_cube = tcube.extract(year_constraint)

        df = create_df(temperature_year_cube, salinity_year_cube,
                       vcube, bcube, basin=inargs.basin)

        svdist, bin_edges = numpy.histogram(df['temperature'].values, bins=x_edges,
                                            weights=df['volume'].values * df['salinity'].values)
        vdist, bin_edges = numpy.histogram(df['temperature'].values, bins=x_edges,
                                           weights=df['volume'].values)
        sdist = svdist / vdist
        outdata[index, :] = sdist

    outdata = numpy.ma.masked_invalid(outdata)
    outcube = construct_cube(outdata, scube, tcube, years, x_values, x_edges)

    # Metadata
    metadata_dict = {inargs.basin_file: bcube.attributes['history'],
                     inargs.volume_file: vcube.attributes['history'],
                     inargs.temperature_files[0]: thistory[0],
                     inargs.salinity_files[0]: shistory[0]}
    log = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    outcube.attributes['history'] = log
    outcube.attributes['ocean_basin'] = inargs.basin

    iris.save(outcube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate ocean volume distribution in T-S space'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("volume_file", type=str, help="Volume file")
    parser.add_argument("basin_file", type=str, help="Basin file")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--temperature_files", type=str, nargs='*',
                        help="Temperature files") 
    parser.add_argument("--salinity_files", type=str, nargs='*',
                        help="Salinity files")

    parser.add_argument("--basin", type=str, default='globe',
                        choices=('globe', 'indian', 'north_atlantic', 'south_atlantic', 'north_pacific', 'south_pacific'),
                        help='ocean basin to plot')

    parser.add_argument("--temperature_bounds", type=float, nargs=2, default=(-2, 30),
                        help='bounds for the temperature (Y) axis')
    parser.add_argument("--bin_size", type=float, default=0.25,
                        help='bin size (i.e. temperature step)')

    args = parser.parse_args()             

    main(args)

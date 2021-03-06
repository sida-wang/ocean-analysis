"""'Calculate the vertical aggregate."""

import sys
script_dir = sys.path[0]
import pdb
import argparse

import iris
import cmdline_provenance as cmdprov

repo_dir = '/'.join(script_dir.split('/')[:-1])
module_dir = repo_dir + '/modules'
sys.path.append(module_dir)
try:
    import timeseries
    import general_io as gio
    import spatial_weights
except ImportError:
    raise ImportError('Script and modules in wrong directories')


def main(inargs):
    """Run the program."""

    cube, history = gio.combine_files(inargs.infiles, inargs.var, checks=True)

    if inargs.annual:
        cube = timeseries.convert_to_annual(cube, chunk=False)  

    if inargs.aggregation == 'sum':
        cube = cube.collapsed('depth', iris.analysis.SUM)
    else:
        dim_coord_names = [coord.name() for coord in cube.dim_coords]
        depth_coord = cube.coord('depth')
        assert depth_coord.units in ['m', 'dbar'], "Unrecognised depth axis units"
        if depth_coord.units == 'm':
            vert_extents = spatial_weights.calc_vertical_weights_1D(depth_coord, dim_coord_names, cube.shape)
        elif depth_coord.units == 'dbar':
            vert_extents = spatial_weights.calc_vertical_weights_2D(depth_coord, cube.coord('latitude'), dim_coord_names, cube.shape)
        cube = cube.collapsed('depth', iris.analysis.MEAN, weights=vert_extents)
    cube.remove_coord('depth')
    
    metadata_dict = {}
    metadata_dict[inargs.infiles[0]] = history
    cube.attributes['history'] = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    iris.save(cube, inargs.outfile)  


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("var", type=str, help="Variable")
    parser.add_argument("aggregation", type=str, choices=('mean', 'sum'), help="Method for zonal aggregation")
    parser.add_argument("outfile", type=str, help="Output file")
    
    parser.add_argument("--annual", action="store_true", default=False,
                        help="Output annual mean [default=False]")

    args = parser.parse_args()           
    main(args)

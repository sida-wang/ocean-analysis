"""
Filename:     apply_mask.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Apply a lat/lon mask to a data file

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
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def check_coords(cube):
    """Check that lat and lon are last two coordinates."""

    coord_names = [coord.name() for coord in cube.dim_coords]
    assert coord_names[-2] == 'latitude'
    assert coord_names[-1] == 'longitude'


def read_data(infile):
    """Read a data file."""

    cube_list = iris.load(infile)
    assert len(cube_list) == 1
    cube = cube_list[0]

    check_coords(cube)

    return cube
    

def copy_mask(mask_cube, target_shape):
    """Copy mask."""

    mask_coords = [coord.name() for coord in mask_cube.dim_coords]

    assert mask_cube.ndim in [2, 3, 4]
    if mask_cube.ndim == 2:
        mask_cube_subset = mask_cube.data
    elif mask_cube.ndim == 3:
        mask_cube_subset = mask_cube[0, ::]
        print(mask_cube_subset.coord(mask_coords[0]))
    else:
        mask_cube_subset = mask_cube[0, 0, ::]
        print(mask_cube_subset.coord(mask_coords[0]))
        print(mask_cube_subset.coord(mask_coords[1]))

    mask = uconv.broadcast_array(mask_cube_subset.data.mask, [mask_cube.ndim - 2, mask_cube.ndim - 1], target_shape)

    return mask


def get_outfile(infile, outfile_list, fnum, fixed=False):
    """Modify the infile to define outfile."""

    if outfile_list:
        outfile = outfile_list[fnum]
    else:
        file_components = infile.split('/')
        file_name = file_components.pop(-1)
        file_dir = "/".join(file_components)

        file_dir = file_dir.replace('ua6', 'r87/dbi599')
        if fixed:
            file_dir = file_dir + '/fixed'

        outfile = file_dir + '/' + file_name
        os.system('mkdir -p %s'  %(file_dir) )

    return outfile
    

def main(inargs):
    """Run the program."""

    if inargs.outfiles:
        assert len(inargs.infiles) == len(inargs.outfiles)

    for fnum, infile in enumerate(inargs.infiles):

        data_cube = read_data(infile)
        mask_cube = read_data(inargs.mask_file)

        if inargs.mask_method == 'copy':    
            assert type(data_cube.data) == numpy.ndarray, "It is assumed that the input data has no mask"

            mask = copy_mask(mask_cube, data_cube.shape)

            data_cube.data = numpy.ma.asarray(data_cube.data)
            data_cube.data.mask = mask

        outfile_metadata = {infile: data_cube.attributes['history'],}
        data_cube.attributes['history'] = gio.write_metadata(file_info=outfile_metadata)

        outfile = get_outfile(infile, inargs.outfiles, fnum, fixed=inargs.fixed)
        print('infile:', infile) 
        print('outfile:', outfile)
       
        if not inargs.dry_run:
            iris.save(data_cube, outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com
"""

    description='Apply a lat/lon mask to a data file'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input data files")
    parser.add_argument("mask_file", type=str, help="Input mask file")
    parser.add_argument("mask_method", type=str, choices=('copy', 'sftlf'), help="Mask method")

    parser.add_argument("--outfiles", type=str, nargs='*', default=None, 
                        help="Custom outfile names (otherwise they are automatically generated)")    

    parser.add_argument("--fixed", action="store_true", default=False,
                        help="Put the output files in a directory labelled fixed")
    parser.add_argument("--dry_run", action="store_true", default=False,
                        help="Print outfile names instead of executing")

    args = parser.parse_args()             

    main(args)
"""
Filename:     plot_pe_heatmap.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot heatmap using output from calc_pe_spatial_totals.py
"""

# Import general Python modules

import sys, os, pdb
import argparse
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def get_data(infile, var, data_type, time_constraint, pct=False):
    """Get the data for a particular model"""
    
    cube, history = gio.combine_files(infile, var, new_calendar='365_day')
    cube = cube.extract(time_constraint)

    if data_type == 'cumulative_anomaly':
        anomaly_data = cube.data - cube.data[0, ::]
        data = anomaly_data[-1, ::]
    elif data_type == 'climatology':
        cube = cube.collapsed('time', iris.analysis.MEAN)
        cube.remove_coord('time')
        dat = cube.data    

    basins = ['Atlantic', 'Pacific', 'Indian', 'Arctic', 'Marginal Seas', 'Land', 'Ocean', 'Globe']
    pe_regions = ['SH Precip', 'SH Evap', 'Tropical Precip', 'NH Evap', 'NH Precip', 'Globe']
    df = pd.DataFrame(data, columns=basins, index=pe_regions)
    df.loc['Globe', 'Globe'] = np.nan
    df = df.iloc[::-1]
    if pct:
        total_pos = df[df['Globe'] > 0]['Globe'].sum()
        total_neg = abs(df[df['Globe'] < 0]['Globe'].sum())
        df = df / max(total_pos, total_neg)
        
    return df, history


def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time_bounds)
    df, history = get_data(inargs.infile, inargs.var, inargs.data_type,
                           time_constraint, pct=inargs.pct)     
    if inargs.scale_factor:
        assert not inargs.pct
        df = df / 10**inargs.scale_factor

    basins_to_plot = ['Atlantic', 'Indian', 'Pacific', 'Arctic', 'Land', 'Globe']
    if inargs.data_type == 'cumulative_anomaly':
        title = 'Time-integrated net mositure (P-E) import/export anomaly, 1850-2014'
    elif inargs.data_type == 'climatology':
        title = 'Annual mean net mositure (P-E) import/export'

    if inargs.pct:
        fmt = '.0%'
        label = 'fraction of total import/export'
    else:
        fmt='.2g'
        if inargs.scale_factor:
            label = 'time-integrated anomaly ($10^{%s}$ kg)'  %(str(inargs.scale_factor))
        else:
            label = 'time-integrated anomaly (kg)'

    vmax = df[basins_to_plot].abs().max().max() * 1.05

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(df[basins_to_plot], annot=True, cmap='BrBG', linewidths=.5, ax=ax,
                vmin=-vmax, vmax=vmax, fmt=fmt,
                cbar_kws={'label': label})
    plt.title(title)
  
    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={inargs.infile: history})


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

example:

"""

    description = 'Plot heatmap using output from calc_pe_spatial_totals.py'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="input file")                                    
    parser.add_argument("var", type=str, help="variable")
    parser.add_argument("data_type", type=str, choices=('cumulative_anomaly', 'climatology'), help="type of data")
    parser.add_argument("outfile", type=str, help="output file") 

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1850-01-01', '2014-12-31'), help="Time period [default = entire]")
    parser.add_argument("--pct", action="store_true", default=False,
                        help="Change output units to percentage of total net import/export")
    parser.add_argument("--scale_factor", type=int, default=None,
                        help="Scale factor (e.g. scale factor of 17 will divide data by 10^17")

    args = parser.parse_args()             
    main(args)
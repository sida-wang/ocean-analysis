"""
Filename:     data_csv.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Take a drift metadata file and output a csv file with the data

"""

# Import general Python modules

import sys, os, pdb
import argparse
import pandas as pd
from operator import add


# Define functions

headers = ['trend, OHC',
           'trend, barystatic OHC',
           'trend, thermal OHC',
           'trend, cumulative hfds',
           'trend, cumulative netTOA',
           'trend, cumulative wfo',
           'trend, global ocean mass',
           'trend, global mean salinity',
           'trend, global ocean mass',
           'trend, barystatic sea level',
           'trend, thermosteric sea level',
           'trend, global ocean mass',
           'ocean surface area',
           'regression coefficient, change in global ocean mass vs global mean salinity anomaly (cubic dedrift, decadal mean)',
           'regression coefficient, change in global ocean mass vs global mean salinity anomaly (cubic dedrift, decadal mean), CI lower',
           'regression coefficient, change in global ocean mass vs global mean salinity anomaly (cubic dedrift, decadal mean), CI upper',           
           'regression coefficient, cumulative netTOA radiative flux vs cumulative surface heat flux (cubic dedrift, decadal mean)',
           'regression coefficient, cumulative netTOA radiative flux vs cumulative surface heat flux (cubic dedrift, decadal mean), CI lower',
           'regression coefficient, cumulative netTOA radiative flux vs cumulative surface heat flux (cubic dedrift, decadal mean), CI upper',
           'regression coefficient, cumulative netTOA radiative flux vs thermal OHC anomaly (cubic dedrift, decadal mean)',
           'regression coefficient, cumulative netTOA radiative flux vs thermal OHC anomaly (cubic dedrift, decadal mean), CI lower',
           'regression coefficient, cumulative netTOA radiative flux vs thermal OHC anomaly (cubic dedrift, decadal mean), CI upper',
           'regression coefficient, cumulative surface freshwater flux vs change in global ocean mass (cubic dedrift, decadal mean)',
           'regression coefficient, cumulative surface freshwater flux vs change in global ocean mass (cubic dedrift, decadal mean), CI lower',
           'regression coefficient, cumulative surface freshwater flux vs change in global ocean mass (cubic dedrift, decadal mean), CI upper',
           'regression coefficient, cumulative surface freshwater flux vs global mean salinity anomaly (cubic dedrift, decadal mean)',
           'regression coefficient, cumulative surface freshwater flux vs global mean salinity anomaly (cubic dedrift, decadal mean), CI lower',
           'regression coefficient, cumulative surface freshwater flux vs global mean salinity anomaly (cubic dedrift, decadal mean), CI upper',
           'regression coefficient, cumulative surface heat flux vs thermal OHC anomaly (cubic dedrift, decadal mean)',
           'regression coefficient, cumulative surface heat flux vs thermal OHC anomaly (cubic dedrift, decadal mean), CI lower',
           'regression coefficient, cumulative surface heat flux vs thermal OHC anomaly (cubic dedrift, decadal mean), CI upper'
           ]

units = ['J/yr',
         'J/yr',
         'J/yr',
         'J/yr',
         'J/yr',
         'kg/yr',
         'kg/yr',
         'g/kg/yr',
         'g/kg/yr',
         'm/yr',
         'm/yr',
         'm/yr',
         'm2',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         ''
        ]


def myadd(first, last):
    """Create column headings"""
    
    if 'regression' in first:
        output = first
    else:
        output = first + ' (' + last + ')'

    return output
    

def main(inargs):
    """Run the program."""

    df = pd.DataFrame(index=[0], columns=list(map(myadd, headers, units)))
    
    file = open(inargs.infile, "r")
    for line in file:
        for col, header in enumerate(headers): 
            if header in line:
                value = line.split(':')[-1].split(' ')[1]
                file_unit = line.split(' ')[-1].strip()
                match_unit = units[col].strip()
                if ('regression' in header) and not 'ERROR' in value:
                    df[header] = value
                    lower_ci = line.split('[')[1].split(',')[0]
                    upper_ci = line.split(']')[0].split(' ')[-1]
                    df[header + ', CI lower'] = lower_ci
                    df[header + ', CI upper'] = upper_ci
                elif file_unit == match_unit:
                    df[header + ' (' + file_unit + ')'] = value

    outfile = inargs.infile.replace('.met', '.csv')
    df.to_csv(outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Take a drift metadata file and output a csv file with the data'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="File that needs new time axis")

    args = parser.parse_args()             
    main(args)

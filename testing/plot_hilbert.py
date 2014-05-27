"""
Filename:     plot_hilbert.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Produce a number of plots for testing and understanding 
              the Hilbert Transform

"""

# Import general Python modules #

import sys, os
import argparse
import numpy
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import cdms2
import pdb

# Import my modules #

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'phd':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)
anal_dir = os.path.join(repo_dir, 'data_processing')
sys.path.append(anal_dir)
vis_dir = os.path.join(repo_dir, 'visualisation')
sys.path.append(vis_dir)

try:
    import netcdf_io as nio
    import calc_fourier_transform as cft
    import calc_envelope as cenv
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')


# Define functions # 

def simple_signal():
    """Define a sample signal"""
    
    numpy.random.seed(1234)

    time_step = 1.
    period = 120.

    time_vec = numpy.arange(0, 360, time_step)
#    signal = numpy.cos(((2 * numpy.pi) / period) * time_vec) + 0.5 * numpy.random.randn(time_vec.size)
#    signal = numpy.cos(((2 * numpy.pi) / 360.) * time_vec) + numpy.sin(((2 * numpy.pi) / 180.) * time_vec) + \
#             numpy.sin(((2 * numpy.pi) / 120.) * time_vec) - numpy.cos(((2 * numpy.pi) / 90.) * time_vec) 
#             + 0.5 * numpy.random.randn(time_vec.size)
    signal = numpy.cos(((2 * numpy.pi) / (360. / 6.)) * time_vec) + numpy.cos(((2 * numpy.pi) / (360. / 7.)) * time_vec) + \
             numpy.cos(((2 * numpy.pi) / (360. / 8.)) * time_vec)

    signal = 3 * signal
    
    return time_vec, signal


def data_signal(infile, var, lon, date):
    fin = cdms2.open(infile)
    data = fin(var, latitude=(float(lon) - 0.1, float(lon) + 0.1), time=(date, date), squeeze=1)
    xaxis = data.getLongitude()[:]
    
    return numpy.array(xaxis), numpy.array(data)
    

def plot_spectrum(freqs, power, tag=None, window=20):
    """Plot power spectrum.
    
    Input arguments:
        Window  -> There is an inset winow for the first 0:window frequencies
    
    """
    
    plt.figure()  
    
    # Outer plot
    plt.plot(freqs, power)
    plt.xlabel('Frequency [cycles / domain]')
    plt.ylabel('power')
    
    # Inner plot
    axes = plt.axes([0.3, 0.3, 0.5, 0.5])
    plt.title('Peak frequency')
    plt.plot(freqs[:window], power[:window])
    plt.setp(axes, yticks=[])
    outfile = 'power_spectrum_'+tag+'.png' if tag else 'power_spectrum.png'
    plt.savefig(outfile)
    plt.clf()


def plot_wavenumbers(num_list, filtered_signal, xaxis, tag=None):
    """Plot the individual wavenumbers, including their positive and negative wavenumber parts"""
    
    colors = ['blue', 'red', 'green', 'orange', 'pink', 'black', 'purple', 'brown', 'cyan', 'magenta']
    for wavenum in num_list:
        plt.plot(xaxis, 2*filtered_signal[None, wavenum, wavenum], color=colors[wavenum-1], label='w'+str(wavenum))
        plt.plot(xaxis, 2*filtered_signal['positive', wavenum, wavenum], color=colors[wavenum-1], linestyle=':')
        plt.plot(xaxis, 2*filtered_signal['negative', wavenum, wavenum], color=colors[wavenum-1], linestyle='--')

    plt.legend()
    outfile = 'individual_wavenumbers_'+tag+'.png' if tag else 'individual_wavenumbers.png'
    plt.savefig(outfile)
    plt.clf()


def plot_hilbert(num_list, original_signal, filtered_signal, my_signal, xaxis, tag=None):
    """Plot the Hilbert transform and key components of it"""

    for wavenum in num_list:
	color = 'orange' if wavenum in [2, 3, 4] else '0.5'
        plt.plot(xaxis, 2*filtered_signal['positive', wavenum, wavenum], color=color, linestyle='--')

    plt.plot(xaxis, 2*filtered_signal['positive', num_list[0], num_list[-1]], color='black', linestyle='--', label='w'+str(num_list[0])+'-'+str(num_list[-1])+' signal')
    plt.plot(xaxis, numpy.abs(2*filtered_signal['positive', num_list[0], num_list[-1]]), color='black', label='w'+str(num_list[0])+'-'+str(num_list[-1])+' envelope')
    plt.plot(xaxis, 2*filtered_signal['positive', 2, 4], color='red', linestyle='--', label='w2-4 signal')
    plt.plot(xaxis, numpy.abs(2*filtered_signal['positive', 2, 4]), color='red', label='w2-4 envelope')
    plt.plot(xaxis, my_signal, color='cyan', linestyle=':', label='Glatt signal')
    plt.plot(xaxis, original_signal, color='green', label='original signal')

    print 'Signal vals:', 2*filtered_signal['positive', num_list[0], num_list[-1]][0:10]
    print 'Envelope vals:', numpy.abs(2*filtered_signal['positive', num_list[0], num_list[-1]])[0:10]

    if tag:
        plt.title(tag.replace('_',' '))
    font = font_manager.FontProperties(size='small')
    plt.legend(loc=4, prop=font)
    
    outfile = 'hilbert_transform_'+tag+'.png' if tag else 'hilbert_transform.png'
    plt.savefig(outfile)
    plt.clf()


def main(inargs):
    """Run the program."""
    
    # Get the data
    if inargs.simple:
        xaxis, sig = simple_signal()
    else:
        xaxis, sig = data_signal(inargs.infile, inargs.variable, inargs.longitude, inargs.date)

    # Do the Hilbert transform
    my_signal = cenv.envelope(sig, inargs.wavenumbers[0], inargs.wavenumbers[-1])  #My method
    sig_fft, sample_freq, freqs, power = cft.fourier_transform(sig, xaxis) # Scipy method
 
    filtered_signal = {}
    wavenum_list = range(inargs.wavenumbers[0], inargs.wavenumbers[-1] + 1)
    for filt in [None, 'positive', 'negative']:
        for wave_min in wavenum_list:
            for wave_max in wavenum_list:
	        filtered_signal[filt, wave_min, wave_max] = cft.inverse_fourier_transform(sig_fft, sample_freq, 
	                                                                                  min_freq=wave_min, max_freq=wave_max, 
										          exclude=filt)
    
    # Create plots
    plot_spectrum(freqs, power, tag=inargs.tag, window=14)
    plot_wavenumbers(wavenum_list, filtered_signal, xaxis, tag=inargs.tag)
    plot_hilbert(wavenum_list, sig, filtered_signal, my_signal, xaxis, tag=inargs.tag)
    

if __name__ == '__main__':

    extra_info =""" 

example:
    /usr/local/uvcdat/1.4.0/bin/cdat plot_hilbert.py 
    ~/Downloads/Data/va_Merra_250hPa_30day-runmean-2002_r360x181.nc va -50 2002-04-17

notes:
   Interesting dates are 2002-01-15 (extent=180), 2002-01-23 (extent=150), 2002-02-13 (extent=100), 
   2002-04-24 (extent=350), 2002-05-12 (extent=360), 2002-06-19 (extent=240)                     

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Explore the Hilbert transform'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name, containing the meridional wind")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("longitude", type=str, help="Longitude over which to extract the wave")
    parser.add_argument("date", type=str, help="Date for which to extract the wave")
    parser.add_argument("tag", type=str, help="Tag for output files")
    
    parser.add_argument("--wavenumbers", type=int, nargs=2, metavar=('LOWER', 'UPPER'), default=[1, 10],
                        help="Wavenumber range [default = (1, 10)]. The upper and lower values are included (i.e. default selection includes 1 and 10).")
    parser.add_argument("--simple", action="store_true", default=False,
                        help="switch for plotting an idealistic sample wave instead [default: False]")
  
    args = parser.parse_args()            

    main(args)

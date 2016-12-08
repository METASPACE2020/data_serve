from __future__ import print_function

def get_spectrum(ds_id, ix, minmz=None, maxmz=None, npeaks=None):
    from pyimzml import ImzMLParser
    import numpy as np
    import os
    import six.moves.cPickle as pickle
    imzml_fname = get_ds_info(ds_id)['imzml']
    imzml_idx = get_imzml_index(imzml_fname)

    mzs, ints = _getspectrum(imzml_idx, open(imzml_idx['bin_filename'], "rb"), ix)
    mzs, ints = np.asarray(mzs), np.asarray(ints)
    if minmz:
        lower_ix = np.searchsorted(mzs, float(minmz))
    else:
        lower_ix = 0
    if maxmz:
        upper_ix = np.searchsorted(mzs, float(maxmz))
    else:
        upper_ix = len(mzs)
    sort_ix = np.argsort(ints[lower_ix:upper_ix])
    to_return = sort_ix + lower_ix
    if npeaks < len(to_return):
        to_return = to_return[-npeaks:]
    to_return = np.sort(to_return[to_return < len(ints)])
    mzs = mzs[to_return]
    ints = ints[to_return]
    return mzs, ints

def get_image(ds_id, mz, ppm):
    from cpyImagingMSpec import ImzbReader
    import numpy as np
    print(mz, ppm)
    imzb_fname = get_ds_info(ds_id)['imzb']
    print(imzb_fname)
    imzb = ImzbReader(imzb_fname)
    print(imzb.width, imzb.height)
    ion_image = imzb.get_mz_image(mz, ppm)
    return ion_image.T

DS_INFO_FILENAME = 'data_serve/ds_info.json'

def get_ds_info(id):
    # todo reimplement this in database
    # quick hack -> this will go into the database
    import json
    ds_info = json.load(open(DS_INFO_FILENAME))
    return ds_info[id]

def get_ds_name(ds_id):
    return get_ds_info(ds_id)['name']


def get_all_dataset_names_and_ids():
    import json
    import numpy as np
    ds_info = json.load(open(DS_INFO_FILENAME))
    ds_ids = list(ds_info.keys())
    ds_names = [ds_info[k]['name'] for k in ds_ids]
    ord = np.argsort(ds_names)
    return [ds_names[_n] for _n in ord], [ds_ids[_n] for _n in ord]


def b64encode(im_vect, im_shape, colormap_name='viridis'):
    import base64
    import matplotlib.pyplot as plt
    import numpy as np
    import six
    in_memory_path = six.BytesIO()
    plt.imsave(in_memory_path, np.reshape(im_vect, im_shape), cmap=plt.get_cmap(colormap_name))
    encoded = base64.b64encode(in_memory_path.getvalue())
    return encoded.decode('ascii')

def coord_to_ix(ds_id, x, y):
    import numpy as np
    imzml_fname = get_ds_info(ds_id)['imzml']
    imzml_index = get_imzml_index(imzml_fname)
    print(x, y, imzml_fname)
    print(np.min(imzml_index['coordinates'], axis=0), np.max(imzml_index['coordinates'], axis=0))
    ix = np.where([all([c[0]==x, c[1]==y]) for c in imzml_index['coordinates']])[0][0]
    return ix

def parse_imzml_index(imzml_filename):
    from pyimzml import ImzMLParser
    imzml = ImzMLParser.ImzMLParser(imzml_filename)
    imzml_idx = {'bin_filename': imzml.filename[:-5] + "ibd",
                 'mzOffsets': imzml.mzOffsets,
                 'mzLengths': imzml.mzLengths,
                 'intensityOffsets': imzml.intensityOffsets,
                 'intensityLengths': imzml.intensityLengths,
                 'sizeDict': imzml.sizeDict,
                 'mzPrecision': imzml.mzPrecision,
                 'intensityPrecision': imzml.intensityPrecision,
                 'coordinates': imzml.coordinates
                 }
    return imzml_idx

def get_imzml_index(imzml_fname):
    import six.moves.cPickle as pickle
    import os
    imzml_idx_fname = imzml_fname + '.idx'
    if not os.path.exists(imzml_idx_fname):
        imzml_idx = parse_imzml_index(imzml_fname)
        pickle.dump(imzml_idx, open(imzml_idx_fname, 'wb'))
    else:
        imzml_idx = pickle.load(open(imzml_idx_fname, 'rb'))
    return imzml_idx

def _get_spectrum_as_string(imzml_idx, m, index):
    """
    Reads m/z array and intensity array of the spectrum at specified location
    from the binary file as a byte string. The string can be unpacked by the struct
    module. To get the arrays as numbers, use getspectrum
    :param index:
        Index of the desired spectrum in the .imzML file
    :rtype: Tuple[str, str]
    Output:
    mz_string:
        string where each character represents a byte of the mz array of the
        spectrum
    intensity_string:
        string where each character represents a byte of the intensity array of
        the spectrum
    """
    offsets = [imzml_idx['mzOffsets'][index], imzml_idx['intensityOffsets'][index]]
    lengths = [imzml_idx['mzLengths'][index], imzml_idx['intensityLengths'][index]]
    lengths[0] *= imzml_idx['sizeDict'][imzml_idx['mzPrecision']]
    lengths[1] *= imzml_idx['sizeDict'][imzml_idx['intensityPrecision']]
    m.seek(offsets[0])
    mz_string = m.read(lengths[0])
    m.seek(offsets[1])
    intensity_string = m.read(lengths[1])
    return mz_string, intensity_string


def _getspectrum(imzml_idx, m, index):
    """
    Reads the spectrum at specified index from the .ibd file.
    :param index:
        Index of the desired spectrum in the .imzML file
    Output:
    mz_array:
        Sequence of m/z values representing the horizontal axis of the desired mass
        spectrum
    intensity_array:
        Sequence of intensity values corresponding to mz_array
    """
    import struct
    mz_string, intensity_string = _get_spectrum_as_string(imzml_idx, m, index)
    mz_fmt = '<' + str(int(len(mz_string) / imzml_idx['sizeDict'][imzml_idx['mzPrecision']])) + imzml_idx['mzPrecision']
    intensity_fmt = '<' + str(
        int(len(intensity_string) / imzml_idx['sizeDict'][imzml_idx['intensityPrecision']])) + imzml_idx['intensityPrecision']
    mz_array = struct.unpack(mz_fmt, mz_string)
    intensity_array = struct.unpack(intensity_fmt, intensity_string)
    return mz_array, intensity_array

def prettify_spectrum(mzs, ints, peak_type='centroids'):
    import numpy as np
    if peak_type=='centroids':
        mzs = np.concatenate([mzs, mzs-0.00001, mzs+0.00001])
        ints = np.concatenate([ints, np.zeros(2*len(ints))])
        ix = np.argsort(mzs)
        mzs = mzs[ix]
        ints = ints[ix]
    elif peak_type=='profile':
        pass
    return mzs, ints

def peak_type(ds_id):
    import json
    ds_info = json.load(open(DS_INFO_FILENAME))
    return ds_info[ds_id]['peak_type']


def get_isotope_pattern(sf, resolving_power=100000, instrument_type='tof', at_mz=None, cutoff_perc=0.1, charge=None, pts_per_mz=10000, **kwargs):
    from cpyMSpec import isotopePattern, InstrumentModel, ProfileSpectrum
    # layer of compatibility with the original pyMSpec.pyisocalc module
    from pyMSpec.mass_spectrum import MassSpectrum
    import numpy as np
    if charge is None:
        charge = 1
    cutoff = cutoff_perc / 100.0
    abs_charge = max(1, abs(charge))
    p = isotopePattern(str(sf), cutoff / 10.0)
    p.addCharge(charge)
    mzs = np.arange(min(p.masses) / abs_charge - 1,
                    max(p.masses) / abs_charge + 1, 1.0/pts_per_mz)
    instr = InstrumentModel(instrument_type, resolving_power)
    intensities = np.asarray(p.envelope(instr)(mzs * abs_charge))
    intensities *= 100.0 / intensities.max()

    ms = MassSpectrum()
    ms.add_spectrum(mzs, intensities)

    p = ProfileSpectrum(mzs, intensities).centroids(5)
    p.removeIntensitiesBelow(cutoff)
    p.sortByMass()
    ms.add_centroids(p.masses, np.array(p.intensities))
    return ms

def scan_folder_for_imzml(folder):
    import os
    for root, dirs, files in  os.walk(folder):
        if 'CVS' in files:
            print(files)

def get_imzml_header(ds_id):
    # quick and dirty parsing to strip of all spectra objects
    imzml_filename = get_ds_info(ds_id)['imzml']
    header = ''
    with open(imzml_filename) as f:
        for line in f.readlines():
            if line.strip().startswith('<run'):
                header=header+'</mzML>'
                break
            header = header + line
    return header
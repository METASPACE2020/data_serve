def get_spectrum(ds_id, ix, minmz, maxmz, npeaks):
    from pyimzml import ImzMLParser
    import numpy as np
    assert(minmz<maxmz)
    imzml_fname = get_ds_info(ds_id)['imzml']
    imzml = ImzMLParser.ImzMLParser(imzml_fname)
    mzs, ints = imzml.getspectrum(int(ix))
    mzs, ints = np.asarray(mzs), np.asarray(ints)
    lower_ix, upper_ix = np.searchsorted(mzs, minmz), np.searchsorted(mzs, maxmz)
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
    print mz, ppm
    imzb_fname = get_ds_info(ds_id)['imzb']
    imzb = ImzbReader(imzb_fname)
    ion_image = imzb.get_mz_image(mz, ppm)
    return ion_image

ds_info = {
    '0': {
        'name': '12hour_5_210',
        'imzml': '/home/palmer/Documents/tmp_data/test_dataset/12hour_5_210_centroid.imzML',
        'imzb': '/home/palmer/Documents/tmp_data/test_dataset/12hour_5_210_centroid.imzb'
    },
    '1': {
        'name': '12hour_5_210',
        'imzml': '/home/palmer/Documents/tmp_data/test_dataset/12hour_5_210_centroid.imzML',
        'imzb': '/home/palmer/Documents/tmp_data/test_dataset/12hour_5_210_centroid.imzb'
    },
}
def get_ds_info(id):
    # todo reimplement this in database
    # quick hack -> this will go into the database
    return ds_info[id]

def get_ds_name(ds_id):
    return get_ds_info(ds_id)['name']


def get_all_dataset_names_and_ids():
    ds_ids = ds_info.keys()
    ds_names = [ds_info[k]['name'] for k in ds_ids]
    return ds_names, ds_ids


def b64encode(im_vect, im_shape):
    import base64
    import matplotlib.pyplot as plt
    import numpy as np
    import StringIO
    in_memory_path  = StringIO.StringIO()
    plt.imsave(in_memory_path, np.reshape(im_vect, im_shape))
    encoded = base64.b64encode(in_memory_path.getvalue())
    return encoded

def coord_to_ix(ds_id, x, y):
    from pyimzml import ImzMLParser
    import numpy as np
    imzml_fname = get_ds_info(ds_id)['imzml']
    imzml = ImzMLParser.ImzMLParser(imzml_fname)
    print x, y
    ix = np.where([all([c[0]==x, c[1]==y]) for c in imzml.coordinates])[0][0]
    return ix

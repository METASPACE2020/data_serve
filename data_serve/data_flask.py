from __future__ import print_function
from flask import Flask, jsonify, request, render_template,  make_response
from datetime import date
from utils import *
import numpy as np

app = Flask(__name__)

@app.route('/_version')
def version():
    response = {'version': '0.0.1',
                'last_build': date.today().isoformat()}
    return jsonify(response)

@app.route('/datasets/')
def fetch_datasets():
    ds_names, ds_ids = get_all_dataset_names_and_ids()
    response = {'ds_names': ds_names, 'ds_ids': ds_ids}
    return jsonify(response)

@app.route('/dataset/<ds_id>/spec/<spec_ix>')
def fetch_spectrum(ds_id=None, spec_ix=None):
    npeaks = request.args.get('npeaks', '25', type=int)
    minmz =  request.args.get('minmz', None, type=float)
    maxmz =  request.args.get('maxmz', None, type=float)
    mzs, ints = get_spectrum(ds_id, spec_ix, minmz, maxmz, npeaks)
    mzs, ints = prettify_spectrum(mzs, ints, peak_type(ds_id))
    response = {'ds_id': ds_id,
                'spec_ix': int(spec_ix.strip('/')),
                'spec' : [(_mz,_int) for _mz, _int in zip(mzs, ints)],
                'xstart': minmz,
                'xend': maxmz,
                }
    return jsonify(response)


@app.route('/dataset/<ds_id>/spec_xy/<x>/<y>/')
def fetch_spectrum_xy(ds_id=None, x=None, y=None):
    npeaks = request.args.get('npeaks', '25', type=int)
    minmz =  request.args.get('minmz', None, type=float)
    maxmz =  request.args.get('maxmz', None, type=float)
    spec_ix = coord_to_ix(ds_id, int(x), int(y))
    mzs, ints = get_spectrum(ds_id, spec_ix, minmz, maxmz, int(npeaks))
    mzs, ints = prettify_spectrum(mzs, ints, peak_type(ds_id))
    response = {'ds_id': ds_id,
                'spec_ix': int(spec_ix),
                'spec' : [(_mz,_int) for _mz, _int in zip(mzs, ints)],
                'x': x,
                'y': y,
                'xstart': minmz,
                'xend': maxmz,
                }
    return jsonify(response)


@app.route('/dataset/<ds_id>/im/<mz>')
def fetch_image(ds_id=None, mz=None):
    mz = float(mz)
    ppm = float(request.args.get('ppm', '5.'))
    colormap = request.args.get('colormap', 'viridis')
    mapalpha =  request.args.get('mapalpha', 'false')=='true'
    hotspot = request.args.get('hotspot', 'true')=='true'
    im = get_image(ds_id, mz, ppm)
    im_vect = [ float(ii) for ii in im.flatten()]
    print("im max:", np.max(im_vect))
    im_arr = color_image(im_vect, im.shape, colormap, mapalpha, hotspot)
    response = {'ds_id': ds_id,
                'ds_name': get_ds_name(ds_id),
                'mz': mz,
                'ppm': ppm,
                'im_shape': im.shape,
                'min_intensity' : np.min(im_vect),
                'max_intensity': np.max(im_vect),
                'b64_im': b64encode(im_arr)
                }
    return jsonify(response)


@app.route('/dataset/<ds_id>/optical_im/')
def fetch_optical_image(ds_id=None):
    ix = int(request.args.get('ix', '0'))
    im, transform = get_optical_image(ds_id, ix)
    im_vect = [ float(ii) for ii in im.flatten()]
    response = {'ds_id': ds_id,
                'ds_name': get_ds_name(ds_id),
                'ix': ix,
                'transform': transform,
                'im_shape': im.shape,
                'min_intensity' : np.min(im_vect),
                'max_intensity': np.max(im_vect),
                'b64_im': b64encode(im)
                }
    return jsonify(response)

@app.route('/dataset/<ds_id>/annotations')
def fetch_annotations(ds_id=None):
    from sm_annotation_utils import sm_annotation_utils
    fdr = request.args.get('fdr', '0.1', float)
    dbn = request.args.get('database', 'HMDB', str)
    sm = sm_annotation_utils.SMInstance()
    ds = sm.dataset(id=ds_id)
    an = ds.annotations(database=dbn, fdr=fdr)
    return jsonify(an)

@app.route('/dataset/<ds_id>/metadata')
def fetch_meta(ds_id=None):
    print(("get meta", ds_id))
    meta = get_ds_info(ds_id)
    return jsonify(meta)

@app.route('/dataset/<ds_id>/meanspectrum')
def fetch_mean_spectrum(ds_id=None):
    print(("get meta", ds_id))
    meanspec = get_mean_spectrum(ds_id)
    return jsonify({"mzs": list(meanspec[0]), "intensities": list(meanspec[1])})

@app.route('/dataset/<ds_id>/correlation')
def fetch_correlation(ds_id=None):
    mz = request.args.get('mz', None, float)
    opticalix = request.args.get('opticalIx', None, int)
    print(('mz', mz, 'optix', opticalix))
    if not mz==None:
        corr = correlation(ds_id, mz)
    elif not opticalix==None:
        corr = correlation_optical(ds_id, opticalix)
    s_ix = np.argsort(corr[1])
    return jsonify({"mzs": list(np.round(corr[0][s_ix], decimals=4)), "correlation": list(corr[1][s_ix])})


@app.route('/dataset/<ds_id>/px_vals/<mz>')
def fetch_vals(ds_id=None, mz=None):
    mz = float(mz)
    ppm = float(request.args.get('ppm', '5.'))
    im = get_image(ds_id, mz, ppm)
    im_vect = [ float(ii) for ii in im.flatten()]
    response = {'ds_id': ds_id,
                'ds_name': get_ds_name(ds_id),
                'mz': mz,
                'ppm': ppm,
                'im_shape': im.shape,
                'min_intensity' : np.min(im_vect),
                'max_intensity': np.max(im_vect),
                'im_vect': im_vect
                }
    return jsonify(response)

@app.route('/dataset/<ds_id>/imzml_header')
def fetch_header(ds_id=None):
    header = get_imzml_header(ds_id)
    response = {'ds_id': ds_id,
                'ds_name': get_ds_name(ds_id),
                'imzml_header': header,
                }
    return jsonify(response)

@app.route('/dataset/<ds_id>/imzml_header/txt')
def serve_header_file(ds_id=None):
    header = get_imzml_header(ds_id)
    response = make_response(header)
    response.headers["Content-Disposition"] = "attachment; filename={}.header.imzml".format(get_ds_name(ds_id))
    return response

@app.route('/_isotope/<sf>/<a_charge>/')
def generate_isotope_pattern(sf, a_charge):
    rp = request.args.get('resolving_power', '100000', type=float)
    a, chg = a_charge.split('_')
    sf = sf+a
    print(sf, rp, int(chg))
    spec = get_isotope_pattern(sf, resolving_power=float(rp), instrument_type='tof', at_mz=None, cutoff_perc=0.1, charge=int(chg), pts_per_mz=10000)
    p_spec = spec.get_spectrum(source='profile')
    response = {
        'sf': sf,
        'spec': [("{:3.5f}".format(_mz), "{:3.2f}".format(_int)) for _mz, _int in zip(*p_spec) if _int>0.01]
    }
    return jsonify(response)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dataset/<ds_id>')
def dataset(ds_id):
    return render_template('dataset.html', ds_id=ds_id, ds_name = get_ds_name(ds_id ))
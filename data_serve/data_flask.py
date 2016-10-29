from flask import Flask, jsonify, request, render_template
from datetime import date
from utils import get_spectrum, get_image, get_ds_name, get_all_dataset_names_and_ids, b64encode, coord_to_ix, prettify_spectrum, peak_type, get_isotope_pattern

app = Flask(__name__)

@app.route('/_version')
def version():
    response = {'version': '3.5.1',
                'last_build': date.today().isoformat()}
    return jsonify(response)

@app.route('/_ds/')
def fetch_datasets():
    ds_names, ds_ids = get_all_dataset_names_and_ids()
    response = {'ds_names': ds_names, 'ds_ids': ds_ids}
    return jsonify(response)

@app.route('/<ds_id>/spec/<spec_ix>')
def fetch_spectrum(ds_id=None, spec_ix=None):
    npeaks = request.args.get('npeaks', '25', type=int)
    minmz =  request.args.get('minmz', '0', type=float)
    maxmz =  request.args.get('maxmz', '1e9', type=float)
    mzs, ints = get_spectrum(ds_id, spec_ix, minmz, maxmz, npeaks)
    mzs, ints = prettify_spectrum(mzs, ints, peak_type(ds_id))
    response = {'ds_id': int(ds_id),
                'spec_ix': int(spec_ix.strip('/')),
                'spec' : [(_mz,_int) for _mz, _int in zip(mzs, ints)],
                }
    return jsonify(response)


@app.route('/<ds_id>/spec_xy/<x>/<y>/')
def fetch_spectrum_xy(ds_id=None, x=None, y=None):
    npeaks = request.args.get('npeaks', '25', type=int)
    minmz =  request.args.get('minmz', '0.', type=float)
    maxmz =  request.args.get('maxmz', '1e9', type=float)
    spec_ix = coord_to_ix(ds_id, int(x), int(y))
    mzs, ints = get_spectrum(ds_id, spec_ix, float(minmz), float(maxmz), int(npeaks))
    mzs, ints = prettify_spectrum(mzs, ints, peak_type(ds_id))
    response = {'ds_id': int(ds_id),
                'spec_ix': spec_ix,
                'spec' : [(_mz,_int) for _mz, _int in zip(mzs, ints)],
                'x': x,
                'y': y,
                }
    return jsonify(response)


@app.route('/<ds_id>/im/<mz>')
def fetch_image(ds_id=None, mz=None):
    mz = float(mz)
    ppm = float(request.args.get('ppm', '5.'))
    im = get_image(ds_id, mz, ppm)
    im_vect = [ float(ii) for ii in im.flatten()]
    response = {'ds_id': int(ds_id),
                'ds_name': get_ds_name(ds_id),
                'mz': mz,
                'ppm': ppm,
                'im_shape': im.shape,
                'im_vect' : im_vect,
                'b64_im': b64encode(im_vect, im.shape)
                }
    return jsonify(response)


@app.route('/_isotope/<sf>/<a_charge>/')
def generate_isotope_pattern(sf, a_charge):
    rp = request.args.get('resolving_power', '100000', type=float)
    a, chg = a_charge.split('_')
    sf = sf+a
    print sf, rp
    spec = get_isotope_pattern(sf, resolving_power=rp, instrument_type='tof', at_mz=None, cutoff_perc=0.1, charge=None, pts_per_mz=10000)
    p_spec = spec.get_spectrum(source='profile')
    response = {
        'sf': sf,
        'spec': [("{:3.5f}".format(_mz), "{:3.2f}".format(_int)) for _mz, _int in zip(*p_spec) if _int>0.01]
    }
    return jsonify(response)


@app.route('/')
def index():
    return render_template('index.html')
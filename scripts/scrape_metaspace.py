import json
import boto3
from boto3.s3.transfer import S3Transfer
import os
import subprocess
import json
from sm_annotation_utils import sm_annotation_utils
import sys
import traceback
import argparse


def check_dir(destination, ds_name):
    destination_dir = os.path.join(destination, ds_name)
    if not os.path.isdir(destination_dir):
        os.makedirs(destination_dir)

def get_dataset(path, destination):
    bucket_name, ds_name = path.split('/', 1)
    check_dir(destination, ds_name)
    s3 = boto3.resource('s3')
    transfer = S3Transfer(boto3.client('s3'))
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=ds_name):
        if obj.key.endswith('/'): #can't download a folder object
            continue
        dest_file = os.path.join(destination, obj.key)
        dest_dir = os.path.split(dest_file)[0].replace(".", "").replace("@","")
        dest_file = os.path.join(dest_dir, os.path.split(dest_file)[1]).replace('.imzml', '.imzML')
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        transfer.download_file(bucket_name, obj.key, dest_file)
        if obj.key.lower().endswith('.imzml'):
            imzml = dest_file
            imzb = imzml.replace('.imzML', '.imzb')
    return imzml, imzb

def convert_dataset(imzml, imzb, ds_id, ds_meta, ims_path):
    assert os.path.exists(imzml)
    ret = subprocess.check_call([ims_path, "convert", imzml, imzb])
    return {ds_id:{
        'name': ds_meta['metaspace_options']['Dataset_Name'],
        'imzml': imzml,
        'imzb': imzb,
        'peak_type': 'centroids',
        "instrument": ds_meta['MS_Analysis']['Analyzer'],
        "polarity": ds_meta['MS_Analysis']['Polarity'],
        "resolving_power": ds_meta['MS_Analysis']['Detector_Resolving_Power']['Resolving_Power'],
        "at_mz": ds_meta['MS_Analysis']['Detector_Resolving_Power']['mz'],
                "ppm": 3}}


if __name__ == '__main__':
    # scripts/scrape_metaspace.py --ds-ids 2017-08-22_23h34m34s --destination /tmp
    parser = argparse.ArgumentParser(description='Scrape data from metaspace')
    parser.add_argument('--ds-ids', nargs='+', required=True)
    parser.add_argument('--destination', required=True)
    parser.add_argument("--ims-path", default="ims")
    args = parser.parse_args()
    jsons = {}
    for ds_id in args.ds_ids:
        try:
            md = sm_annotation_utils.SMInstance().dataset(id = ds_id)
            imzml_fn, imzb_fn = get_dataset(md.s3dir[6:], args.destination)
            #print imzml_fn, imzb_fn
            jsons.update(convert_dataset(imzml=imzml_fn, imzb=imzb_fn, ds_id=ds_id,
                                         ds_meta=json.loads(md.metadata.json), ims_path=args.ims_path))
        except Exception as e:
            print e
            print ds_id
            raise
    print json.dumps(jsons, indent=2)

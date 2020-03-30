# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import boto3
import botocore

import logging
import datetime
import xml.etree.ElementTree as ET
import xmltodict
import json
import csv
import pprint
import time
import os
import sys

from GPPXml import GPPXml

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def write_to_json(records, out_fname):

    with open(out_fname, 'w') as file_json:
        for rec in records:
            file_json.write(json.dumps(rec)+"\n")

    return None


def write_to_csv(header, records, out_fname):
    
    with open(out_fname, 'w', encoding='utf8', newline='') as file_csv:
        fc = csv.DictWriter(file_csv,
                            fieldnames=header,
                            delimiter='|',
                            lineterminator='\n')
        fc.writeheader()
        fc.writerows(records)

    return None


def lambda_handler(event, context):
    
    bucket = event['Records'][0]['s3']['bucket']['name']     
    key = event['Records'][0]['s3']['object']['key']
    fname = key.split('/')[-1].split('.')[0]

    output_format = os.environ['output_format'].upper()

    tmp_out_dir = '/tmp'

    fprefix = str(int(round(time.time() * 1000)))
    tmp_xml_file = tmp_out_dir+'/'+fprefix+'_'+fname+'.xml'

    tmp_out_fname = ''
    out_transform_prefix = ''

    if output_format == 'JSON':
        tmp_out_fname = fprefix+'_'+fname+'.json'
        out_transform_prefix = 'raw_transform_json'
    elif output_format == 'CSV':
        tmp_out_fname = fprefix+'_'+fname+'.csv'
        out_transform_prefix = 'raw_transform_csv'
    else:
        raise

    tmp_out_file = tmp_out_dir+'/'+ tmp_out_fname

    logger.info("In S3 Bucket    : "+bucket)
    logger.info("In S3 Key       : "+key)
    logger.info("Output Format   : "+output_format)
    logger.info("Temp out dir    : "+tmp_out_dir)
    logger.info("Temp out fname  : "+tmp_out_fname)
    logger.info("File Name       : "+fname)
    logger.info("Out File Prefix : "+fprefix)
    logger.info("Temp XML file   : "+tmp_xml_file)
    logger.info("Temp OUT file   : "+tmp_out_file)
    logger.info("Out S3 Prefix   : "+out_transform_prefix)

    s3 = boto3.resource('s3')
    
    try:
        s3.Bucket(bucket).download_file(key, tmp_xml_file)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            err = "The object s3://"+bucket+"/"+key+"does not exist."
            logger.error(err)
            sys.exit(err)
        else:
            raise

    ET.register_namespace("","http://www.3gpp.org/ftp/specs/archive/32_series/32.435#measCollec")

    tree = ET.parse(tmp_xml_file)
    xml_data = tree.getroot()
    xmlstr = ET.tostring(xml_data, encoding='utf8', method='xml')
    xml = dict(xmltodict.parse(xmlstr))

    x = GPPXml(xml.get('measCollecFile'))
    records = x.convert_to_records('s3://'+bucket+'/'+key, 
                                   datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                   's3://'+bucket+'/'+out_transform_prefix+'/'+tmp_out_fname                                  
                                  )

    if output_format == 'JSON':
        write_to_json(records, tmp_out_file)
    elif output_format == 'CSV':
        write_to_csv(x.get_record_header(), records, tmp_out_file)

    s3.meta.client.upload_file(tmp_out_file, bucket, out_transform_prefix+'/'+tmp_out_fname)

    return { 
        'message' : 'S3 Object : s3://'+bucket+'/'+out_transform_prefix+'/'+tmp_out_fname+' succesfully created from : s3://'+bucket+'/'+key
    }

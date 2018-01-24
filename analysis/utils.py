import json
import os
import subprocess

import pandas as pd

from network import models

BIGWIG_AVERAGE_OVER_BED_PATH = \
    os.path.abspath(os.path.join(
        os.path.dirname(__file__), os.pardir, 'bin', 'bigWigAverageOverBed'))


def call_bigwig_average_over_bed(bigwig_name, bed_name, out_name):
    '''
    Call Kent tools bigWigAverageOverBed.
    '''
    FNULL = open(os.devnull, 'w')
    cmd = [
        BIGWIG_AVERAGE_OVER_BED_PATH,
        bigwig_name,
        bed_name,
        out_name,
    ]
    print('Running subprocess: {}'.format(' '.join(cmd)))
    subprocess.call(cmd, stdout=FNULL, stderr=subprocess.STDOUT)


def generate_intersection_df(locus_group, experiment_type, datasets=None,
                             loci=None):
    '''
    For a given LocusGroup, generate a pandas DF with intersection values.
    '''
    if not datasets:
        datasets = models.Dataset.objects.all()

    d = {}
    for intersection in models.DatasetIntersectionJson.objects.filter(
        locus_group=locus_group,
        dataset__experiment__experiment_type=experiment_type,
        dataset__in=datasets,
    ):
        values = json.loads(intersection.intersection_values)
        series = pd.Series(
            values['normalized_values'], index=values['locus_pks'])
        d.update({intersection.dataset.pk: series})
    df = pd.DataFrame(d)

    if loci:
        df = df.loc[[x.pk for x in loci]]

    return df

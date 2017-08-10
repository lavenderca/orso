from django.core.management.base import BaseCommand
from network import models
import json
import math
import os

ASSEMBLY_TO_SPECIES = {
    'hg19': 'Human',
    'GRCh38': 'Human',
    'mm9': 'Mouse',
    'mm10': 'Mouse',
    'ce10': 'Celeganz',
    'ce11': 'Celeganz',
    'dm3': 'Dmelanogaster',
    'dm6': 'Dmelanogaster',
}

ASSAY_REPLACEMENT = {
    'single cell isolation followed by RNA-seq': 'SingleCell RNA-seq',
    'shRNA knockdown followed by RNA-seq': 'shRNA-KD RNA-seq',
    'siRNA knockdown followed by RNA-seq': 'siRNA-KD RNA-seq',
    'CRISPR genome editing followed by RNA-seq': 'CRISPR RNA-seq',
    'whole-genome shotgun bisulfite sequencing': 'WGBS',
    'microRNA-seq': 'miRNA-seq',
}

EXPERIMENT_DESCRIPTION_FIELDS = [
    'assay_slims',
    'assay_synonyms',
    'assay_term_name',
    'assay_title',
    'biosample_summary',
    'biosample_synonyms',
    'biosample_term_name',
    'biosample_type',
    'category_slims',
    'objective_slims',
    'organ_slims',
    'target',
    'system_slims',
]

DATASET_DESCRIPTION_FIELDS = [
    'assembly',
    'biological_replicates',
    'output_category',
    'output_type',
    'technical_replicates',
]


def get_encode_url(url):
    return 'https://www.encodeproject.org{}'.format(url)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('input_json', type=str)
        parser.add_argument('project_name', type=str)

        parser.add_argument(
            '--data_directory',
            action='store',
            dest='data_directory',
            type=str,
            help='Directory of metaplot and intersection JSON files',
        )

        parser.add_argument(
            '--owner',
            action='store',
            dest='owner',
            type=str,
            help='Assign project to owner',
        )

    def handle(self, *args, **options):

        with open(options['input_json']) as _in:
            experiments = json.load(_in)

        project = models.Project.objects.create(
            name=options['project_name'],
        )
        if options['owner']:
            project.owner = options['owner']
            project.save()

        #  Get number of entries in GenomicRegions
        gr_lengths = dict()
        for gr in models.GenomicRegions.objects.all():
            count = 0
            for line in gr.bed_file:
                if not line.decode("utf-8").startswith('track'):
                    count += 1
            gr_lengths[gr] = count

        for experiment in experiments:
            experiment_description = ''
            for field in EXPERIMENT_DESCRIPTION_FIELDS:
                try:
                    experiment['detail'][field]
                except:
                    pass
                else:
                    if type(experiment['detail'][field]) is list:
                        value = '; '.join(experiment['detail'][field])
                    else:
                        value = experiment['detail'][field]
                    if field == 'target':
                        value = value.split('/')[2]
                    experiment_description += '{}:{}\n\n'.format(
                        ' '.join(field.split('_')).title(),
                        value.capitalize(),
                    )

            experiment_description = experiment_description.rstrip()

            if experiment['detail']['assay_term_name'] in ASSAY_REPLACEMENT:
                assay = \
                    ASSAY_REPLACEMENT[experiment['detail']['assay_term_name']]
            else:
                assay = experiment['detail']['assay_term_name']
            base_name = assay.replace('-seq', 'seq').replace(' ', '_')

            data_type = experiment['detail']['assay_term_name']

            try:
                target = '-'.join(
                    experiment['detail']['target']
                    .split('/')[2]
                    .split('-')[:-1]
                ).replace('%20', ' ')
            except:
                target = None
            else:
                base_name += '-{}'.format(
                    target.replace(' ', '_').replace('-', '_'))

            try:
                biosample_term_name = \
                    experiment['detail']['biosample_term_name']
            except:
                biosample_term_name = None
            else:
                base_name += '-{}'.format(
                    ('').join(w.replace('-', '').capitalize() for w in
                              biosample_term_name.split())
                )
            experiment_name = '{}-{}-{}'.format(
                experiment['name'],
                base_name,
                ASSEMBLY_TO_SPECIES[experiment['datasets'][0]['assembly']],
            )

            e = models.Experiment.objects.create(
                name=experiment_name,
                project=project,
                description=experiment_description,
                data_type=data_type,
                cell_type=biosample_term_name,
            )

            if target:
                e.target = target
                e.save()

            for dataset in experiment['datasets']:

                dataset_description = ''
                for field in DATASET_DESCRIPTION_FIELDS:
                    for detail in ['ambiguous_detail',
                                   'plus_detail',
                                   'minus_detail']:
                        values = set()
                        try:
                            dataset[detail][field]
                        except:
                            pass
                        else:
                            if type(dataset[detail][field]) is list:
                                values.update(dataset[detail][field])
                            else:
                                values.add(dataset[detail][field])
                            dataset_description += '{}:\n{}\n\n'.format(
                                field,
                                '\n'.join(str(val) for val in values)
                            )
                dataset_description = dataset_description.rstrip()

                assembly = dataset['assembly']
                try:
                    ambiguous_url = get_encode_url(dataset['ambiguous_href'])
                except:
                    ambiguous_url = None
                else:
                    slug = dataset['ambiguous']

                try:
                    plus_url = get_encode_url(dataset['plus_href'])
                    minus_url = get_encode_url(dataset['minus_href'])
                except:
                    plus_url = None
                    minus_url = None
                else:
                    slug = '{}-{}'.format(
                        dataset['plus'],
                        dataset['minus'],
                    )
                dataset_name = '{}-{}-{}'.format(
                    slug,
                    base_name,
                    assembly,
                )

                assembly_obj = \
                    models.Assembly.objects.get(name=assembly)

                ds = models.Dataset.objects.create(
                    description=dataset_description,
                    experiment=e,
                    name=dataset_name,
                    slug=slug,
                    assembly=assembly_obj,
                )
                if ambiguous_url:
                    ds.ambiguous_url = ambiguous_url
                if plus_url:
                    ds.plus_url = plus_url
                    ds.minus_url = minus_url
                ds.save()

                regions = models.GenomicRegions.objects.filter(
                    assembly=assembly_obj)

                for gr in regions:
                    meta_name = '{}.{}.metaplot.json'.format(
                        slug.replace('-', '.'),
                        gr.name
                            .replace('_RefSeq', '')
                            .replace('promoters', 'promoter'),
                    )
                    intersection_name = '{}.{}.intersection.json'.format(
                        slug.replace('-', '.'),
                        gr.name
                            .replace('_RefSeq', '')
                            .replace('promoters', 'promoter'),
                    )

                    meta_path = os.path.join(
                        options['data_directory'],
                        meta_name,
                    )
                    intersection_path = os.path.join(
                        options['data_directory'],
                        intersection_name,
                    )

                    if not (
                        os.path.isfile(meta_path) and
                        os.path.isfile(intersection_path)
                    ):
                        meta_check = False
                        intersection_check = False
                    else:
                        try:
                            with open(meta_path) as mfn, open(intersection_path) as ifn:  # noqa
                                m = json.load(mfn)
                                i = json.load(ifn)

                                meta_check = len(m['bin_values']) == 50
                                intersection_check = len(i) == gr_lengths[gr]

                                for val in m['metaplot_values']:
                                    if math.isnan(val):
                                        meta_check = False

                                for val in i:
                                    if math.isnan(val):
                                        intersection_check = False

                        except:
                            meta_check = False
                            intersection_check = False

                    if meta_check:
                        with open(meta_path) as f:
                            models.MetaPlot.objects.create(
                                genomic_regions=gr,
                                dataset=ds,
                                meta_plot=json.load(f),
                            )

                    if intersection_check:
                        with open(intersection_path) as f:
                            models.IntersectionValues.objects.create(
                                genomic_regions=gr,
                                dataset=ds,
                                intersection_values=json.load(f),
                            )

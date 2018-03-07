# import numpy
from celery import group
from celery.decorators import task
from progress.bar import Bar

from analysis import score
from network import models
from network.tasks.process_datasets import update_data_recommendation_scores


def update_data_scores():
    all_pcas = models.PCA.objects.all()
    relevant_pcas = [
        pca for pca in all_pcas if
        pca.locus_group.group_type == pca.experiment_type.relevant_regions
    ]

    group(update_data_recommendation_scores.s(pca.pk)
          for pca in relevant_pcas).apply_async().join()


def update_dataset_data_scores(datasets):
    # Get relevant datasets
    relevant_assemblies = models.Assembly.objects.filter(
        dataset__in=datasets)
    relevant_experiment_types = models.ExperimentType.objects.filter(
        experiment__dataset__in=datasets)
    other_datasets = models.Dataset.objects.filter(
        assembly__in=relevant_assemblies,
        experiment__experiment_type__in=relevant_experiment_types,
    )

    for ds_1 in datasets:

        assembly_1 = ds_1.assembly
        exp_type_1 = ds_1.experiment.experiment_type

        relevant_regions = exp_type_1.relevant_regions

        try:
            pca = models.PCA.objects.get(
                locus_group__assembly=assembly_1,
                experiment_type=exp_type_1,
                locus_group__group_type=relevant_regions,
            )
        except models.PCA.DoesNotExist:
            pass
        else:

            vec_1 = models.PCATransformedValues.objects.get(
                dataset=ds_1, pca=pca).transformed_values

            for ds_2 in other_datasets:

                assembly_2 = ds_2.assembly
                exp_type_2 = ds_2.experiment.experiment_type

                if all([
                    ds_1 != ds_2,
                    assembly_1 == assembly_2,
                    exp_type_1 == exp_type_2,
                ]):

                    vec_2 = models.PCATransformedValues.objects.get(
                        dataset=ds_2, pca=pca).transformed_values
                    vec = pca.neural_network_scaler.transform([vec_1 + vec_2])
                    sim = pca.neural_network.predict(vec)[0]

                    models.DatasetDataDistance.objects.update_or_create(
                        dataset_1=ds_1,
                        dataset_2=ds_2,
                        defaults={
                            'distance': sim,
                        },
                    )


# @task
# def update_dataset_data_scores(datasets, quiet=False):
#     '''
#     Update or create dataset data distance values.
#     '''
#     bar = Bar('Processing', max=len(datasets))
#
#     for ds_1 in datasets:
#
#         dataset_to_score = dict()
#
#         for ds_2 in models.Dataset.objects.filter(
#             assembly=ds_1.assembly,
#             experiment__experiment_type=ds_1.experiment.experiment_type,
#         ):
#
#             exp_type_1 = ds_1.experiment.experiment_type
#             exp_type_2 = ds_2.experiment.experiment_type
#
#             if all([
#                 ds_1 != ds_2,
#                 models.PCATransformedValues.objects.filter(
#                     dataset=ds_1,
#                     pca__locus_group__group_type=exp_type_1.relevant_regions,
#                 ).exists(),
#                 models.PCATransformedValues.objects.filter(
#                     dataset=ds_2,
#                     pca__locus_group__group_type=exp_type_2.relevant_regions,
#                 ).exists(),
#             ]):
#
#                 distance = score.score_datasets_by_pca_distance(ds_1, ds_2)
#                 dataset_to_score[ds_2] = distance
#
#         distances = list(dataset_to_score.values())
#
#         average = numpy.mean(distances)
#         sd = numpy.std(distances)
#
#         for ds_2, distance in dataset_to_score.items():
#             z_score = (distance - average) / sd
#
#             models.DatasetDataDistance.objects.update_or_create(
#                 dataset_1=ds_1,
#                 dataset_2=ds_2,
#                 defaults={
#                     'distance': z_score,
#                 },
#             )
#
#         bar.next()
#
#     bar.finish()


@task
def update_experiment_data_scores(experiments):
    '''
    Update or create experiment data distance values.
    '''
    bar = Bar('Processing', max=len(experiments))

    for exp_1 in experiments:
        assemblies = models.Assembly.objects.filter(dataset__experiment=exp_1)
        for exp_2 in models.Experiment.objects.filter(
            dataset__assembly__in=assemblies,
            experiment_type=exp_1.experiment_type,
        ):

            rr_1 = exp_1.experiment_type.relevant_regions
            rr_2 = exp_2.experiment_type.relevant_regions
            if all([
                exp_1 != exp_2,
                models.PCATransformedValues.objects.filter(
                    dataset__experiment=exp_1,
                    pca__locus_group__group_type=rr_1,
                ).exists(),
                models.PCATransformedValues.objects.filter(
                    dataset__experiment=exp_2,
                    pca__locus_group__group_type=rr_2,
                ).exists(),
            ]):

                distance = score.score_experiments_by_pca_distance(
                    exp_1, exp_2)
                models.ExperimentDataDistance.objects.update_or_create(
                    experiment_1=exp_1,
                    experiment_2=exp_2,
                    defaults={
                        'distance': distance,
                    },
                )

        bar.next()

    bar.finish()

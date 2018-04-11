# from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver

from . import tasks, models

# Note: post save experiment actions are relegated to tasks executed from
# forms and management commands.


@receiver(post_save, sender=models.Follow)
def follow_post_save_update(sender, instance, created, **kwargs):
    if created:
        lock = tasks.locks.UserRecUpdateQueueLock(
            instance.following, instance.followed)
        if lock.add():
            (tasks.recommendations
                  .update_user_recommendations
                  .si(instance.following.pk, instance.followed.pk).delay())

        models.Activity.objects.get_or_create(
            user=instance.following,
            followed_user=instance.followed,
        )


@receiver(pre_delete, sender=models.Follow)
def follow_pre_delete_update(sender, instance, **kwargs):
    lock = tasks.locks.UserRecUpdateQueueLock(
        instance.following, instance.followed)
    if lock.add():
        (tasks.recommendations
              .update_user_recommendations
              .si(instance.following.pk, instance.followed.pk).delay())

    try:
        models.Activity.objects.get(
            user=instance.following,
            followed_user=instance.followed,
        ).delete()
    except models.Activity.DoesNotExist:
        pass


@receiver(post_save, sender=models.Favorite)
def favorite_post_save_update(sender, instance, created, **kwargs):
    if created:
        lock = tasks.locks.ExpRecUpdateQueueLock(instance.experiment)
        if lock.add():
            (tasks.recommendations
                  .update_recommendations
                  .si(instance.experiment.pk).delay())

        models.Activity.objects.get_or_create(
            user=instance.user,
            favorited_experiment=instance.experiment,
        )


@receiver(pre_delete, sender=models.Favorite)
def favorite_pre_delete_update(sender, instance, **kwargs):
    lock = tasks.locks.ExpRecUpdateQueueLock(instance.experiment)
    if lock.add():
        (tasks.recommendations
              .update_recommendations
              .si(instance.experiment.pk).delay())

    try:
        models.Activity.objects.get(
            user=instance.user,
            favorited_experiment=instance.experiment,
        ).delete()
    except models.Activity.DoesNotExist:
        pass


@receiver(post_delete, sender=User)
def user_post_delete(sender, instance, **kwargs):
    my_user = models.MyUser.objects.get(user=instance)
    my_user.delete()

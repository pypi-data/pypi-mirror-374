import os

from django.db import models
from django.core.validators import FileExtensionValidator

from django_hls.conf import get_setting


USE_CELERY = get_setting('USE_CELERY')
CELERY_QUEUE = get_setting('CELERY_QUEUE')


class HLSMedia(models.Model):
    stream_media = models.ForeignKey(
        "DjangoHLSMedia", on_delete=models.CASCADE, related_name="segments"
    )

    def upload_to_path(instance, filename):
        return os.path.join(
            "django_hls/hls",
            os.path.basename(instance.stream_media.media.name),
            filename,
        )

    file = models.FileField(upload_to=upload_to_path, max_length=400)


class DjangoHLSMedia(models.Model):
    media = models.FileField(
        upload_to="django_hls/uploads/",
        validators=[FileExtensionValidator(allowed_extensions=["mp4", "mp3", "m4a"])],
    )
    
    def upload_to_path(instance, filename):
        return os.path.join("django_hls/hls", os.path.basename(instance.media.name), filename)

    hls_file = models.FileField(upload_to=upload_to_path, blank=True, null=True, max_length=400)
    key_file = models.FileField(upload_to=upload_to_path, blank=True, null=True, max_length=400)
    generating_hls = False

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            from django_hls.utils import is_celery_running, is_queue_available
            from django_hls.tasks import generate_hls

            if USE_CELERY:
                if not is_celery_running():
                    raise RuntimeError("Celery is not running.")

                if not is_queue_available(CELERY_QUEUE):
                    raise RuntimeError(f"Celery queue '{CELERY_QUEUE}' is not available.")

                generate_hls.apply_async(args=[self.id], queue=CELERY_QUEUE)
            else:
                from django_hls.services.hls_generator import HLSGenerator
                HLSGenerator(self).generate()

import time
import logging
import sys
from django.apps import AppConfig
from django_hls.conf import get_setting

class DjangoHlsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_hls'

    def ready(self):
        import django_hls.tasks
        import django_hls.models

        if get_setting('USE_CELERY') and not any("celery" in arg for arg in sys.argv):
            from django_hls.utils import is_celery_running

            max_retries = 5
            delay_seconds = 2

            for attempt in range(max_retries):
                try:
                    if is_celery_running():
                        logging.info("Celery is enabled and running.")
                        return
                    else:
                        logging.warning("Celery not responding, attempt %d/%d", attempt + 1, max_retries)
                except Exception as e:
                    logging.warning("Error checking Celery: %s", e)

                time.sleep(delay_seconds)

            # After retries, raise fatal error
            raise RuntimeError("Celery is enabled but not responding after retries. App will not start.")
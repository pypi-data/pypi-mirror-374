from django.conf import settings


DEFAULTS = {
    'SEGMENT_DURATION': 10,
    'USE_CELERY' : False,
    'CELERY_QUEUE' : 'celery',
    'TEMP_DIR' : 'hls_temp_dir',
    'QUALITIES' : ["360", "480", "720"]
}


def get_setting(name):
    return getattr(settings, f"HLS_{name}", DEFAULTS.get(name))
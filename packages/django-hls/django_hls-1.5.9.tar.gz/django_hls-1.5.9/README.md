Django HLS
=============

django-hls is a reusable Django application for streaming video and audio using the HLS

Installation
------------

Install using pip:

    pip install django-hls

Then add ``'django_hls'`` to your ``INSTALLED_APPS``.

    INSTALLED_APPS = [
        ...
        'django_hls',
    ]

If you are using Celery, you can set USE_CELERY to true.

    HLS_USE_CELERY = True
- If django hls cannot connect to celery, the application will stop.
- Not using Celery is not suitable for a production environment.

You can specify a specific queue that you want to use for django hls.

    HLS_CELERY_QUEUE = 'celery' # default queue
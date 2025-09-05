Django HLS
=============

django-hls is a reusable Django application for streaming video and audio using the HLS

Requirements
------------
- Django>=5.2.2,<6.0                 
- celery>=5.5.3,<6.0                
- ffmpeg-progress-yield>=0.12.0,<1.0 
- ffmpeg-python>=0.2.0,<0.3

**You must have ffmpeg installed on your machine or container.**

Installation
------------

Install using pip:

    $ pip install django-hls

Then add ``'django_hls'`` to your ``INSTALLED_APPS``.

    INSTALLED_APPS = [
        ...
        'django_hls',
    ]
    
Run migrations:

    $ python manage.py migrate

Special configurations
------------

If you are using Celery, you can set USE_CELERY to true. \
this allows you to generate HLS format with celery

    HLS_USE_CELERY = True
- If django-hls cannot connect to celery, the application will stop.
- Not using celery is not suitable for a production environment.

You can specify a specific queue that you want to use for django hls.

    HLS_CELERY_QUEUE = 'celery' # default queue
- by default django-hls looking for **celery** queue

You can specify different production qualities.

    HLS_QUALITIES = ["360", "480", "720"] # default qualities

To set the media segment duration:

    HLS_SEGMENT_DURATION = 10 # default duration

Usage
------------
django-hls uses ffmpeg to generate the HLS **format**, so as mentioned above, you need to install ffmpeg.

To add upload fields, inherit from the DjangoHLSMedia model.

```python
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django_hls.models import DjangoHLSMedia


class Course(models.Model):
    title = models.CharField(max_length=250)
    rate = models.IntegerField(
        default=1,
        verbose_name='Stars',
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )
    created_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.title

# this will add media, hls_file, key_file fields to model
class CourseSession(DjangoHLSMedia):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_sessions')
    title = models.CharField(max_length=250)
    created_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.course.title} - {self.title}'
```

Leave the **hls_file** and **key_file** fields blank and just upload the media. django-hls will fill these fields during generation.




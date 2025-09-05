"""
Configuration for Gunicorn
"""

import multiprocessing


bind = '127.0.0.1:__PORT__'

# https://docs.gunicorn.org/en/latest/settings.html#workers
workers = multiprocessing.cpu_count() * 2 + 1

# -----------------------------------------------------------------------------

# Redirect stdout and stderr to the log file
capture_output = True

# https://docs.gunicorn.org/en/latest/settings.html#logging
loglevel = 'INFO'.lower()

# https://docs.gunicorn.org/en/latest/settings.html#logging
accesslog = '/home/jens/repos/cookiecutter_templates/generated_templates/yunohost_django_package/django_example_ynh/local_test/var_log_django_example.log'
errorlog = '/home/jens/repos/cookiecutter_templates/generated_templates/yunohost_django_package/django_example_ynh/local_test/var_log_django_example.log'

# -----------------------------------------------------------------------------

# https://docs.gunicorn.org/en/latest/settings.html#pidfile
pidfile = '/home/jens/repos/cookiecutter_templates/generated_templates/yunohost_django_package/django_example_ynh/local_test/opt_yunohost/gunicorn.pid'  # /home/yunohost.app/$app/gunicorn.pid

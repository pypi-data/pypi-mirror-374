#!/home/jens/repos/cookiecutter_templates/generated_templates/yunohost_django_package/django_example_ynh/local_test/opt_yunohost/.venv/bin/python3

import os
import sys


def main():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

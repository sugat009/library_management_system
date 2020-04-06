from django.core.management import BaseCommand
from news.models import Menu,User
from django.utils import timezone


class Command(BaseCommand):
    help = 'Adds the root menu '

    def handle(self, *args, **options):
        root, created = Menu.objects.get_or_create(title='root', urls='/', position=0,created_by=User.objects.get(id=1))

        if created:
            print('root menu is created')
        else:
            print('root already exists')

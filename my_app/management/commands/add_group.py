from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Add Default Groups'

    def handle(self, *args, **options):
        group_list = ['head_librarian', 'librarian', 'member', ]

        for group in group_list:
            grp, created = Group.objects.get_or_create(name=group)
        print('Default Groups are created')

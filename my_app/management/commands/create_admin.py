from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.core.validators import validate_email
from django.forms import ValidationError
from analytics_app.models import Staff
import getpass


class Command(BaseCommand):
    help = 'Create employee with superuser power'

    def validate_username(self):
        if User.objects.filter(username=self.username).exists():
            print("Username already exists")

    def email_input(self):
        try:
            validate_email(self.email)
        except:
            print("Enter an email address with proper format.")
            self.email = input('Email: ')
            self.email_input()

    def match_password(self):
        if self.password != self.confirm_password:
            print("Passwords do not match")
            self.password = getpass.getpass()
            self.confirm_password = getpass.getpass('Password Retype:')
            self.match_password()

    def handle(self, *args, **options):
        self.username = input('Username: ')
        self.validate_username()
        self.email = input('Email: ')
        self.email_input()
        self.password = getpass.getpass()
        self.confirm_password = getpass.getpass('Password Retype:')
        self.match_password()

        obj = Staff.objects.create(username=self.username, email=self.email,
                                   is_superuser=True,is_staff=True)
        obj.set_password(self.password)
        obj.save()

        support_staff, created = Group.objects.get_or_create(name="Support Staff")
        obj.groups.add(support_staff)
        print('Staff with superadmin access is created')

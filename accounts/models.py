from django.contrib.auth.models import AbstractUser
from django.db import models

from my_app.models import DateTimeModel


class User(AbstractUser, DateTimeModel):
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=32, null=True, blank=True)
    photo = models.ImageField(upload_to="profile_pics/", default="default.jpg")
    email_confirmed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at", ]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username


class Librarian(User):
    joined_date = models.DateField()

    class Meta:
        ordering = ["-created_at", ]
        verbose_name = "Librarian"
        verbose_name_plural = "Librarians"


class Member(User):
    profession = models.ForeignKey(
        "my_app.Profession", on_delete=models.CASCADE, related_name="member_profession", null=True, blank=True)
    category_interests = models.ManyToManyField(
        "my_app.Category", related_name="interest_categories", blank=True)
    possible_interests = models.ManyToManyField(
        "my_app.Category", related_name="possible_categories", blank=True)
    semi_possible_interests = models.ManyToManyField(
        "my_app.Category", related_name="semi_interested_categories", blank=True)

    class Meta:
        ordering = ["-created_at", ]
        verbose_name = "Member"
        verbose_name_plural = "Members"

    def remove(self):
        self.__class__.objects.filter(id=self.id).delete()

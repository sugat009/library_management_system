from django.conf import settings
from django.db import models
from django.utils import timezone

from jsonfield import JSONField

AUDIT_TYPE_CHOICES = (
    (1, 'LOGIN'),
    (2, 'LOGOUT'),
    (3, 'CREATE'),
    (4, 'UPDATE'),
    (5, 'DELETE'),
)

BOOKING_CHOICES = (
    (1, 'BOOKED'),
    (2, 'LENT'),
    (3, 'RETURNED'),
)


class AuditTrial(models.Model):
    modelType = models.CharField('Model Type', max_length=255)
    objectId = models.IntegerField('Model Obj Id')
    action = models.IntegerField(
        choices=AUDIT_TYPE_CHOICES, default=0, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, on_delete=models.SET_NULL)
    ip = models.GenericIPAddressField(null=True)
    fromObj = JSONField(null=True)
    toObj = JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.modelType) + ' ' + str(dict(AUDIT_TYPE_CHOICES)[self.action]) + ' by : ' + str(
            self.user.username)


class DateTimeModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, )
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True, )
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        super().save()


class Menu(DateTimeModel):
    title = models.CharField(max_length=100)
    position = models.IntegerField(unique=True, null=True, blank=True)
    urls = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='menus')

    class Meta:
        ordering = ["position"]

    def get_root():
        try:
            return Menu.objects.get(title="root")
        except:
            return None

    def not_deleted_children(self):
        return self.menus.filter(deleted_at=None)

    def __str__(self):
        return self.title


class Category(DateTimeModel):
    title = models.CharField(max_length=255)

    class Meta:
        ordering = ["-created_at", ]

    def __str__(self):
        return self.title


class Publisher(DateTimeModel):
    title = models.CharField(max_length=255)

    class Meta:
        ordering = ["-created_at", ]

    def __str__(self):
        return self.title


class Book(DateTimeModel):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, related_name="book_category", blank=True, null=True)
    avg_rating = models.FloatField(default=0.0)
    isbn = models.CharField(max_length=13)
    publisher = models.ForeignKey(Publisher, related_name="book_publisher")
    published_date = models.DateField()
    image = models.ImageField(null=True, blank=True,
                              default="default-book.jpg")
    available = models.BooleanField(default=False)
    number_in_stock = models.IntegerField(default=0)

    class Meta:
        ordering = ["-created_at", ]
        unique_together = ["title", "isbn", ]

    def __str__(self):
        return self.title


class Ratings(DateTimeModel):
    user = models.ForeignKey("accounts.Member", related_name="ratings_user")
    book = models.ForeignKey(Book, related_name="ratings_book")
    ratings = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at', ]
        verbose_name = "Ratings"
        verbose_name_plural = "Ratings"

    def __str__(self):
        return "User {} rated as {}".format(self.user, self.book)


class Booking(DateTimeModel):
    user = models.ForeignKey("accounts.Member", related_name="booking_user")
    book = models.ForeignKey(Book, related_name="booking_book")
    status = models.IntegerField(choices=BOOKING_CHOICES, default=1)
    return_date = models.DateField(null=True, blank=True)
    fine = models.FloatField(default=0.0)

    class Meta:
        ordering = ["-created_at", ]

    def __str__(self):
        return "{0} {2} {1}".format(self.user, self.book, dict(BOOKING_CHOICES)[self.status])


class JaccardSimilarity(DateTimeModel):
    user = models.ForeignKey("accounts.Member", related_name="jaccard_member")
    top_thirty_users = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", ]
        verbose_name = "Jaccard Similarity"
        verbose_name_plural = "Jaccard Similarity"

    def __str__(self):
        return "Jaccard Similarity for user {}".format(self.user)


class UserBasedSimilar(DateTimeModel):
    user = models.ForeignKey("accounts.Member", related_name="user_based_similar_member", null=True, blank=True)
    book = models.ForeignKey(Book, related_name="user_based_similar_book", null=True, blank=True)
    prediction = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-created_at',]
        verbose_name="User Based Similar Object"
        verbose_name_plural="User Based Similar Objects"
    
    def remove(self):
        self.__class__.objects.filter(id=self.id).delete()

    def __str__(self):
        return "User Based similar object for {}--{} book".format(self.user, self.book)


class ItemBasedSimilar(DateTimeModel):
    user = models.ForeignKey("accounts.Member", related_name="item_based_similar_member", null=True, blank=True)
    book = models.ForeignKey(Book, related_name="item_based_similar_book", null=True, blank=True)
    prediction = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-created_at',]
        verbose_name="Item Based Similar Object"
        verbose_name_plural="Item Based Similar Objects"
    
    def remove(self):
        self.__class__.objects.filter(id=self.id).delete()

    def __str__(self):
        return "Item Based similar object for {}--{} book".format(self.user, self.book)


class MemberTestimonial(DateTimeModel):
    user = models.ForeignKey(
        "accounts.Member", related_name="testimonial_member")
    testimonial_text = models.TextField()

    class Meta:
        ordering = ["-created_at", ]
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return "{}'s testimonial".format(self.user)


class Contacts(DateTimeModel):
    name = models.CharField(max_length=48)
    email = models.EmailField()
    subject = models.CharField(max_length=48)
    message = models.TextField()

    class Meta:
        ordering = ["-created_at", ]
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

    def __str__(self):
        return "Contact object: {}".format(self.id)


class Profession(DateTimeModel):
    title = models.CharField(max_length=255, default="null")

    class Meta:
        ordering = ["-title",]
        verbose_name = "Profession Name"
        verbose_name_plural = "Profession Names"

    def __str__(self):
        return self.title
    
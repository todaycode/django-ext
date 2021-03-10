# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models

from django_extensions.db.fields import AutoSlugField, ModificationDateTimeField, RandomCharField, ShortUUIDField
from django_extensions.db.fields.json import JSONField
from django_extensions.db.models import ActivatorModel, TimeStampedModel

from .fields import UniqField


class Secret(models.Model):
    name = models.CharField(blank=True, max_length=255, null=True)
    text = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'django_extensions'


class Name(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = 'django_extensions'


class Note(models.Model):
    note = models.TextField()
    # for DumpScriptTests.test_with_datetimefield
    user = models.ForeignKey('Person', null=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'django_extensions'


class Personality(models.Model):
    description = models.CharField(max_length=50)


class Club(models.Model):
    name = models.CharField(max_length=50)


class Person(models.Model):
    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    age = models.PositiveIntegerField()
    children = models.ManyToManyField('self')
    notes = models.ManyToManyField(Note)
    personality = models.OneToOneField(
        Personality,
        null=True,
        on_delete=models.CASCADE)
    clubs = models.ManyToManyField(Club, through='testapp.Membership')

    class Meta:
        app_label = 'django_extensions'


class Membership(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)


class Post(ActivatorModel):
    title = models.CharField(max_length=255)

    class Meta:
        app_label = 'django_extensions'


class PostWithTitleOrdering(Post):
    class Meta:
        proxy = True
        ordering = ['title']


class DummyRelationModel(models.Model):

    class Meta:
        app_label = 'django_extensions'


class SecondDummyRelationModel(models.Model):

    class Meta:
        app_label = 'django_extensions'


class ThirdDummyRelationModel(models.Model):

    class Meta:
        app_label = 'django_extensions'


class PostWithUniqField(models.Model):

    uniq_field = UniqField(
        max_length=255,
        boolean_attr=True,
        non_boolean_attr='non_boolean_attr'
    )
    common_field = models.CharField(max_length=10)
    another_common_field = models.CharField(max_length=10)
    many_to_one_field = models.ForeignKey(DummyRelationModel, on_delete=models.CASCADE)
    one_to_one_field = models.OneToOneField(SecondDummyRelationModel, on_delete=models.CASCADE)
    many_to_many_field = models.ManyToManyField(ThirdDummyRelationModel, related_name='posts_with_uniq')

    class Meta:
        app_label = 'django_extensions'
        unique_together = ('common_field', 'uniq_field',)


class ReverseModel(models.Model):
    post_field = models.ForeignKey(
        PostWithUniqField, related_name='reverse_models', on_delete=models.CASCADE)

    class Meta:
        app_label = 'django_extensions'


class InheritedFromPostWithUniqField(PostWithUniqField):
    new_field = models.CharField(max_length=10)

    class Meta:
        app_label = 'django_extensions'


class AbstractInheritanceTestModelParent(models.Model):
    my_field_that_my_child_will_inherit = models.BooleanField()

    class Meta:
        app_label = 'django_extensions'
        abstract = True


class AbstractInheritanceTestModelChild(AbstractInheritanceTestModelParent):
    class Meta:
        app_label = 'django_extensions'


class SluggedTestModel(models.Model):
    title = models.CharField(max_length=42)
    slug = AutoSlugField(populate_from='title')

    class Meta:
        app_label = 'django_extensions'


class CustomFuncSluggedTestModel(models.Model):

    def slugify_function(self, content):
        return content.upper()

    title = models.CharField(max_length=42)
    slug = AutoSlugField(populate_from='title')

    class Meta:
        app_label = 'django_extensions'


class CustomFuncPrecedenceSluggedTestModel(models.Model):
    def custom_slug_one(self, content):
        return content.upper()

    def custom_slug_two(content):
        return content.lower()

    slugify_function = custom_slug_one

    title = models.CharField(max_length=42)
    slug = AutoSlugField(populate_from='title', slugify_function=custom_slug_two)

    class Meta:
        app_label = 'django_extensions'


class ChildSluggedTestModel(SluggedTestModel):
    class Meta:
        app_label = 'django_extensions'


class SluggedTestNoOverwriteOnAddModel(models.Model):
    title = models.CharField(max_length=42)
    slug = AutoSlugField(populate_from='title', overwrite_on_add=False)

    class Meta:
        app_label = 'django_extensions'


def get_readable_title(instance):
    return "The title is {}".format(instance.title)


class ModelMethodSluggedTestModel(models.Model):
    title = models.CharField(max_length=42)
    slug = AutoSlugField(populate_from='get_readable_title')

    class Meta:
        app_label = 'django_extensions'

    def get_readable_title(self):
        return get_readable_title(self)


class FunctionSluggedTestModel(models.Model):
    title = models.CharField(max_length=42)
    slug = AutoSlugField(populate_from=get_readable_title)

    class Meta:
        app_label = 'django_extensions'


class FKSluggedTestModel(models.Model):
    related_field = models.ForeignKey(SluggedTestModel, on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from="related_field__title")

    class Meta:
        app_label = 'django_extensions'


class FKSluggedTestModelCallable(models.Model):
    related_field = models.ForeignKey(ModelMethodSluggedTestModel, on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from="related_field__get_readable_title")

    class Meta:
        app_label = 'django_extensions'


class JSONFieldTestModel(models.Model):
    a = models.IntegerField()
    j_field = JSONField()

    class Meta:
        app_label = 'django_extensions'


class ShortUUIDTestModel_field(models.Model):
    a = models.IntegerField()
    uuid_field = ShortUUIDField()

    class Meta:
        app_label = 'django_extensions'


class ShortUUIDTestModel_pk(models.Model):
    uuid_field = ShortUUIDField(primary_key=True)

    class Meta:
        app_label = 'django_extensions'


class ShortUUIDTestAgregateModel(ShortUUIDTestModel_pk):
    a = models.IntegerField()

    class Meta:
        app_label = 'django_extensions'


class ShortUUIDTestManyToManyModel(ShortUUIDTestModel_pk):
    many = models.ManyToManyField(ShortUUIDTestModel_field)

    class Meta:
        app_label = 'django_extensions'


class RandomCharTestModel(models.Model):
    random_char_field = RandomCharField(length=8, unique=False)

    class Meta:
        app_label = 'django_extensions'


class RandomCharTestModelUnique(models.Model):
    random_char_field = RandomCharField(length=8, unique=True)

    class Meta:
        app_label = 'django_extensions'


class RandomCharTestModelAlphaDigits(models.Model):
    random_char_field = RandomCharField(length=8, unique=True)

    class Meta:
        app_label = 'django_extensions'


class RandomCharTestModelLowercaseAlphaDigits(models.Model):
    random_char_field = RandomCharField(length=8, lowercase=True)

    class Meta:
        app_label = 'django_extensions'
        verbose_name = 'lowercase alpha digits'


class RandomCharTestModelUppercaseAlphaDigits(models.Model):
    random_char_field = RandomCharField(length=8, uppercase=True)

    class Meta:
        app_label = 'django_extensions'
        verbose_name = 'uppercase alpha digits'


class RandomCharTestModelLowercase(models.Model):
    random_char_field = RandomCharField(length=8, lowercase=True, include_digits=False)

    class Meta:
        app_label = 'django_extensions'


class RandomCharTestModelUppercase(models.Model):
    random_char_field = RandomCharField(length=8, uppercase=True, include_digits=False)

    class Meta:
        app_label = 'django_extensions'


class RandomCharTestModelAlpha(models.Model):
    random_char_field = RandomCharField(length=8, include_digits=False)

    class Meta:
        app_label = 'django_extensions'


class RandomCharTestModelDigits(models.Model):
    random_char_field = RandomCharField(length=8, include_alpha=False)

    class Meta:
        app_label = 'django_extensions'


class RandomCharTestModelPunctuation(models.Model):
    random_char_field = RandomCharField(
        length=8,
        include_punctuation=True,
        include_digits=False,
        include_alpha=False,
    )

    class Meta:
        app_label = 'django_extensions'


class TimestampedTestModel(TimeStampedModel):
    class Meta:
        app_label = 'django_extensions'


class UnicodeVerboseNameModel(models.Model):
    cafe = models.IntegerField(verbose_name=u'café')
    parent_cafe = models.ForeignKey('self', related_name='children',
                                    on_delete=models.CASCADE,
                                    verbose_name='café latte')

    class Meta:
        app_label = 'django_extensions'
        verbose_name = u'café unicode model'


class Permission(models.Model):
    text = models.CharField(max_length=32)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)


class UniqueTestAppModel(models.Model):
    global_id = models.CharField(max_length=32, unique=True)


class SqlDiff(models.Model):
    number = models.CharField(max_length=40, null=True, verbose_name='Chargennummer')
    creator = models.CharField(max_length=20, null=True, blank=True)


class SqlDiffUniqueTogether(models.Model):
    aaa = models.CharField(max_length=20)
    bbb = models.CharField(max_length=20)

    class Meta:
        unique_together = ['aaa', 'bbb']


class Photo(models.Model):
    photo = models.FileField()


class CustomModelModificationDateTimeField(models.Model):
    field_to_update = models.BooleanField(default=True)
    custom_modified = ModificationDateTimeField()

    class Meta:
        app_label = 'django_extensions'


class ModelModificationDateTimeField(models.Model):
    field_to_update = models.BooleanField(default=True)
    modified = ModificationDateTimeField()

    class Meta:
        app_label = 'django_extensions'


class DisabledUpdateModelModificationDateTimeField(models.Model):
    field_to_update = models.BooleanField(default=True)
    modified = ModificationDateTimeField()

    update_modified = False

    class Meta:
        app_label = 'django_extensions'

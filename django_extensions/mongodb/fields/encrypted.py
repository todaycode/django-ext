# -*- coding: utf-8 -*-
import warnings

from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from mongoengine.base import BaseField
from django_extensions.utils.deprecation import RemovedInNextVersionWarning

try:
    from keyczar import keyczar
except ImportError:
    raise ImportError('Using an encrypted field requires the Keyczar module.  You can obtain Keyczar from http://www.keyczar.org/.')


class BaseEncryptedField(BaseField):
    prefix = 'enc_str:::'

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Please do not use these fields. Since Keyczar is deprecated and authors deleted "
            "all code we highly recommend to stop using potentially unsafe abandonware directly "
            "these versions of encrypted fields will be removed soon but it's highly likely their "
            "names will be reused. Please see github issues/1359 for discussion on possible "
            "replacement fields",
            RemovedInNextVersionWarning,
            stacklevel=2,
        )

        if not getattr(settings, 'ENCRYPTED_KEYCZAR_THISISUNSAFE', None):
            raise ImproperlyConfigured(
                "Please do not use these fields. Since Keyczar is deprecated and authors deleted "
                "all code we highly recommend to stop using potentially unsafe abandonware directly "
                "these versions of encrypted fields will be removed soon but it's highly likely their "
                "names will be reused. Please see github issues/1359 for discussion on possible "
                "replacement fields",
            )

        if not hasattr(settings, 'ENCRYPTED_FIELD_KEYS_DIR'):
            raise ImproperlyConfigured('You must set settings.ENCRYPTED_FIELD_KEYS_DIR to your Keyczar keys directory.')
        self.crypt = keyczar.Crypter.Read(settings.ENCRYPTED_FIELD_KEYS_DIR)
        super(BaseEncryptedField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value.startswith(self.prefix):
            retval = self.crypt.Decrypt(value[len(self.prefix):])
        else:
            retval = value

        return retval

    def get_db_prep_value(self, value):
        if not value.startswith(self.prefix):
            value = self.prefix + self.crypt.Encrypt(value)
        return value


class EncryptedTextField(BaseEncryptedField):
    def get_internal_type(self):
        return 'StringField'

    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(EncryptedTextField, self).formfield(**defaults)


class EncryptedCharField(BaseEncryptedField):
    def __init__(self, max_length=None, *args, **kwargs):
        if max_length:
            max_length += len(self.prefix)

        super(EncryptedCharField, self).__init__(max_length=max_length, *args, **kwargs)

    def get_internal_type(self):
        return "StringField"

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        return super(EncryptedCharField, self).formfield(**defaults)

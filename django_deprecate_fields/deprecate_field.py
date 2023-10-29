# Copyright 2023 Adrian Torres
# Copyright 2018-2023 3YOURMIND GmbH

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This file has been modified by Adrian Torres in order to implement new
# features, fix bugs and improve code and documentation.


import logging
import sys
import warnings

logger = logging.getLogger(__name__)


class FieldDeprecatedError(Exception):
    pass


class DeprecatedField(object):
    """
    Descriptor class for deprecated fields. Do not use directly, use the
    deprecate_field function instead.
    """

    def __init__(self, val, raise_on_access=False):
        self.val = val
        self.raise_on_access = raise_on_access
        self.model_name = "Unknown"
        self.field_name = "unknown"

    def _warn(self, prefix):
        """
        Log and warn about access to the deprecated field.
        """
        if (name := str(self)) and name == "Unknown.unknown":
            message = f"{prefix} unknown deprecated field"
        else:
            message = f"{prefix} deprecated field {name}"
        if self.raise_on_access:
            raise FieldDeprecatedError(message)
        warnings.warn(message, DeprecationWarning, stacklevel=2)
        logger.warning(message)

    def _log_read(self):
        self._warn("Accessing")

    def _log_write(self):
        self._warn("Writing to")

    def __get__(self, obj, objtype=None):
        self._log_read()
        if obj is None:
            return self
        if not callable(self.val):
            return self.val
        # we pass the Model object instance to the callable in case the
        # value of the deprecated field can be extrapolated from another
        # field
        return self.val(obj)

    def __set__(self, obj, val):
        self._log_write()
        self.val = val

    def __set_name__(self, owner, name):
        self.model_name = owner.__name__
        self.field_name = name

    def __str__(self):
        return f"{self.model_name}.{self.field_name}"


def deprecate_field(base_field, return_instead=None, raise_on_access=False):
    """
    Can be used in models to delete a Field in a Backwards compatible manner.
    The process for deleting old model Fields is:
    1. Mark a field as deprecated by wrapping the field with this function
    2. Wait until (1) is deployed to every relevant server/branch
    3. Delete the field from the model.

    For (1) and (3) you need to run ./manage.py makemigrations:
    :param field_instance: The field to deprecate
    :param return_instead: A value or function that
    the field will pretend to have
    :param raise_on_access: If true, raise FieldDeprecated instead of logging a warning
    """
    if not set(sys.argv) & {"makemigrations", "migrate", "showmigrations"}:
        return DeprecatedField(return_instead, raise_on_access=raise_on_access)

    base_field.null = True
    return base_field

# Copyright 2023 Adrian Torres

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django.db import models

from django_deprecate_fields import deprecate_field


def calc_baz(_):
    return "baz"


class DeprecationModel(models.Model):
    def _deprecate_ham(self):
        return self.eggs

    foo = deprecate_field(models.IntegerField())
    bar = deprecate_field(models.CharField(max_length=30), return_instead="bar")
    baz = deprecate_field(models.CharField(max_length=30), return_instead=calc_baz)
    eggs = models.CharField(max_length=30, blank=True)
    ham = deprecate_field(
        models.CharField(max_length=30), return_instead=_deprecate_ham
    )


class InheritingDeprecationModel(DeprecationModel):
    @property
    def cheese(self):
        return super().foo

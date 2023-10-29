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


import pytest

from django_deprecate_fields.deprecate_field import DeprecatedField
from tests.models import DeprecationModel, InheritingDeprecationModel


class TestWarnings:
    def test_deprecation_warning(self):
        with pytest.deprecated_call():
            DeprecationModel().foo


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
class TestLogging:
    def test_logging_read(self, caplog):
        """
        Test that accessing a deprecated field produces a correct log entry.
        """
        # trigger a logging of the deprecated field being accessed
        DeprecationModel().foo
        assert len(caplog.records) == 1
        assert "Accessing deprecated field" in caplog.records[0].msg
        assert caplog.records[0].levelname == "WARNING"

    def test_logging_write(self, caplog):
        """
        Test that writing to a deprecated field produces a correct log entry.
        """
        DeprecationModel().foo = 5
        assert len(caplog.records) == 1
        assert "Writing to deprecated field" in caplog.records[0].msg
        assert caplog.records[0].levelname == "WARNING"
        # rest its value as it's kept across instances
        DeprecationModel().foo = None

    def test_logging_instance(self, caplog):
        """
        Test that access through a model instance produces a correct log entry.
        """
        DeprecationModel().foo
        assert (
            caplog.records[0].msg == "Accessing deprecated field DeprecationModel.foo"
        )

    def test_logging_class(self, caplog):
        """
        Test that access through a model class produces a correct log entry.
        """
        DeprecationModel.foo
        assert (
            caplog.records[0].msg == "Accessing deprecated field DeprecationModel.foo"
        )
        assert (
            caplog.records[0].msg == "Accessing deprecated field DeprecationModel.foo"
        )

    def test_logging_super(self, caplog):
        """
        Test that access through a super object produces a correct log entry.
        """
        # since cheese calls super().foo we should be able to test how the descriptor
        # handles super objects
        InheritingDeprecationModel().cheese
        assert (
            caplog.records[0].msg == "Accessing deprecated field DeprecationModel.foo"
        )

    def test_logging_unknown(self, caplog):
        DeprecatedField(5)._log_read()
        assert caplog.records[0].msg == "Accessing unknown deprecated field"


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
class TestCore:
    def test_descriptor_access(self):
        """
        Test that accessing a descriptor through Model class works.

        When accessing a descriptor through a Model instance (i.e. a concrete
        record), the result should be whatever logic the descriptor is set up
        to execute.

        When accessing a descriptor through a Model class, the result should be
        the descriptor itself as there is no object on which to act.
        """
        assert DeprecationModel().foo is None
        assert isinstance(DeprecationModel.foo, DeprecatedField)

    def test_static_return_instead(self):
        """
        Test that a deprecated field with a static return_instead value works.
        """
        assert DeprecationModel().bar == "bar"

    def test_function_return_instead(self):
        """
        Test that a deprecated field with a function-based return_instead works.
        """
        assert DeprecationModel().baz == "baz"

    def test_method_return_instead(self):
        """
        Test that a deprecated field with a method-based return_instead works.
        """
        dm = DeprecationModel(eggs="eggs")
        assert dm.ham == "eggs"
        assert dm.ham == dm.eggs

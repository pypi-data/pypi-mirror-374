# This file is part of pydantic-kitbash.
#
# Copyright 2025 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License version 3, as published by the Free
# Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranties of MERCHANTABILITY, SATISFACTORY
# QUALITY, or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import enum
import typing
from importlib import import_module
from typing import Annotated, TypeVar

import pydantic
import pytest
import yaml
from docutils import nodes
from docutils.core import publish_doctree
from pydantic_kitbash.directives import (
    FieldEntry,
    build_examples_block,
    create_field_node,
    create_table_node,
    find_fieldinfo,
    format_type_string,
    get_annotation_docstring,
    get_enum_field_data,
    get_enum_member_docstring,
    get_enum_values,
    get_optional_annotated_field_data,
    get_pydantic_model,
    is_deprecated,
    is_enum_type,
    parse_rst_description,
    strip_whitespace,
)


class EnumType(enum.Enum):
    VALUE = "value"


class MockObject:
    # contents don't matter, this is just for testing type formatting
    the_real_treasure: str

    def __init__(self):
        self.the_real_treasure = "the friends we made along the way"


def validator(value: str) -> str:
    return value.strip()


# Used for testing `get_optional_annotated_field_data` edge case
T = TypeVar("T")

UniqueList = Annotated[
    list[T],
    pydantic.Field(json_schema_extra={"uniqueItems": True}),
]


TEST_TYPE = Annotated[
    str,
    pydantic.AfterValidator(validator),
    pydantic.BeforeValidator(validator),
    pydantic.Field(
        description="This is the description of test type.",
        examples=["str1", "str2", "str3"],
    ),
]

TYPE_NO_FIELD = Annotated[
    str,
    pydantic.AfterValidator(validator),
    pydantic.BeforeValidator(validator),
]

ENUM_TYPE = Annotated[
    EnumType,
    pydantic.Field(description="Enum field."),
]

RST_SAMPLE = """This is an rST sample.

**Examples**

.. code-block:: yaml

    test: passed

"""

TABLE_RST = """\

.. list-table::
    :header-rows: 1

    * - Value
      - Description
    * - ``1.1``
      - 1.2
    * - ``2.1``
      - 2.2

"""

KEY_ENTRY_RST = """\

.. important::

    Don't use this.

**Type**

``str``

**Description**

This is the key description

"""

LIST_YAML = """\
key:
  - item1: val1
    item2: val2
"""


LITERAL_LIST_ENTRY_RST = """\

.. important::

    Don't use this.

**Type**

One of: ``['one', 'two', 'three']``

**Description**

This is the key description

"""


def test_get_pydantic_model(fake_field_directive):
    """Test for get_pydantic_model with valid input."""

    module = import_module("tests.unit.conftest")
    expected = module.MockModel
    actual = get_pydantic_model(fake_field_directive)

    assert type(expected) is type(actual)


@pytest.mark.parametrize(
    "fake_field_directive",
    [{"arguments": ["MockFieldModel", "mock_field"]}],
    indirect=True,
)
def test_get_pydantic_model_with_module(fake_field_directive):
    """Test for get_pydantic_model when py:module is set."""
    module = import_module("tests.unit.conftest")
    expected = module.MockModel

    fake_field_directive.env.ref_context["py:module"] = fake_field_directive.__module__
    actual = get_pydantic_model(fake_field_directive)

    assert type(expected) is type(actual)


@pytest.mark.parametrize(
    "fake_model_directive", [{"model": ".OopsNoModel"}], indirect=True
)
def test_kitbash_model_invalid(fake_model_directive):
    """Test for get_pydantic_model with invalid input."""

    with pytest.raises(
        TypeError, match="OopsNoModel is not a subclass of pydantic.BaseModel"
    ):
        fake_model_directive.run()


def test_find_fieldinfo():
    """Test for find_fieldinfo with valid input."""

    metadata = getattr(TEST_TYPE, "__metadata__", None)
    if metadata is not None:
        expected = metadata[2]
        actual = find_fieldinfo(metadata)
        assert expected == actual
    else:
        pytest.fail("No metadata found")


def test_find_fieldinfo_none():
    """Test for find_fieldinfo() when no FieldInfo object is present."""
    expected = None
    actual = find_fieldinfo(None)

    assert expected == actual


def test_is_deprecated():
    """Test for is_deprecated()"""

    class Model(pydantic.BaseModel):
        field1: TEST_TYPE
        field2: str = pydantic.Field(deprecated=False)
        field3: str = pydantic.Field(deprecated=True)
        union_field: str | None = pydantic.Field(
            deprecated="pls don't use this :)",
        )

    assert not is_deprecated(Model, "field1")
    assert not is_deprecated(Model, "field2")
    assert is_deprecated(Model, "field3") == "This key is deprecated."
    assert is_deprecated(Model, "union_field") == "Deprecated. pls don't use this :)"


def test_is_deprecated_invalid():
    """Test for is_deprecated when passed a nonexistent field."""

    class Model(pydantic.BaseModel):
        field1: TEST_TYPE

    try:
        is_deprecated(Model, "nope")
        pytest.fail("Invalid fields should raise a ValueError.")
    except ValueError:
        assert True


def test_is_enum_type():
    """Test for is_enum_type when passed an enum."""

    class Model(pydantic.BaseModel):
        field: EnumType

    assert is_enum_type(Model.model_fields["field"].annotation)


def test_is_enum_type_false():
    """Test for is_enum_type when passed a non-enum field."""

    class Model(pydantic.BaseModel):
        field: int

    assert not is_enum_type(Model.model_fields["field"].annotation)


def test_create_field_node(fake_field_directive):
    """Test for create_field_node."""

    # need to set up section node manually
    expected = nodes.section(ids=["key-name", "key-name"])
    expected["classes"].append("kitbash-entry")
    title_node = nodes.title(text="key-name")
    expected += title_node
    target_node = nodes.target()
    target_node["refid"] = "key-name"
    expected += target_node
    expected += publish_doctree(KEY_ENTRY_RST).children

    test_entry = FieldEntry("key-name", fake_field_directive)
    test_entry.alias = "key-name"
    test_entry.label = "key-name"
    test_entry.deprecation_warning = "Don't use this."
    test_entry.field_type = "str"
    test_entry.description = "This is the key description"

    # "Values" and "Examples" are tested separately because while
    # their HTML output is identical, their docutils nodes are structured
    # differently from the publish_doctree output
    actual = create_field_node(test_entry)

    assert str(expected) == str(actual)


def test_create_field_node_literal_list(fake_field_directive):
    """Test for create_field_node with a FieldEntry of type Literal[]."""

    # need to set up section node manually
    expected = nodes.section(ids=["key-name", "key-name"])
    expected["classes"].append("kitbash-entry")
    title_node = nodes.title(text="key-name")
    expected += title_node
    target_node = nodes.target()
    target_node["refid"] = "key-name"
    expected += target_node
    expected += publish_doctree(LITERAL_LIST_ENTRY_RST).children

    test_entry = FieldEntry("key-name", fake_field_directive)
    test_entry.alias = "key-name"
    test_entry.label = "key-name"
    test_entry.deprecation_warning = "Don't use this."
    test_entry.field_type = "Literal['one', 'two', 'three']"
    test_entry.description = "This is the key description"
    actual = create_field_node(test_entry)

    assert str(expected) == str(actual)


def test_create_minimal_field_node(fake_field_directive):
    """Test for create_field_node with a minimal set of attributes."""

    # need to set up section node manually
    expected = nodes.section(ids=["key-name", "key-name"])
    expected["classes"].append("kitbash-entry")
    title_node = nodes.title(text="key-name")
    expected += title_node
    target_node = nodes.target()
    target_node["refid"] = "key-name"
    expected += target_node

    test_entry = FieldEntry("key-name", fake_field_directive)

    actual = create_field_node(test_entry)

    assert str(expected) == str(actual)


def test_build_valid_examples_block():
    """Test for build_examples_block with valid input."""

    # Not using publish_doctree because the nodes differ, despite the HTML
    # of the rendered output being identical. This test could be improved
    # by using publish_doctree and the Sphinx HTML writer, which I couldn't
    # seem to get working.
    yaml_str = "test: {subkey: [good, nice]}"
    yaml_str = yaml.dump(yaml.safe_load(yaml_str), default_flow_style=False)
    yaml_str = yaml_str.replace("- ", "  - ").rstrip("\n")

    expected = nodes.literal_block(text=yaml_str)
    expected["language"] = "yaml"

    actual = build_examples_block("test", "{subkey: [good, nice]}")

    # comparing strings because docutils `__eq__`
    # method compares by identity rather than state
    assert str(expected) == str(actual)


def test_build_list_example():
    """Test for build_examples_block when rendering lists of dicts."""
    expected = nodes.literal_block(text=(LIST_YAML.rstrip("\n")))
    expected["language"] = "yaml"

    actual = build_examples_block("key", "[{item1: val1, item2: val2}]")

    assert str(expected) == str(actual)


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_build_invalid_examples_block():
    """Test for build_examples_block with invalid input."""

    expected = nodes.literal_block(text="test: {[ oops")
    expected["language"] = "yaml"

    actual = build_examples_block("test", "{[ oops")

    # comparing strings because docutils `__eq__`
    # method compares by identity rather than state
    assert str(expected) == str(actual)


def test_create_table_node(fake_field_directive):
    """Test for create_table_node."""

    expected = nodes.container()
    expected += publish_doctree(TABLE_RST).children

    actual = create_table_node([["1.1", "1.2"], ["2.1", "2.2"]], fake_field_directive)

    # comparing strings because docutils `__eq__`
    # method compares by identity rather than state
    assert str(expected) == str(actual)


def test_get_annotation_docstring():
    """Test for get_annotation_docstring."""

    class MockModel(pydantic.BaseModel):
        field1: int

        field2: str
        """The second field."""

        """Should never see this docstring."""

    assert get_annotation_docstring(MockModel, "field1") is None
    assert get_annotation_docstring(MockModel, "field2") == "The second field."


def test_get_enum_member_docstring():
    """Test for get_enum_member_docstring."""

    class MockEnum(enum.Enum):
        VAL1 = "one"

        VAL2 = "two"
        """This is the second value."""

        """Should never see this docstring."""

    assert get_enum_member_docstring(MockEnum, "VAL1") is None
    assert get_enum_member_docstring(MockEnum, "VAL2") == "This is the second value."


def test_get_enum_values():
    """Test for get_enum_values."""

    class MockEnum(enum.Enum):
        VAL1 = "one"
        """Docstring 1."""

        VAL2 = "two"
        """Docstring 2."""

    assert get_enum_values(MockEnum) == [
        ["one", "Docstring 1."],
        ["two", "Docstring 2."],
    ]


def test_parse_rst_description(fake_field_directive):
    """Test parse_rst_description."""

    # use docutils to build rST like Sphinx would
    expected = publish_doctree(RST_SAMPLE).children
    # function output
    actual = parse_rst_description(RST_SAMPLE, fake_field_directive)

    # comparing strings because docutils `__eq__`
    # method compares by identity rather than state
    assert str(expected) == str(actual)


def test_strip_whitespace():
    """Test for strip_whitespace."""

    docstring1 = """Description.

      **Examples**

      .. code-block:: yaml

          test: passed

      """

    docstring2 = """\
      Description.

      **Examples**

      .. code-block:: yaml

          test: passed

      """

    expected = (
        "Description.\n\n**Examples**\n\n.. code-block:: yaml\n\n    test: passed\n"
    )

    assert strip_whitespace(docstring1) == expected
    assert strip_whitespace(docstring2) == expected
    assert strip_whitespace(None) == ""


def test_format_type_string():
    """Test for format_type_string."""

    annotated_type = typing.Annotated[str, pydantic.Field(description="test")]
    object_type = type(MockObject())
    list_type = typing.Literal["val1", "val2", "val3"]

    assert format_type_string(None) == ""
    assert format_type_string(getattr(annotated_type, "__origin__", None)) == "str"
    assert format_type_string("dict[idk.man.str, typing.Any]") == "dict[str, Any]"
    assert format_type_string(object_type) == "MockObject"
    assert format_type_string(list_type) == "Literal['val1', 'val2', 'val3']"


def test_get_optional_annotated_field_data_no_annotation(fake_field_directive):
    """\
    Test for get_optional_annotated_field_data when the first arg has no
    annotation.
    """

    class MockModel(pydantic.BaseModel):
        field1: str | UniqueList[str] = pydantic.Field(
            description="desc",
            examples=["one", "two"],
        )

    annotation = MockModel.model_fields["field1"].annotation

    entry = FieldEntry("nom", fake_field_directive)
    get_optional_annotated_field_data(entry, annotation)

    assert entry.name == "nom"
    assert entry.field_type is None
    assert entry.description is None
    assert entry.examples is None


def test_get_optional_annotated_field_data_none(fake_field_directive):
    """Test for get_optional_annotated_field_data when no field is provided."""

    entry = FieldEntry("nice try", fake_field_directive)
    assert get_optional_annotated_field_data(entry, None) is None


def test_get_enum_field_data_none(fake_field_directive):
    """Test for get_enum_field_data when no annotation is provided."""

    entry = FieldEntry("nice try", fake_field_directive)
    assert get_enum_field_data(entry, None) is None

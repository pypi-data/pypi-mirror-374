"""Tests related to xivapy models."""

from typing import Annotated

from pydantic import ValidationError
import pytest

from xivapy.model import Model, FieldMapping, QueryField
from xivapy.types import LangDict


@pytest.mark.unit
def test_model_sheet_name_from_class():
    """Test that we get the class name when no sheet name is defined."""

    class TestItem(Model):
        name: str

    assert TestItem.get_sheet_name() == 'TestItem'


@pytest.mark.unit
def test_model_sheet_name_from_sheetname():
    """Test getting sheet name from defined field."""

    class CustomModel(Model):
        name: str
        __sheetname__ = 'Ackchyally'

    assert CustomModel.get_sheet_name() == 'Ackchyally'


@pytest.mark.unit
def test_basic_model_validation():
    """Test that fields map even without specific fields defined."""

    class SimpleModel(Model):
        row_id: int
        name: str
        level: int = 0

    data = {'row_id': 1, 'name': 'Test', 'level': 50}
    model = SimpleModel.model_validate(data)

    assert model.row_id == 1
    assert model.name == 'Test'
    assert model.level == 50


@pytest.mark.unit
def test_get_xivapi_fields_basic():
    """Test that defined basic fields in model generate as Title Cased names for xivapi."""

    class BasicModel(Model):
        row_id: int
        Name: str
        level: int

    fields = BasicModel.get_xivapi_fields()
    expected = {'row_id', 'Name', 'level'}
    assert fields == expected


@pytest.mark.unit
def test_get_xivapi_fields_with_override():
    """Test overriding a field name to an xivapi-specific alias."""

    class BasicModel(Model):
        id: Annotated[int, FieldMapping('row_id')]
        name: str

    fields = BasicModel.get_xivapi_fields()
    expected = {'row_id', 'name'}
    assert fields == expected


@pytest.mark.unit
def test_multiple_fields_with_same_nested_source():
    """Test that data is non-destructively pulled out of a nested dict."""

    class TestModel(Model):
        tanks: Annotated[int, FieldMapping('ContentMemberType.TanksPerParty')]
        healers: Annotated[int, FieldMapping('ContentMemberType.HealersPerParty')]

    data = {
        'ContentMemberType': {
            'fields': {
                'TanksPerParty': 2,
                'HealersPerParty': 1,
            }
        }
    }

    result = TestModel.model_validate(data)
    assert result.tanks == 2
    assert result.healers == 1


@pytest.mark.unit
def test_model_with_no_fields():
    """Test defining an empty model."""

    class EmptyModel(Model): ...

    fields = EmptyModel.get_xivapi_fields()
    assert fields == set()


@pytest.mark.unit
def test_field_custom_spec():
    """Test that you can completely override the field with a custom specification."""
    custom_spec = FieldMapping('custom', custom_spec='custom@as(custom)')

    assert custom_spec.to_field_specs() == ['custom@as(custom)']


@pytest.mark.unit
def test_field_language_spec():
    """Test that you can define a series of language(s) as a specification."""
    all_langs = FieldMapping('all', languages=['en', 'fr', 'de', 'ja'])
    no_french = FieldMapping('NoRomance', languages=['en', 'de', 'ja'])

    all_langs_specs = all_langs.to_field_specs()
    assert all_langs_specs == [
        'all@lang(en)',
        'all@lang(fr)',
        'all@lang(de)',
        'all@lang(ja)',
    ]

    no_french_specs = no_french.to_field_specs()
    assert no_french_specs == [
        'NoRomance@lang(en)',
        'NoRomance@lang(de)',
        'NoRomance@lang(ja)',
    ]


@pytest.mark.unit
def test_process_language_fields():
    """Test processing language fields from xivapi responses."""

    class Test(Model):
        name: Annotated[
            LangDict, FieldMapping('Name', languages=['en', 'fr', 'de', 'ja'])
        ]

    result = Test.model_validate(
        {
            'row_id': 44,
            'Name@lang(en)': 'Hello America',
            'Name@lang(fr)': 'Hello France',
            'Name@lang(de)': 'Hello Germany',
            'Name@lang(ja)': 'Hello Japan',
        }
    )

    assert isinstance(result, Test)
    assert 'en' in result.name and result.name['en'] == 'Hello America'
    assert 'fr' in result.name and result.name['fr'] == 'Hello France'
    assert 'de' in result.name and result.name['de'] == 'Hello Germany'
    assert 'ja' in result.name and result.name['ja'] == 'Hello Japan'


@pytest.mark.unit
def test_process_fields_missing_language():
    """Test what happens when a requested language just doesn't come back."""

    class Test(Model):
        name: Annotated[LangDict, FieldMapping('Name', languages=['en', 'fr'])]

    result = Test.model_validate(
        {
            'row_id': 1,
            'Name@lang(en)': 'Hello',
        }
    )

    assert 'fr' not in result.name
    assert 'en' in result.name
    assert result.name['en'] == 'Hello'


@pytest.mark.unit
def test_queryfield_model_fields():
    """Test that models with QueryField behave as normal when instantiated."""

    class Test(Model):
        row_id: QueryField[int]
        name: QueryField[str] = QueryField(FieldMapping('Name'))

    result = Test.model_validate(
        {
            'row_id': 1,
            'Name': 'Foo',
        }
    )

    assert isinstance(result, Test)
    assert result.row_id == 1
    assert result.name == 'Foo'


@pytest.mark.unit
def test_queryfield_type_responses():
    """At a minimum, QueryFields should accept int, str, and dict responses."""

    class Test(Model):
        row_id: QueryField[int]
        Name: QueryField[str]
        Params: QueryField[dict]

    result = Test.model_validate(
        {
            'row_id': 432,
            'Name': 'Foo',
            'Params': {
                'foo': 'bar',
                'baz': 2,
            },
        }
    )

    assert isinstance(result, Test)
    assert result.row_id == 432
    assert result.Name == 'Foo'
    assert result.Params == {'foo': 'bar', 'baz': 2}


@pytest.mark.unit
def test_get_queryfield_mappings():
    """Test basic QueryField mappings API returns correct QueryDescriptors."""

    class Test(Model):
        row_id: QueryField[int]
        name: QueryField[str] = QueryField(FieldMapping('Name'))

    mappings = Test.get_queryfield_mappings()

    assert 'row_id' in mappings
    assert 'name' in mappings
    assert len(mappings) == 2

    from xivapy.query import QueryDescriptor

    assert isinstance(mappings['row_id'], QueryDescriptor)
    assert isinstance(mappings['name'], QueryDescriptor)


@pytest.mark.unit
def test_get_queryfield_mappings_from_field_mapping():
    """Test that FieldMapping configuration is preserved in QueryDescriptors."""

    class Test(Model):
        name: QueryField[str] = QueryField(FieldMapping('Name', languages=['en', 'fr']))
        bgm: QueryField[str] = QueryField(FieldMapping('Content.BGM.File'))

    mappings = Test.get_queryfield_mappings()

    assert mappings['name'].xivapi_field == 'Name'
    assert mappings['bgm'].xivapi_field == 'Content.BGM.File'


@pytest.mark.unit
def test_get_queryfield_mappings_empty_model():
    """Test that QueryField mappings are absent when none are annotated."""

    class Empty(Model):
        row_id: int

    mappings = Empty.get_queryfield_mappings()
    assert mappings == {}


@pytest.mark.unit
def test_get_queryfield_mappings_inheritance():
    """Test mappings with model inheritance."""

    class Base(Model):
        row_id: QueryField[int]
        Name: str

    class Derived(Base):
        content: QueryField[str] = QueryField(FieldMapping('Content'))

    base_mappings = Base.get_queryfield_mappings()
    derived_mappings = Derived.get_queryfield_mappings()

    assert 'row_id' in base_mappings
    assert 'Name' not in base_mappings
    assert len(base_mappings) == 1

    assert 'row_id' in derived_mappings
    assert 'content' in derived_mappings
    assert 'Name' not in base_mappings
    assert len(derived_mappings) == 2


@pytest.mark.unit
@pytest.mark.regression
def test_queryfield_mappings_immutable():
    """Test that returned mappings are copies, not refs."""

    class Test(Model):
        name: QueryField[str]

    mapping_one = Test.get_queryfield_mappings()
    mapping_two = Test.get_queryfield_mappings()

    assert mapping_one == mapping_two
    assert mapping_one is not mapping_two


@pytest.mark.unit
@pytest.mark.regression
def test_queryfield_mappings_private():
    """Test that returned mappings are copies, not refs."""

    class Test(Model):
        row_id: QueryField[int]
        name: QueryField[str] = QueryField(FieldMapping('Name'))

    assert not hasattr(Test, '_queryfield_mappings')  # old name
    assert hasattr(Test, '__queryfield_mappings__')
    assert hasattr(Test, '__querydescriptor_mappings__')

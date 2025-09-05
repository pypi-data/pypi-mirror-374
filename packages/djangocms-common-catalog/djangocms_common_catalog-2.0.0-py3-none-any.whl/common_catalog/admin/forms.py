from ..models import Attribute, AttributeType, CatalogItem
from .translatable_entangled import CommonCatalogEntangledTranslatableModelForm


class AttributeTypeForm(CommonCatalogEntangledTranslatableModelForm):
    """Attribute Type form."""

    class Meta(CommonCatalogEntangledTranslatableModelForm.Meta):
        model = AttributeType
        untangled_fields = [
            'name',
            'display_in_location',
        ]


class AttributeForm(CommonCatalogEntangledTranslatableModelForm):
    """Attribute form."""

    class Meta(CommonCatalogEntangledTranslatableModelForm.Meta):
        model = Attribute
        untangled_fields = [
            'name',
            'attr_type',
        ]


class CatalogItemForm(CommonCatalogEntangledTranslatableModelForm):
    """Catalog Item form."""

    class Meta(CommonCatalogEntangledTranslatableModelForm.Meta):
        model = CatalogItem
        untangled_fields = [
            'name',
            'ident',
            'perex',
            'description',
            'attrs',
            'display_from',
            'display_until',
            'app_config',
        ]

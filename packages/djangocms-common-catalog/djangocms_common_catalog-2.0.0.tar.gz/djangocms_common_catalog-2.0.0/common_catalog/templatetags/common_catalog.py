from typing import Optional

from django import template
from django.db.models.query import QuerySet
from django.utils.http import urlencode

from ..models import CatalogItem, Location

register = template.Library()


@register.filter
def filters_in_location(item: CatalogItem, code: str) -> QuerySet:
    """Display filters in location defined by code."""
    try:
        location = Location.objects.get(app_config=item.app_config, code=code)
    except Location.DoesNotExist:
        return item.attrs.all()
    return item.attrs.filter(attr_type__display_in_location=location)


@register.filter()
def catalog_list_page_params(page_params: dict, page: Optional[int] = None) -> str:
    """Catalog list page params. Views must have 'page_params' key with dict in context."""
    params = []
    page_set = False
    for key, value in page_params.items():
        if key == 'page' and page is not None:
            value = page
            page_set = True
        if isinstance(value, (list, set, tuple)):
            for item in value:
                params.append((key, item))
        else:
            params.append((key, value))
    if page is not None and not page_set:
        params.append(('page', page))
    return "?" + urlencode(params) if params else ""

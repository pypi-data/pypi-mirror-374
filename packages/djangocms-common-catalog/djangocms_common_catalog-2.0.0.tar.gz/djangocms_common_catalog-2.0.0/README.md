# Common Catalog

Common catalog for various uses.

The program is built on the  [Django CMS](https://www.django-cms.org/) framework.

The program itself does not contain any cascading styles or javascript code.

## Install

Install the package from pypi.org.

```
pip install djangocms-common-catalog
```

Add into `INSTALLED_APPS` in your site `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'common_catalog',
]
```

### Extra settings

 - ``COMMON_CATALOG_TEMPLATE_LIST`` - custom template for the list of items.
 - ``COMMON_CATALOG_TEMPLATE_DETAIL`` - custom template the Item detail.
 - ``COMMON_CATALOG_LOCATIONS`` - Custom filter location names.
 - ``COMMON_CATALOG_FILTER_QUERY_NAME`` - URL query name. Default is `cocaf`.
 - ``COMMON_CATALOG_DETAIL_PARENT_TEMPLATE`` - Name of parent template on Item detail page.


## License

GPLv3+

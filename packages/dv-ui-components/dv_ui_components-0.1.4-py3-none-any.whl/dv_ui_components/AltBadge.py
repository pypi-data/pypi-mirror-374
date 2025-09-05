# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class AltBadge(Component):
    """An AltBadge component.
An altmetrics badge

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- doi (string; optional):
    doi.

- id_type (a value equal to: 'doi', 'pmid'; optional):
    ID stype.

- loadScript (list; default ['https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js']):
    loadScript.

- pmid (string; optional):
    Pubmed ID.

- style (dict; optional):
    Inline CSS style."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'AltBadge'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, style=Component.UNDEFINED, loadScript=Component.UNDEFINED, doi=Component.UNDEFINED, pmid=Component.UNDEFINED, id_type=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'doi', 'id_type', 'loadScript', 'pmid', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'doi', 'id_type', 'loadScript', 'pmid', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(AltBadge, self).__init__(**args)

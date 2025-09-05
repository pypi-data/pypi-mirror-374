# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpModal(Component):
    """A DvpModal component.
An Ant Design Modal component
See https://ant.design/components/modal

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Child components.

- id (string; optional):
    The ID used to identify this component.

- bodyStyle (dict; optional):
    Body style.

- className (string | dict; optional):
    CSS classes to be added to the component.

- closable (boolean; default True):
    Whether the modal is closable.

- closeIconType (a value equal to: 'default', 'outlined', 'two-tone'; default 'default'):
    Close icon type.

- style (dict; optional):
    Inline CSS style.

- title (a list of or a singular dash component, string or number; optional):
    Title.

- transitionType (a value equal to: 'none', 'fade', 'zoom', 'zoom-big', 'zoom-big-fast', 'slide-up', 'slide-down', 'slide-left', 'slide-right', 'move-up', 'move-down', 'move-left', 'move-right'; default 'fade'):
    Transition animation:
    'fade'、'zoom'、'zoom-big'、'zoom-big-fast'、'zoom-up'、
    'zoom-down'、'zoom-left'、'zoom-right'、'slide-up'、'slide-down'、'slide-left'、
    'slide-right'、'move-up'、'move-down'、'move-left'、'move-right'.

- visible (boolean; default True):
    Whether the component is visible.

- width (number | string; optional):
    Width of the modal.

- zIndex (number; default 1000):
    Z-index."""
    _children_props = ['title']
    _base_nodes = ['title', 'children']
    _namespace = 'dv_ui_components'
    _type = 'DvpModal'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, title=Component.UNDEFINED, visible=Component.UNDEFINED, width=Component.UNDEFINED, transitionType=Component.UNDEFINED, closable=Component.UNDEFINED, closeIconType=Component.UNDEFINED, zIndex=Component.UNDEFINED, bodyStyle=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'bodyStyle', 'className', 'closable', 'closeIconType', 'style', 'title', 'transitionType', 'visible', 'width', 'zIndex']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'bodyStyle', 'className', 'closable', 'closeIconType', 'style', 'title', 'transitionType', 'visible', 'width', 'zIndex']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpModal, self).__init__(children=children, **args)

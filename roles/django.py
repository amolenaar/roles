"""
Support for Django.
"""



try:
    from django.db.models.base import ModelBase
except ImportError as e:
    import logging
    logging.warning('Django could not be imported: %s' % str(e))
else:
    from .role import RoleType, class_fields

    overrides = class_fields(RoleType).intersection(class_fields(ModelBase))
    assert not overrides, \
        'Methods in RoleType should not override methods in ModelBase (%s)' \
            % (overrides,)

    class ModelRoleType(RoleType, ModelBase):
        class Meta:
            proxy = True

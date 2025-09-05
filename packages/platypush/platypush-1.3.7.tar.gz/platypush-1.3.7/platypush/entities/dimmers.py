from sqlalchemy import Column, Integer, ForeignKey, Float, String

from platypush.common.db import is_defined

from .devices import Device


if not is_defined('dimmer'):

    class Dimmer(Device):
        """
        This class models dimmer entities. A dimmer is any actionable entity
        with numeric values and an optional min/max range.
        """

        __tablename__ = 'dimmer'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        min = Column(Float)
        max = Column(Float)
        step = Column(Float, default=1.0)
        value = Column(Float)
        unit = Column(String)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

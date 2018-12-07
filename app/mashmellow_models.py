# from app import mashmellow_models
# for generating Json SChemas

from app import models, ma
import pprint as pp

class MaModel():
	def __init__(self, names):
		for nm in names:
			print(nm)

class MarshmellowModels():
	def __init__(self, names):
		for nm in names:
			setattr(self, nm, \
				type(str(nm)+"Schema", (ma.ModelSchema,), 
				{'Meta': type('Meta', (object,), {'model': getattr(models, nm)})}))
	

class EntrySchema(ma.ModelSchema):
    class Meta:
        model = models.EnterpriseAgreement

entry_schema = EntrySchema()

mode = MarshmellowModels(models.table_classes)

from marshmallow_jsonschema import JSONSchema

json_schema = JSONSchema()
json_schema.dump(models.EnterpriseAgreement()).data
#json_schema.dump(models.EnterpriseAgreement).data

json_schema.dump(EntrySchema).data
#json_schema.dump(AuthorSchema).data
# mashmellow_models.models
# json_schema.dump(mashmellow_models.models.EnterpriseAgreement).data
# json_schema.dump(models.EnterpriseAgreement).data


import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Group(Base):
    """model for test"""
    __tablename__ = "Group"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=False)


class User(Base):
    __tablename__ = "User"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=True)
    group_id = sa.Column(sa.Integer, sa.ForeignKey(Group.pk), nullable=False)
    group = orm.relationship(Group, uselist=False, backref="users")

# https://github.com/podhmo/alchemyjsonschema
import pprint as pp
from alchemyjsonschema import SchemaFactory
from alchemyjsonschema import NoForeignKeyWalker

factory = SchemaFactory(NoForeignKeyWalker, container_factory = dict)
pp.pprint(factory(User))
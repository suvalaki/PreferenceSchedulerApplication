import pprint as pp
from alchemyjsonschema import SchemaFactory
from alchemyjsonschema import NoForeignKeyWalker
from alchemyjsonschema import StructuralWalker

import app.models as models


def json_model(schema):
	factory = SchemaFactory(NoForeignKeyWalker)
	return factory(schema)


schema = dict()
schema_keys = models.table_classes
for cls_name in schema_keys:
	schema[cls_name] = json_model(getattr(models,cls_name))



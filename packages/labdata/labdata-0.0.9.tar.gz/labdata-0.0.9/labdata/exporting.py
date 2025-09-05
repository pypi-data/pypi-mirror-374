# to load export to another table (e.g. for a data release).

def load_new_schema(new_schema_name):
    import sys
    import os 
    os.environ['LABDATA_DATABASE'] = new_schema_name
    for k in [k for k in sys.modules if 'labdata.schema' in k]:
        del sys.modules[k]
    import labdata.schema as newschema
    del os.environ['LABDATA_DATABASE']
    for k in [k for k in sys.modules if 'labdata.schema' in k]:
        del sys.modules[k]
    return newschema
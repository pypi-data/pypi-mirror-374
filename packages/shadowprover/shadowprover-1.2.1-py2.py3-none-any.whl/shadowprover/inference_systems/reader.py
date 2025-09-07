from edn_format import Keyword
from ..syntax.expression import *
from edn_format import Keyword
from ..syntax.reader import read_symbol_or_symbols
from ..syntax.expression import *
from ..fol.fol_prover import *
from ..syntax.reader import *
from ..unifiers.first_order_unify import *
from .unification_schema  import  UnificationSchema
from .unifcation_inference_system import UnificationInferenceSchema

name_keyword = Keyword("name")

inputs_keyword = Keyword("inputs")
output_keyword = Keyword("output")
schema_keyword = Keyword("schema")

def read_schema(schema_spec):
    name = str(schema_spec.get(name_keyword))
    inputs = list(map(read_symbol_or_symbols, (schema_spec.get(inputs_keyword))))
    output = read_symbol_or_symbols(schema_spec.get(output_keyword))
    
    return UnificationSchema(name=name, inputs=inputs, output=output)

def read_inference_system(inference_system_spec):
    name = str(inference_system_spec.get(name_keyword))
    schema_specs = inference_system_spec.get(schema_keyword)

    schema = [ read_schema(schema_spec) for schema_spec in
        schema_specs.values()
    ]
    
    return UnificationInferenceSchema(name, schema=schema)


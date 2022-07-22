CREATE OR REPLACE FUNCTION UDF_COMPUTE_ECI(ICD10_LIST ARRAY)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
HANDLER = 'compute'
IMPORTS = ('@stg_udf/eci_v1/elixhauser_comorbidity_index.zip')
as
$$
from elixhauser_comorbidity_index.eci import ElixhauserEngine

def compute(icd10_list):
    ee = ElixhauserEngine()
    out = ee.get_elixhauser(icd10_list)
    return out
$$
;

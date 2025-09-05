import pytest
from pyspark.sql import SparkSession
from validador_cnpj import padronizar_cnpj

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[2]").appName("validador-cnpj-tests").getOrCreate()

def test_padrao_basico(spark):
    df = spark.createDataFrame([("12.345.678/0001-95",)], ["cnpj_bruto"])
    out = padronizar_cnpj(df, "cnpj_bruto")
    row = out.first()
    assert row["f_tipo"] in ("numerico", "alfanumerico")
    assert isinstance(row["f_eh_valido"], bool)

def test_preenche_dv(spark):
    df = spark.createDataFrame([("123456780001",)], ["cnpj_bruto"])
    out = padronizar_cnpj(df, "cnpj_bruto")
    row = out.first()
    assert row["cnpj14"] is not None
    assert len(row["cnpj14"]) == 14

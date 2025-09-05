# validador-cnpj — núcleo PySpark
# Compatível com Databricks (Spark 3.x+)

from typing import Tuple, Optional, Literal
import re

from pyspark.sql import DataFrame, functions as F, types as T

# ------------------------------------------------------------
# Regras oficiais (RFB/SERPRO):
# - 12 caracteres base (A–Z, 0–9) + 2 DVs numéricos
# - DV via módulo 11, pesos cíclicos 2..9 da direita p/ esquerda
# - Valor de cada char = ord(char) - 48  (0-9 => 0..9; A..Z => 17..42)
# - Se resto em {0,1} => DV = 0; senão DV = 11 - resto
# ------------------------------------------------------------

_RE_ALNUM = re.compile(r"[A-Za-z0-9]")

def _apenas_alnum_maiusculo(s: str) -> str:
    if s is None:
        return ""
    # Mantém somente A-Z, 0-9 (remove máscara, espaços, símbolos); uppercase
    return "".join(_RE_ALNUM.findall(str(s).upper()))

def _separar_base_dv(alnum: str) -> Tuple[str, str]:
    """Separa base (12) e DV (2) quando possível/óbvio; caso contrário retorna ("", "")."""
    if len(alnum) == 14 and alnum[-2:].isdigit():
        return alnum[:12], alnum[12:]
    # Ambíguo; devolve vazio para forçar estratégia de reparo
    return "", ""

def _pesos_primeiros_12() -> list:
    # Para 12 posições: [5,4,3,2,9,8,7,6,5,4,3,2]
    return [5,4,3,2,9,8,7,6,5,4,3,2]

def _pesos_primeiros_13() -> list:
    # Para 13 posições (após adicionar o 1º DV): [6,5,4,3,2,9,8,7,6,5,4,3,2]
    return [6,5,4,3,2,9,8,7,6,5,4,3,2]

def _valor_char(c: str) -> int:
    # Valor para cálculo do DV: ASCII-48
    return ord(c) - 48

def _calcular_dv_duplo(base12: str) -> Optional[str]:
    if len(base12) != 12 or any(ch not in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" for ch in base12):
        return None
    vals = [_valor_char(c) for c in base12]
    w1 = _pesos_primeiros_12()
    s1 = sum(v*w for v,w in zip(vals, w1))
    r1 = s1 % 11
    dv1 = 0 if r1 in (0,1) else 11 - r1

    vals2 = vals + [dv1]
    w2 = _pesos_primeiros_13()
    s2 = sum(v*w for v,w in zip(vals2, w2))
    r2 = s2 % 11
    dv2 = 0 if r2 in (0,1) else 11 - r2

    return f"{dv1}{dv2}"

def _eh_valido_14(alnum14: str) -> bool:
    if len(alnum14) != 14 or not alnum14[-2:].isdigit():
        return False
    base, dv = alnum14[:12], alnum14[12:]
    esperado = _calcular_dv_duplo(base)
    return esperado == dv

def _mascara_cnpj(alnum14: str) -> str:
    # Formata como AA.AAA.AAA/AAAA-DV (máscara oficial)
    b, dv = alnum14[:12], alnum14[12:]
    return f"{b[0:2]}.{b[2:5]}.{b[5:8]}/{b[8:12]}-{dv}"

def _detectar_tipo(base12: str) -> Literal["numerico","alfanumerico","desconhecido"]:
    if len(base12) != 12:
        return "desconhecido"
    return "numerico" if base12.isdigit() else "alfanumerico"

# ------------------------------------------------------------
# Estratégias de reparo
# ------------------------------------------------------------
EstrategiaReparo = Literal["rigorosa","flex_pad_esquerda","corte_direita"]

def _reparar_para_14(alnum: str, estrategia: EstrategiaReparo) -> Optional[str]:
    """
    Normaliza para 14 caracteres (12 base + 2 DVs).
    - 'rigorosa': aceita apenas casos claros (14 válido; ou 12 exatos -> calcula DV).
    - 'flex_pad_esquerda': cobre cenários legados:
        * 12..14: se 14 tenta validar; se 12 calcula DV; se 13 assume base com 11 -> left-pad base até 12 e recalcula DV
        * <12: left-pad base com '0' até 12 e calcula DV
        * >14: usa os 12 últimos antes dos 2 últimos dígitos se estes forem dígitos; senão pega os 12 últimos e recalcula DV
    - 'corte_direita': quando sobram caracteres, prioriza recortar à direita e “encostar” o DV no final.
    Retorna None se não der para reparar com consistência.
    """
    if not alnum:
        return None

    # Caso “perfeito”
    base, dv = _separar_base_dv(alnum)
    if base and _eh_valido_14(base+dv):
        return base+dv

    if estrategia == "rigorosa":
        if len(alnum) == 12:
            dv2 = _calcular_dv_duplo(alnum)
            return (alnum + dv2) if dv2 else None
        return None

    if estrategia == "flex_pad_esquerda":
        cleaned = alnum
        if len(cleaned) >= 14:
            if cleaned[-2:].isdigit() and len(cleaned[:-2]) >= 12:
                base12 = cleaned[-14:-2]
                candidato = base12 + cleaned[-2:]
                if not _eh_valido_14(candidato):
                    dv2 = _calcular_dv_duplo(base12)
                    return (base12 + dv2) if dv2 else None
                return candidato
            else:
                base12 = cleaned[-12:]
                dv2 = _calcular_dv_duplo(base12)
                return (base12 + dv2) if dv2 else None

        if len(cleaned) == 13:
            base_guess = cleaned[:-1]
            base12 = base_guess.rjust(12, "0")[:12]
            dv2 = _calcular_dv_duplo(base12)
            return (base12 + dv2) if dv2 else None

        if len(cleaned) <= 12:
            base12 = cleaned.rjust(12, "0")
            dv2 = _calcular_dv_duplo(base12)
            return (base12 + dv2) if dv2 else None

    if estrategia == "corte_direita":
        if len(alnum) < 12:
            return None
        base12 = alnum[:12]
        if len(alnum) >= 14 and alnum[-2:].isdigit():
            cand = base12 + alnum[-2:]
            if _eh_valido_14(cand):
                return cand
        dv2 = _calcular_dv_duplo(base12)
        return (base12 + dv2) if dv2 else None

    return None

def normalizar_cnpj(
    bruto: Optional[str],
    *,
    estrategia: EstrategiaReparo = "flex_pad_esquerda",
    com_mascara: bool = False
) -> Tuple[Optional[str], bool, str, Optional[str]]:
    """
    Normaliza/valida um CNPJ (numérico ou alfanumérico).
    Retorna:
      (cnpj14, eh_valido, tipo, mascarado)
    - cnpj14: 14 chars (12 base + 2 DV) ou None
    - eh_valido: True/False
    - tipo: 'numerico' | 'alfanumerico' | 'desconhecido'
    - mascarado: versão com máscara oficial (ou None)
    """
    cleaned = _apenas_alnum_maiusculo(bruto)
    reparado = _reparar_para_14(cleaned, estrategia=estrategia)
    if not reparado:
        return None, False, "desconhecido", None
    valido = _eh_valido_14(reparado)
    tipo = _detectar_tipo(reparado[:12])
    mascarado = _mascara_cnpj(reparado) if (com_mascara and valido) else None
    return reparado, valido, tipo, mascarado

# ---------------- UDFs para Spark ----------------

@F.udf(returnType=T.StructType([
    T.StructField("cnpj14", T.StringType(), True),
    T.StructField("eh_valido", T.BooleanType(), False),
    T.StructField("tipo", T.StringType(), False),
    T.StructField("mascarado", T.StringType(), True),
]))
def normalizar_cnpj_udf(bruto: T.StringType) -> tuple:
    return normalizar_cnpj(bruto, estrategia="flex_pad_esquerda", com_mascara=False)

@F.udf(returnType=T.BooleanType())
def cnpj_eh_valido_udf(bruto: T.StringType) -> bool:
    cleaned = _apenas_alnum_maiusculo(bruto)
    reparado = _reparar_para_14(cleaned, estrategia="flex_pad_esquerda")
    return bool(reparado and _eh_valido_14(reparado))

@F.udf(returnType=T.StringType())
def tipo_cnpj_udf(bruto: T.StringType) -> str:
    cleaned = _apenas_alnum_maiusculo(bruto)
    reparado = _reparar_para_14(cleaned, estrategia="flex_pad_esquerda")
    return _detectar_tipo(reparado[:12]) if reparado else "desconhecido"

@F.udf(returnType=T.StringType())
def mascarar_cnpj_udf(bruto: T.StringType) -> Optional[str]:
    cleaned = _apenas_alnum_maiusculo(bruto)
    reparado = _reparar_para_14(cleaned, estrategia="flex_pad_esquerda")
    if reparado and _eh_valido_14(reparado):
        return _mascara_cnpj(reparado)
    return None

def padronizar_cnpj(
    df: DataFrame,
    coluna: str,
    *,
    coluna_saida: str = "cnpj14",
    com_mascara: bool = True,
    estrategia: EstrategiaReparo = "flex_pad_esquerda"
) -> DataFrame:
    """
    Produz colunas padronizadas e flags úteis:
      - coluna_saida: 14 chars (12 base + 2 DV)
      - f_eh_valido: boolean
      - f_tipo: 'numerico' | 'alfanumerico' | 'desconhecido'
      - cnpj_mascara: máscara oficial (opcional)
      - bruto_limpo: apenas A-Z/0-9 maiúsculo
    """
    _norm = F.udf(
        lambda s: normalizar_cnpj(s, estrategia=estrategia, com_mascara=com_mascara),
        T.StructType([
            T.StructField("cnpj14", T.StringType(), True),
            T.StructField("eh_valido", T.BooleanType(), False),
            T.StructField("tipo", T.StringType(), False),
            T.StructField("mascarado", T.StringType(), True),
        ])
    )
    res = (
        df
        .withColumn("bruto_limpo", F.regexp_replace(F.upper(F.col(coluna)), r"[^A-Z0-9]", ""))
        .withColumn("_norm", _norm(F.col(coluna)))
        .withColumn(coluna_saida, F.col("_norm.cnpj14"))
        .withColumn("f_eh_valido", F.col("_norm.eh_valido"))
        .withColumn("f_tipo", F.col("_norm.tipo"))
    )
    if com_mascara:
        res = res.withColumn("cnpj_mascara", F.col("_norm.mascarado"))
    return res.drop("_norm")

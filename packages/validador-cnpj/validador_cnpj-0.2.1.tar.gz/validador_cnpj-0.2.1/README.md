````markdown
# validador-cnpj

[![PyPI version](https://img.shields.io/pypi/v/validador-cnpj.svg)](https://pypi.org/project/validador-cnpj/)
[![Python](https://img.shields.io/pypi/pyversions/validador-cnpj.svg)](https://pypi.org/project/validador-cnpj/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

UDFs **PySpark** para **limpeza, reparo, normalização e validação** de CNPJ (numérico e alfanumérico).  
**Distribuição (PyPI):** `validador-cnpj` • **Import (Python):** `validador_cnpj`

---

## Instalação

```bash
pip install validador-cnpj
````

---

## Uso rápido (Spark)

```python
from validador_cnpj import padronizar_cnpj

df = spark.createDataFrame(
    [("12.345.678/0001-95",), ("12.ABC.345/01DE-35",), ("123456780001",)],
    ["cnpj_bruto"]
)

out = padronizar_cnpj(df, "cnpj_bruto", com_mascara=True)
display(out)
```

**Colunas geradas**:

* `cnpj14` — 14 chars (12 base + 2 DV)
* `f_eh_valido` — boolean
* `f_tipo` — `"numerico"` | `"alfanumerico"` | `"desconhecido"`
* `cnpj_mascara` — `AA.AAA.AAA/AAAA-DV` (quando válido e `com_mascara=True`)
* `bruto_limpo` — entrada higienizada (apenas A–Z/0–9, maiúsculo)

---

## Principais recursos

* Aceita entradas **sujas** (máscaras, espaços, símbolos, caixa mista).
* **Repara** casos com **falta**/**excesso** de caracteres (configurável por estratégia).
* **Valida DV** (módulo 11) para CNPJ **numérico e alfanumérico**.
* UDFs prontas para **PySpark** e função pura para uso em Python/driver.

---

## API (Python)

```python
from validador_cnpj import (
    padronizar_cnpj,
    normalizar_cnpj_udf,
    cnpj_eh_valido_udf,
    tipo_cnpj_udf,
    mascarar_cnpj_udf,
)
```

### `padronizar_cnpj(df, coluna, *, coluna_saida="cnpj14", com_mascara=True, estrategia="flex_pad_esquerda") -> DataFrame`

Aplica limpeza/reparo/validação em lote e devolve colunas utilitárias.

Parâmetros:

* `coluna` — nome da coluna de entrada.
* `coluna_saida` — nome da coluna com o CNPJ normalizado (14 chars).
* `com_mascara` — adiciona `cnpj_mascara` quando válido.
* `estrategia` — `"rigorosa" | "flex_pad_esquerda" | "corte_direita"`.

### UDFs

* `normalizar_cnpj_udf(string) -> struct(cnpj14, eh_valido, tipo, mascarado)`
* `cnpj_eh_valido_udf(string) -> boolean`
* `tipo_cnpj_udf(string) -> string`
* `mascarar_cnpj_udf(string) -> string | null`

> Dica: use as UDFs quando quiser compor sua própria transformação; use `padronizar_cnpj` para o caminho mais simples.

---

## Estratégias de reparo

* **`rigorosa`** — aceita apenas 12 ou 14 caracteres válidos, senão retorna `None`.
* **`flex_pad_esquerda`** *(padrão)* — cobre truncamentos/legados comuns (completa à esquerda, recalcula DV quando necessário).
* **`corte_direita`** — prioriza cortar à direita (12 primeiros como base, tenta usar os 2 últimos como DV).

---

## Casos de uso práticos

1. Limpeza e validação em lote
2. Apenas checar se é válido
3. Identificar tipo (numérico x alfanumérico)
4. Aplicar máscara oficial somente se válido
5. Usar estratégia **rigorosa**
6. Preferir cortes à direita
7. Compor manualmente com `normalizar_cnpj_udf`
8. **Exemplo em SQL (Databricks)**

```sql
-- Exemplo SQL
SELECT
  normalizar_cnpj(cnpj_bruto).cnpj14       AS cnpj14,
  normalizar_cnpj(cnpj_bruto).eh_valido    AS f_eh_valido,
  normalizar_cnpj(cnpj_bruto).tipo         AS f_tipo,
  normalizar_cnpj(cnpj_bruto).mascarado    AS cnpj_mascara
FROM tabela;
```

---

## Exemplos detalhados de entradas → saídas

| Entrada (`cnpj_bruto`)       | Estratégia          | `cnpj14` (normalizado) |        `f_eh_valido`       | `f_tipo`       | Observação                                   |
| ---------------------------- | ------------------- | ---------------------: | :------------------------: | :------------- | -------------------------------------------- |
| `12.345.678/0001-95`         | qualquer            |       `12345678000195` |    :white\_check\_mark:    | `numerico`     | Formato clássico com máscara                 |
| `12.ABC.345/01DE-35`         | qualquer            |       `12ABC34501DE35` |    :white\_check\_mark:    | `alfanumerico` | Alfanumérico com máscara mista               |
| `123456780001`               | flex\_pad\_esquerda |       `123456780001??` | :white\_check\_mark:/ \:x: | `numerico`     | Faltam DVs → calculados                      |
| `123`                        | flex\_pad\_esquerda |       `000000000123??` | :white\_check\_mark:/ \:x: | `numerico`     | Completa à esquerda até 12 e calcula DV      |
| `00012345678000195`          | flex\_pad\_esquerda |       `12345678000195` |    :white\_check\_mark:    | `numerico`     | Excesso à esquerda → usa 12 anteriores ao DV |
| `12ABC34501DEXX`             | flex\_pad\_esquerda |       `12ABC34501DE??` | :white\_check\_mark:/ \:x: | `alfanumerico` | Lixo no fim, sem DV confiável → recalcula    |
| `12abc345/01de-35`           | qualquer            |       `12ABC34501DE35` |    :white\_check\_mark:    | `alfanumerico` | Caixa/símbolos higienizados                  |
| `foo 12.ABC.345/01DE-35 bar` | flex\_pad\_esquerda |       `12ABC34501DE35` |    :white\_check\_mark:    | `alfanumerico` | Texto ao redor ignorado                      |
| `A2345678000195`             | rigorosa            |                 `None` |             :x:            | `desconhecido` | 14 chars mas DV não numérico → rejeita       |
| `None` / vazio               | qualquer            |                 `None` |             :x:            | `desconhecido` | Valor nulo                                   |

---

## Boas práticas de performance

* Prefira `padronizar_cnpj` (uma passada) e **reutilize** as colunas derivadas.
* Filtre válidos após normalizar.
* Ajuste `estrategia` conforme a qualidade do dado.

---

## Tratamento de erros & decisões de negócio

A biblioteca **não** toma decisões de negócio (ex.: descartar registros inválidos).
Ela fornece sinais (`f_eh_valido`, `f_tipo`, `cnpj14`, `bruto_limpo`) para que **você** defina as regras.

---

## Compatibilidade

* **Python**: 3.8+
* **PySpark**: 3.3 – 3.x
* **Databricks**: testado em clusters 10.x/11.x/12.x (Spark 3.x)

---

## Alterações recentes

Veja o [CHANGELOG.md](CHANGELOG.md).

---

## Licença

MIT

---

## Detalhes técnicos

* Cálculo de DV (módulo 11) aplicável a CNPJ **numérico** e **alfanumérico**.
* Máscara padrão: `AA.AAA.AAA/AAAA-DV`.

```
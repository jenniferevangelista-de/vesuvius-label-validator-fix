# Vesuvius: correção candidata para validação de máscaras binárias

**Candidato experimental, com testes locais. Não submetido ao prêmio nem aceito upstream.**

## Resultado

O validador oficial permite apenas valores `0`, `1` e `255` nas máscaras TIFF.
Porém, converte os valores para inteiro antes de checá-los, aceitando erroneamente
`0.5`, `1.5`, `255.5` e `-0.5`. O patch remove essa conversão e preserva os valores
originais no diagnóstico. Valores binários válidos continuam passando; valores
fracionários e não finitos são sinalizados.

Foram executados **29 casos de teste**, incluindo quatro chamadas completas da CLI
com arquivos TIFF/Zarr sintéticos. Antes: **19 falhas e 10 sucessos**. Depois:
**29 sucessos**. São casos de teste para **um defeito**, não 19 bugs diferentes.
O número inclui verificações do texto do diagnóstico e do tratamento de NaN/Inf.
Uma revisão independente adicional executou **17 casos em três métodos de teste**,
todos aprovados. Essa contagem é separada dos 29 casos da suíte principal e cobre
parte dos mesmos comportamentos; não representa 17 novas correções nem validação
humana. Arquivo: `test_independent.py`; resumo estruturado em `evidence.json`.
O validador interno original lança exceção para NaN/Inf; a CLI já captura essa
exceção. Não se afirma que a CLI inteira travava.

## Limite importante

Os casos de regressão são sintéticos: não demonstram corrupção em uma máscara pública
nem ganho científico no processamento dos papiros. A revisão humana permanece pendente.
Não foram executados treino, inferência, suíte completa do repositório ou teste em
macOS. Não há medição de desempenho ou acurácia.

O [CONTRIBUTING.md oficial](https://github.com/ScrollPrize/villa/blob/d57c28ebee8776b618f9851c2289cc407ea99dd4/CONTRIBUTING.md)
exige uso humano real dos dados dos papiros, demonstração antes/depois em dados reais,
capturas de tela e justificativa escrita pelo humano. Exemplos sintéticos não são
aceitos como essa evidência. **Este pacote ainda não atende aos requisitos para PR.**
Não deve ser submetido como se comprovasse esses requisitos.

## Teste adicional com dados reais

Foi lida integralmente, sem conversão ou alteração, a máscara pública original
`ink/0500p2/-1/-1_inklabels.tif` (2.364.343 bytes, uint8, 24659 × 13696, LZW).
Os 5.238 segmentos TIFF foram decodificados; os valores únicos são `0` e `255`.
**Original e corrigido passaram sem apontar problemas.** Isso demonstra
compatibilidade com essa máscara válida, **não ocorrência do defeito em dados reais**.
Foi executado o validador por arquivo, não a CLI completa sobre o dataset real.

SHA256 antes/depois: `9dc65d6a83ac3e932e0579f0d577e56f17972b9d57910ee8df0fc993d92e2c8b`.
[Arquivo público original](https://huggingface.co/buckets/scrollprize/datasets/tree/ink/0500p2/-1/-1_inklabels.tif).
A licença indicada pelo dataset restringe redistribuição; o TIFF e seus pixels
**não estão incluídos**. `real_data_result.json` contém somente metadados/resultados.
A segunda máscara original, `-1_supervision_mask.tif`, também passou nas duas
versões, com os mesmos shape/dtype/valores e 5.238 segmentos decodificados.
Ela tem 2.358.265 bytes; SHA256 antes/depois:
`7920e1eb28f5972209eff9f12afadde0f43385272080210e0395c60615fef770`.
[Segunda máscara original](https://huggingface.co/buckets/scrollprize/datasets/tree/ink/0500p2/-1/-1_supervision_mask.tif).
Resultado em `real_supervision_result.json`. Nenhum TIFF é redistribuído.

**Feito:** patch local, regressões sintéticas e compatibilidade por arquivo em duas
máscaras públicas originais, com hashes preservados.

**Pendente:** demonstração de um problema real afetando o trabalho com os papiros,
revisão humana e evidências necessárias para propor contribuição upstream.

**Cobertura não executada:** CLI completa sobre o segmento real. A validação dos dados reais foi feita por arquivo. Não há evidência de um caso humano real afetado pelo defeito.

## Reproduzir

Testado em Linux, Python 3.12.14. Dependências não estão incluídas neste pacote.
Os comandos abaixo são instruções para execução voluntária em um ambiente isolado:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. VALIDATOR_MODULE=upstream_validate_segments python -m pytest -q test_label_values.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. python -m pytest -q test_label_values.py
PYTHONPATH=. python -m unittest -v test_independent.py
```

A primeira execução deve falhar nos casos de regressão; a segunda deve passar.
Os testes criam arquivos temporários próprios, sem editar dados existentes.
O patch aplica-se ao caminho oficial; o harness local seleciona módulo original
ou corrigido por variável de ambiente. Uma futura integração substituiria essa
seleção pelo import normal do pacote Vesuvius.

## Arquivos e proveniência

- `fix_binary_float_labels.patch`: mudança mínima no código oficial.
- `upstream_validate_segments.py`: original byte a byte, git blob
  `0e2069fd4f619da80cdc0a3da45fb8ceccf539a2`.
- `patched_validate_segments.py`: versão corrigida.
- `vesuvius/utils/cli.py`: dependência CLI do mesmo commit upstream.
- `test_label_values.py`: regressões e testes CLI com dados sintéticos.
- `evidence.json`: resumo dos resultados, versões e hashes.
- `real_data_result.json`, `real_supervision_result.json`: metadados e resultados de compatibilidade, sem pixels.
- `LICENSE`: licença MIT e atribuição upstream.

Commit: `d57c28ebee8776b618f9851c2289cc407ea99dd4`.
[Código original](https://github.com/ScrollPrize/villa/blob/d57c28ebee8776b618f9851c2289cc407ea99dd4/vesuvius/src/vesuvius/ink_detection/preprocessing/validate_segments.py).
[Documentação da CLI ativa](https://github.com/ScrollPrize/villa/blob/d57c28ebee8776b618f9851c2289cc407ea99dd4/vesuvius/src/vesuvius/ink_detection/README.md).

Buscas focadas por PRs não identificaram correção equivalente; isso não garante
originalidade exaustiva. Investigação, implementação e testes tiveram auxílio de IA.

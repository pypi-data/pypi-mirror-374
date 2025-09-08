```python
from anpseisearch import SeiRegisterSearcher

searcher = SeiRegisterSearcher()

filters = {
    "txtDataInicio": "05/09/2025",
    "txtDataFim": "06/09/2025",
}
searcher.set_filters(filters=filters)

registers = searcher.execute_search()

for reg in registers:
    print(reg)
```

### Campos do Form Data

|Name|Value|
|--|--|
|txtProtocoloPesquisa||
|q||
|chkSinProcessos|P|
|txtParticipante||
|hdnIdParticipante||
|txtUnidade||
|hdnIdUnidade||
|selTipoProcedimentoPesquisa||
|selSeriePesquisa||
|txtDataInicio|06/09/2025|
|txtDataFim||
|txtInfraCaptcha|2MI42G|
|hdnInfraCaptcha|1|
|txtNumeroDocumentoPesquisa||
|txtAssinante||
|hdnIdAssinante||
|txtDescricaoPesquisa||
|txtAssunto||
|hdnIdAssunto||
|txtSiglaUsuario1||
|txtSiglaUsuario2||
|txtSiglaUsuario3||
|txtSiglaUsuario4||
|hdnSiglasUsuarios||
|hdnSiglasUsuarios||
|hdnCId|PESQUISA_PUBLICA1757167558039|
|partialfields|sta_prot:P AND (dta_ger:[2025-09-06T00:00:00Z TO 2025-09-06T00:00:00Z] OR dta_inc:[2025-09-06T00:00:00Z TO 2025-09-06T00:00:00Z])|
|requiredfields||
|as_q||
|hdnFlagPesquisa|1|

### Informações Retornadas
![alt text](image.png)

|Nome|Descrição|
|--|--|
|Título|Fiscalização: Instalações de Abastecimento, de Produção de Combustíveis e de Biocombustíveis nº48610.203905/2024-63 (Despacho de Instrução)|
|Tipo do Documento|Despacho de Instrução|
|Número Documento|5288361|
|Link do Documento|https://sei.anp.gov.br/sei/modulos/pesquisa/md_pesq_documento_consulta_externa.php?bQdXWIUhq46-kuNuYYlAsyjFfu3aG4dBu2PjbFgpOb_9MvqFNtXlXEMWSYTBr1f7z0g5p97pRY7Jz5GItK4e8RvlI7fF4M_3rhU7FzzGv2MjCGt9GpNNDDzSF7oe5eU-
|Resumo Documento|DESPACHO DE INSTRUÇÃO Processo nº 48610.203905/2024-63 In...|
|Número do Processo|48610.203905/2024-63|
|Link Processo|https://sei.anp.gov.br/sei/modulos/pesquisa/md_pesq_processo_exibir.php?iI3OtHvPArITY997V09rhsSkbDKbaYSycOHqqF2xsM0IaDkkEyJpus7kCPb435VNEAb16AAxmJKUdrsNWVIqQ-yulaTaM4mmRLEnUJpUaCRKqJL8jA88N5XXeNCDl9-A|
|Unidade|SFI-CNPS-CJP DF|
|Data|06/09/2025|


anpseisearch/
├── __pycache__/
├── anpseisearch/         
│   ├── __init__.py       
│   └── searcher.py       
├── tests/                
│   ├── __init__.py
│   ├── test_miner.py
│   └── test_utils.py
├── venv/
├── image.png
├── LICENSE               
├── pyproject.toml        
├── README.md             
├── requirements.txt
├── setup.cfg             
└── .gitignore

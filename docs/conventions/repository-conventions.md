# Convenções do repositório

**Status:** Approved v1.0

- Código e identificadores técnicos em inglês.
- Documentação principal em português.
- Código/configuração/documentação no Git; dados grandes fora.
- Runtime local em volumes ou `.runtime/`, nunca versionado.
- DAGs coordenam; lógica pesada fica em módulos.
- Notebooks são exploratórios, nunca fonte obrigatória de produção.
- Prompts estruturais do Agent são versionados.
- Outputs reproduzíveis ficam fora do Git salvo justificativa.
- Configuração por código/import/script tem prioridade sobre estado manual em UI.
- UTF-8, LF e newline no fim de arquivo.
- YAML: 2 espaços. Python: 4 espaços.

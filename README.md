# uefi-uefimcp-pedagogia

Servidor MCP de **Licenciatura em Pedagogia**, UFABC. Nível: **curso** (segundo ciclo, acessado a partir da LEILA).

## Origem

Derivado de [`uefi-uefimcp`](https://github.com/uefiabece/uefi-uefimcp) por `git clone`
(commit de origem registrado em `config/subject.json`), sem importar materiais acadêmicos.
As ferramentas curriculares são de curso único (padrão `uefi-uefimcp-comp`/`uefi-uefimcp-dados`).
A camada compartilhada (PDF, SDK MCP v1, `scripts/check_mcp.py`) vem de `uefi-uefimcp-bct` e `uefi-uefimcp-neuro`.

```text
uefi-uefimcp
  └── uefi-uefimcp-leila   (1º ciclo)
      └── uefi-uefimcp-pedagogia
          └── (disciplinas de Pedagogia)
```

## Executar

Requer Python 3.11 ou superior. No diretório deste repositório:

```sh
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[pdf,math]"
.venv/Scripts/python run.py
```

O processo usa transporte **stdio**: deve ser iniciado por um cliente MCP.
Em Linux/macOS, use `.venv/bin/python`.

## Conectar

```sh
claude mcp add --scope user uefi-uefimcp-pedagogia -- "CAMINHO_ABSOLUTO/uefi-uefimcp-pedagogia/.venv/Scripts/python.exe" "CAMINHO_ABSOLUTO/uefi-uefimcp-pedagogia/run.py"
```

Outros clientes: veja `config/mcp.example.json`.

## Ferramentas

17 ferramentas:

- **Conteúdo / ensino / exercícios (template):** `get_syllabus`, `get_bibliography`, `get_past_exams`, `search_content`, `get_notes`, `explain_concept`, `get_topic_outline`, `generate_study_plan`, `get_exercises`, `solve_exercise`, `generate_exercise`, `generate_flashcards`
- **Navegação curricular:** `get_curriculum_structure`, `list_subjects_by_area`, `get_disciplinas_limitadas`, `get_progression_requirements`, `plan_academic_journey`

Prompts: `teach` e `solve`.

## Conteúdo

As pastas de `content/` estão vazias. Sugestões: PPC de Pedagogia em `content/bibliography/` e uma síntese em `content/syllabus/curriculo.md`. Ao adicionar o PPC, preencha `course_code` e os metadados em `config/subject.json`.
Sem materiais, as consultas retornam a ausência de conteúdo.

## Verificar

```sh
.venv/Scripts/python scripts/check_mcp.py
```

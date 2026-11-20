"""
Ferramentas de navegação curricular — específicas para o Bacharelado em
Pedagogia da UFABC.

Estas ferramentas complementam as ferramentas genéricas do template com
funcionalidades voltadas para a navegação do currículo de um curso inteiro,
não apenas de uma disciplina individual. Pedagogia é um curso de segundo ciclo:
o estudante ingressa nele a partir da LEILA.
"""

from __future__ import annotations

from mcp import types

from ..resources.loader import ContentLoader


def register_curriculum_tools(
    tools: list[types.Tool],
    handlers: dict,
    loader: ContentLoader,
    config: dict,
) -> None:
    if not config.get("features", {}).get("curriculum_navigation"):
        return

    course_name = config.get("course_name", "Licenciatura em Pedagogia")
    metadata = config.get("metadata", {})
    ppc_version = metadata.get("ppc_version") or "vigente"
    ppc_versions = metadata.get("ppc_versions_available") or []

    ppc_schema: dict = {
        "type": "string",
        "description": f"Versão do PPC a consultar. Padrão: {ppc_version}.",
    }
    if ppc_versions:
        ppc_schema["enum"] = ppc_versions

    # --- get_curriculum_structure ---
    tools.append(
        types.Tool(
            name="get_curriculum_structure",
            description=(
                f"Retorna a estrutura curricular completa do {course_name}: "
                "disciplinas obrigatórias, de opção limitada, livres, extensão e TCC. "
                "Baseado nos arquivos carregados em content/syllabus/."
            ),
            inputSchema={
                "type": "object",
                "properties": {"ppc": ppc_schema},
                "required": [],
            },
        )
    )

    async def handle_get_curriculum_structure(args: dict) -> str:
        ppc = args.get("ppc", ppc_version)

        # Try to find PPC-specific syllabus files first
        all_syllabus = loader.get_section("syllabus")
        ppc_items = [i for i in all_syllabus if ppc in i["name"]]
        items = ppc_items if ppc_items else all_syllabus

        if not items:
            # Fall back to searching bibliography for PPC documents
            bib_results = loader.search(f"ppc_{ppc}", section="bibliography")
            bib_results += loader.search("obrigatória", section="bibliography")
            if bib_results:
                snippets = "\n\n".join(r["snippet"] for r in bib_results[:5])
                return (
                    f"## Estrutura Curricular — {course_name} (PPC {ppc})\n\n"
                    f"[Extraído da bibliografia]\n\n{snippets}\n\n"
                    f"[O assistente deve apresentar a estrutura curricular completa "
                    f"com base nos trechos acima e no seu conhecimento do {course_name}.]"
                )
            return (
                "Nenhum arquivo de ementa carregado ainda. "
                "Adicione arquivos em content/syllabus/ ou verifique se os PDFs do PPC "
                "estão em content/bibliography/ e se o suporte a PDF está instalado "
                "(`pip install -e \".[pdf]\"`). "
            )

        combined = "\n\n---\n\n".join(f"# {i['name']}\n\n{i['text']}" for i in items)
        return (
            f"## Estrutura Curricular — {course_name} (PPC {ppc})\n\n"
            f"{combined}"
        )

    handlers["get_curriculum_structure"] = handle_get_curriculum_structure

    # --- list_subjects_by_area ---
    tools.append(
        types.Tool(
            name="list_subjects_by_area",
            description=(
                "Lista as disciplinas de Pedagogia agrupadas por área "
                "(ex: Fundamentos da Educação, Didática e Currículo, Alfabetização e Letramento, Educação Infantil, Gestão Escolar, Educação Inclusiva). "
                "Útil para explorar opções limitadas e livres."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": (
                            "Área a filtrar (ex: 'fundamentos', 'didática', 'currículo', 'alfabetização', 'educação infantil', 'gestão escolar', 'inclusão'). Omita para listar todas."
                        ),
                    }
                },
                "required": [],
            },
        )
    )

    async def handle_list_subjects_by_area(args: dict) -> str:
        area = args.get("area", "").strip().lower()

        query = area if area else "disciplina"
        results = loader.search(query, section="syllabus")
        if not results:
            results = loader.search(query, section="bibliography")

        context_block = ""
        if results:
            snippets = "\n\n".join(r["snippet"] for r in results[:6])
            context_block = f"\n\n## Trechos relevantes dos materiais\n\n{snippets}"

        area_label = f" — Área: {area.title()}" if area else ""
        return (
            f"## Disciplinas do {course_name}{area_label}\n"
            f"{context_block}\n\n"
            f"[O assistente deve listar as disciplinas de Pedagogia"
            f"{' na área de ' + area if area else ''}, "
            f"organizadas por categoria (obrigatória / opção limitada / livre), "
            f"indicando quais já são cursadas na LEILA, "
            f"baseando-se nos materiais acima e no conhecimento do currículo de Pedagogia da UFABC.]"
        )

    handlers["list_subjects_by_area"] = handle_list_subjects_by_area

    # --- get_disciplinas_limitadas ---
    tools.append(
        types.Tool(
            name="get_disciplinas_limitadas",
            description=(
                "Retorna as disciplinas de opção limitada de Pedagogia e as disciplinas com "
                "oferta restrita, a partir do PPC ou do planejamento de oferta carregado. "
                "Útil para planejar a matrícula com antecedência."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Filtrar por área ou nome de disciplina (opcional).",
                    }
                },
                "required": [],
            },
        )
    )

    async def handle_get_disciplinas_limitadas(args: dict) -> str:
        area = args.get("area", "").strip()

        results = loader.search("limitad", section="syllabus")
        results += loader.search("limitad", section="bibliography")
        if area:
            results = [r for r in results if area.lower() in r["snippet"].lower()] or results

        if not results:
            return (
                "Nenhum material sobre disciplinas de opção limitada encontrado. "
                "Adicione o PPC de Pedagogia ou a lista de oferta em content/bibliography/ "
                "e verifique se o suporte a PDF está instalado "
                "(`pip install -e \".[pdf]\"`). "
            )

        snippets = "\n\n".join(r["snippet"] for r in results[:8])
        filter_note = f" (filtrado por: '{area}')" if area else ""
        return (
            f"## Disciplinas de Opção Limitada{filter_note}\n\n"
            f"{snippets}\n\n"
            f"[O assistente deve apresentar as disciplinas de opção limitada "
            f"listadas nos trechos acima de forma organizada, indicando nomes e códigos.]"
        )

    handlers["get_disciplinas_limitadas"] = handle_get_disciplinas_limitadas

    # --- get_progression_requirements ---
    tools.append(
        types.Tool(
            name="get_progression_requirements",
            description=(
                "Retorna os requisitos de ingresso, progressão e formatura de Pedagogia: "
                "ingresso a partir da LEILA, créditos mínimos por categoria, TCC, estágio supervisionado em docência, "
                "extensão, coeficientes (CR, CA, CP) e regras de jubilamento."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": (
                            "Aspecto específico a consultar, ex: 'ingresso', 'TCC', "
                            "'estágio', 'extensão', 'opção limitada', 'coeficiente de rendimento'."
                        ),
                    }
                },
                "required": [],
            },
        )
    )

    async def handle_get_progression_requirements(args: dict) -> str:
        topic = args.get("topic", "").strip()

        query = topic if topic else "créditos"
        results = loader.search(query, section="syllabus")
        if not results:
            results = loader.search(query, section="bibliography")

        context_block = ""
        if results:
            snippets = "\n\n".join(r["snippet"] for r in results[:5])
            context_block = f"\n\n## Trechos relevantes dos materiais\n\n{snippets}"

        topic_note = f" — {topic.title()}" if topic else ""
        return (
            f"## Requisitos de Progressão e Formatura — {course_name}{topic_note}\n"
            f"{context_block}\n\n"
            f"[O assistente deve descrever os requisitos{' relacionados a ' + topic if topic else ''} "
            f"para ingresso, progressão e formatura em Pedagogia na UFABC (PPC {ppc_version}), "
            f"baseando-se nos materiais acima e no conhecimento do PPC. "
            f"Se não houver material carregado, avise que a resposta não está fundamentada "
            f"nos documentos oficiais.]"
        )

    handlers["get_progression_requirements"] = handle_get_progression_requirements

    # --- plan_academic_journey ---
    tools.append(
        types.Tool(
            name="plan_academic_journey",
            description=(
                "Gera um planejamento acadêmico sugerido rumo a Pedagogia, "
                "considerando o quadrimestre atual, disciplinas já cursadas (da LEILA e de Pedagogia) "
                "e a área de interesse dentro de Pedagogia. "
                "Sugere disciplinas para os próximos quadrimestres."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "current_quarter": {
                        "type": "integer",
                        "description": "Quadrimestre atual na UFABC (contando desde o ingresso na LEILA).",
                    },
                    "completed_subjects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista de disciplinas já concluídas (nomes ou códigos).",
                    },
                    "focus_area": {
                        "type": "string",
                        "description": (
                            "Área de interesse para orientar as opções limitadas e livres, ex: "
                            "'Educação Infantil', 'Alfabetização', 'Educação Inclusiva', 'Gestão Escolar', 'Educação de Jovens e Adultos'."
                        ),
                    },
                },
                "required": ["current_quarter"],
            },
        )
    )

    async def handle_plan_academic_journey(args: dict) -> str:
        quarter = args.get("current_quarter", 1)
        completed = args.get("completed_subjects", [])
        focus = args.get("focus_area", "")

        # Pull curriculum context
        syllabus_items = loader.get_section("syllabus")
        syllabus_text = (
            "\n\n".join(i["text"] for i in syllabus_items)
            if syllabus_items
            else "Nenhuma ementa carregada."
        )

        completed_note = (
            f"\nDisciplinas concluídas: {', '.join(completed)}" if completed else ""
        )
        focus_note = f"\nÁrea de interesse: {focus}" if focus else ""

        return (
            f"## Planejamento Acadêmico — {course_name}\n"
            f"**Quadrimestre atual:** {quarter}"
            f"{completed_note}"
            f"{focus_note}\n\n"
            f"## Referência curricular\n\n{syllabus_text}\n\n"
            f"[O assistente deve sugerir um planejamento quadrimestral a partir do "
            f"quadrimestre {quarter}, separando o que ainda falta da LEILA (pré-requisito "
            f"para o diploma de Pedagogia) e as obrigatórias do curso, respeitando a cadeia de "
            f"pré-requisitos recomendados"
            f"{' e priorizando opções limitadas ligadas a ' + focus if focus else ''}. "
            f"Apresente o plano em tabela ou lista por quadrimestre.]"
        )

    handlers["plan_academic_journey"] = handle_plan_academic_journey

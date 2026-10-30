import asyncio
import datetime
from pathlib import Path

from app.agent import (
    FerramentasDeArquivo,
    PLANOS_DIR,
    SKILL_DIR,
    app,
    obter_instrucao,
    root_agent,
)


def test_agent_basics() -> None:
    assert root_agent.name == "agente_estudos"
    assert app.name == "app"
    assert SKILL_DIR.exists()
    assert (SKILL_DIR / "SKILL.md").exists()
    assert PLANOS_DIR.exists()


def test_instruction_provider_contains_date() -> None:
    instrucao = obter_instrucao()
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    assert hoje in instrucao
    assert "plano-de-estudos" in instrucao
    assert "gating" in instrucao


def test_ferramentas_de_arquivo_filtering() -> None:
    from google.adk.environment import LocalEnvironment

    env = LocalEnvironment(working_dir=PLANOS_DIR)
    ferramentas = FerramentasDeArquivo(environment=env)
    tools = asyncio.run(ferramentas.get_tools())
    tool_names = [t.name for t in tools]

    assert "ReadFile" in tool_names
    assert "WriteFile" in tool_names
    assert "Execute" not in tool_names
    assert "EditFile" not in tool_names

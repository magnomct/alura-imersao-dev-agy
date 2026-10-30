import datetime
import os
from pathlib import Path

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.environment import LocalEnvironment
from google.adk.models import Gemini
from google.adk.skills import load_skill_from_dir
from google.adk.tools.environment import EnvironmentToolset
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types

# Caminhos base calculados a partir deste arquivo
APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent
SKILL_DIR = APP_DIR / "skills" / "plano-de-estudos"
PLANOS_DIR = BASE_DIR / "planos"
PLANOS_DIR.mkdir(parents=True, exist_ok=True)

# Modelo configurável via variável de ambiente MODEL (padrão: gemini-3.8-flash)
MODEL = os.getenv("MODEL", "gemini-3.8-flash")


class FerramentasDeArquivo(EnvironmentToolset):
    """Toolset de ambiente restrito que expõe apenas ReadFile e WriteFile."""

    async def get_tools(self, readonly_context=None):
        tools = await super().get_tools(readonly_context)
        return [t for t in tools if t.name in ("ReadFile", "WriteFile")]


def obter_instrucao(readonly_context=None) -> str:
    """Instruction provider que injeta a data de hoje para interpretação de termos relativos."""
    hoje = datetime.date.today()
    dias_semana = {
        0: "segunda-feira",
        1: "terça-feira",
        2: "quarta-feira",
        3: "quinta-feira",
        4: "sexta-feira",
        5: "sábado",
        6: "domingo",
    }
    dia_nome = dias_semana[hoje.weekday()]
    hoje_fmt = hoje.strftime("%d/%m/%Y")

    return (
        f"Hoje é {dia_nome}, {hoje_fmt} ({hoje.isoformat()}). "
        "Você é um mentor especialista em estudos. "
        "Seu papel é orientar o estudante e montar planos de estudo personalizados, com revisão espaçada, "
        "checkpoints de autoavaliação e agenda exportável para o Google Agenda (CSV), usando a skill `plano-de-estudos`. "
        "Siga rigorosamente as regras da skill `plano-de-estudos`, incluindo a regra de gating: "
        "não inicie o planejamento nem carregue recursos da skill antes de ter todas as 4 informações obrigatórias "
        "(objetivo, prazo, disponibilidade e nível atual)."
    )


# Carrega a skill plano-de-estudos
skill_plano = load_skill_from_dir(SKILL_DIR)
skill_toolset = SkillToolset(skills=[skill_plano])

# Configura o ambiente local apontando para a pasta planos/
env = LocalEnvironment(working_dir=PLANOS_DIR)
arquivo_toolset = FerramentasDeArquivo(environment=env)

root_agent = Agent(
    name="agente_estudos",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=obter_instrucao,
    tools=[skill_toolset, arquivo_toolset],
)

app = App(
    root_agent=root_agent,
    name="app",
)

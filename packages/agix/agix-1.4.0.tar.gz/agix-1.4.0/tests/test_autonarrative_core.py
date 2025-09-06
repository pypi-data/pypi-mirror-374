import pytest

from src.agix.autonarrative.autonarrative_core import AutonarrativeCore, Experience


def test_store_experience_and_query():
    core = AutonarrativeCore()
    exp = Experience(text="hola mundo", metadata={"tipo": "saludo"})
    exp_id = core.store_experience(exp)
    assert isinstance(exp_id, int)

    resultados = core.query_experiences("hola", {})
    assert resultados
    assert resultados[0].text == "hola mundo"


def test_query_experiences_filters():
    core = AutonarrativeCore()
    core.store_experience(Experience(text="hola", metadata={"categoria": "saludo"}))
    core.store_experience(Experience(text="adios", metadata={"categoria": "despedida"}))

    resultados = core.query_experiences("hola", {"categoria": "saludo"})
    assert len(resultados) == 1
    assert resultados[0].metadata["categoria"] == "saludo"


def test_query_similarity_order():
    core = AutonarrativeCore()
    core.store_experience(Experience(text="hola mundo", metadata={}))
    core.store_experience(Experience(text="hola", metadata={}))
    core.store_experience(Experience(text="adios", metadata={}))

    resultados = core.query_experiences("hola", {})
    assert resultados[0].text == "hola"
    assert resultados[1].text == "hola mundo"


def test_self_model_updates_and_snapshots():
    core = AutonarrativeCore()
    exp = Experience(
        text="día soleado",
        metadata={
            "values": ["alegría"],
            "goals": ["aprender"],
            "affective_states": "feliz",
        },
    )
    core.store_experience(exp)

    assert core.self_model.values["alegría"] == 1
    assert core.self_model.goals["aprender"] == 1
    assert core.self_model.affective_states["feliz"] == 1
    assert len(core.self_model.history) == 1


def test_evaluate_action_adjusts_scores():
    core = AutonarrativeCore()
    core.store_experience(
        Experience(
            text="estudio de física",
            metadata={
                "goals": ["aprender"],
                "affective_states": ["curioso"],
            },
        )
    )

    result = core.evaluate_action("aprender con actitud curioso")
    assert result["compatibility"] > 0
    assert core.self_model.planning_score > 0.5
    assert core.self_model.motivation_score > 0.5


def test_self_model_multiple_updates():
    core = AutonarrativeCore()
    core.store_experience(
        Experience(text="día", metadata={"values": ["curiosidad"]})
    )
    core.store_experience(
        Experience(
            text="noche de estudio",
            metadata={
                "values": ["curiosidad"],
                "goals": ["aprender"],
                "affective_states": ["motivado"],
            },
        )
    )

    assert core.self_model.values["curiosidad"] == 2
    assert core.self_model.goals["aprender"] == 1
    assert core.self_model.affective_states["motivado"] == 1
    assert len(core.self_model.history) == 2


def test_evaluate_action_penalizes_mismatch():
    core = AutonarrativeCore()
    core.store_experience(
        Experience(
            text="estudio de historia",
            metadata={
                "goals": ["aprender"],
                "affective_states": ["curioso"],
            },
        )
    )

    result = core.evaluate_action("jugar fútbol")
    assert result["compatibility"] == 0
    assert core.self_model.planning_score == 0.45
    assert core.self_model.motivation_score == 0.45

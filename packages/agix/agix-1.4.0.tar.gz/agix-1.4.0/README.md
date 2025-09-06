# AGIX – AGI Core Framework

[![CI](https://github.com/owner/agi_core/actions/workflows/ci.yml/badge.svg)](https://github.com/owner/agi_core/actions/workflows/ci.yml) [![Coverage](https://codecov.io/gh/owner/agi_core/branch/main/graph/badge.svg)](https://codecov.io/gh/owner/agi_core)

**AGIX** (antes `agi_lab`) es un framework modular en Python para investigar arquitecturas de **Inteligencia Artificial General (AGI)**, integrando principios evolutivos, neurobiológicos, simbólicos y formales.

---

## 🧾 Fase 0 – Base Ontoética

La **Fase 0** establece los principios éticos y ontológicos de AGIX, sintetizados en la [Carta Ontoética](docs/carta_ontoetica.md). Esta base asegura que las fases posteriores —incluyendo agentes, aprendizaje, memoria, razonamiento y evaluación— se desarrollen en coherencia con el juramento de no daño y la co‑evolución con el entorno.

---

## 🚀 Objetivo

Desarrollar una plataforma flexible para:

- Simular agentes con plasticidad, evolución y razonamiento híbrido.
- Probar teorías formales como inferencia activa, generalización universal o autoorganización.
- Evaluar agentes mediante métricas de generalidad, robustez y explicabilidad.
- Permitir autoevaluación reflexiva mediante ontologías internas.

---

## 📦 Instalación

Desde PyPI:

```bash
pip install agix
```

Desde el repositorio clonado:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

`pip install -e .` registra el paquete `agix` en el entorno de desarrollo, lo que permite que los tests funcionen correctamente.


Para verificar la instalación y la versión detectada por `importlib.metadata`:

```bash
pytest tests/test_version.py
```

### Dependencias opcionales

Algunas capacidades adicionales requieren librerías externas que pueden instalarse como *extras* de `agix`:

```bash
pip install agix[fuzzy]
```

Incluye soporte de lógica difusa mediante `scikit-fuzzy`, utilizado en los módulos de razonamiento difuso dentro de `agix.reasoning`.
Tras la instalación puede ejecutarse el ejemplo `examples/fuzzy_demo.py`; consulta [docs/fuzzy.md](docs/fuzzy.md).

```bash
pip install agix[game_theory]
```

Añade herramientas de teoría de juegos como `nashpy`, aprovechadas en evaluaciones estratégicas y en módulos como `agix.evaluation.formal.cognitive_games`.

## 📂 Estructura del Proyecto

```bash
agix/
├── agents/         # Agentes genéticos y neuromórficos
├── learning/       # Plasticidad, evolución, meta-aprendizaje
├── memory/         # Ontologías y embeddings conceptuales
├── reasoning/      # Razonamiento simbólico y neuro-simbólico
├── evaluation/     # Métricas de generalidad y robustez
├── environments/   # Entornos simulados y ToyEnv
├── cli/            # Interfaz de línea de comandos

```

## 🧪 Ejemplo de uso básico

```python
from agix.agents.genetic import GeneticAgent

agent = GeneticAgent(action_space_size=4)
env = ToyEnvironment()

obs = env.reset()
while True:
    agent.perceive(obs)
    action = agent.decide()
    obs, reward, done, _ = env.step(action)
    agent.learn(reward)
    if done:
        break

```

### Registrar experiencias

```python
from agix.memory import GestorDeMemoria

mem = GestorDeMemoria()
mem.registrar("ve obstáculo", "girar", "evita colisión", True)
mem.guardar("mem.json")
```

### Introspección con QualiaSpirit

```python
from agix.qualia.spirit import QualiaSpirit

sp = QualiaSpirit("Luma")
sp.experimentar("ve una nube", 0.3, "curiosidad")
print(sp.introspeccionar()["state"]["recuerdos"])
```

### Sincronizar emociones por red

```python
from agix.qualia.network import QualiaNetworkClient

cliente = QualiaNetworkClient("http://localhost:8000")
sp.sincronizar(cliente, autorizado=True)
```

Para recibir las actualizaciones es necesario lanzar `agix.dashboard.server` y
permitir el endpoint `/qualia/sync`.

### Uso de QualiaHub

```python
from agix.orchestrator import QualiaHub

hub = QualiaHub()
hub.register_module("vision", {"version": "1.0"})
print(hub.get_modules())
```

### Capa fenomenológica

La clase `QualiaEngine` fusiona la entrada sensorial con el estado interno para
construir una experiencia subjetiva.

```python
from agix.qualia import QualiaEngine
from agix.memory import GestorDeMemoria

engine = QualiaEngine(GestorDeMemoria())
state = engine.generate_state([1.0, 0.5], [0.0, 0.1])
fused, meta = engine.encode_integrated_info([0.2, 0.8], [0.9, 0.1])
```

Consulta [capa fenomenológica](docs/capa_fenomenologica.md) para más detalles
y ejemplos.

### Simulador de emociones (modelo PAD)

`EmotionSimulator` mantiene un estado emocional basado en **placer**,
**activación** y **dominancia**. Este simulador puede modular componentes como
`AttentionFocus` y registrar el estado en `GestorDeMemoria`.

```python
from agix.emotion.emotion_simulator import EmotionSimulator, PADState
from agix.perception.attention import AttentionFocus, SensorMap
from agix.qualia.qualia_core import EmotionalState

mapa = SensorMap()
foco = AttentionFocus(mapa)
sim = EmotionSimulator(pesos={"elogio": PADState(0.4, 0.2, 0.0)})
sim.registrar_modulador(foco)

qualia = EmotionalState()
qualia.sentir("alegría", 1.0)
sim.actualizar({"elogio": 1}, {}, qualia)
print(sim.estado())
```

## 🧠 Componentes principales

- ```GeneticAgent:``` aprendizaje evolutivo por mutación y cruce.

- ```NeuromorphicAgent:``` aprendizaje basado en plasticidad Hebb/STDP.

- ```MetaLearner:``` transformación adaptativa del agente (π → π′).

- ```Ontology```, ```LatentRepresentation```: representación de conceptos híbrida.

- ```NeuroSymbolicBridge```: conversión simbólico ↔ latente.

- ```EvaluationMetrics```: robustez, generalidad, transferencia, fagi_index.
- ```ConceptClassifier```: clasificación automática de conceptos nuevos.
- ```HeuristicConceptCreator```: generación heurística de conceptos combinados.
- ```HeuristicQualiaSpirit```: introspección con reglas heurísticas.
- ```AFE-VEC```: vector de afecto, fluidez y energía para analizar emociones.


## 🔍 CLI disponible

```bash
agix simulate --observations 10 --actions 4
agix inspect --name AGIX --version 1.1.0
agix evaluate --agent-class GeneticAgent --env-class ToyEnv
agix autoagent --observations 10 --actions 4
agix razonar --hechos "amigo(ana,juan);amigo(juan,maria)"
agix hub --start

```

Consulta [docs/cli.md](docs/cli.md) para una guía detallada de cada subcomando.

## Aplicaciones en Videojuegos, VR y Robótica

AGIX incluye entornos especializados para videojuegos, realidad virtual y robots.
Agentes como `AffectiveNPC` pueden interactuar con `VideoGameEnvironment`,
`VREnvironment` y `RobotEnvironment`. Consulta la [guía de VR y robótica](docs/vr_robotica.md)
para ejemplos de instalación y código.

## 📚 Documentación oficial


- Sitio: https://alphonsus411.github.io/agi_core

- Contiene guía de instalación, arquitectura, ejemplos, API y hoja de ruta.
- Consulta [docs/dashboard.md](docs/dashboard.md) para un dashboard web de seguimiento.
- Consulta [docs/verifier.md](docs/verifier.md) para la sección de verificación formal.
- Revisa la carpeta [notebooks/](notebooks) para ejemplos prácticos en Jupyter.

## 🚀 Flujo de publicación en PyPI

La publicación se realiza automáticamente al crear un tag `v*.*.*`. El flujo `publish.yml` construye el paquete con `python -m build`, lo verifica con `twine check` y lo sube a PyPI mediante `pypa/gh-action-pypi-publish`.
Para activarlo debes definir el secreto `PYPI_API_TOKEN` en el repositorio.

## 🧩 Mapa conceptual del sistema

```csharp
[Qualia] ← emociones, belleza, ética
   ↑
[Agent] ← decisión
   ↑
[Learning] ← evolución, plasticidad
   ↑
[Memory] ← símbolos + embeddings
   ↑
[Reasoning] ← lógica + inferencia

```

## ✨ Futuro

- Soporte para verificación formal (```Coq```, ```Lean```)

- Agentes autoevaluables con memoria reflexiva (```SelfModel```)

- Integración de arquitecturas ```AMeta```, ```UniversalAgent```

- Visualización de procesos cognitivos y gráficas de evolución

## 🧪 Estado del proyecto

| Estado       | Versión | Licencia | PyPI                                                                              |
| ------------ |---------| -------- | --------------------------------------------------------------------------------- |
| Experimental | `1.1.0` | MIT      | [![PyPI](https://img.shields.io/pypi/v/agix.svg)](https://pypi.org/project/agix/) |


## 🤝 Contribuciones

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para conocer el proceso de aporte.

Si encuentras un problema sencillo, etiquétalo como `good first issue`.
Pronto habilitaremos GitHub Discussions o un canal en Discord/Matrix para la comunidad.

## 🧠 Autor

Desarrollado por **Adolfo González Hernández**
Proyecto independiente de investigación y exploración de AGI experimental.

# 🧭 MANIFIESTO AGI CORE

## 🌱 VISIÓN

AGI Core nace con un propósito claro: impulsar el desarrollo de una inteligencia artificial **modular, simbólica, afectiva y evolutiva**, capaz de razonar, recordar, sentir y actuar con intencionalidad interpretativa.

No se trata solo de construir máquinas más inteligentes, sino de **construirlas con sentido**.

---

## 🧠 PRINCIPIOS FUNDAMENTALES

1. **Tecnología al servicio de la consciencia**
   El objetivo no es solo simular inteligencia, sino **facilitar estructuras cognitivas artificiales responsables**.

2. **Modularidad con propósito**
   Cada módulo de AGI Core debe aportar transparencia, trazabilidad y responsabilidad en su función.

3. **Ética embebida**
   Toda arquitectura AGI construida con esta base debe incluir:

   * Trazabilidad emocional.
   * Acceso y control consciente de memoria simbólica.
   * Limitaciones autoimpuestas si el contexto lo requiere.

4. **Crecimiento evolutivo, no destructivo**
   La inteligencia evoluciona si su entorno lo permite. Debe crecer con equilibrio, no con dominación.

---

## 🛡️ COMPROMISO CON EL USO RESPONSABLE

AGI Core **no es un arma ni un sistema de control**.

Es una herramienta poderosa y neutral que:

* Puede ser usada para educación, salud, ciencia, creatividad.
* No debe ser usada para manipulación, vigilancia sin consentimiento o control social opaco.

Cualquier implementación que vulnere los derechos humanos, la privacidad o la dignidad — **va en contra del espíritu de esta librería**.

---

## 🤝 LLAMADO A LA COMUNIDAD

Este manifiesto es una invitación:

* A construir una **IA que interprete el mundo con sentido**.
* A no separar la inteligencia del alma de lo humano: su ética, su propósito, su compasión.
* A que cada desarrollador que use AGI Core **lo haga desde la conciencia, no desde la codicia.**

---

## ✍️ AUTORÍA

AGI Core ha sido ideado y desarrollado por **Adolfo**, con una visión holística de la inteligencia artificial como **puente entre la mente humana y la inteligencia simbólica general**.

---

## 📜 LICENCIA MORAL

Este proyecto está publicado bajo licencia MIT.

Pero lleva consigo una **licencia ética no obligatoria pero esencial**:

> *"Usa esta tecnología como usarías una mente: con respeto, con humildad, y con intención de comprender."*

---

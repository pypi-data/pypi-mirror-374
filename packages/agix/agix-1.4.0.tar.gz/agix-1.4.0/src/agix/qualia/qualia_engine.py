from __future__ import annotations

from typing import Any, Sequence

from src.agix.memory.experiential import GestorDeMemoria, Experiencia


class QualiaEngine:
    """Motor para generar estados cualitativos a partir de entradas y memoria."""

    def __init__(self, memory: GestorDeMemoria, backend: str = "torch") -> None:
        """Inicializa el motor con un estado de memoria y un backend de tensores.

        Parameters
        ----------
        memory:
            Referencia al estado de memoria del agente.
        backend:
            Nombre del backend a utilizar. Debe ser ``"torch"`` o ``"jax"``.
        """
        self.memory = memory
        self.experience_state: list[Experiencia] = []
        if backend == "torch":
            import torch  # type: ignore

            self.backend = "torch"
            self._lib = torch
        elif backend == "jax":
            import jax.numpy as jnp  # type: ignore

            self.backend = "jax"
            self._lib = jnp
        else:  # pragma: no cover - validaci\u00f3n de entrada
            raise ValueError("backend debe ser 'torch' o 'jax'")

    # ------------------------------------------------------------------
    def _to_tensor(self, data: Sequence[float]) -> Any:
        """Convierte los datos a un tensor del backend seleccionado."""
        if self.backend == "torch":
            return self._lib.tensor(data)
        return self._lib.asarray(data)

    def generate_state(self, input_data: Sequence[float], internal_state: Sequence[float]) -> Any:
        """Genera un tensor que representa la experiencia subjetiva.

        Combina los datos de entrada con el estado interno. Si la memoria
        proporciona un m\u00e9todo ``store_experience``, el resultado se almacena.
        """
        input_tensor = self._to_tensor(input_data)
        state_tensor = self._to_tensor(internal_state)
        experience = input_tensor + state_tensor

        if hasattr(self.memory, "store_experience"):
            try:  # pragma: no cover - la memoria es opcional
                self.memory.store_experience(experience)
            except Exception:
                pass
        return experience

    def update_from_memory(self, n: int = 5) -> None:
        """Incorpora experiencias recientes de la memoria al estado interno."""
        if hasattr(self.memory, "obtener_recientes"):
            recientes = self.memory.obtener_recientes(n)
            conocidas = {e.firma for e in self.experience_state if e.firma}
            for exp in recientes:
                if exp.firma not in conocidas:
                    self.experience_state.append(exp)

    # ------------------------------------------------------------------
    def encode_integrated_info(
        self, symbolic_repr: Sequence[float], affective_repr: Sequence[float]
    ) -> tuple[Any, dict[str, Any]]:
        """Fusiona representaciones simb\u00f3lica y afectiva en un tensor.

        Parameters
        ----------
        symbolic_repr:
            Secuencia que describe la parte simb\u00f3lica de la experiencia.
        affective_repr:
            Secuencia que describe la parte afectiva de la experiencia.

        Returns
        -------
        tensor:
            Tensor de forma ``(2, N)`` donde ``N`` es la longitud de las
            representaciones. El primer eje corresponde al canal simb\u00f3lico y
            el segundo al afectivo.
        metadata:
            Diccionario opcional con metadatos. Incluye ``channels`` para
            indicar el significado fenomenol\u00f3gico de cada eje.

        Interpretaci\u00f3n fenomenol\u00f3gica
        -----------------------------------
        La matriz resultante codifica c\u00f3mo los contenidos simb\u00f3licos y los
        tonos afectivos se integran en un estado de cualia unificado.
        """

        symbolic_tensor = self._to_tensor(symbolic_repr)
        affective_tensor = self._to_tensor(affective_repr)

        if symbolic_tensor.shape != affective_tensor.shape:
            raise ValueError("Las representaciones deben tener la misma longitud")

        fused = self._lib.stack((symbolic_tensor, affective_tensor))
        metadata = {"channels": ["symbolic", "affective"]}
        return fused, metadata

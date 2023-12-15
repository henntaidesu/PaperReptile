from typing import Any
from dataclasses import dataclass
import json


@dataclass
class ArxivOrgPageModel:
    Astrophysics: str
    Condensed_Matter: str
    General_Relativity_and_Quantum_Cosmology: str
    High_Energy_Physics_Experiment: str
    High_Energy_Physi_Physics_Phenomenology: str
    High_Energy_Physics_Theory: str
    Mathematical_Physics: str
    Nonlinear_Sciences: str
    Nuclear_Experiment: str
    Physics: str
    Quantum_Physics: str
    Mathematics: str
    computer_science: str
    quantitative_biology: str
    quantitative_finance: str
    Electrical_Engineering_and_Systems_Science: str
    Economics: str

    @staticmethod
    def from_dict(obj: Any) -> 'ArxivOrgPageModel':
        _Astrophysics = f"astro-ph"
        _Condensed_Matter = f"cond-mat"
        _General_Relativity_and_Quantum_Cosmology = "gr-qc"
        _High_Energy_Physics_Experiment = "hep-ex"
        _High_Energy_Physi_Physics_Phenomenology = "hep-ph"
        _High_Energy_Physics_Theory = "hep-th"
        _Mathematical_Physics = "math-ph"
        _Nonlinear_Sciences = "nlin"
        _Nuclear_Experiment = "nucl-ex"
        _Physics = "physics"
        _Quantum_Physics = "quant-ph"
        _Mathematics = "math"
        _computer_science = "cs"
        _quantitative_biology = "q-bio"
        _quantitative_finance = "q-fin"
        _Electrical_Engineering_and_Systems_Science = "eess"
        _Economics = "econ"
        _Statistics = "stat"

        return ArxivOrgPageModel(_Astrophysics, _Condensed_Matter, _General_Relativity_and_Quantum_Cosmology
                                 , _High_Energy_Physics_Experiment, _High_Energy_Physi_Physics_Phenomenology
                                 , _High_Energy_Physics_Theory, _Mathematical_Physics, _Nonlinear_Sciences
                                 , _Nuclear_Experiment, _Physics, _Quantum_Physics, _Mathematics, _computer_science
                                 , _quantitative_biology, _quantitative_finance
                                 , _Electrical_Engineering_and_Systems_Science, _Economics)

    def to_json(self) -> str:
        return json.dumps(self.__dict__)



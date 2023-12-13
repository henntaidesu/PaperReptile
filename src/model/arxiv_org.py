from typing import Any
from dataclasses import dataclass
import json


@dataclass
class ArxivOrgPageModel:
    Abstract: str
    Title: str
    Authors: str

    @staticmethod
    def from_dict(obj: Any) -> 'ArxivOrgPageModel':
        _Abstract = str(obj.get("Abstract"))
        _Title = str(obj.get("Title"))
        _Authors = float(obj.get("Authors"))

        return ArxivOrgPageModel(_Abstract, _Title, _Authors)

    def to_json(self) -> str:
        return json.dumps(self.__dict__)


class PageUrl:

    def all_url(self):
        paysice_url = self.paysice()
        mathematics_url = self.mathematics()
        computer_science_url = self.computer_science()
        quantitative_biology_url = self.quantitative_biology()
        quantitative_finance_url = self.quantitative_biology()
        statistics_url = self.statistics()
        Electrical_Engineering_and_Systems_Science_url = self.Electrical_Engineering_and_Systems_Science()
        Economics_url = self.Economics()
        url_list = (paysice_url + mathematics_url + computer_science_url + quantitative_finance_url +
                    quantitative_finance_url + statistics_url + Electrical_Engineering_and_Systems_Science_url +
                    Economics_url)
        # url_list = [computer_science_url]

        return url_list

    def paysice(self):
        Astrophysics = f"astro-ph"
        Condensed_Matter = f"cond-mat"
        General_Relativity_and_Quantum_Cosmology = "gr-qc"
        High_Energy_Physics_Experiment = "hep-ex"
        High_Energy_Physi_Physics_Phenomenology = "hep-ph"
        High_Energy_Physics_Theory = "hep-th"
        Mathematical_Physics = "math-ph"
        Nonlinear_Sciences = "nlin"
        Nuclear_Experiment = "nucl-ex"
        Physics = "physics"
        Quantum_Physics = "quant-ph"

        return [Astrophysics, Condensed_Matter, General_Relativity_and_Quantum_Cosmology,
                High_Energy_Physics_Experiment, High_Energy_Physi_Physics_Phenomenology,
                High_Energy_Physics_Theory, Mathematical_Physics, Nonlinear_Sciences, Nuclear_Experiment,
                Physics, Quantum_Physics]

    def mathematics(self):
        Mathematics = "math"
        return [Mathematics]

    def computer_science(self):
        computer_science = "cs"
        return [computer_science]

    def quantitative_biology(self):
        quantitative_biology = "q-bio"
        return [quantitative_biology]

    def quantitative_finance(self):
        quantitative_finance = "quantitative_finance"
        return [quantitative_finance]

    def statistics(self):
        statistics = "stat"
        return [statistics]

    def Electrical_Engineering_and_Systems_Science(self):
        Electrical_Engineering_and_Systems_Science = "eess"
        return [Electrical_Engineering_and_Systems_Science]

    def Economics(self):
        Economics = "econ"
        return [Economics]

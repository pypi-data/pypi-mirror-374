"""
This file implements a perturbation estimator from haar.
"""

import logging
import typing
import dataclasses
import tyro
from .common import CommonConfig
from .subcommand_dict import subcommand_dict


@dataclasses.dataclass
class PerturbationConfig:
    """
    The perturbation estimator from haar.
    """

    common: typing.Annotated[CommonConfig, tyro.conf.OmitArgPrefixes]

    def main(self, *, model_param: typing.Any = None, network_param: typing.Any = None) -> None:
        """
        The main function of two-step optimization process based on imaginary time.
        """
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-branches

        model, _, data = self.common.main(model_param=model_param, network_param=network_param)

        if "haar" not in data and "imag" in data:
            data["haar"] = data.pop("imag")
        configs, psi = data["haar"]["pool"]
        configs = configs.to(self.common.device)
        psi = psi.to(self.common.device)

        energy0_num = psi.conj() @ model.apply_within(configs, psi, configs)
        energy0_den = psi.conj() @ psi
        energy0 = (energy0_num / energy0_den).real.item()
        logging.info("Current energy is %.8f", energy0)
        logging.info("Reference energy is %.8f", model.ref_energy)

        number = configs.size(0)
        last_result_number = 0
        current_target_number = number
        logging.info("Starting finding relative configurations with %d.", number)
        while True:
            other_configs = model.find_relative(configs, psi, current_target_number, configs)
            current_result_number = other_configs.size(0)
            logging.info("Found %d relative configurations.", current_result_number)
            if current_result_number == last_result_number:
                logging.info("No new configurations found, stopping at %d.", current_result_number)
                break
            current_target_number = current_target_number * 2
            logging.info("Doubling target number to %d.", current_target_number)
            break

        hamiltonian_psi = model.apply_within(configs, psi, other_configs)
        energy2_num = (hamiltonian_psi.conj() @ hamiltonian_psi).real / (psi.conj() @ psi).real
        energy2_den = energy0 - model.diagonal_term(other_configs).real
        energy2 = (energy2_num / energy2_den).sum().item()
        logging.info("Correct energy is %.8f", energy2)
        logging.info("Error is reduced from %.8f to %.8f", energy0 - model.ref_energy, energy2 - model.ref_energy)


subcommand_dict["pert"] = PerturbationConfig

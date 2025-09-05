"""
This file provides an interface to work with openfermion models.
"""

import os
import typing
import logging
import dataclasses
import pathlib
import torch
import tyro
import openfermion
from .mlp import WaveFunctionElectronUpDown as MlpWaveFunction
from .attention import WaveFunctionElectronUpDown as AttentionWaveFunction
from .crossmlp import WaveFunction as CrossMlpWaveFunction
from .hamiltonian import Hamiltonian
from .model_dict import model_dict, ModelProto, NetworkProto, NetworkConfigProto

QMB_MODEL_PATH = "QMB_MODEL_PATH"


@dataclasses.dataclass
class ModelConfig:
    """
    The configuration of the model.
    """

    # The openfermion model name
    model_name: typing.Annotated[str, tyro.conf.Positional, tyro.conf.arg(metavar="MODEL")]
    # The path of models folder
    model_path: typing.Annotated[pathlib.Path | None, tyro.conf.arg(aliases=["-M"], help_behavior_hint=f"default: \"models\", can be overridden by `${QMB_MODEL_PATH}'")] = None

    def __post_init__(self) -> None:
        if self.model_path is not None:
            self.model_path = pathlib.Path(self.model_path)
        else:
            if QMB_MODEL_PATH in os.environ:
                self.model_path = pathlib.Path(os.environ[QMB_MODEL_PATH])
            else:
                self.model_path = pathlib.Path("models")


class Model(ModelProto[ModelConfig]):
    """
    This class handles the openfermion model.
    """

    network_dict: dict[str, type[NetworkConfigProto["Model"]]] = {}

    config_t = ModelConfig

    @classmethod
    def default_group_name(cls, config: ModelConfig) -> str:
        return config.model_name

    def __init__(self, args: ModelConfig) -> None:
        logging.info("Input arguments successfully parsed")
        logging.info("Model name: %s, Model path: %s", args.model_name, args.model_path)

        model_name = args.model_name
        model_path = args.model_path
        assert model_path is not None

        model_file_name = model_path / f"{model_name}.hdf5"
        logging.info("Loading OpenFermion model '%s' from file: %s", model_name, model_file_name)
        openfermion_model: openfermion.MolecularData = openfermion.MolecularData(filename=str(model_file_name))  # type: ignore[no-untyped-call]
        logging.info("OpenFermion model '%s' successfully loaded", model_name)

        self.n_qubits: int = int(openfermion_model.n_qubits)  # type: ignore[arg-type]
        self.n_electrons: int = int(openfermion_model.n_electrons)  # type: ignore[arg-type]
        logging.info("Identified %d qubits and %d electrons for model '%s'", self.n_qubits, self.n_electrons, model_name)

        self.ref_energy: float = float(openfermion_model.fci_energy)  # type: ignore[arg-type]
        logging.info("Reference energy for model '%s' is %.10f", model_name, self.ref_energy)

        logging.info("Converting OpenFermion Hamiltonian to internal Hamiltonian representation")
        self.hamiltonian: Hamiltonian = Hamiltonian(
            openfermion.transforms.get_fermion_operator(openfermion_model.get_molecular_hamiltonian()).terms,  # type: ignore[no-untyped-call]
            kind="fermi",
        )
        logging.info("Internal Hamiltonian representation for model '%s' has been successfully created", model_name)

    def apply_within(self, configs_i: torch.Tensor, psi_i: torch.Tensor, configs_j: torch.Tensor) -> torch.Tensor:
        return self.hamiltonian.apply_within(configs_i, psi_i, configs_j)

    def find_relative(self, configs_i: torch.Tensor, psi_i: torch.Tensor, count_selected: int, configs_exclude: torch.Tensor | None = None) -> torch.Tensor:
        return self.hamiltonian.find_relative(configs_i, psi_i, count_selected, configs_exclude)

    def diagonal_term(self, configs: torch.Tensor) -> torch.Tensor:
        return self.hamiltonian.diagonal_term(configs)

    def single_relative(self, configs: torch.Tensor) -> torch.Tensor:
        return self.hamiltonian.single_relative(configs)

    def show_config(self, config: torch.Tensor) -> str:
        string = "".join(f"{i:08b}"[::-1] for i in config.cpu().numpy())
        return "[" + "".join(self._show_config_site(string[index:index + 2]) for index in range(0, self.n_qubits, 2)) + "]"

    def _show_config_site(self, string: str) -> str:
        match string:
            case "00":
                return " "
            case "10":
                return "↑"
            case "01":
                return "↓"
            case "11":
                return "↕"
            case _:
                raise ValueError(f"Invalid string: {string}")


model_dict["openfermion"] = Model


@dataclasses.dataclass
class MlpConfig:
    """
    The configuration of the MLP network.
    """

    # The hidden widths of the network
    hidden: typing.Annotated[tuple[int, ...], tyro.conf.arg(aliases=["-w"])] = (512,)

    def create(self, model: Model) -> NetworkProto:
        """
        Create a MLP network for the model.
        """
        logging.info("Hidden layer widths: %a", self.hidden)

        network = MlpWaveFunction(
            double_sites=model.n_qubits,
            physical_dim=2,
            is_complex=True,
            spin_up=model.n_electrons // 2,
            spin_down=model.n_electrons // 2,
            hidden_size=self.hidden,
            ordering=+1,
        )

        return network


Model.network_dict["mlp"] = MlpConfig


@dataclasses.dataclass
class AttentionConfig:
    """
    The configuration of the attention network.
    """

    # Embedding dimension
    embedding_dim: typing.Annotated[int, tyro.conf.arg(aliases=["-e"])] = 512
    # Heads number
    heads_num: typing.Annotated[int, tyro.conf.arg(aliases=["-m"])] = 8
    # Feedforward dimension
    feed_forward_dim: typing.Annotated[int, tyro.conf.arg(aliases=["-f"])] = 2048
    # Shared expert number
    shared_expert_num: typing.Annotated[int, tyro.conf.arg(aliases=["-s"])] = 1
    # Routed expert number
    routed_expert_num: typing.Annotated[int, tyro.conf.arg(aliases=["-r"])] = 0
    # Selected expert number
    selected_expert_num: typing.Annotated[int, tyro.conf.arg(aliases=["-c"])] = 0
    # Network depth
    depth: typing.Annotated[int, tyro.conf.arg(aliases=["-d"])] = 6

    def create(self, model: Model) -> NetworkProto:
        """
        Create an attention network for the model.
        """
        logging.info(
            "Attention network configuration: "
            "embedding dimension: %d, "
            "number of heads: %d, "
            "feed-forward dimension: %d, "
            "shared expert number: %d, "
            "routed expert number: %d, "
            "selected expert number: %d, "
            "depth: %d",
            self.embedding_dim,
            self.heads_num,
            self.feed_forward_dim,
            self.shared_expert_num,
            self.routed_expert_num,
            self.selected_expert_num,
            self.depth,
        )

        network = AttentionWaveFunction(
            double_sites=model.n_qubits,
            physical_dim=2,
            is_complex=True,
            spin_up=model.n_electrons // 2,
            spin_down=model.n_electrons // 2,
            embedding_dim=self.embedding_dim,
            heads_num=self.heads_num,
            feed_forward_dim=self.feed_forward_dim,
            shared_num=self.shared_expert_num,
            routed_num=self.routed_expert_num,
            selected_num=self.selected_expert_num,
            depth=self.depth,
            ordering=+1,
        )

        return network


Model.network_dict["attention"] = AttentionConfig


@dataclasses.dataclass
class CrossMlpConfig:
    """
    The configuration of the cross MLP network.
    """

    # The hidden widths of the embedding subnetwork
    embedding_hidden: typing.Annotated[tuple[int, ...], tyro.conf.arg(aliases=["-w"])] = (64,)
    # The dimension of the embedding
    embedding_size: typing.Annotated[int, tyro.conf.arg(aliases=["-e"])] = 16
    # The hidden widths of the momentum subnetwork
    momentum_hidden: typing.Annotated[tuple[int, ...], tyro.conf.arg(aliases=["-m"])] = (64,)
    # The number of max momentum order
    momentum_count: typing.Annotated[int, tyro.conf.arg(aliases=["-n"])] = 1
    # The hidden widths of the tail part
    tail_hidden: typing.Annotated[tuple[int, ...], tyro.conf.arg(aliases=["-t"])] = (64,)
    # The kind of the crossmlp forward function
    kind: typing.Annotated[typing.Literal[0, 1, 2], tyro.conf.arg(aliases=["-k"])] = 0
    # The ordering of the sites
    ordering: typing.Annotated[int | list[int], tyro.conf.arg(aliases=["-o"])] = +1

    def create(self, model: Model) -> NetworkProto:
        """
        Create a cross MLP network for the model.
        """
        logging.info(
            "Cross MLP network configuration: "
            "embedding hidden widths: %a, "
            "embedding size: %d, "
            "momentum hidden widths: %a, "
            "momentum count: %d, "
            "tail hidden widths: %a, "
            "kind: %d, "
            "ordering: %s",
            self.embedding_hidden,
            self.embedding_size,
            self.momentum_hidden,
            self.momentum_count,
            self.tail_hidden,
            self.kind,
            self.ordering,
        )

        network = CrossMlpWaveFunction(
            sites=model.n_qubits,
            physical_dim=2,
            is_complex=False,
            embedding_hidden_size=self.embedding_hidden,
            embedding_size=self.embedding_size,
            momentum_hidden_size=self.momentum_hidden,
            momentum_count=self.momentum_count,
            tail_hidden_size=self.tail_hidden,
            kind=self.kind,
            ordering=self.ordering,
        )

        return network


Model.network_dict["crossmlp"] = CrossMlpConfig

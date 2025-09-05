"""
This file offers an interface for defining Ising-like models on a two-dimensional lattice.
"""

import typing
import logging
import dataclasses
import collections
import torch
import tyro
from .mlp import WaveFunctionNormal as MlpWaveFunction
from .attention import WaveFunctionNormal as AttentionWaveFunction
from .hamiltonian import Hamiltonian
from .model_dict import model_dict, ModelProto, NetworkProto, NetworkConfigProto


@dataclasses.dataclass
class ModelConfig:
    """
    The configuration for the Ising-like model.
    """

    # pylint: disable=too-many-instance-attributes

    # The width of the ising lattice
    m: typing.Annotated[int, tyro.conf.Positional]
    # The height of the ising lattice
    n: typing.Annotated[int, tyro.conf.Positional]

    # The coefficient of X
    x: typing.Annotated[float, tyro.conf.arg(aliases=["-xe"])] = 0
    # The coefficient of Y
    y: typing.Annotated[float, tyro.conf.arg(aliases=["-ye"])] = 0
    # The coefficient of Z
    z: typing.Annotated[float, tyro.conf.arg(aliases=["-ze"])] = 0
    # The coefficient of XX for horizontal bond
    xh: typing.Annotated[float, tyro.conf.arg(aliases=["-xh"])] = 0
    # The coefficient of YY for horizontal bond
    yh: typing.Annotated[float, tyro.conf.arg(aliases=["-yh"])] = 0
    # The coefficient of ZZ for horizontal bond
    zh: typing.Annotated[float, tyro.conf.arg(aliases=["-zh"])] = 0
    # The coefficient of XX for vertical bond
    xv: typing.Annotated[float, tyro.conf.arg(aliases=["-xv"])] = 0
    # The coefficient of YY for vertical bond
    yv: typing.Annotated[float, tyro.conf.arg(aliases=["-yv"])] = 0
    # The coefficient of ZZ for vertical bond
    zv: typing.Annotated[float, tyro.conf.arg(aliases=["-zv"])] = 0
    # The coefficient of XX for diagonal bond
    xd: typing.Annotated[float, tyro.conf.arg(aliases=["-xd"])] = 0
    # The coefficient of YY for diagonal bond
    yd: typing.Annotated[float, tyro.conf.arg(aliases=["-yd"])] = 0
    # The coefficient of ZZ for diagonal bond
    zd: typing.Annotated[float, tyro.conf.arg(aliases=["-zd"])] = 0
    # The coefficient of XX for antidiagonal bond
    xa: typing.Annotated[float, tyro.conf.arg(aliases=["-xa"])] = 0
    # The coefficient of YY for antidiagonal bond
    ya: typing.Annotated[float, tyro.conf.arg(aliases=["-ya"])] = 0
    # The coefficient of ZZ for antidiagonal bond
    za: typing.Annotated[float, tyro.conf.arg(aliases=["-za"])] = 0

    # The ref energy of the model
    ref_energy: typing.Annotated[float, tyro.conf.arg(aliases=["-r"])] = 0


class Model(ModelProto[ModelConfig]):
    """
    This class handles the Ising-like model.
    """

    network_dict: dict[str, type[NetworkConfigProto["Model"]]] = {}

    config_t = ModelConfig

    @classmethod
    def default_group_name(cls, config: ModelConfig) -> str:
        # pylint: disable=too-many-locals
        x = f"_x{config.x}" if config.x != 0 else ""
        y = f"_y{config.y}" if config.y != 0 else ""
        z = f"_z{config.z}" if config.z != 0 else ""
        xh = f"_xh{config.xh}" if config.xh != 0 else ""
        yh = f"_yh{config.yh}" if config.yh != 0 else ""
        zh = f"_zh{config.zh}" if config.zh != 0 else ""
        xv = f"_xv{config.xv}" if config.xv != 0 else ""
        yv = f"_yv{config.yv}" if config.yv != 0 else ""
        zv = f"_zv{config.zv}" if config.zv != 0 else ""
        xd = f"_xd{config.xd}" if config.xd != 0 else ""
        yd = f"_yd{config.yd}" if config.yd != 0 else ""
        zd = f"_zd{config.zd}" if config.zd != 0 else ""
        xa = f"_xa{config.xa}" if config.xa != 0 else ""
        ya = f"_ya{config.ya}" if config.ya != 0 else ""
        za = f"_za{config.za}" if config.za != 0 else ""
        desc = x + y + z + xh + yh + zh + xv + yv + zv + xd + yd + zd + xa + ya + za
        return f"Ising_{config.m}_{config.n}" + desc

    @classmethod
    def _prepare_hamiltonian(cls, args: ModelConfig) -> dict[tuple[tuple[int, int], ...], complex]:
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-nested-blocks

        def _index(i: int, j: int) -> int:
            return i + j * args.m

        def _x(i: int, j: int) -> tuple[tuple[tuple[tuple[int, int], ...], complex], ...]:
            return (
                (((_index(i, j), 1),), +1),
                (((_index(i, j), 0),), +1),
            )

        def _y(i: int, j: int) -> tuple[tuple[tuple[tuple[int, int], ...], complex], ...]:
            return (
                (((_index(i, j), 1),), -1j),
                (((_index(i, j), 0),), +1j),
            )

        def _z(i: int, j: int) -> tuple[tuple[tuple[tuple[int, int], ...], complex], ...]:
            return (
                (((_index(i, j), 1), (_index(i, j), 0)), +1),
                (((_index(i, j), 0), (_index(i, j), 1)), -1),
            )

        hamiltonian: dict[tuple[tuple[int, int], ...], complex] = collections.defaultdict(lambda: 0)
        # Express spin pauli matrix in hard core boson language.
        for i in range(args.m):
            for j in range(args.n):
                k: tuple[tuple[int, int], ...]
                k1: tuple[tuple[int, int], ...]
                k2: tuple[tuple[int, int], ...]
                v: complex
                v1: complex
                v2: complex
                if True:  # pylint: disable=using-constant-test
                    if args.x != 0:
                        for k, v in _x(i, j):
                            hamiltonian[k] += v * args.x
                    if args.y != 0:
                        for k, v in _y(i, j):
                            hamiltonian[k] += v * args.y
                    if args.z != 0:
                        for k, v in _z(i, j):
                            hamiltonian[k] += v * args.z
                if i != 0:
                    if args.xh != 0:
                        for k1, v1 in _x(i, j):
                            for k2, v2 in _x(i - 1, j):
                                hamiltonian[(*k1, *k2)] += v1 * v2 * args.xh
                    if args.yh != 0:
                        for k1, v1 in _y(i, j):
                            for k2, v2 in _y(i - 1, j):
                                hamiltonian[(*k1, *k2)] += v1 * v2 * args.yh
                    if args.zh != 0:
                        for k1, v1 in _z(i, j):
                            for k2, v2 in _z(i - 1, j):
                                hamiltonian[(*k1, *k2)] += v1 * v2 * args.zh
                if j != 0:
                    if args.xv != 0:
                        for k1, v1 in _x(i, j):
                            for k2, v2 in _x(i, j - 1):
                                hamiltonian[(*k1, *k2)] += v1 * v2 * args.xv
                    if args.yv != 0:
                        for k1, v1 in _y(i, j):
                            for k2, v2 in _y(i, j - 1):
                                hamiltonian[(*k1, *k2)] += v1 * v2 * args.yv
                    if args.zv != 0:
                        for k1, v1 in _z(i, j):
                            for k2, v2 in _z(i, j - 1):
                                hamiltonian[(*k1, *k2)] += v1 * v2 * args.zv
                if i != 0 and j != 0:
                    if args.xd != 0:
                        for k1, v1 in _x(i, j):
                            for k2, v2 in _x(i - 1, j - 1):
                                hamiltonian[(*k1, *k2)] += v1 * v2 * args.xd
                    if args.yd != 0:
                        for k1, v1 in _y(i, j):
                            for k2, v2 in _y(i - 1, j - 1):
                                hamiltonian[(*k1, *k2)] += v1 * v2 * args.yd
                    if args.zd != 0:
                        for k1, v1 in _z(i, j):
                            for k2, v2 in _z(i - 1, j - 1):
                                hamiltonian[(*k1, *k2)] += v1 * v2 * args.zd
                if i != 0 and j != args.n - 1:
                    if args.xa != 0:
                        for k1, v1 in _x(i, j):
                            for k2, v2 in _x(i - 1, j + 1):
                                hamiltonian[(*k1, *k2)] += v1 * v2 * args.xa
                    if args.ya != 0:
                        for k1, v1 in _y(i, j):
                            for k2, v2 in _y(i - 1, j + 1):
                                hamiltonian[(*k1, *k2)] += v1 * v2 * args.ya
                    if args.za != 0:
                        for k1, v1 in _z(i, j):
                            for k2, v2 in _z(i - 1, j + 1):
                                hamiltonian[(*k1, *k2)] += v1 * v2 * args.za
        return hamiltonian

    def __init__(self, args: ModelConfig) -> None:
        logging.info("Input arguments successfully parsed")

        self.m: int = args.m
        self.n: int = args.n
        logging.info("Constructing Ising model with dimensions: width = %d, height = %d", self.m, self.n)
        logging.info("Element-wise coefficients: X = %.10f, Y = %.10f, Z = %.10f", args.x, args.y, args.z)
        logging.info("Horizontal bond coefficients: X = %.10f, Y = %.10f, Z = %.10f", args.xh, args.yh, args.zh)
        logging.info("Vertical bond coefficients: X = %.10f, Y = %.10f, Z = %.10f", args.xv, args.yv, args.zv)
        logging.info("Diagonal bond coefficients: X = %.10f, Y = %.10f, Z = %.10f", args.xd, args.yd, args.zd)
        logging.info("Anti-diagonal bond coefficients: X = %.10f, Y = %.10f, Z = %.10f", args.xa, args.ya, args.za)

        logging.info("Initializing Hamiltonian for the lattice")
        hamiltonian_dict: dict[tuple[tuple[int, int], ...], complex] = self._prepare_hamiltonian(args)
        logging.info("Hamiltonian initialization complete")

        self.ref_energy: float = args.ref_energy
        logging.info("The ref energy is set to %.10f", self.ref_energy)

        logging.info("Converting the Hamiltonian to internal Hamiltonian representation")
        self.hamiltonian: Hamiltonian = Hamiltonian(hamiltonian_dict, kind="bose2")
        logging.info("Internal Hamiltonian representation for model has been successfully created")

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
        return "[" + ".".join("".join("↑" if string[i + j * self.m] == "0" else "↓" for i in range(self.m)) for j in range(self.n)) + "]"


model_dict["ising"] = Model


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
            sites=model.m * model.n,
            physical_dim=2,
            is_complex=True,
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
            sites=model.m * model.n,
            physical_dim=2,
            is_complex=True,
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

from dataclasses import dataclass
from omegaconf import OmegaConf


@dataclass
class ConLPoCArguments:
    # data args
    data_cache_dir: str = "./data/"
    partition_method: str = "hetero"
    partition_alpha: float = 10.
    random_seed: int = 42

    # device args
    worker_num: int = 1

    @classmethod
    def from_yml(cls, yml_path: str):
        loaded = OmegaConf.load(yml_path)
        read_conf = ConLPoCArguments(**loaded.poc)

        base_conf = OmegaConf.structured(ConLPoCArguments)
        merged = OmegaConf.merge(base_conf, read_conf)
        return cls(**merged)

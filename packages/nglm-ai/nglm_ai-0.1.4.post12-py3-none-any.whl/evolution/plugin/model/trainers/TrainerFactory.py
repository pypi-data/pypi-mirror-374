# TrainerFactory.py
from typing import Type, Dict
from .base import BaseTrainer


def _all_subclasses(c):
    subclasses = []
    for sub in c.__subclasses__():
        subclasses.append(sub)
        subclasses.extend(_all_subclasses(sub))
        print(subclasses)
    return subclasses


class TrainerFactory:

    _registry: Dict[str, Type[BaseTrainer]] = {}



    @classmethod
    def register_trainer(cls, name: str, trainer_cls: Type[BaseTrainer]) -> None:
        if not issubclass(trainer_cls, BaseTrainer):
            raise TypeError(f"Trainer '{trainer_cls.__name__}' must inherit from BaseTrainer.")
        cls._registry[name.lower()] = trainer_cls

    @classmethod
    def create(cls, config) -> BaseTrainer:
        model_type = config.get("model", {}).get("active")
        if not model_type:
            raise ValueError("Config must define 'model.active'.")

        trainer_cls = _all_subclasses(BaseTrainer).get(model_type.lower())
        if trainer_cls is None:
            available = ", ".join(cls._registry.keys()) or "none"
            raise ValueError(
                f"Unsupported trainer type '{model_type}'. Available trainers: {available}"
            )
        return trainer_cls(config)

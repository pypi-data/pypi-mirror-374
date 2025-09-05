import copy
from typing import Type

from pydantic import BaseModel
from pydantic.fields import FieldInfo, Field


def prune_model(
        *,
        model_cls: Type[BaseModel],
        fields_to_remove: set[str],
        new_class_name: str,
) -> Type[BaseModel]:
    """
    Создаёт новый класс-модель (Pydantic v2), который:
      - наследуется от тех же баз, что и model_cls (в том же порядке);
      - содержит только поля, объявленные В САМОМ model_cls (а не у его баз),
        за вычетом fields_to_remove;
      - копирует каждое поле целиком через deepcopy(FieldInfo), сохраняя ВСЕ атрибуты
        (alias, constraints, repr, json_schema_extra и т.д.).
      - НЕ копирует валидаторы, конфиг, docstring и прочее — только поля.

    Наследованные от баз поля сохранятся за счёт наследования. Удалить наследуемое поле
    таким способом нельзя — нужно менять базовые классы / MRO.
    """
    if not (isinstance(model_cls, type) and issubclass(model_cls, BaseModel)):
        raise TypeError("model_cls должен быть подклассом pydantic.BaseModel (v2).")

    namespace: dict = {
        "__module__": getattr(model_cls, "__module__", "__main__"),
        "__annotations__": {},
    }

    for name, annotation in dict(getattr(model_cls, "__annotations__", {})).items():
        if name in fields_to_remove:
            continue

        field_info: FieldInfo | None = getattr(model_cls, "model_fields", {}).get(name)

        if isinstance(field_info, FieldInfo):
            namespace["__annotations__"][name] = annotation
            namespace[name] = copy.deepcopy(field_info)

    new_model = type(new_class_name, model_cls.__bases__, namespace)

    if not issubclass(new_model, BaseModel):
        raise RuntimeError("not issubclass(new_model, BaseModel)")

    return new_model


def __example():
    from typing import Optional
    from pydantic import BaseModel

    class Timestamped(BaseModel):
        created_at: int = 1
        updated_at: int = 1

        class Names:
            arsen = "arse"

    class User(Timestamped):
        id: int = Field(default=1)
        email: str = "asasf"
        password_hash: str = "asasf"
        nickname: Optional[str] = None

    PublicUser = prune_model(
        model_cls=User,
        fields_to_remove={"id"},
        new_class_name="PublicUser",
    )

    print(PublicUser())


if __name__ == '__main__':
    __example()

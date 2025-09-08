from maleo.enums.cache import Origin, Layer
from maleo.types.base.string import ListOfStrings, OptionalString


def build_namespace(
    *ext: str,
    base: str,
    client: OptionalString = None,
    origin: Origin,
    layer: Layer,
    sep: str = ":",
) -> str:
    slugs: ListOfStrings = []
    slugs.extend([base, origin, layer])
    if client is not None:
        slugs.append(client)
    slugs.extend(ext)
    return sep.join(slugs)


def build_key(*ext: str, namespace: str, sep: str = ":"):
    return sep.join([namespace, *ext])

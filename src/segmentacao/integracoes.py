def obter_api_rembg():
    from rembg import new_session, remove

    return new_session, remove


def obter_resolvedor_providers():
    from src.runtime.runtime_config import resolver_providers

    return resolver_providers

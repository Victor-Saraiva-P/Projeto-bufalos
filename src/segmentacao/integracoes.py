def obter_api_rembg():
    from rembg import new_session, remove

    return new_session, remove


def obter_resolvedor_providers():
    try:
        from src.runtime.runtime_config import resolver_providers
    except ModuleNotFoundError as erro:
        def resolver_providers(
            provider_config: str,
            nome_modelo: str,
        ) -> list[str]:
            if provider_config == "cpu":
                return ["CPUExecutionProvider"]

            raise ModuleNotFoundError(
                "onnxruntime e obrigatorio para usar providers diferentes de CPU."
            ) from erro

    return resolver_providers

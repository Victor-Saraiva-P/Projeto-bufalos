def imprimir_resumo_verificacao_png(resumo) -> None:
    print("\nVerificacao de integridade concluida.")
    print(f" - Total de PNGs verificados: {resumo.total_png}")
    print(f" - Arquivos integros: {resumo.arquivos_integros}")
    print(f" - Arquivos removidos por corrupcao: {resumo.arquivos_removidos}")
    print(f" - Falhas ao remover: {resumo.falhas_remocao}")

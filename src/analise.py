"""
Controle de Qualidade Industrial com Python
Lê medições de peças, calcula indicadores e exporta aprovadas/reprovadas.
"""

import csv
from pathlib import Path
from collections import defaultdict


# Raiz do projeto: um nível acima da pasta src
PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_DADOS = PASTA_PROJETO / "dados"

ARQUIVO_ENTRADA = PASTA_DADOS / "medicoes.csv"
ARQUIVO_APROVADAS = PASTA_DADOS / "aprovadas.csv"
ARQUIVO_REPROVADAS = PASTA_DADOS / "reprovadas.csv"


def ler_medicoes(caminho=ARQUIVO_ENTRADA):
    """Lê o CSV e converte as colunas numéricas, validando os dados básicos."""
    medicoes = []

    with open(caminho, mode="r", newline="", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo)
        campos_obrigatorios = {
            "id_peca", "tipo", "medida_mm", "nominal_mm",
            "tolerancia_mm", "data", "inspetor"
        }

        if not campos_obrigatorios.issubset(leitor.fieldnames or []):
            faltantes = campos_obrigatorios - set(leitor.fieldnames or [])
            raise ValueError(f"Colunas ausentes no CSV: {', '.join(sorted(faltantes))}")

        for numero_linha, linha in enumerate(leitor, start=2):
            try:
                registro = {
                    "id_peca": linha["id_peca"].strip(),
                    "tipo": linha["tipo"].strip(),
                    "medida_mm": float(linha["medida_mm"]),
                    "nominal_mm": float(linha["nominal_mm"]),
                    "tolerancia_mm": float(linha["tolerancia_mm"]),
                    "data": linha["data"].strip(),
                    "inspetor": linha["inspetor"].strip(),
                }
            except (TypeError, ValueError) as erro:
                raise ValueError(
                    f"Valor inválido na linha {numero_linha}: {erro}"
                ) from erro

            if not registro["tipo"] or not registro["id_peca"]:
                raise ValueError(f"Identificação vazia na linha {numero_linha}.")
            if registro["tolerancia_mm"] < 0:
                raise ValueError(f"Tolerância negativa na linha {numero_linha}.")

            medicoes.append(registro)

    if not medicoes:
        raise ValueError("O arquivo CSV não contém medições.")

    return medicoes


def media(valores):
    """Calcula a média aritmética."""
    if not valores:
        return 0.0
    return sum(valores) / len(valores)


def desvio_padrao(valores):
    """Calcula o desvio padrão amostral (divisor n - 1)."""
    if len(valores) < 2:
        return 0.0

    valor_medio = media(valores)
    soma_quadrados = sum((valor - valor_medio) ** 2 for valor in valores)
    return (soma_quadrados / (len(valores) - 1)) ** 0.5


def fora_de_tolerancia(medicao):
    """
    Retorna True quando a peça está fora da tolerância.
    O arredondamento a 6 casas evita reprovação causada apenas por
    imprecisão binária de ponto flutuante. A regra é estritamente >:
    estar exatamente no limite ainda é aprovado.
    """
    diferenca = round(
        abs(medicao["medida_mm"] - medicao["nominal_mm"]), 6
    )
    tolerancia = round(medicao["tolerancia_mm"], 6)
    return diferenca > tolerancia


def agrupar_por_tipo(medicoes):
    """Agrupa os registros pelo tipo de peça."""
    grupos = defaultdict(list)
    for medicao in medicoes:
        grupos[medicao["tipo"]].append(medicao)
    return dict(grupos)


def calcular_capabilidade(medicoes):
    """
    Calcula Cp e Cpk para um grupo homogêneo de peças.
    Considera limites bilaterais: nominal +/- tolerância.
    """
    if len(medicoes) < 2:
        return None, None

    nominais = {round(m["nominal_mm"], 6) for m in medicoes}
    tolerancias = {round(m["tolerancia_mm"], 6) for m in medicoes}

    if len(nominais) != 1 or len(tolerancias) != 1:
        raise ValueError(
            "Não é possível calcular Cp/Cpk: nominal e tolerância "
            "precisam ser iguais dentro do mesmo tipo."
        )

    nominal = medicoes[0]["nominal_mm"]
    tolerancia = medicoes[0]["tolerancia_mm"]
    valores = [m["medida_mm"] for m in medicoes]
    desvio = desvio_padrao(valores)

    if desvio == 0:
        return float("inf"), float("inf")

    limite_superior = nominal + tolerancia
    limite_inferior = nominal - tolerancia
    cp = (limite_superior - limite_inferior) / (6 * desvio)

    valor_medio = media(valores)
    cpu = (limite_superior - valor_medio) / (3 * desvio)
    cpl = (valor_medio - limite_inferior) / (3 * desvio)
    cpk = min(cpu, cpl)

    return cp, cpk


def salvar_csv(caminho, registros):
    """Exporta uma lista de registros para CSV."""
    campos = [
        "id_peca", "tipo", "medida_mm", "nominal_mm",
        "tolerancia_mm", "data", "inspetor"
    ]

    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho, mode="w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(registros)


def exibir_relatorio(medicoes):
    """Exibe o resumo geral e os indicadores por tipo de peça."""
    aprovadas = [m for m in medicoes if not fora_de_tolerancia(m)]
    reprovadas = [m for m in medicoes if fora_de_tolerancia(m)]

    print("=" * 62)
    print("       RELATÓRIO DE CONTROLE DE QUALIDADE INDUSTRIAL")
    print("=" * 62)
    print(f"Total de peças: {len(medicoes)}")
    print(f"Aprovadas:      {len(aprovadas)} ({len(aprovadas) / len(medicoes) * 100:.1f}%)")
    print(f"Reprovadas:     {len(reprovadas)} ({len(reprovadas) / len(medicoes) * 100:.1f}%)")

    print("\nINDICADORES POR TIPO")
    print("-" * 62)

    for tipo, grupo in sorted(agrupar_por_tipo(medicoes).items()):
        valores = [m["medida_mm"] for m in grupo]
        reprovadas_tipo = [m for m in grupo if fora_de_tolerancia(m)]
        cp, cpk = calcular_capabilidade(grupo)

        print(f"\nTipo: {tipo}")
        print(f"  Quantidade:          {len(grupo)}")
        print(f"  Média:               {media(valores):.6f} mm")
        print(f"  Desvio padrão:       {desvio_padrao(valores):.6f} mm")
        print(f"  Reprovadas:          {len(reprovadas_tipo)}")
        print(f"  % de reprovação:     {len(reprovadas_tipo) / len(grupo) * 100:.1f}%")
        print(f"  Cp:                  {cp:.3f}" if cp is not None else "  Cp:                  indisponível")
        print(f"  Cpk:                 {cpk:.3f}" if cpk is not None else "  Cpk:                 indisponível")

        if cpk is not None and cpk < 1.33:
            print("  Avaliação:           abaixo do critério Cp/Cpk de 1,33")

    print("\nPEÇAS REPROVADAS")
    print("-" * 62)
    if reprovadas:
        for peca in reprovadas:
            diferenca = abs(peca["medida_mm"] - peca["nominal_mm"])
            print(
                f'{peca["id_peca"]} | {peca["tipo"]} | '
                f'{peca["medida_mm"]:.3f} mm | '
                f'diferença: {diferenca:.3f} mm'
            )
    else:
        print("Nenhuma peça reprovada.")

    return aprovadas, reprovadas


def main():
    try:
        medicoes = ler_medicoes()
        aprovadas, reprovadas = exibir_relatorio(medicoes)
        salvar_csv(ARQUIVO_APROVADAS, aprovadas)
        salvar_csv(ARQUIVO_REPROVADAS, reprovadas)

        print("\nArquivos exportados:")
        print(f"  Aprovadas:  {ARQUIVO_APROVADAS}")
        print(f"  Reprovadas: {ARQUIVO_REPROVADAS}")

    except (OSError, ValueError) as erro:
        print(f"Erro ao executar a análise: {erro}")
        raise


if __name__ == "__main__":
    main()


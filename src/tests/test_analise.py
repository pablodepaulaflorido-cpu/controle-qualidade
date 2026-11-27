import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from analise import (  # noqa: E402
    media,
    desvio_padrao,
    fora_de_tolerancia,
    agrupar_por_tipo,
    calcular_capabilidade,
)


def criar_medicao(medida, nominal=25.0, tolerancia=0.05, tipo="EIXO-A"):
    return {
        "id_peca": "P-TESTE",
        "tipo": tipo,
        "medida_mm": medida,
        "nominal_mm": nominal,
        "tolerancia_mm": tolerancia,
        "data": "2026-11-01",
        "inspetor": "Teste",
    }


def test_media():
    assert media([2, 4, 6]) == 4


def test_desvio_padrao_amostral():
    assert round(desvio_padrao([2, 4, 6]), 6) == 2.0


def test_limite_exato_da_tolerancia_e_aprovado():
    assert fora_de_tolerancia(criar_medicao(25.05)) is False


def test_medicao_dentro_da_tolerancia_e_aprovada():
    assert fora_de_tolerancia(criar_medicao(25.049)) is False


def test_medicao_fora_da_tolerancia_e_reprovada():
    assert fora_de_tolerancia(criar_medicao(25.051)) is True


def test_agrupar_por_tipo():
    pecas = [
        criar_medicao(25.0, tipo="EIXO-A"),
        criar_medicao(12.5, nominal=12.5, tolerancia=0.03, tipo="BUCHA-B"),
        criar_medicao(25.01, tipo="EIXO-A"),
    ]
    grupos = agrupar_por_tipo(pecas)
    assert len(grupos["EIXO-A"]) == 2
    assert len(grupos["BUCHA-B"]) == 1


def test_cpk_nao_supera_cp_quando_processo_descentralizado():
    grupo = [
        criar_medicao(12.490, nominal=12.5, tolerancia=0.03, tipo="BUCHA-B"),
        criar_medicao(12.500, nominal=12.5, tolerancia=0.03, tipo="BUCHA-B"),
        criar_medicao(12.510, nominal=12.5, tolerancia=0.03, tipo="BUCHA-B"),
    ]
    cp, cpk = calcular_capabilidade(grupo)
    assert cpk <= cp

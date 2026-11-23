import pytest

from app.services.product_relevance import (
    is_product_in_deal_category,
    is_relevant_product,
)


@pytest.mark.parametrize(
    "title",
    [
        "Placa de Vídeo GeForce RTX 4060",
        "Memória RAM DDR5 32GB",
        "Processador Ryzen 7 5700X",
        "Monitor gamer 144Hz",
        "Mouse gamer sem fio",
        "Teclado mecânico RGB",
    ],
)
def test_accepts_requested_pc_and_peripheral_products(title):
    assert is_relevant_product(title)


@pytest.mark.parametrize(
    "title",
    [
        "Livro: guia completo de placas de vídeo",
        "Película de vidro para iPhone",
        "Carregador USB-C para celular",
        "Romance em edição de bolso",
        "Conjunto de instrumentos musicais de percussão para crianças",
        "Teclado musical infantil de brinquedo",
        "Guitarra Baby Einstein Hape Color Magic Touch",
        "Cabo DisplayPort 2 metros",
        "Adaptador USB-C para HDMI",
        "Case para PC Gamer",
        "Suporte articulado para monitor",
        "Violão acústico profissional",
        "Interface de Áudio USB",
        "Teclado musical Yamaha",
        "Monitor de áudio de estúdio",
        "Teclado Yamaha arranjador 61 teclas",
        "Fonte para teclado PA130B Yamaha",
        "Processador elétrico de alimentos",
        "Triturador multiprocessador de alimentos",
    ],
)
def test_rejects_books_accessories_and_out_of_scope_products(title):
    assert not is_relevant_product(title)


def test_rejects_missing_title():
    assert not is_relevant_product(None)


@pytest.mark.parametrize(
    ("title", "category", "expected"),
    [
        ("Placa de vídeo GeForce RTX 4060", "pc", True),
        ("Memória RAM DDR5", "pc", True),
        ("Monitor gamer 144Hz", "peripherals", True),
        ("Mouse gamer sem fio", "peripherals", True),
        ("Cabo para mouse gamer", "peripherals", False),
        ("Suporte para monitor", "peripherals", False),
        ("Case PC Gamer", "pc", False),
        ("Teclado musical Yamaha", "peripherals", False),
        ("Fonte para teclado PA130B Yamaha", "peripherals", False),
        ("Processador de alimentos", "pc", False),
        ("Guitarra elétrica Ibanez Artcore", "guitars", False),
        ("Mouse gamer sem fio", "music", False),
    ],
)
def test_filters_deals_by_category(title, category, expected):
    assert is_product_in_deal_category(title, category) is expected

import re
import unicodedata
from typing import Optional


_RELEVANT_TERMS = (
    "placa de video", "gpu", "geforce", "rtx", "gtx", "radeon",
    "processador", "cpu", "ryzen", "intel core", "core i3", "core i5",
    "core i7", "core i9", "threadripper", "memoria ram", "ddr3", "ddr4",
    "ddr5", "ssd", "nvme", "hd interno", "placa mae", "motherboard",
    "gabinete gamer", "gabinete pc", "fonte atx", "fonte pc", "water cooler",
    "cooler cpu", "mouse", "teclado", "keyboard", "monitor", "headset",
    "fone gamer", "webcam", "microfone", "mousepad", "mouse pad",
    "controle gamer", "gamepad", "joystick", "mesa digitalizadora",
    "placa de captura",
    "pc gamer", "computador gamer", "desktop gamer", "notebook gamer",
)
_EXCLUDED_TERMS = (
    "livro", "livros", "apostila", "ebook", "e book", "revista", "enciclopedia",
    "infantil", "crianca", "criancas", "brinquedo", "brinquedos", "educativo",
    "bebe", "bebes", "baby", "kids", "toy", "toys", "children", "child", "juguete",
    "juguetes", "ninos", "ninas", "cabo", "cabos", "cable", "cables",
    "adaptador", "adaptadores", "adapter", "adapters", "capa", "capas", "case",
    "cases", "suporte", "suportes", "support", "stand", "stands", "funda",
    "fundas", "estuche", "estuches", "soporte", "soportes",
    "guitarra", "violao", "contrabaixo", "baixo eletrico", "ukulele", "piano",
    "teclado musical", "teclado yamaha", "fonte para teclado", "sintetizador",
    "bateria acustica", "bateria eletronica", "processador de alimentos",
    "processador eletrico de alimentos", "multiprocessador", "triturador",
    "liquidificador",
    "interface de audio", "placa de audio", "mesa de som", "monitor de audio",
    "amplificador de guitarra", "amplificador de baixo", "pedal de guitarra",
)
_DEAL_CATEGORY_TERMS = {
    "pc": (
        "placa de video", "gpu", "geforce", "rtx", "gtx", "radeon", "processador",
        "cpu", "ryzen", "intel core", "memoria ram", "ddr3", "ddr4", "ddr5",
        "ssd", "nvme", "hd interno", "placa mae", "motherboard", "gabinete gamer",
        "gabinete pc", "fonte atx", "fonte pc", "water cooler", "cooler cpu",
        "pc gamer", "computador gamer", "desktop gamer", "notebook gamer",
    ),
    "peripherals": (
        "mouse", "teclado", "keyboard", "monitor", "headset", "fone gamer",
        "webcam", "microfone", "mousepad", "mouse pad", "controle gamer",
        "gamepad", "joystick", "mesa digitalizadora",
    ),
}


def _normalize_title(title: str) -> str:
    decomposed = unicodedata.normalize("NFKD", title.casefold())
    without_accents = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    return re.sub(r"[^a-z0-9]+", " ", without_accents).strip()


def is_relevant_product(title: Optional[str]) -> bool:
    if not title:
        return False

    normalized = f" {_normalize_title(title)} "
    if any(f" {term} " in normalized for term in _EXCLUDED_TERMS):
        return False
    return any(f" {term} " in normalized for term in _RELEVANT_TERMS)


def is_product_in_deal_category(title: Optional[str], category: str) -> bool:
    if not title:
        return False

    terms = _DEAL_CATEGORY_TERMS.get(category)
    if terms is None:
        return False

    normalized = f" {_normalize_title(title)} "
    if any(f" {term} " in normalized for term in _EXCLUDED_TERMS):
        return False
    return any(f" {term} " in normalized for term in terms)

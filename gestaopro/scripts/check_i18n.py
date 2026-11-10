#!/usr/bin/env python3
"""
check_i18n.py — Verifica integridade dos arquivos de tradução do GestãoPro.

Uso:
    python gestaopro/scripts/check_i18n.py

Sai com código 1 se:
- Algum JSON estiver com sintaxe inválida
- Alguma chave existente em pt-BR.json não existir nos outros idiomas
- Alguma chave extra (presente em outro idioma, mas não em pt-BR) for encontrada

Retorna 0 se tudo estiver correto.
"""
import json
import sys
from pathlib import Path

# Pasta raiz do workspace
ROOT = Path(__file__).resolve().parent.parent
I18N_DIR = ROOT / "frontend" / "i18n"
REFERENCE_LANG = "pt-BR"

COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "reset": "\033[0m",
}


def colored(text, color):
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def load_json(path: Path) -> dict | None:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(colored(f"  ERRO JSON em {path.name}: {e}", "red"))
        return None


def flatten(d: dict, prefix: str = "") -> set:
    """Retorna o conjunto de chaves no formato 'a.b.c'."""
    keys = set()
    for k, v in d.items():
        full = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys |= flatten(v, full)
        else:
            keys.add(full)
    return keys


def main() -> int:
    json_files = sorted(I18N_DIR.glob("*.json"))
    if not json_files:
        print(colored("ERRO: Nenhum arquivo JSON encontrado em frontend/i18n/", "red"))
        return 1

    print(f"Verificando {len(json_files)} arquivo(s) em {I18N_DIR.relative_to(ROOT)}\n")

    data: dict[str, dict] = {}
    for f in json_files:
        loaded = load_json(f)
        if loaded is None:
            return 1
        data[f.stem] = loaded

    if REFERENCE_LANG not in data:
        print(colored(f"ERRO: arquivo de referência '{REFERENCE_LANG}.json' não encontrado.", "red"))
        return 1

    ref_keys = flatten(data[REFERENCE_LANG])
    print(f"Referência ({REFERENCE_LANG}): {len(ref_keys)} chaves\n")

    errors = 0

    for lang, translations in data.items():
        if lang == REFERENCE_LANG:
            continue
        lang_keys = flatten(translations)

        missing = ref_keys - lang_keys
        extra   = lang_keys - ref_keys

        if missing or extra:
            print(colored(f"  [{lang}] ❌", "red"))
            for k in sorted(missing):
                print(colored(f"      FALTANDO: {k}", "red"))
            for k in sorted(extra):
                print(colored(f"      EXTRA:    {k}", "yellow"))
            errors += len(missing)
        else:
            print(colored(f"  [{lang}] ✓ ({len(lang_keys)} chaves)", "green"))

    print()
    if errors:
        print(colored(f"FALHOU: {errors} chave(s) ausente(s). Corrija os arquivos de tradução.", "red"))
        return 1

    print(colored("OK: Todos os arquivos de tradução estão completos.", "green"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

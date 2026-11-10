# Como adicionar um novo idioma ao GestãoPro

## Estrutura dos arquivos de tradução

Cada idioma é um arquivo JSON em `gestaopro/frontend/i18n/`:

```
frontend/i18n/
├── pt-BR.json   (Português Brasileiro — padrão)
├── en.json      (English)
├── es.json      (Español)
└── README.md    (este arquivo)
```

## Passos para incluir um novo idioma

1. Copie `pt-BR.json` para o novo arquivo, ex: `fr.json`
2. Traduza todos os valores (não altere as chaves)
3. Verifique se **todas** as chaves existem usando o script de validação:
   ```bash
   python gestaopro/scripts/check_i18n.py
   ```
4. No `frontend/js/layout.js`, adicione a opção no `<select>` de idioma:
   ```html
   <option value="fr">🇫🇷 FR</option>
   ```
5. No `frontend/js/i18n.js`, atualize `_detectLang()` se quiser detectar automaticamente.

## Estrutura das chaves

As chaves seguem o padrão `secao.subsecao` com suporte a `{{variavel}}` para interpolação:

```json
{
  "messages": {
    "saved": "Salvo com sucesso!",
    "loading": "Carregando...",
    "showing": "Exibindo {{from}}–{{to}} de {{total}} registros"
  }
}
```

## Erros de API

O backend retorna códigos de erro estáveis (ex.: `"DUPLICATE_EMAIL"`). 
O frontend traduz pelo caminho `errors.<CODIGO>` em cada JSON.

## Formatos regionais

Use sempre `Intl.NumberFormat` e `Intl.DateTimeFormat` passando o locale atual via `I18N.getLang()`. 
Nunca hardcode formatos de data ou moeda.

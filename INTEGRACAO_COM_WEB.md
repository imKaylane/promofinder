# PromoFinder Android — integração com a Web

O aplicativo Android utiliza o backend FastAPI do projeto Web como fonte de busca. A chamada Retrofit é feita para `GET /api/v1/products/search/live`, o mesmo endpoint usado pela interface React. Assim, as credenciais e chamadas ao Mercado Livre permanecem centralizadas no backend e não são armazenadas no APK.

## Executar localmente

1. Inicie o backend do projeto Web (`docker compose up --build`) e confirme `http://localhost:8000/health`.
2. Abra este projeto no Android Studio e sincronize o Gradle.
3. Execute no Android Emulator: o endereço padrão `http://10.0.2.2:8000/` aponta para a máquina host.
4. Para um aparelho físico, passe o IP local do computador em `PROMOFINDER_API_URL`, nas opções Gradle, por exemplo `-PPROMOFINDER_API_URL=http://192.168.0.10:8000/`. Libere a porta 8000 no firewall, se necessário.

## Publicação

Configure `PROMOFINDER_API_URL` para o endereço HTTPS público do backend. Desative tráfego HTTP não criptografado no Manifest antes de publicar. O valor padrão HTTP existe somente para desenvolvimento local.

## Escopo desta integração

A busca de produtos está conectada ao backend compartilhado. Favoritos e alertas continuam usando o armazenamento local existente no aplicativo; a API Web tem endpoints próprios para esses recursos, mas ainda não existe neste app uma camada de autenticação/sincronização compatível com os contratos reais do backend.

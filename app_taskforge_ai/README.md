# TaskForge-AI Flutter Frontend

## Rodando no navegador (Edge, Chrome, etc.)

1. Instale as dependências:
   ```powershell
   flutter pub get
   ```
2. Execute para web (Edge):
   ```powershell
   flutter run -d edge
   ```
   Ou para Chrome:
   ```powershell
   flutter run -d chrome
   ```
   Você pode listar dispositivos web disponíveis com:
   ```powershell
   flutter devices
   ```

3. O backend deve estar rodando em `http://localhost:8000`.
   - O frontend já está configurado para usar esse endereço em web (veja `main.dart` e ajuste se necessário).

## Observações
- O backend já aceita CORS de qualquer origem (Edge, Chrome, etc.).
- Se rodar em outro IP/porta, ajuste o `baseUrl` em `lib/main.dart`.
- Para produção, configure variáveis de ambiente ou use um arquivo `.env` para o endpoint do backend.

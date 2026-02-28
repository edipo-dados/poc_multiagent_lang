# Instalação do pgvector no PostgreSQL 18 (Windows)

## Opção 1: Baixar binário pré-compilado (RECOMENDADO)

1. Acesse: https://github.com/pgvector/pgvector/releases
2. Baixe o arquivo para PostgreSQL 18 Windows: `pgvector-v0.7.4-pg18-windows-x64.zip`
3. Extraia o arquivo ZIP
4. Copie os arquivos para a pasta do PostgreSQL:
   - `vector.dll` → `C:\Program Files\PostgreSQL\18\lib\`
   - `vector.control` → `C:\Program Files\PostgreSQL\18\share\extension\`
   - `vector--*.sql` → `C:\Program Files\PostgreSQL\18\share\extension\`

5. Reinicie o serviço PostgreSQL:
   ```powershell
   Restart-Service postgresql-x64-18
   ```

6. Execute novamente: `.\setup-db-manual.bat`

## Opção 2: Usar Docker (MAIS FÁCIL)

Se a instalação manual for complicada, use Docker com a imagem que já tem pgvector:

```powershell
docker compose up -d db
```

Depois atualize o .env:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/regulatory_ai
```

## Verificar instalação

Após instalar, verifique se funcionou:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d regulatory_ai -c "CREATE EXTENSION vector;"
```

Se não mostrar erro, está funcionando!

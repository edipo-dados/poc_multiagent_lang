# Setup PostgreSQL para Regulatory AI POC

Write-Host "========================================"
Write-Host "Setup PostgreSQL para Regulatory AI POC"
Write-Host "========================================"
Write-Host ""

# Configurações
$PGHOST = "localhost"
$PGPORT = "5432"
$PGUSER = "postgres"

# Solicitar senha
$SecurePassword = Read-Host "Digite a senha do usuário postgres" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecurePassword)
$PGPASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

Write-Host ""
Write-Host "Criando banco de dados e extensão pgvector..."

# Criar banco de dados
$env:PGPASSWORD = $PGPASSWORD
& psql -U $PGUSER -h $PGHOST -p $PGPORT -c "CREATE DATABASE regulatory_ai;" 2>$null

# Conectar ao banco e criar extensão
& psql -U $PGUSER -h $PGHOST -p $PGPORT -d regulatory_ai -c "CREATE EXTENSION IF NOT EXISTS vector;"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Banco de dados configurado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Criando arquivo .env..."
    
    $envContent = @"
DATABASE_URL=postgresql+asyncpg://$PGUSER`:$PGPASSWORD@$PGHOST`:$PGPORT/regulatory_ai
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    
    Write-Host "✓ Arquivo .env criado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:"
    Write-Host "1. Execute: python backend/scripts/init_embeddings.py"
    Write-Host "2. Execute: .\run-backend-postgres.bat"
    Write-Host "3. Execute: .\run-frontend.bat"
} else {
    Write-Host ""
    Write-Host "✗ Erro ao configurar banco de dados" -ForegroundColor Red
    Write-Host "Verifique se o PostgreSQL está rodando e se a senha está correta"
}

# Limpar senha da memória
Remove-Variable PGPASSWORD
$env:PGPASSWORD = $null

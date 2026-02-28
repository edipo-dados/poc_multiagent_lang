Write-Host "Setup PostgreSQL para Regulatory AI POC"
Write-Host ""

$PGUSER = "postgres"
$PGPASSWORD = Read-Host "Digite a senha do postgres"

Write-Host ""
Write-Host "Criando banco de dados..."

$env:PGPASSWORD = $PGPASSWORD
psql -U $PGUSER -h localhost -c "CREATE DATABASE regulatory_ai;" 2>$null
psql -U $PGUSER -h localhost -d regulatory_ai -c "CREATE EXTENSION IF NOT EXISTS vector;"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Banco configurado com sucesso!"
    Write-Host ""
    Write-Host "Criando arquivo .env..."
    
    "DATABASE_URL=postgresql+asyncpg://$PGUSER`:$PGPASSWORD@localhost:5432/regulatory_ai" | Out-File -FilePath ".env" -Encoding ASCII
    "LLM_PROVIDER=ollama" | Out-File -FilePath ".env" -Append -Encoding ASCII
    "OLLAMA_BASE_URL=http://localhost:11434" | Out-File -FilePath ".env" -Append -Encoding ASCII
    "OLLAMA_MODEL=llama2" | Out-File -FilePath ".env" -Append -Encoding ASCII
    
    Write-Host "Arquivo .env criado!"
} else {
    Write-Host "Erro ao configurar banco"
}

$env:PGPASSWORD = $null

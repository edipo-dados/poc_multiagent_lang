# 🤖 Configurar LLM para a Aplicação

A aplicação precisa de um LLM (Large Language Model) para funcionar. Você tem 3 opções:

## Opção 1: Ollama (Local - Gratuito) ⭐ Recomendado para testes

### Instalar Ollama:
1. Baixe: https://ollama.ai/download
2. Instale o executável
3. Abra um terminal e rode:
```bash
ollama pull llama2
```

### Iniciar Ollama:
```bash
ollama serve
```

Pronto! A aplicação vai conectar automaticamente em `localhost:11434`

---

## Opção 2: OpenAI API (Pago - Mais Poderoso)

### Configurar:
1. Obtenha sua API key em: https://platform.openai.com/api-keys
2. Configure a variável de ambiente:

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sua-api-key-aqui"
$env:LLM_PROVIDER="openai"
```

3. Reinicie o backend

---

## Opção 3: Anthropic Claude (Pago - Alternativa)

### Configurar:
1. Obtenha sua API key em: https://console.anthropic.com/
2. Configure a variável de ambiente:

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="sua-api-key-aqui"
$env:LLM_PROVIDER="anthropic"
```

3. Reinicie o backend

---

## Verificar Configuração

Após configurar, teste o health check:
```bash
curl http://localhost:8000/health
```

## Custos Estimados

| Provedor | Custo por 1M tokens | Recomendação |
|----------|---------------------|--------------|
| Ollama | Gratuito | ✅ Melhor para desenvolvimento |
| OpenAI GPT-4 | ~$30 | Para produção |
| OpenAI GPT-3.5 | ~$2 | Bom custo-benefício |
| Anthropic Claude | ~$15 | Alternativa ao GPT-4 |

## Próximos Passos

1. Escolha uma opção acima
2. Configure conforme instruções
3. Reinicie o backend
4. Teste a aplicação novamente!

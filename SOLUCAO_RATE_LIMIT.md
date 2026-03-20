# Solução para Rate Limit da API Groq

## Problema
Erro 429: Limite de 100.000 tokens/dia atingido no modelo `llama-3.3-70b-versatile`.

## Soluções Imediatas

### 1. Trocar para modelo mais leve (RECOMENDADO)
Edite seu arquivo `.env`:

```env
GROQ_MODEL=llama-3.1-8b-instant
```

**Vantagens:**
- ✅ 10x mais rápido
- ✅ Consome menos tokens
- ✅ Mantém qualidade para consultas objetivas
- ✅ Ideal para produção

### 2. Usar múltiplas chaves Groq (Portfólio)
Crie múltiplas contas gratuitas Groq e alterne entre elas:

```env
GROQ_API_KEY=key1,key2,key3
```

Implemente rotação no código (próximo passo se necessário).

### 3. Aguardar reset (temporário)
O limite reseta diariamente. Aguarde o tempo indicado no erro (ex: 7m22s).

---

## Para seu Portfólio

### Opção A: Manter Groq com modelo leve
```env
GROQ_MODEL=llama-3.1-8b-instant
```
- Grátis
- Rápido
- Suficiente para demonstração

### Opção B: Adicionar OpenAI como fallback
```python
# Adicionar no .env
OPENAI_API_KEY=sua_chave_openai
USE_OPENAI_FALLBACK=true
```

### Opção C: Cache de respostas
Implementar cache local para perguntas repetidas (próximo passo se necessário).

---

## Recomendação Final

**Para portfólio profissional:**
1. Troque para `llama-3.1-8b-instant` no `.env`
2. Adicione nota no README explicando a escolha (eficiência vs custo)
3. Demonstre consciência de otimização de recursos

**Código para README:**
```markdown
## Otimizações de Performance

- **Modelo LLM**: Llama 3.1 8B Instant (Groq)
  - Escolhido por balancear velocidade, custo e qualidade
  - 10x mais rápido que modelos maiores
  - Ideal para consultas objetivas de dados estruturados
```

---

## Próximos Passos (se necessário)

1. Implementar rotação de chaves API
2. Adicionar sistema de cache
3. Implementar fallback para OpenAI
4. Adicionar rate limiting no frontend

Deseja que eu implemente alguma dessas soluções?

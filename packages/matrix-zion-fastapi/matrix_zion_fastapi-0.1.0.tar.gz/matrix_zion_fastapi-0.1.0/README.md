# Matrix Zion FastAPI Plugin

[![PyPI version](https://badge.fury.io/py/matrix-zion-fastapi.svg)](https://badge.fury.io/py/matrix-zion-fastapi)
[![Python Versions](https://img.shields.io/pypi/pyversions/matrix-zion-fastapi.svg)](https://pypi.org/project/matrix-zion-fastapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Plugin FastAPI para o Matrix Zion Framework, fornecendo capacidades de API REST.

## 🚀 Características

- **FastAPI Integration**: Integração nativa com FastAPI
- **Auto-routing**: Descoberta automática de rotas
- **Middleware Support**: Suporte para middlewares customizados
- **OpenAPI**: Documentação automática via Swagger/OpenAPI
- **Auto-descoberta**: Registra-se automaticamente no framework Matrix

## 📦 Instalação

```bash
pip install matrix-zion-fastapi
```

**Nota**: Este plugin requer o `matrix-zion` como dependência base.

## 🎯 Uso Básico

```python
from matrix.zion import Zion

# Inicializar o framework
app = Zion()

# O plugin FastAPI será automaticamente descoberto e carregado
app.discover_plugins()

# Usar funcionalidades FastAPI através do plugin
fastapi_plugin = app.get_plugin('fastapi')
api_app = fastapi_plugin.get_app()

@api_app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Executar servidor
fastapi_plugin.run(host="0.0.0.0", port=8000)
```

## ⚙️ Configuração

Configure o servidor através de variáveis de ambiente:

```bash
export FASTAPI_HOST=0.0.0.0
export FASTAPI_PORT=8000
export FASTAPI_DEBUG=true
```

## 🔧 Dependências

- `matrix-zion>=0.1.0`
- `fastapi>=0.100.0`
- `uvicorn>=0.20.0`

## 📚 Documentação

Para documentação completa, visite: [GitHub Repository](https://github.com/tuyoshivinicius/python-microservice-v2)

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

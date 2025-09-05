# Matrix Zion Framework

[![PyPI version](https://badge.fury.io/py/matrix-zion.svg)](https://badge.fury.io/py/matrix-zion)
[![Python Versions](https://img.shields.io/pypi/pyversions/matrix-zion.svg)](https://pypi.org/project/matrix-zion/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Framework modular para microserviços Python com arquitetura de plugins extensível.

## 🚀 Características

- **Arquitetura de Plugins**: Sistema extensível baseado em entry points
- **Modular**: Core minimalista com funcionalidades via plugins
- **Type Safe**: Suporte completo ao sistema de tipos do Python
- **Configurável**: Configuração via variáveis de ambiente e arquivos
- **Testável**: Projetado para facilitar testes unitários e de integração

## 📦 Instalação

```bash
pip install matrix-zion
```

## 🎯 Uso Básico

```python
from matrix.zion import Zion

# Inicializar o framework
app = Zion()

# O framework automaticamente descobre e carrega plugins instalados
app.discover_plugins()

# Executar a aplicação
app.run()
```

## 🔌 Plugins Disponíveis

- **matrix-zion-aws**: Integração com serviços AWS (DynamoDB, S3, SQS)
- **matrix-zion-fastapi**: Suporte para APIs REST com FastAPI

## 📚 Documentação

Para documentação completa, visite: [GitHub Repository](https://github.com/tuyoshivinicius/python-microservice-v2)

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia nosso guia de contribuição antes de submeter PRs.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

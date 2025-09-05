# Matrix Zion AWS Plugin

[![PyPI version](https://badge.fury.io/py/matrix-zion-aws.svg)](https://badge.fury.io/py/matrix-zion-aws)
[![Python Versions](https://img.shields.io/pypi/pyversions/matrix-zion-aws.svg)](https://pypi.org/project/matrix-zion-aws/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Plugin AWS para o Matrix Zion Framework, fornecendo integração com serviços AWS.

## 🚀 Características

- **DynamoDB**: Operações simplificadas com DynamoDB
- **S3**: Upload e download de arquivos
- **SQS**: Mensageria com filas SQS
- **SNS**: Notificações via SNS
- **Auto-descoberta**: Registra-se automaticamente no framework Matrix

## 📦 Instalação

```bash
pip install matrix-zion-aws
```

**Nota**: Este plugin requer o `matrix-zion` como dependência base.

## 🎯 Uso Básico

```python
from matrix.zion import Zion

# Inicializar o framework
app = Zion()

# O plugin AWS será automaticamente descoberto e carregado
app.discover_plugins()

# Usar funcionalidades AWS através do plugin
aws_plugin = app.get_plugin('aws')
dynamodb = aws_plugin.get_dynamodb_client()
```

## ⚙️ Configuração

Configure suas credenciais AWS através de variáveis de ambiente:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## 🔧 Dependências

- `matrix-zion>=0.1.0`
- `boto3>=1.34.0`

## 📚 Documentação

Para documentação completa, visite: [GitHub Repository](https://github.com/tuyoshivinicius/python-microservice-v2)

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

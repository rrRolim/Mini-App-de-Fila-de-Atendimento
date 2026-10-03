# Mini App de Fila de Atendimento

Aplicação web desenvolvida com **Python, Flask e SQLite** para gerenciamento de uma fila de atendimento.

## Funcionalidades

### Obrigatórias
- Cadastro de clientes na fila;
- Visualização da fila;
- Chamada do próximo cliente;
- Ordem de atendimento baseada em FIFO;
- Alteração de status:
  - Aguardando
  - Em Atendimento
  - Concluído
- Cancelamento de atendimento.

### Bônus implementados
- **Prioridade:** Normal ou Preferencial;
- **Histórico:** atendimentos concluídos e cancelados;
- **Atualização automática:** a página verifica alterações na fila a cada 5 minutos 
- Contadores de clientes aguardando, em atendimento, concluídos e cancelados;
- Interface responsiva.

## Regra da fila

A fila respeita a ordem de chegada dentro de cada nível de prioridade:

1. Clientes **Preferenciais**;
2. Clientes **Normais**;
3. Dentro de cada grupo, permanece a ordem de chegada.

Exemplo:

- João — Normal
- Maria — Normal
- Pedro — Preferencial
- Ana — Preferencial

A ordem de chamada será:

**Pedro → Ana → João → Maria**

## Tecnologias

- Python 3
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript

## Como executar

### 1. Clonar o projeto

```bash
git clone https://github.com/rrRolim/Mini-App-de-Fila-de-Atendimento.git
cd Mini-App-de-Fila-de-Atendimento
```

### 2. Criar ambiente virtual

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Executar

```bash
python app.py
```

O sistema ficará disponível em:

`http://127.0.0.1:5000`

O arquivo `fila.db` é criado automaticamente na primeira execução.

## Estrutura

```text
mini-fila-atendimento/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    └── style.css
```

## API

Também existe um endpoint para consultar a fila em JSON:

```text
GET /api/fila
```

## Autor

Projeto desenvolvido para o desafio de Mini App de Fila de Atendimento.

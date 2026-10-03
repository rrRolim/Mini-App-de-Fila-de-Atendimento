from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chave-dev-fila-atendimento"
DATABASE = "fila.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            prioridade TEXT NOT NULL DEFAULT 'Normal',
            status TEXT NOT NULL DEFAULT 'Aguardando',
            criado_em TEXT NOT NULL,
            chamado_em TEXT,
            concluido_em TEXT,
            cancelado_em TEXT
        )
    """)
    conn.commit()
    conn.close()


def agora():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


@app.route("/")
def index():
    conn = get_db()
    fila = conn.execute("""
        SELECT * FROM atendimentos
        WHERE status IN ('Aguardando', 'Em Atendimento')
        ORDER BY
            CASE WHEN status = 'Em Atendimento' THEN 0 ELSE 1 END,
            CASE WHEN prioridade = 'Preferencial' THEN 0 ELSE 1 END,
            id ASC
    """).fetchall()

    aguardando = conn.execute(
        "SELECT COUNT(*) FROM atendimentos WHERE status = 'Aguardando'"
    ).fetchone()[0]
    em_atendimento = conn.execute(
        "SELECT COUNT(*) FROM atendimentos WHERE status = 'Em Atendimento'"
    ).fetchone()[0]
    concluidos = conn.execute(
        "SELECT COUNT(*) FROM atendimentos WHERE status = 'Concluído'"
    ).fetchone()[0]
    cancelados = conn.execute(
        "SELECT COUNT(*) FROM atendimentos WHERE status = 'Cancelado'"
    ).fetchone()[0]

    historico = conn.execute("""
        SELECT * FROM atendimentos
        WHERE status IN ('Concluído', 'Cancelado')
        ORDER BY id DESC
        LIMIT 30
    """).fetchall()
    conn.close()

    return render_template(
        "index.html",
        fila=fila,
        historico=historico,
        aguardando=aguardando,
        em_atendimento=em_atendimento,
        concluidos=concluidos,
        cancelados=cancelados
    )


@app.post("/cadastrar")
def cadastrar():
    nome = request.form.get("nome", "").strip()
    prioridade = request.form.get("prioridade", "Normal")

    if not nome:
        flash("Informe o nome do cliente.", "erro")
        return redirect(url_for("index"))

    if prioridade not in ("Normal", "Preferencial"):
        prioridade = "Normal"

    conn = get_db()
    conn.execute(
        "INSERT INTO atendimentos (nome, prioridade, status, criado_em) VALUES (?, ?, 'Aguardando', ?)",
        (nome, prioridade, agora())
    )
    conn.commit()
    conn.close()

    flash(f"{nome} foi adicionado à fila.", "sucesso")
    return redirect(url_for("index"))


@app.post("/chamar-proximo")
def chamar_proximo():
    conn = get_db()

    atual = conn.execute(
        "SELECT id FROM atendimentos WHERE status = 'Em Atendimento' LIMIT 1"
    ).fetchone()

    if atual:
        flash("Já existe um cliente em atendimento.", "erro")
        conn.close()
        return redirect(url_for("index"))

    proximo = conn.execute("""
        SELECT id, nome FROM atendimentos
        WHERE status = 'Aguardando'
        ORDER BY
            CASE WHEN prioridade = 'Preferencial' THEN 0 ELSE 1 END,
            id ASC
        LIMIT 1
    """).fetchone()

    if not proximo:
        flash("Não há clientes aguardando.", "erro")
        conn.close()
        return redirect(url_for("index"))

    conn.execute(
        "UPDATE atendimentos SET status = 'Em Atendimento', chamado_em = ? WHERE id = ?",
        (agora(), proximo["id"])
    )
    conn.commit()
    conn.close()

    flash(f"Próximo cliente: {proximo['nome']}.", "sucesso")
    return redirect(url_for("index"))


@app.post("/status/<int:id>")
def alterar_status(id):
    novo_status = request.form.get("status")
    permitidos = ("Aguardando", "Em Atendimento", "Concluído")

    if novo_status not in permitidos:
        flash("Status inválido.", "erro")
        return redirect(url_for("index"))

    conn = get_db()
    atendimento = conn.execute(
        "SELECT * FROM atendimentos WHERE id = ?", (id,)
    ).fetchone()

    if not atendimento:
        conn.close()
        flash("Atendimento não encontrado.", "erro")
        return redirect(url_for("index"))

    if novo_status == "Em Atendimento":
        outro = conn.execute(
            "SELECT id FROM atendimentos WHERE status = 'Em Atendimento' AND id != ?",
            (id,)
        ).fetchone()
        if outro:
            conn.close()
            flash("Já existe outro cliente em atendimento.", "erro")
            return redirect(url_for("index"))

    chamado_em = atendimento["chamado_em"]
    concluido_em = atendimento["concluido_em"]

    if novo_status == "Em Atendimento" and not chamado_em:
        chamado_em = agora()
    if novo_status == "Concluído":
        concluido_em = agora()

    conn.execute("""
        UPDATE atendimentos
        SET status = ?, chamado_em = ?, concluido_em = ?
        WHERE id = ?
    """, (novo_status, chamado_em, concluido_em, id))
    conn.commit()
    conn.close()

    flash("Status atualizado.", "sucesso")
    return redirect(url_for("index"))


@app.post("/cancelar/<int:id>")
def cancelar(id):
    conn = get_db()
    atendimento = conn.execute(
        "SELECT id, nome, status FROM atendimentos WHERE id = ?", (id,)
    ).fetchone()

    if not atendimento:
        conn.close()
        flash("Atendimento não encontrado.", "erro")
        return redirect(url_for("index"))

    if atendimento["status"] == "Concluído":
        conn.close()
        flash("Um atendimento concluído não pode ser cancelado.", "erro")
        return redirect(url_for("index"))

    conn.execute(
        "UPDATE atendimentos SET status = 'Cancelado', cancelado_em = ? WHERE id = ?",
        (agora(), id)
    )
    conn.commit()
    conn.close()

    flash(f"Atendimento de {atendimento['nome']} cancelado.", "sucesso")
    return redirect(url_for("index"))


@app.get("/api/fila")
def api_fila():
    conn = get_db()
    fila = conn.execute("""
        SELECT id, nome, prioridade, status, criado_em, chamado_em
        FROM atendimentos
        WHERE status IN ('Aguardando', 'Em Atendimento')
        ORDER BY
            CASE WHEN status = 'Em Atendimento' THEN 0 ELSE 1 END,
            CASE WHEN prioridade = 'Preferencial' THEN 0 ELSE 1 END,
            id ASC
    """).fetchall()
    conn.close()

    return jsonify([dict(item) for item in fila])


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw, ImageFont
import json
import os
import io

st.set_page_config(page_title="Editor Polaroid A4", layout="wide")

# ==== Configurações ====
ARQUIVO_DADOS = "dados.json"
PASTA_IMAGENS = "imagens"

os.makedirs(PASTA_IMAGENS, exist_ok=True)

# Carregar dados
if os.path.exists(ARQUIVO_DADOS):
    with open(ARQUIVO_DADOS, "r") as f:
        dados = json.load(f)
else:
    dados = {"fotos": []}

def salvar_dados():
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(dados, f, indent=4)

st.title("📸 Editor Polaroid - A4")

# ===== Canvas A4 =====
A4_WIDTH = 595  # px ~ 210mm
A4_HEIGHT = 842  # px ~ 297mm

st.subheader("Arraste e ajuste suas fotos dentro dos quadrados polaroid")

uploaded_files = st.file_uploader(
    "Escolha suas fotos (máx 15):",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# Limitar a 15 fotos
if uploaded_files:
    uploaded_files = uploaded_files[:15]

# Posições iniciais para 15 polaroids
polaroid_width = 100
polaroid_height = 120
margem = 10
posicoes = []
x, y = margem, margem
for i in range(15):
    posicoes.append({"x": x, "y": y, "width": polaroid_width, "height": polaroid_height})
    x += polaroid_width + margem
    if x + polaroid_width > A4_WIDTH:
        x = margem
        y += polaroid_height + margem

# Criar canvas
canvas_result = st_canvas(
    fill_color="#FFFFFF",
    stroke_width=1,
    stroke_color="#000000",
    background_color="#f0f0f0",
    width=A4_WIDTH,
    height=A4_HEIGHT,
    drawing_mode="rect",
    key="canvas",
    update_streamlit=True,
)

# Processar upload
for i, file in enumerate(uploaded_files):
    if i >= 15:
        break
    img = Image.open(file)
    img.thumbnail((polaroid_width-10, polaroid_height-30))
    nome_arquivo = f"{file.name}"
    dados["fotos"].append({
        "nome_arquivo": nome_arquivo,
        "x": posicoes[i]["x"],
        "y": posicoes[i]["y"],
        "width": img.width,
        "height": img.height,
        "legenda": ""
    })
    img.save(os.path.join(PASTA_IMAGENS, nome_arquivo))

salvar_dados()

# Adicionar legenda para cada foto
st.subheader("Adicionar legenda às fotos")
for i, foto in enumerate(dados["fotos"]):
    legenda = st.text_input(f"Legenda da foto {foto['nome_arquivo']}", value=foto.get("legenda",""), key=f"legenda_{i}")
    dados["fotos"][i]["legenda"] = legenda
salvar_dados()

# Gerar PDF final
if st.button("📄 Gerar PDF"):
    pdf_img = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(pdf_img)
    font = ImageFont.load_default()
    for foto in dados["fotos"]:
        caminho = os.path.join(PASTA_IMAGENS, foto["nome_arquivo"])
        if os.path.exists(caminho):
            img = Image.open(caminho)
            # Criar polaroid
            borda = Image.new("RGB", (polaroid_width, polaroid_height), (255, 255, 255))
            borda.paste(img, (5,5))
            pdf_img.paste(borda, (foto["x"], foto["y"]))
            draw.text((foto["x"]+5, foto["y"]+img.height+5), foto["legenda"], fill="black", font=font)
    buf = io.BytesIO()
    pdf_img.save(buf, format="PNG")
    buf.seek(0)
    st.download_button("📥 Baixar PDF", data=buf, file_name="montagem_polaroid.pdf")

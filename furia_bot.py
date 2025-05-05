from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters,
)

# ===== Token do bot =====
TOKEN = "7974386602:AAGePVQPN52_6BfToAAXh5rZfOyankROFRg"

# ===== Perguntas do quiz =====
quiz_perguntas = [
    {"pergunta": "Em que ano a FURIA foi fundada?", "opcoes": ["2015", "2017", "2019", "2020"], "correta": "2017"},
    {"pergunta": "Qual jogador é conhecido por seu estilo agressivo e uso frequente de AWP?", "opcoes": ["yuurih", "KSCERATO", "fallen", "chelo"], "correta": "yuurih"},
    {"pergunta": "Qual foi a melhor colocação da FURIA em um Major até agora?", "opcoes": ["Campeã", "Vice-campeã", "Semifinal", "Quartas de final"], "correta": "Semifinal"},
    {"pergunta": "Qual desses é um patrocinador histórico da FURIA?", "opcoes": ["Red Bull", "Nike", "Betway", "Gucci"], "correta": "Nike"},
    {"pergunta": "Qual é o nome do centro de treinamento da FURIA nos EUA?", "opcoes": ["FURIA Core", "FURIA Arena", "FURIA House", "FURIA Training Center"], "correta": "FURIA Training Center"}
]

# ===== Armazenar progresso do quiz =====
user_data = {}

def gerar_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Partidas", callback_data="jogos"),
         InlineKeyboardButton("📈 Ranking", callback_data="ranking")],
        [InlineKeyboardButton("🧠 Estatísticas", callback_data="estatisticas"),
         InlineKeyboardButton("🕹️ Quiz FURIOSO", callback_data="quiz")],
        [InlineKeyboardButton("🔥 Mandar Apoio!", callback_data="apoio")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("/start chamado")

    try:
        with open("imagens\\channels4_profile.jpg", "rb") as img:
            await update.message.reply_photo(
                photo=img,
                caption=(
                    "🇧🇷 *Bem-vindo ao FURIABOT!* 🧠\n"
                    "Sou seu assistente oficial da torcida da *FURIA CS*.\n\n"
                    "👉 Acesse o [site oficial da FURIA](https://www.furia.gg/) para informações e compras."
                ),
                parse_mode="Markdown"
            )
    except FileNotFoundError:
        await update.message.reply_text(
            "🇧🇷 *Bem-vindo ao FURIABOT!* 🧠\n"
            "Sou seu assistente oficial da torcida da *FURIA CS*.\n\n"
            "👉 Acesse o [site oficial da FURIA](https://www.furia.gg/) para informações e compras.",
            parse_mode="Markdown"
        )

    await update.message.reply_text("👇 Menu de opções:", reply_markup=gerar_menu())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("quiz_"):
        opcao = query.data.split("quiz_")[1]
        user_id = query.from_user.id
        progresso = user_data.get(user_id, {"pontuacao": 0, "indice": 0})
        pergunta = quiz_perguntas[progresso["indice"] - 1]

        correta = pergunta["correta"]
        if opcao == correta:
            progresso["pontuacao"] += 1
            resposta = f"✅ Resposta correta! ({opcao})"
        else:
            resposta = f"❌ Resposta errada! Você escolheu {opcao}. A correta era: {correta}"

        if progresso["indice"] < len(quiz_perguntas):
            user_data[user_id] = progresso
            await query.edit_message_text(resposta)
            await enviar_pergunta(update, context, user_id)
        else:
            total = progresso["pontuacao"]
            await query.edit_message_text(
                text=f"{resposta}\n\n🎉 Fim do quiz! Você acertou {total} de {len(quiz_perguntas)} perguntas.",
                reply_markup=gerar_menu()
            )
            user_data.pop(user_id, None)
        return

    elif query.data == "quiz":
        user_id = query.from_user.id
        user_data[user_id] = {"pontuacao": 0, "indice": 0}
        await query.edit_message_text("🧠 Iniciando o quiz da FURIA!")
        await enviar_pergunta(update, context, user_id)
        return

    # Respostas para outros botões
    respostas = {
        "jogos": "🎮 Próximas partidas da FURIA:\n\nFURIA vs NAVI - 05/05 - 16:00\nFURIA vs Vitality - 07/05 - 18:00",
        "ranking": "📈 Ranking atual ESL Pro League:\n1. G2\n2. Vitality\n3. NAVI\n4. FURIA",
        "estatisticas": "🧠 Estatísticas dos jogadores:\n- KSCERATO: 1.22 K/D\n- yuurih: 1.15 K/D\n- arT: 0.98 K/D",
        "apoio": "🔥 Envie sua mensagem de apoio! [Funcionalidade simulada]"
    }

    await query.edit_message_text(
        text=respostas.get(query.data, "Comando desconhecido."),
        reply_markup=gerar_menu()
    )


async def enviar_pergunta(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    progresso = user_data[user_id]
    indice = progresso["indice"]
    if indice >= len(quiz_perguntas):
        return

    pergunta = quiz_perguntas[indice]
    progresso["indice"] += 1
    user_data[user_id] = progresso

    keyboard = [[InlineKeyboardButton(opcao, callback_data=f"quiz_{opcao}")]
                for opcao in pergunta["opcoes"]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=user_id,
        text=f"{indice + 1}. {pergunta['pergunta']}",
        reply_markup=reply_markup
    )

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /start ou clique no botão abaixo:", reply_markup=gerar_menu())

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
    print("✅ Bot rodando... Vá até o Telegram e digite /start.")
    app.run_polling()

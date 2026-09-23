FUNNEL_MESSAGES = {
    "START": (
        "Oiiie, {nome}! 😈🔥\n\n"
        "Acho que você vai amar o que uma ALBINA tem para mostrar "
        "para você... 🤭🤍\n\n"
        "No meu VIP tem muito conteúdo exclusivo para deixar sua "
        "imaginação bem longe do controle 😏💋🔥\n\n"
        "E se quiser algo ainda mais especial... também faço chamada "
        "👀📲❤️‍🔥\n\n"
        "Quer entrar? 😈👇\n"
        "Escolha seu plano VIP: 💎🔥"
    ),
    "FOLLOWUP_5MIN": (
        "😈🔥 Corninho... hoje eu fui dividida com um amigo dele 👀\n\n"
        "Vem ver o que rolou... 🤭❤️‍🔥\n\n"
        "O vídeo 3 está te esperando. 😏🔥\n\n"
        "Ainda quer entrar no meu VIP? 💎👇"
    ),
    "FOLLOWUP_10MIN": (
        "😈🔥 Esse vídeo é especial...\n\n"
        "Foi a primeira vez que eu fiz isso. 👀❤️‍🔥\n\n"
        "Vem me ver dando meu cuzinho. 😏🔥"
    ),
}


def get_funnel_message(stage: str, first_name: str | None) -> str:
    message = FUNNEL_MESSAGES.get(stage)

    if message is None:
        raise ValueError(f"Etapa de funil inválida: {stage}")

    name = first_name.strip() if first_name else "lindo"

    return message.format(nome=name)
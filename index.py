import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from Menu import Menu
from MenuPreguntasNuevas import MenuPreguntasNuevas
from database import connect_database

load_dotenv()

TOKEN = os.getenv('TOKEN_DISCORD')

nltk.download('stopwords')
nltk.download('punkt')
mybd = connect_database()

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)  # Prefijo del bot


stop_words = set(stopwords.words('spanish'))


def process_question(question, db_data):
    # Tokenizamos la pregunta y eliminamos las stop words
    tokens = word_tokenize(question.lower())
    filtered_tokens = [token for token in tokens if token not in stop_words]

    # Comparamos la pregunta filtrada con cada pregunta de nuestro diccionario
    max_similarity = 0
    best_match = []
    for id, question, answer in db_data:
        similarity = sum(
            [1 for token in filtered_tokens if token in question.lower()])
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = [id, answer]

    # Si encontramos una pregunta similar, devolvemos su respuesta
    if max_similarity > 0:
        return best_match

    # Si no encontramos ninguna pregunta similar, devolvemos una respuesta por defecto
    return ['Lo siento, no tengo una respuesta para esa pregunta.', None]


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command(name="pregunta")
async def faq(ctx, *, question):
    """
    Responde una pregunta frecuente utilizando NLTK para procesamiento de lenguaje natural.
    """

    # Obtenemos las preguntas y respuestas almacenadas en la base de datos
    cursor = mybd.cursor()

    cursor.execute("""
        SELECT id,question, answer
        FROM support_chatbot
    """)
    db_data = cursor.fetchall()

    result = process_question(question, db_data)
    if result[1]:
        # Agrega un mensaje de saludo y despedida
        await ctx.send(f'Hola {ctx.author.mention}, aquí está la respuesta a tu pregunta:')

        # Formatea las respuestas para que sean más fáciles de leer
        formatted_answers = '\n\n'.join(
            [f'{i}. {a}' for i, a in enumerate([result[1]], 1)])
        await ctx.send(f'```{formatted_answers}```')

        view = Menu(db_data, result[0], mybd)
        await ctx.reply("Te sirvio la respuesta?", view=view)

        await ctx.send('¿Te puedo ayudar con algo más?')
    else:
        await ctx.send('Lo siento, no tengo una respuesta para esa pregunta por favor comuniquese con el admin del canal.')
        view = MenuPreguntasNuevas(question, mybd)
        await ctx.reply("Queres que analizemos esta pregunta para el futuro?", view=view)

    cursor.close()


@bot.command(name="deprecadas")
async def faq(ctx):
    cursor = mybd.cursor()
    cursor.execute("""
        SELECT id, answer, helpful_responses, unhelpful_responses
        FROM support_chatbot
        WHERE state_answer = 'inappropriate'
    """)
    rows = cursor.fetchall()
    if not rows:
        await ctx.send("No se encontraron respuestas inapropiadas.")
        return

    formatted_answers = '\n\n'.join(
        [f'{i}. \n -Respuesta: {row[1]} \n -ID: {row[0]} \n -Porcentaje de respuesta util: {row[2]/(row[2]+row[3]):.2%} \n -Porcentaje de respuesta no util: {row[3]/(row[2]+row[3]):.2%}' for i, row in enumerate(rows, 1)])
    message = f"Respuestas inapropiadas:\n{formatted_answers}"

    await ctx.send(f'```{message}```')
    cursor.close()


@bot.command(name="analizar")
async def faq(ctx):
    cursor = mybd.cursor()
    cursor.execute("""
        SELECT *
        FROM questions
    """)
    rows = cursor.fetchall()
    if not rows:
        await ctx.send("No se encontraron respuestas para analizar.")
        return

    formatted_answers = '\n\n'.join(
        [f'{i}. \n -ID: {row[0]} \n -Pregunta: {row[1]}' for i, row in enumerate(rows, 1)])
    message = f"Respuestas para analizar:\n{formatted_answers}"

    await ctx.send(f'```{message}```')
    cursor.close()

bot.run(TOKEN)

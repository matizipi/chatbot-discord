import discord


class MenuPreguntasNuevas(discord.ui.View):
    def __init__(self, question, db):
        super().__init__()
        self.value = None
        self.db = db
        self.question = question

    @discord.ui.button(label="Si", style=discord.ButtonStyle.green)
    async def menu1(self,  interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Se a guardado la pregunta, se analizara para ponerle una respuesta adecuada")
        self.value = False
        self.stop()
        await self.interaction_callback()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def menu2(self,  interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("No se tendra en cuenta esta pregunta para analizar")
        self.value = False
        self.stop()

    async def interaction_callback(self):

        cursor = self.db.cursor()

        # Insertamos la pregunta en la tabla questions
        cursor.execute("""
            INSERT INTO questions (question)
            VALUES (%s)
        """, (self.question,))
        self.db.commit()
        cursor.close()

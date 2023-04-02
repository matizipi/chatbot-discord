import discord


class Menu(discord.ui.View):
    def __init__(self, db_data, answer_id, db):
        super().__init__()
        self.value = None
        self.db_data = db_data
        self.answer_id = answer_id
        self.helpful = False
        self.db = db

    @discord.ui.button(label="Si", style=discord.ButtonStyle.green)
    async def menu1(self,  interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Gracias, me alegra haberte ayudado")
        self.value = False
        self.helpful = True
        self.stop()
        await self.interaction_callback()
        await self.evaluate_status_answer()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def menu2(self,  interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Perdon por no haber podido ayudarte")
        self.value = False
        self.helpful = False
        self.stop()
        await self.interaction_callback()
        await self.evaluate_status_answer()

    async def interaction_callback(self):
        # Actualizamos el número de respuestas útiles o no útiles según la opción elegida por el usuario
        cursor = self.db.cursor()
        if self.helpful:
            cursor.execute("""
                UPDATE support_chatbot
                SET helpful_responses = helpful_responses + 1
                WHERE id = %s
            """, (self.answer_id,))
        else:
            cursor.execute("""
                UPDATE support_chatbot
                SET unhelpful_responses = unhelpful_responses + 1
                WHERE id = %s
            """, (self.answer_id,))
        self.db.commit()
        cursor.close()

    async def evaluate_status_answer(self):

        cursor = self.db.cursor()

        cursor.execute("""
             SELECT helpful_responses, unhelpful_responses
             FROM support_chatbot
             WHERE id = %s
         """, (self.answer_id,))

        helpful_responses, unhelpful_responses = cursor.fetchone()

        total_responses = helpful_responses + unhelpful_responses
        if total_responses == 0:
            return

        helpful_percentage = helpful_responses / total_responses
        unhelpful_percentage = unhelpful_responses / total_responses

        if helpful_percentage > unhelpful_percentage:
            cursor.execute("""
                 UPDATE support_chatbot
                 SET state_answer = 'appropriate'
                 WHERE id = %s
             """, (self.answer_id,))
        else:
            cursor.execute("""
                 UPDATE support_chatbot
                 SET state_answer = 'inappropriate'
                 WHERE id = %s
             """, (self.answer_id,))
        self.db.commit()
        cursor.close()

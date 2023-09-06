from kivymd.app import MDApp
from kivy.lang import Builder
import json
import re
import sympy as sp
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout

class FazuInfoApp(App):
    def build(self):
        self.conocimiento = self.cargar_conocimiento()

        layout = FloatLayout(size=(400, 600))

        chat_box = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 0.85))
        
        self.chat_label = Label(text="¡Bienvenido! Haz una pregunta. Para más información, escribe 'quiero informacion'.")
        chat_box.add_widget(self.chat_label)

        self.chat_history = ScrollView(size_hint=(1, 1))
        self.chat_messages = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.chat_messages.bind(minimum_height=self.chat_messages.setter('height'))
        self.chat_history.add_widget(self.chat_messages)
        chat_box.add_widget(self.chat_history)

        self.input_box = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.15))
        self.pregunta_input = TextInput(hint_text="Escribe aquí tu pregunta recuerda si no es una operacion empiezala con '/'")
        self.input_box.add_widget(self.pregunta_input)

        buscar_button = Button(text="Enviar", size_hint=(0.2, 1))
        buscar_button.bind(on_press=self.buscar_respuesta)
        self.input_box.add_widget(buscar_button)

        chat_box.add_widget(self.input_box)
        layout.add_widget(chat_box)

        return layout


    def cargar_conocimiento(self):
        try:
            with open("conocimiento.json", "r") as archivo:
                return json.load(archivo)
        except FileNotFoundError:
            return {}

    def guardar_conocimiento(self):
        with open("conocimiento.json", "w") as archivo:
            json.dump(self.conocimiento, archivo)

    def buscar_respuesta(self, instance):
        pregunta = self.pregunta_input.text.lower()

        if pregunta.lower() == 'infok':
            # Mostrar información de ayuda
            self.mostrar_respuesta("¡Bienvenido! Haz una pregunta. Para más información, escribe 'infok'.")
            return

        if re.match(r"^(calcula|calcular)?\s*(.*)$", pregunta):
            expresion = re.sub(r"^(calcula|calcular)?\s*", "", pregunta)
            try:
                resultado = sp.sympify(expresion)  # Utilizar sympy para evaluar expresiones matemáticas
                self.mostrar_respuesta(f"El resultado es: {resultado}")
                return
            except Exception as e:
                pass

        # Reconocer problemas de Bernoulli
        if "principio de bernoulli" in pregunta:
            respuesta, formula = self.resolver_problema_bernulli(pregunta)
            self.mostrar_respuesta_larga(respuesta, formula)
        elif pregunta in self.conocimiento:
            respuesta = self.conocimiento[pregunta]
            self.mostrar_respuesta(respuesta)
        else:
            # Si la pregunta es desconocida, mostrar un cuadro para ingresar la respuesta.
            self.mostrar_cuadro_respuesta_pendiente(pregunta)

    def mostrar_respuesta(self, respuesta):
        mensaje = Label(text=respuesta, halign="left", valign="top", size_hint_y=None)
        mensaje.bind(size=mensaje.setter('text_size'))
        self.chat_messages.add_widget(mensaje)
        self.pregunta_input.text = ""
        self.chat_history.scroll_to(mensaje)

    def mostrar_respuesta_larga(self, respuesta, formula):
        mensaje_respuesta = Label(text=respuesta, halign="left", valign="top", size_hint_y=None)
        mensaje_respuesta.bind(size=mensaje_respuesta.setter('text_size'))

        mensaje_formula = Label(text=formula, halign="left", valign="top", size_hint_y=None)
        mensaje_formula.bind(size=mensaje_formula.setter('text_size'))

        self.chat_messages.add_widget(mensaje_respuesta)
        self.chat_messages.add_widget(mensaje_formula)

        self.pregunta_input.text = ""
        self.chat_history.scroll_to(mensaje_formula)

    def mostrar_cuadro_respuesta_pendiente(self, pregunta):
        # Mostrar un cuadro emergente para ingresar la respuesta.
        content = BoxLayout(orientation='vertical')
        respuesta_input = TextInput(hint_text="Escribe aquí la respuesta")
        content.add_widget(respuesta_input)

        popup = Popup(title='Agregar Respuesta', content=content, size_hint=(None, None), size=(400, 200))
        content.add_widget(Button(text='Guardar', on_press=lambda x: self.guardar_respuesta_popup(popup, pregunta, respuesta_input.text)))
        popup.open()

    def guardar_respuesta_popup(self, popup, pregunta, respuesta):
        if respuesta:
            self.conocimiento[pregunta] = respuesta
            self.guardar_conocimiento()
            # Mostrar la respuesta recién agregada en el chat.
            self.mostrar_respuesta(respuesta)
            popup.dismiss()
        else:
            popup.dismiss()  # Cerrar el cuadro emergente si no se ingresó respuesta.

    def resolver_problema_bernulli(self, pregunta):
        # Analizar la pregunta para extraer datos relevantes (velocidades, presiones, alturas, etc.)
        # Calcular la presión en el punto 2 usando la fórmula de Bernoulli

        # Supongamos que los valores conocidos se obtienen de la pregunta.
        p1 = 6000  # Presión en el punto 1 en Pa
        v1 = 3  # Velocidad en el punto 1 en m/s
        v2 = 2  # Velocidad en el punto 2 en m/s
        h1 = 8  # Altura en el punto 1 en metros
        h2 = 8  # Altura en el punto 2 en metros
        g = 9.81  # Aceleración debida a la gravedad en m/s^2
        p = 1000  # Densidad del fluido en kg/m^3 (para agua)

        # Calcular la presión en el punto 2 usando la fórmula de Bernoulli
        p2 = p1 + 0.5 * p * (v1 ** 2 - v2 ** 2) + p * g * (h1 - h2)

        formula = f"Fórmula: P2 = P1 + 0.5 * p * (v1^2 - v2^2) + p * g * (h1 - h2)\n\n" \
                  f"P2 = {p1} + 0.5 * {p} * ({v1}^2 - {v2}^2) + {p} * {g} * ({h1} - {h2})"

        return f"La presión en el punto 2 es {p2} Pa.", formula

if __name__ == "__main__":
    FazuInfoApp().run()

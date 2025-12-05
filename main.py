import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
import requests
import json


class PokedexApp(App):
    def build(self):
        # Configuración de la ventana
        Window.size = (800, 600)
        Window.title = "Pokedex - Consulta de Pokémon"
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Título
        title = Label(
            text="Pokedex - Consulta de Pokémon",
            size_hint_y=None,
            height=50,
            font_size='20sp',
            bold=True
        )
        main_layout.add_widget(title)
        
        # Sección de búsqueda
        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        self.search_input = TextInput(
            hint_text="Ingresa ID o nombre del Pokémon",
            multiline=False,
            size_hint_x=0.7
        )
        self.search_input.bind(on_text_validate=self.buscar_pokemon)
        
        search_button = Button(
            text="Buscar",
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        search_button.bind(on_press=self.buscar_pokemon)
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_button)
        main_layout.add_widget(search_layout)
        
        # Layout para mostrar la información
        self.info_layout = BoxLayout(orientation='horizontal', spacing=10)
        
        # Panel izquierdo (imagen)
        self.left_panel = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=10)
        
        self.pokemon_image = AsyncImage(
            size_hint=(1, 0.7),
            source=''
        )
        
        self.basic_info = Label(
            text="Ingresa un ID o nombre para buscar",
            size_hint_y=0.3,
            halign='center',
            valign='middle'
        )
        self.basic_info.bind(size=self.basic_info.setter('text_size'))
        
        self.left_panel.add_widget(self.pokemon_image)
        self.left_panel.add_widget(self.basic_info)
        
        # Panel derecho (estadísticas)
        self.right_panel = BoxLayout(orientation='vertical', size_hint_x=0.6, spacing=10)
        
        # Scroll view para las estadísticas
        stats_scroll = ScrollView()
        self.stats_layout = GridLayout(cols=2, spacing=5, size_hint_y=None)
        self.stats_layout.bind(minimum_height=self.stats_layout.setter('height'))
        stats_scroll.add_widget(self.stats_layout)
        
        self.right_panel.add_widget(Label(text="Estadísticas Base", size_hint_y=None, height=30))
        self.right_panel.add_widget(stats_scroll)
        
        self.info_layout.add_widget(self.left_panel)
        self.info_layout.add_widget(self.right_panel)
        main_layout.add_widget(self.info_layout)
        
        # Mensaje de estado
        self.status_label = Label(
            text="Listo para buscar",
            size_hint_y=None,
            height=30
        )
        main_layout.add_widget(self.status_label)
        
        return main_layout
    
    def buscar_pokemon(self, instance):
        query = self.search_input.text.strip().lower()
        if not query:
            self.mostrar_error("Por favor, ingresa un ID o nombre")
            return
        
        self.status_label.text = "Buscando..."
        
        try:
            # Hacer la petición a la PokeAPI
            url = f"https://pokeapi.co/api/v2/pokemon/{query}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                self.mostrar_pokemon(data)
                self.status_label.text = "Búsqueda completada"
            else:
                self.mostrar_error("Pokémon no encontrado")
                
        except requests.exceptions.RequestException as e:
            self.mostrar_error(f"Error de conexión: {str(e)}")
        except Exception as e:
            self.mostrar_error(f"Error inesperado: {str(e)}")
    
    def mostrar_pokemon(self, data):
        # Limpiar estadísticas anteriores
        self.stats_layout.clear_widgets()
        
        # Información básica
        pokemon_id = data['id']
        name = data['name'].capitalize()
        types = [t['type']['name'].capitalize() for t in data['types']]
        types_str = " / ".join(types)
        
        # Actualizar información básica
        self.basic_info.text = f"ID: {pokemon_id}\n{name}\nTipo: {types_str}"
        
        # Cargar imagen 3D (usando la versión oficial)
        sprite_url = data['sprites']['other']['official-artwork']['front_default']
        if sprite_url:
            self.pokemon_image.source = sprite_url
        else:
            # Fallback a sprite regular
            self.pokemon_image.source = data['sprites']['front_default']
        
        # Mostrar estadísticas
        total_stats = 0
        stats = data['stats']
        
        for stat in stats:
            stat_name = stat['stat']['name'].replace('-', ' ').title()
            base_stat = stat['base_stat']
            total_stats += base_stat
            
            # Nombre de la estadística
            stat_label = Label(
                text=f"{stat_name}:",
                size_hint_y=None,
                height=30,
                halign='right'
            )
            stat_label.bind(size=stat_label.setter('text_size'))
            
            # Valor de la estadística
            value_label = Label(
                text=str(base_stat),
                size_hint_y=None,
                height=30,
                halign='left'
            )
            value_label.bind(size=value_label.setter('text_size'))
            
            self.stats_layout.add_widget(stat_label)
            self.stats_layout.add_widget(value_label)
        
        # Agregar total
        total_label = Label(
            text="TOTAL:",
            size_hint_y=None,
            height=30,
            bold=True,
            halign='right'
        )
        total_label.bind(size=total_label.setter('text_size'))
        
        total_value = Label(
            text=str(total_stats),
            size_hint_y=None,
            height=30,
            bold=True,
            halign='left'
        )
        total_value.bind(size=total_value.setter('text_size'))
        
        self.stats_layout.add_widget(total_label)
        self.stats_layout.add_widget(total_value)
    
    def mostrar_error(self, mensaje):
        self.status_label.text = mensaje
        self.basic_info.text = "Error en la búsqueda"
        self.pokemon_image.source = ''
        self.stats_layout.clear_widgets()

if __name__ == '__main__':
    PokedexApp().run()

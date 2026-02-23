import json
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage, Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from functools import partial


API_BASE_URL = 'http://localhost:8000'


# ----------------------------------------------------------------------
# Layouts y comportamiento de selección
# ----------------------------------------------------------------------
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass


# ----------------------------------------------------------------------
# Elemento de la lista principal de Pokémon
# ----------------------------------------------------------------------
class PokemonListItem(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    pokemon_id = NumericProperty(0)
    pokemon_name = StringProperty('')
    pokemon_image = StringProperty('')

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.pokemon_id = data.get('id', 0)
        self.pokemon_name = data.get('name', '').capitalize()
        self.pokemon_image = f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{self.pokemon_id}.png'
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            rv = self.parent.parent
            layout = rv.children[0]
            layout.select_node(self.index)
            return True
        return False

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        if is_selected:
            app = App.get_running_app().root
            if app and app.has_screen('main'):
                main_screen = app.get_screen('main')
                main_screen.load_pokemon_details_by_id(self.pokemon_id)


# ----------------------------------------------------------------------
# Elemento de sugerencia (tarjeta con sprite, ID, nombre y tipos)
# ----------------------------------------------------------------------
class SuggestionCardItem(RecycleDataViewBehavior, BoxLayout):
    index = None
    pokemon_id = NumericProperty(0)
    pokemon_name = StringProperty('')
    pokemon_types = StringProperty('')
    pokemon_image = StringProperty('')

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.pokemon_id = data.get('id', 0)
        self.pokemon_name = data.get('name', '').capitalize()
        types = data.get('types', [])
        self.pokemon_types = ' / '.join([t.capitalize() for t in types])
        self.pokemon_image = data.get('sprite', '')
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            app = App.get_running_app().root
            if app and app.has_screen('main'):
                main_screen = app.get_screen('main')
                main_screen.load_pokemon_details_by_id(self.pokemon_id)
                left_panel = main_screen.ids.left_panel
                left_panel._ignore_text_change = True
                left_panel.search_input.text = self.pokemon_name
                left_panel._ignore_text_change = False
                return True
        return super().on_touch_down(touch)


# ----------------------------------------------------------------------
# Panel izquierdo (búsqueda y lista)
# ----------------------------------------------------------------------
class LeftPanel(BoxLayout):
    current_page = NumericProperty(1)
    total_pages = NumericProperty(1)
    items_per_page = 20

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ignore_text_change = False
        Clock.schedule_once(self._initialize, 0)

    def _initialize(self, dt):
        self.search_input = self.ids.search_input
        self.search_input.bind(on_text_validate=self.on_enter)
        self.search_input.bind(text=self.on_text_changed)
        self.load_pokemon_list(page=self.current_page)

    def on_text_changed(self, instance, value):
        if self._ignore_text_change:
            return
        if hasattr(self, '_search_trigger'):
            self._search_trigger.cancel()
        self._search_trigger = Clock.schedule_once(lambda dt: self._do_search(value), 0.5)

    def _do_search(self, value):
        if len(value) >= 2:
            self.get_suggestions(value)
        else:
            self.hide_suggestions()

    def get_suggestions(self, query):
        url = f'{API_BASE_URL}/pokemon/search/suggestions/detailed?q={query}&limit=10'
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                suggestions = resp.json()
                self.show_suggestions(suggestions)
            else:
                print(f'Error al obtener sugerencias: {resp.status_code}')
        except Exception as e:
            print(f'Error obteniendo sugerencias: {e}')

    def show_suggestions(self, suggestions):
        self.ids.suggestions_view.viewclass = 'SuggestionCardItem'
        self.ids.suggestions_view.data = suggestions
        self.ids.suggestions_view.opacity = 1
        self.ids.suggestions_view.height = min(len(suggestions) * 70, 350)

    def hide_suggestions(self):
        self.ids.suggestions_view.opacity = 0
        self.ids.suggestions_view.height = 0

    def on_enter(self, instance):
        self.search_pokemon(instance.text)
        self.filter_list(instance.text)
        self.hide_suggestions()

    def search_pokemon(self, text):
        if not text.strip():
            return
        main_screen = App.get_running_app().root.get_screen('main')
        if text.strip().isdigit():
            main_screen.load_pokemon_details_by_id(int(text.strip()))
        else:
            main_screen.load_pokemon_details_by_name(text.strip().lower())

    def load_pokemon_list(self, page=1):
        url = f'{API_BASE_URL}/pokemon/?page={page}&items_per_page={self.items_per_page}'
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                self.total_pages = data.get('total_pages', 1)
                items = [{'id': p['id'], 'name': p['name']} for p in data['data']]
                self.ids.pokemon_list.data = items
            else:
                print('Error cargando lista de Pokemon')
        except Exception as e:
            print(f'Error: {e}')

    def go_to_page(self, page):
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self.load_pokemon_list(page=page)

    def filter_list(self, text):
        if text.strip():
            url = f'{API_BASE_URL}/pokemon/?name={text}&items_per_page=50'
        else:
            url = f'{API_BASE_URL}/pokemon/?items_per_page=20'
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                items = [{'id': p['id'], 'name': p['name']} for p in data['data']]
                self.ids.pokemon_list.data = items
        except Exception as e:
            print(f'Error filtrando Pokémon: {e}')


# ----------------------------------------------------------------------
# Vista previa de imagen con botones de ventana
# ----------------------------------------------------------------------
class CustomPopup(Popup):

    def __init__(self, title='', image_source='', **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        layout = BoxLayout(orientation='vertical')
        title_bar = BoxLayout(size_hint_y=None, height=40)
        title_bar.add_widget(Label(text=title, size_hint_x=0.7, color=(1,1,1,1)))
        btn_min = Button(text='_', size_hint_x=0.1)
        btn_min.bind(on_press=self.minimize)
        btn_max = Button(text='□', size_hint_x=0.1)
        btn_max.bind(on_press=self.maximize)
        btn_close = Button(text='X', size_hint_x=0.1, background_color=(1,0,0,1))
        btn_close.bind(on_press=self.dismiss)
        title_bar.add_widget(btn_min)
        title_bar.add_widget(btn_max)
        title_bar.add_widget(btn_close)
        layout.add_widget(title_bar)
        self.image = AsyncImage(source=image_source, size_hint=(1, 1))
        layout.add_widget(self.image)
        self.content = layout

    def minimize(self, instance):
        self.size_hint = (0.3, 0.3)

    def maximize(self, instance):
        self.size_hint = (0.9, 0.9)


# ----------------------------------------------------------------------
# Vista previa de imagen al seleccionar un Pokemon (con botón de cierre)
# ----------------------------------------------------------------------
class ImagePopup(Popup):

    def __init__(self, title='', image_source='', **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        layout = BoxLayout(orientation='vertical')
        img = AsyncImage(source=image_source, size_hint=(1, 0.9), allow_stretch=True, keep_ratio=True)
        layout.add_widget(img)
        btn_close = Button(text='X', size_hint=(1, 0.1), background_color=(1,0,0,1))
        btn_close.bind(on_press=self.dismiss)
        layout.add_widget(btn_close)
        self.content = layout


# ----------------------------------------------------------------------
# Panel derecho (detalles del Pokémon)
# ----------------------------------------------------------------------
class RightPanel(BoxLayout):
    current_pokemon = ObjectProperty(None, allownone=True)
    back_view = BooleanProperty(False)

    def update_details(self, pokemon_data):
        self.current_pokemon = pokemon_data
        sprites = pokemon_data.get('sprites', {})
        self.ids.pokemon_image_main.source = sprites.get('official_artwork') or sprites.get('front_default', '')
        self.ids.pokemon_name.text = pokemon_data.get('name', '').capitalize()
        self.update_sprites()
        self.update_description_tab()
        self.update_sprites_tab()
        self.update_evolutions_tab()
        self.update_locations_tab()

    def update_description_tab(self):
        tab = self.ids.info_content
        tab.clear_widgets()
        stats = [
            ('HP', self.current_pokemon.get('hp', 0)),
            ('Ataque', self.current_pokemon.get('attack', 0)),
            ('Defensa', self.current_pokemon.get('defense', 0)),
            ('Ataque Esp.', self.current_pokemon.get('special_attack', 0)),
            ('Defensa Esp.', self.current_pokemon.get('special_defense', 0)),
            ('Velocidad', self.current_pokemon.get('speed', 0)),
            ('Total', self.current_pokemon.get('total_stats', 0))
        ]
        for label, value in stats:
            tab.add_widget(Label(text=f'{label}: {value}', size_hint_y=None, height=30, color=(1, 1, 1, 1)))
        extras = [
            ('Altura', f"{self.current_pokemon.get('height', 0)} m"),
            ('Peso', f"{self.current_pokemon.get('weight', 0)} kg"),
            ('Exp. base', self.current_pokemon.get('base_experience', 'N/A')),
            ('Captura', self.current_pokemon.get('capture_rate', 'N/A')),
            ('Felicidad', self.current_pokemon.get('base_happiness', 'N/A')),
            ('Tasa crecimiento', self.current_pokemon.get('growth_rate', 'N/A')),
            ('Especie', self.current_pokemon.get('species', 'N/A')),
        ]
        for label, value in extras:
            tab.add_widget(Label(text=f'{label}: {value}', size_hint_y=None, height=30, color=(1, 1, 1, 1)))
        abilities = self.current_pokemon.get('abilities', [])
        if abilities:
            tab.add_widget(Label(
                text='Habilidades:', size_hint_y=None, height=30, color=(1, 1, 1, 1), bold=True
            ))
            for ab in abilities:
                hidden = ' (oculta)' if ab.get('is_hidden') else ''
                tab.add_widget(Label(
                    text=f"• {ab['name'].capitalize()}{hidden}", size_hint_y=None, height=25, color=(0.9, 0.9, 0.9, 1)
                ))

    def update_sprites_tab(self):
        tab = self.ids.sprites_content
        tab.clear_widgets()
        sprites = self.current_pokemon.get('sprites', {})
        generations = sprites.get('generations', {})
        if not generations:
            tab.add_widget(Label(text='No hay sprites por generación', color=(1, 1, 1, 1)))
            return
        for gen_key, gen_data in generations.items():
            gen_label = Label(
                text=gen_key.replace('-', ' ').title(), size_hint_y=None, height=30, bold=True, color=(1, 1, 1, 1)
            )
            tab.add_widget(gen_label)
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=120)
            for version_name, version_sprites in gen_data.items():
                if version_sprites.get('front_default'):
                    img = AsyncImage(
                        source=version_sprites['front_default'], size_hint_x=0.2, size_hint_y=None,
                        height=100, allow_stretch=True, keep_ratio=True
                    )
                    img.bind(
                        on_touch_down=lambda instance, touch, src=version_sprites['front_default']: self.show_image_popup(
                            src) if instance.collide_point(*touch.pos) else None
                    )
                    row.add_widget(img)
            tab.add_widget(row)

    def update_evolutions_tab(self):
        tab = self.ids.evolutions_content
        tab.clear_widgets()
        evos = self.current_pokemon.get('evolutions', [])
        if not evos:
            tab.add_widget(Label(text='No tiene evoluciones', color=(1,1,1,1)))
            return
        chain = BoxLayout(orientation='horizontal', size_hint_y=None, height=150, spacing=10)
        for i, ev in enumerate(evos):
            ev_box = BoxLayout(orientation='vertical')
            img = AsyncImage(
                source=f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{ev.get("id", 0)}.png',
                size_hint_y=0.7, allow_stretch=True, keep_ratio=True
            )
            ev_box.add_widget(img)
            ev_box.add_widget(Label(
                text=ev.get('name', '').capitalize(), color=(1, 1, 1, 1), size_hint_y=0.15
            ))
            condition = f"Nivel {ev.get('min_level', '?')}" if ev.get('min_level') else ev.get('trigger', '')
            ev_box.add_widget(Label(text=condition, color=(0.8, 0.8, 0.8, 1), size_hint_y=0.15))
            chain.add_widget(ev_box)
            if i < len(evos) - 1:
                arrow = Label(text='→', font_size='24sp', color=(1, 1, 1, 1), size_hint_x=0.2)
                chain.add_widget(arrow)
        tab.add_widget(chain)

    def update_locations_tab(self):
        tab = self.ids.locations_content
        tab.clear_widgets()
        locations = self.current_pokemon.get('locations', {})
        if not locations:
            tab.add_widget(Label(text='No hay ubicaciones registradas', color=(1, 1, 1, 1)))
            return
        for loc in locations:
            tab.add_widget(Label(text=f'• {loc}', size_hint_y=None, height=25, color=(0.9, 0.9, 0.9, 1)))

    def update_sprites(self):
        if not self.current_pokemon:
            return
        sprites = self.current_pokemon.get('sprites', {})
        if self.back_view:
            front = sprites.get('back_default', '')
            shiny = sprites.get('back_shiny', '')
        else:
            front = sprites.get('front_default', '')
            shiny = sprites.get('front_shiny', '')
        self.ids.pokemon_image_front.source = front
        self.ids.pokemon_image_shiny.source = shiny

    def toggle_back_view(self):
        self.back_view = not self.back_view
        self.update_sprites()

    def show_image_popup(self, source):
        if not source:
            return
        popup = CustomPopup(title='Vista previa', image_source=source)
        popup.open()


# ----------------------------------------------------------------------
# Pantalla principal
# ----------------------------------------------------------------------
class MainScreen(Screen):

    def load_pokemon_details_by_id(self, pokemon_id):
        url = f'{API_BASE_URL}/pokemon/{pokemon_id}'
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.ids.right_panel.update_details(data)
            else:
                print('Error cargando detalles')
        except Exception as e:
            print(f'Error inesperado: {e}')

    def load_pokemon_details_by_name(self, name):
        url = f'{API_BASE_URL}/pokemon/name/{name}'
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.ids.right_panel.update_details(data)
                left_panel = self.ids.left_panel
                left_panel.hide_suggestions()
                left_panel.search_input.text = name.capitalize()
            else:
                print('Error cargando detalles por nombre')
        except Exception as e:
            print(f'Error: {e}')


class PokedexApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    PokedexApp().run()

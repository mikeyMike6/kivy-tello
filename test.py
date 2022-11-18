from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

class MainApp(MDApp):
    def build(self):
        return MDBoxLayout(
            orientation='vertical',
            MDLabel(text="Hello, World", halign="center")

        )


MainApp().run()
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

# Layout and logic class
class TextInputLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(TextInputLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        # Text input field
        self.input_field = TextInput(
            hint_text='Type something...',
            multiline=False,
            font_size=24,
            size_hint=(1, 0.2)
        )
        self.add_widget(self.input_field)

        # Button to submit text
        self.submit_button = Button(
            text='Display Text',
            font_size=24,
            size_hint=(1, 0.2)
        )
        self.submit_button.bind(on_press=self.display_text)
        self.add_widget(self.submit_button)

        # Label to show the typed text
        self.display_label = Label(
            text='Your text will appear here.',
            font_size=24
        )
        self.add_widget(self.display_label)

    # Function to update the label with the typed text
    def display_text(self, instance):
        user_text = self.input_field.text
        self.display_label.text = f"You typed: {user_text}"

# Main App class
class TextInputApp(App):
    def build(self):
        return TextInputLayout()

# Run the app
if __name__ == '__main__':
    TextInputApp().run()

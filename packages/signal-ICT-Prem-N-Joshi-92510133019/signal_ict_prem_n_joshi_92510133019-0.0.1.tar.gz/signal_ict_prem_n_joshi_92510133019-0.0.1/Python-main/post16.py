from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

# Define layout and logic for counter
class CounterLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(CounterLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'  # Vertical layout

        self.count = 0  # Initial count

        # Label to display the counter
        self.label = Label(text=str(self.count), font_size=50)
        self.add_widget(self.label)

        # Button to increment the counter
        self.button = Button(text='Increment', font_size=30, size_hint=(1, 0.5))
        self.button.bind(on_press=self.increment_counter)
        self.add_widget(self.button)

    # Function to increment counter
    def increment_counter(self, instance):
        self.count += 1
        self.label.text = str(self.count)

# Main App Class
class CounterApp(App):
    def build(self):
        return CounterLayout()

# Run the app
if __name__ == '__main__':
    CounterApp().run()

# Importing necessary modules from kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

# Defining the main application class
class SimpleApp(App):
    def build(self):
        # Creating a layout
        layout = BoxLayout(orientation='vertical')
        
        # Creating a label and adding it to the layout
        self.label = Label(text="Hello, ICT Department")
        layout.add_widget(self.label)
        
        # Creating a button, binding it to the on_button_press function, and adding it to the layout
        button = Button(text="Click Me!")
        button.bind(on_press=self.on_button_press)
        layout.add_widget(button)
        
        # Returning the layout to be displayed
        return layout
    
    # Function to handle button click event
    def on_button_press(self, instance):
        self.label.text = "Button Clicked!"

# Running the application
if __name__ == '__main__':
    SimpleApp().run()

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

# Defining the main application class
class LoginApp(App):
    def build(self):
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Username label and input
        self.username_label = Label(text="Username:")
        layout.add_widget(self.username_label)
        
        self.username_input = TextInput(multiline=False)
        layout.add_widget(self.username_input)
        
        # Password label and input
        self.password_label = Label(text="Password:")
        layout.add_widget(self.password_label)
        
        self.password_input = TextInput(password=True, multiline=False)
        layout.add_widget(self.password_input)
        
        # Login button
        self.login_button = Button(text="Login")
        self.login_button.bind(on_press=self.check_credentials)
        layout.add_widget(self.login_button)
        
        # Label to display the login status
        self.status_label = Label(text="")
        layout.add_widget(self.status_label)
        
        return layout
    
    # Function to check the credentials
    def check_credentials(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        # Simple validation (hardcoded username/password for demonstration)
        if username == "admin" and password == "password":
            self.status_label.text = "Login Successful"
            self.status_label.color = (0, 1, 0, 1)  # Green color for success
        else:
            self.status_label.text = "Invalid Credentials"
            self.status_label.color = (1, 0, 0, 1)  # Red color for error

# Running the application
if __name__ == '__main__':
    LoginApp().run()

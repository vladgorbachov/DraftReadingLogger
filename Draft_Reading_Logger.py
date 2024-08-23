from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.uix.filechooser import FileChooserListView
import os
import webbrowser
from datetime import datetime
import re


class CenteredTextInput(TextInput):
    def __init__(self, **kwargs):
        super(CenteredTextInput, self).__init__(**kwargs)
        self.halign = 'center'
        self.valign = 'middle'
        self.background_color = [1, 1, 1, 1]  # Белый фон
        self.foreground_color = [0, 0, 0, 1]  # Черный текст
        self.cursor_color = [0, 0, 0, 1]  # Черный курсор
        self.font_size = '20sp'
        self.multiline = False
        self.padding = [10, (self.height - self.line_height) / 2]
        self.bind(size=self._update_padding, text=self._update_padding)

    def _update_padding(self, *args):
        self.text_size = self.size
        self.padding_y = (self.height - self.line_height) / 2


class ModernButton(Button):
    def __init__(self, **kwargs):
        super(ModernButton, self).__init__(**kwargs)
        self.background_color = [0, 0, 0, 0]  # Прозрачный фон
        self.color = get_color_from_hex('#4A4A4A')  # Темно-серый текст
        self.font_size = '24sp'

        with self.canvas.before:
            Color(*get_color_from_hex('#D2B48C'))  # Цвет загара
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ModernLabel(Label):
    def __init__(self, **kwargs):
        super(ModernLabel, self).__init__(**kwargs)
        self.color = get_color_from_hex('#4A4A4A')  # Темно-серый текст
        self.font_size = '18sp'


class ColoredLabel(ButtonBehavior, ModernLabel):
    def __init__(self, **kwargs):
        self.bg_color = kwargs.pop('bg_color', get_color_from_hex('#D2B48C'))
        super(ColoredLabel, self).__init__(**kwargs)
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[15])
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos


class DatePickerPopup(Popup):
    def __init__(self, app, **kwargs):
        super(DatePickerPopup, self).__init__(**kwargs)
        self.app = app
        self.title = 'Select Date'
        self.size_hint = (0.8, 0.5)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        spinner_text_size = '25sp'

        self.day_spinner = Spinner(
            text='1',
            values=[str(i) for i in range(1, 32)],
            size_hint=(1, None),
            height=150,
            font_size=spinner_text_size
        )

        self.month_spinner = Spinner(
            text='January',
            values=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                    'November', 'December'],
            size_hint=(1, None),
            height=150,
            font_size=spinner_text_size
        )

        self.year_spinner = Spinner(
            text='2023',
            values=[str(i) for i in range(2023, 2034)],
            size_hint=(1, None),
            height=150,
            font_size=spinner_text_size
        )

        layout.add_widget(ModernLabel(text='Day', size_hint=(1, None), height=40, font_size='18sp'))
        layout.add_widget(self.day_spinner)
        layout.add_widget(ModernLabel(text='Month', size_hint=(1, None), height=40, font_size='18sp'))
        layout.add_widget(self.month_spinner)
        layout.add_widget(ModernLabel(text='Year', size_hint=(1, None), height=40, font_size='18sp'))
        layout.add_widget(self.year_spinner)

        btn_select = ModernButton(text="Select", size_hint_y=None, height=150)
        btn_select.bind(on_press=self.select_date)
        layout.add_widget(btn_select)

        self.add_widget(layout)

    def select_date(self, instance):
        day = self.day_spinner.text
        month = self.month_spinner.text
        year = self.year_spinner.text

        months = {
            'January': '01', 'February': '02', 'March': '03',
            'April': '04', 'May': '05', 'June': '06',
            'July': '07', 'August': '08', 'September': '09',
            'October': '10', 'November': '11', 'December': '12'
        }

        self.app.selected_date = f"{year}-{months[month]}-{int(day):02d}"
        self.app.update_text_input()
        self.dismiss()


class TimePickerPopup(Popup):
    def __init__(self, app, **kwargs):
        super(TimePickerPopup, self).__init__(**kwargs)
        self.app = app
        self.title = 'Select Time'
        self.size_hint = (0.8, 0.38)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        spinner_text_size = '25sp'

        self.hour_spinner = Spinner(
            text='00',
            values=[f'{i:02d}' for i in range(24)],
            size_hint=(1, None),
            height=150,
            font_size=spinner_text_size
        )
        self.minute_spinner = Spinner(
            text='00',
            values=[f'{i:02d}' for i in range(60)],
            size_hint=(1, None),
            height=150,
            font_size=spinner_text_size
        )

        layout.add_widget(ModernLabel(text='Hour', size_hint=(1, None), height=40, font_size='18sp'))
        layout.add_widget(self.hour_spinner)
        layout.add_widget(ModernLabel(text='Minute', size_hint=(1, None), height=40, font_size='18sp'))
        layout.add_widget(self.minute_spinner)

        btn_select = ModernButton(text="Select", size_hint_y=None, height=150)
        btn_select.bind(on_press=self.select_time)
        layout.add_widget(btn_select)

        self.add_widget(layout)

    def select_time(self, instance):
        selected_time = f"{self.hour_spinner.text}:{self.minute_spinner.text}"
        self.app.selected_time = selected_time
        self.app.update_text_input()
        self.dismiss()


class NumericKeyboard(GridLayout):
    def __init__(self, target_input, popup, **kwargs):
        super(NumericKeyboard, self).__init__(**kwargs)
        self.cols = 3
        self.spacing = 5
        self.padding = 5
        self.target_input = target_input
        self.popup = popup

        buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '0', 'OK']
        for button in buttons:
            btn = ModernButton(text=button, size_hint=(1, 1))
            btn.bind(on_press=self.on_button_press)
            self.add_widget(btn)

        # Add backspace button
        backspace_button = ModernButton(text='DEL', size_hint=(1, 1))
        backspace_button.bind(on_press=self.on_backspace)

        # Create a new BoxLayout for the bottom row
        bottom_row = BoxLayout(orientation='horizontal', size_hint=(1, 1))
        bottom_row.add_widget(backspace_button)

        # Add the bottom row to the main layout
        self.add_widget(bottom_row)

    def on_button_press(self, instance):
        if instance.text == 'OK':
            self.popup.dismiss()
        elif instance.text == '.' and '.' in self.target_input.text:
            return  # Prevent multiple decimal points
        else:
            self.target_input.text += instance.text

    def on_backspace(self, instance):
        self.target_input.text = self.target_input.text[:-1]


class NumericTextInput(CenteredTextInput):
    def __init__(self, **kwargs):
        super(NumericTextInput, self).__init__(**kwargs)
        self.readonly = True
        self.bind(on_touch_down=self.show_numeric_keyboard)

    def show_numeric_keyboard(self, instance, touch):
        if self.collide_point(*touch.pos):
            content = BoxLayout(orientation='vertical')
            popup = Popup(title="Enter Value", size_hint=(0.8, 0.7))  # Increased height to accommodate backspace
            keyboard = NumericKeyboard(target_input=self, popup=popup)
            content.add_widget(keyboard)

            popup.content = content
            popup.open()
            return True


class DraftRecorderApp(App):
    selected_date = None
    selected_time = None

    def build(self):
        Window.clearcolor = get_color_from_hex('#FFF5E6')  # Теплый белый фон

        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        header = ColoredLabel(text="DRAFT MARK READINGS", font_size='24sp', size_hint_y=None, height=50)
        main_layout.add_widget(header)

        self.text_input = CenteredTextInput(text=" ", size_hint_y=None, height=150)
        main_layout.add_widget(self.text_input)

        date_time_layout = BoxLayout(size_hint_y=None, height=150, spacing=10)
        date_button = ModernButton(text="DATE", size_hint_x=0.5)
        time_button = ModernButton(text="TIME", size_hint_x=0.5)
        date_button.bind(on_press=self.open_date_picker)
        time_button.bind(on_press=self.open_time_picker)
        date_time_layout.add_widget(date_button)
        date_time_layout.add_widget(time_button)
        main_layout.add_widget(date_time_layout)

        open_button = ModernButton(text="OPEN", size_hint_y=None, height=120)
        open_button.bind(on_press=self.show_file_chooser)
        main_layout.add_widget(open_button)

        draft_layout = GridLayout(cols=2, spacing=10)
        main_layout.add_widget(draft_layout)

        positions = [
            'FORWARD PORTSIDE', 'FORWARD STARBOARD',
            'MIDSHIP PORTSIDE', 'MIDSHIP STARBOARD',
            'AFT PORTSIDE', 'AFT STARBOARD'
        ]

        self.draft_inputs = {}
        for position in positions:
            draft_layout.add_widget(ModernLabel(text=position))
            self.draft_inputs[position] = NumericTextInput(size_hint_y=None, height=150, font_size='40sp')
            draft_layout.add_widget(self.draft_inputs[position])

        button_layout = BoxLayout(size_hint_y=None, height=150, spacing=10)
        save_button = ModernButton(text="SAVE", background_color=get_color_from_hex('#90EE90'))
        exit_button = ModernButton(text="EXIT", background_color=get_color_from_hex('#FFA07A'))
        save_button.bind(on_press=self.save_data)
        exit_button.bind(on_press=self.exit_app)
        button_layout.add_widget(save_button)
        button_layout.add_widget(exit_button)
        main_layout.add_widget(button_layout)

        return main_layout

    def open_date_picker(self, instance):
        date_picker = DatePickerPopup(self)
        date_picker.open()

    def open_time_picker(self, instance):
        time_picker = TimePickerPopup(self)
        time_picker.open()

    def update_text_input(self):
        text_parts = []
        if self.selected_date:
            text_parts.append(self.selected_date)
        if self.selected_time:
            text_parts.append(self.selected_time)
        self.text_input.text = " ".join(text_parts) + " : " + self.text_input.text.split(": ", 1)[-1]

    def save_data(self, instance):
        try:
            save_dir = "/storage/emulated/0/draft readings"
            os.makedirs(save_dir, exist_ok=True)

            date = self.selected_date or datetime.now().strftime('%d-%m-%Y')
            time = self.selected_time or datetime.now().strftime('%H-%M')
            user_text = self.text_input.text.strip().replace(' ', '_')
            file_name = f"{date}_{time}_{user_text}.txt" if user_text else f"{date}_{time}.txt"
            save_path = os.path.join(save_dir, file_name)

            if os.path.exists(save_path):
                self.show_save_dialog(save_path)
            else:
                self.write_to_file(save_path)
        except PermissionError:
            self.show_error_popup("Permission Denied", "Cannot save file. Permission denied.")
        except Exception as e:
            self.show_error_popup("Error", f"An error occurred: {str(e)}")

    def show_save_dialog(self, save_path):
        self.save_popup = Popup(title='File Exists', size_hint=(0.9, 0.5))

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(ModernLabel(text=f"File '{save_path}' already exists. Please enter a new name:"))

        self.file_name_input = CenteredTextInput(text=os.path.basename(save_path), multiline=False, size_hint_y=None,
                                                 height=60)
        layout.add_widget(self.file_name_input)

        save_button = ModernButton(text="Save", size_hint_y=None, height=40)
        save_button.bind(on_press=self._save_file_with_new_name)
        layout.add_widget(save_button)

        self.save_popup.content = layout
        self.save_popup.open()

    def _save_file_with_new_name(self, instance):
        try:
            file_name = self.file_name_input.text
            save_path = os.path.join("/storage/emulated/0/draft readings", file_name)

            if os.path.exists(save_path):
                self.file_name_input.text = f'{os.path.splitext(file_name)[0]}_new{os.path.splitext(file_name)[1]}'
                return

            self.write_to_file(save_path)
            self.save_popup.dismiss()
        except PermissionError:
            self.show_error_popup("Permission Denied", "Cannot save file. Permission denied.")
        except Exception as e:
            self.show_error_popup("Error", f"An error occurred: {str(e)}")

    def write_to_file(self, save_path):
        try:
            with open(save_path, "w") as file:
                file.write("DRAFT MARK DATA\n")
                file.write(f"Reading: {self.text_input.text}\n\n")
                for position, input_field in self.draft_inputs.items():
                    file.write(f"{position}: {input_field.text}\n")

            print(f"Data saved to {save_path}")
            self.show_popup("Success", f"Data saved to {save_path}")
        except PermissionError:
            self.show_error_popup("Permission Denied", "Cannot save file. Permission denied.")
        except Exception as e:
            self.show_error_popup("Error", f"An error occurred: {str(e)}")

    def show_error_popup(self, title, message):
        popup = Popup(title=title, content=ModernLabel(text=message), size_hint=(0.8, 0.4))
        popup.open()

    def show_popup(self, title, message):
        popup = Popup(title=title, content=ModernLabel(text=message), size_hint=(0.8, 0.4))
        popup.open()

    def exit_app(self, instance):
        App.get_running_app().stop()

    def show_file_chooser(self, instance):
        try:
            content = BoxLayout(orientation='vertical')
            self.file_chooser = FileChooserListView(path="/storage/emulated/0/draft readings")
            content.add_widget(self.file_chooser)

            buttons = BoxLayout(size_hint_y=None, height=90)
            select_button = ModernButton(text="Select")
            cancel_button = ModernButton(text="Cancel")

            select_button.bind(on_press=self.load_selected_file)
            cancel_button.bind(on_press=self.dismiss_popup)

            buttons.add_widget(select_button)
            buttons.add_widget(cancel_button)
            content.add_widget(buttons)

            self.popup = Popup(title="Choose File", content=content, size_hint=(0.9, 0.9))
            self.popup.open()
        except Exception as e:
            self.show_error_popup("Error", f"An error occurred: {str(e)}")

    def load_selected_file(self, instance):
        try:
            if self.file_chooser.selection:
                file_path = self.file_chooser.selection[0]
                with open(file_path, 'r') as file:
                    content = file.readlines()

                self.text_input.text = content[1].split(': ')[1].strip()  # Заполнение поля чтения

                for line in content[3:]:
                    position, value = line.split(': ')
                    if position in self.draft_inputs:
                        self.draft_inputs[position].text = value.strip()

                print(f"File {file_path} loaded")
                self.dismiss_popup()
            else:
                self.show_error_popup("Error", "No file selected")
        except Exception as e:
            self.show_error_popup("Error", f"An error occurred: {str(e)}")

    def dismiss_popup(self, instance=None):
        if hasattr(self, 'popup') and self.popup:
            self.popup.dismiss()


if __name__ == '__main__':
    DraftRecorderApp().run()
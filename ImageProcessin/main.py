import os
import tempfile
import numpy as np
import cv2
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.image import Image as KivyImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import OneLineListItem
from kivymd.uix.dialog import MDDialog
from PIL import Image as PILImage, ImageEnhance

# 註冊字體
LabelBase.register(name="NotoSans", fn_regular="NotoSansTC-VariableFont_wght.ttf")

KV = '''
BoxLayout:
    orientation: 'vertical'

    MDTopAppBar:
        title: "WELCOME"
        font_name: "NotoSans"
        left_action_items: [["menu", lambda x: app.open_menu(x)]]
        right_action_items: [["dots-vertical", lambda x: app.show_adjustments(x)]]
        font_name: "NotoSans"  # 指定字體

    BoxLayout:
        id: content_area
        orientation: 'horizontal'
        size_hint: 1, 1

'''
class CustomMDFileManager(MDFileManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = "NotoSans"

class CustomOneLineListItem(OneLineListItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids._lbl_primary.font_name = 'NotoSans'
        self.ids._lbl_primary.color = (0, 0, 0, 1)  # 黑色文本

class ImageProcessingApp(MDApp):
    def build(self):
        self.original_image_path = None
        self.temp_image_path = None

        self.current_brightness = 0
        self.current_contrast = 1
        self.current_saturation = 1

        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True
        )

        menu_items = [
            {
                "viewclass": "CustomOneLineListItem",
                "text": "打開檔案",
                "height": dp(56),
                "on_release": lambda x="打開檔案": self.menu_callback(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "保存",
                "height": dp(56),
                "on_release": lambda x="保存": self.menu_callback(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "另存為...",
                "height": dp(56),
                "on_release": lambda x="另存為...": self.menu_callback(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "圖片旋轉",
                "height": dp(56),
                "on_release": lambda x="圖片旋轉": self.menu_callback(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "過濾器",
                "height": dp(56),
                "on_release": lambda x="過濾器": self.menu_callback(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "重置",
                "height": dp(56),
                "on_release": lambda x="重置": self.menu_callback(x),
            }
        ]
        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=4,
        )

        filter_items = [
            {
                "viewclass": "CustomOneLineListItem",
                "text": "灰階",
                "height": dp(56),
                "on_release": lambda x="灰階": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "負片",
                "height": dp(56),
                "on_release": lambda x="負片": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "銳化",
                "height": dp(56),
                "on_release": lambda x="銳化": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "二值化",
                "height": dp(56),
                "on_release": lambda x="二值化": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "Canny邊緣檢測",
                "height": dp(56),
                "on_release": lambda x="Canny邊緣檢測": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "雙邊過濾器",
                "height": dp(56),
                "on_release": lambda x="雙邊過濾器": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "侵蝕",
                "height": dp(56),
                "on_release": lambda x="侵蝕": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "中值過濾器",
                "height": dp(56),
                "on_release": lambda x="中值過濾器": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "膨脹",
                "height": dp(56),
                "on_release": lambda x="膨脹": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "伽瑪校正",
                "height": dp(56),
                "on_release": lambda x="伽瑪校正": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "均值過濾器",
                "height": dp(56),
                "on_release": lambda x="均值過濾器": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "翻轉",
                "height": dp(56),
                "on_release": lambda x="翻轉": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "Beta校正",
                "height": dp(56),
                "on_release": lambda x="Beta校正": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "高斯過濾器",
                "height": dp(56),
                "on_release": lambda x="高斯過濾器": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "Sobel邊緣檢測",
                "height": dp(56),
                "on_release": lambda x="Sobel邊緣檢測": self.apply_filter(x),
            },
            {
                "viewclass": "CustomOneLineListItem",
                "text": "椒鹽噪聲",
                "height": dp(56),
                "on_release": lambda x="椒鹽噪聲": self.apply_filter(x),
            }
        ]
        
        self.filter_menu = MDDropdownMenu(
            items=filter_items,
            width_mult=4,
        )

        Window.bind(on_resize=self.on_window_resize)
        return Builder.load_string(KV)

    def on_window_resize(self, window, width, height):
        self.adjust_image_size()

    def open_menu(self, button):
        self.menu.caller = button
        self.menu.open()

    def menu_callback(self, text_item):
        self.menu.dismiss()
        if text_item == "打開檔案":
            self.file_manager_open()
        elif text_item == "保存":
            self.confirm_save()
        elif text_item == "另存為...":
            self.file_manager_open_save_as()
        elif text_item == "過濾器":
            self.open_filter_menu()
        elif text_item == "重置":
            self.reset_image()
        elif text_item == "圖片旋轉":
            self.show_rotate_popup()

    def open_filter_menu(self):
        self.filter_menu.caller = self.menu.caller
        self.filter_menu.open()

    def show_adjustments(self, instance):
        popup_content = BoxLayout(orientation='vertical')
        
        self.brightness_slider = Slider(min=-1, max=1, value=self.current_brightness, orientation='horizontal')
        brightness_label = Label(text=f'亮度: {self.brightness_slider.value}', color=(1, 1, 1, 1), font_name="NotoSans")
        self.brightness_slider.bind(value=lambda instance, value: brightness_label.setter('text')(brightness_label, f'亮度: {value:.2f}'))
        
        self.contrast_slider = Slider(min=0, max=2, value=self.current_contrast, orientation='horizontal')
        contrast_label = Label(text=f'對比度: {self.contrast_slider.value}', color=(1, 1, 1, 1), font_name="NotoSans")
        self.contrast_slider.bind(value=lambda instance, value: contrast_label.setter('text')(contrast_label, f'對比度: {value:.2f}'))
        
        self.saturation_slider = Slider(min=0, max=2, value=self.current_saturation, orientation='horizontal')
        saturation_label = Label(text=f'飽和度: {self.saturation_slider.value}', color=(1, 1, 1, 1), font_name="NotoSans")
        self.saturation_slider.bind(value=lambda instance, value: saturation_label.setter('text')(saturation_label, f'飽和度: {value:.2f}'))
        
        apply_button = MDRaisedButton(text='應用', size_hint=(None, None), height=dp(40), font_name="NotoSans")
        apply_button.bind(on_release=self.apply_adjustments)

        clear_button = MDRaisedButton(text='清除', size_hint=(None, None), height=dp(40), font_name="NotoSans")
        clear_button.bind(on_release=self.clear_adjustments)

        buttons_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        buttons_box.add_widget(apply_button)
        buttons_box.add_widget(clear_button)

        popup_content.add_widget(brightness_label)
        popup_content.add_widget(self.brightness_slider)
        popup_content.add_widget(contrast_label)
        popup_content.add_widget(self.contrast_slider)
        popup_content.add_widget(saturation_label)
        popup_content.add_widget(self.saturation_slider)
        popup_content.add_widget(buttons_box)
        
        self.adjustments_popup = Popup(
            title='Modify', 
            content=popup_content, 
            size_hint=(None, None), 
            size=(400, 600), 
            auto_dismiss=True
        )
        self.adjustments_popup.open()
    def show_rotate_popup(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.rotation_slider = Slider(min=-180, max=180, value=0, orientation='horizontal')
        rotation_label = Label(text=f'角度: {self.rotation_slider.value}', font_name="NotoSans")
        self.rotation_slider.bind(value=lambda instance, value: rotation_label.setter('text')(rotation_label, f'角度: {int(value)}'))

        self.rotation_input = TextInput(text='0', multiline=False, font_name="NotoSans")
        self.rotation_input.bind(text=self.on_rotation_input)

        apply_button = MDRaisedButton(text="應用", size_hint=(None, None), height=dp(40), font_name="NotoSans")
        apply_button.bind(on_release=self.apply_rotation)

        layout.add_widget(rotation_label)
        layout.add_widget(self.rotation_slider)
        layout.add_widget(Label(text="或輸入角度：", font_name="NotoSans"))
        layout.add_widget(self.rotation_input)
        layout.add_widget(apply_button)

        self.rotation_popup = Popup(
            title="圖片旋轉",
            content=layout,
            size_hint=(None, None),
            size=(400, 300),
            auto_dismiss=True,
            title_font="NotoSans"
        )
        self.rotation_popup.open()

    def on_rotation_input(self, instance, value):
        try:
            angle = float(value)
            if -180 <= angle <= 180:
                self.rotation_slider.value = angle
        except ValueError:
            pass

    def apply_rotation(self, instance):
        if self.temp_image_path:
            pil_image = PILImage.open(self.temp_image_path)
            pil_image = pil_image.rotate(-self.rotation_slider.value, expand=True)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                pil_image.save(temp_file.name)
                self.temp_image_path = temp_file.name
            self.display_images(self.original_image_path, self.temp_image_path)
            self.rotation_popup.dismiss()
    def file_manager_open(self):
        self.file_manager.show('/')
        self.file_manager_open_state = 'open'

    def file_manager_open_save_as(self):
        self.file_manager.show('/')
        self.file_manager_open_state = 'save_as'

    def select_path(self, path):
        self.exit_manager()
        if self.file_manager_open_state == 'open':
            self.load_image(path)
        elif self.file_manager_open_state == 'save_as':
            self.save_as_popup(path)

    def exit_manager(self, *args):
        self.file_manager.close()

    def load_image(self, path):
        self.original_image_path = path
        self.temp_image_path = path
        self.display_images(path, path)

    def display_images(self, original_path, edited_path):
        content_area = self.root.ids.content_area
        content_area.clear_widgets()
        
        self.original_img = KivyImage(source=original_path, size_hint=(0.5, 1))
        self.edited_img = KivyImage(source=edited_path, size_hint=(0.5, 1))
        
        content_area.add_widget(self.original_img)
        content_area.add_widget(self.edited_img)

    def adjust_image_size(self):
        if hasattr(self, 'original_img') and hasattr(self, 'edited_img'):
            window_width, window_height = Window.size
            self.original_img.size = (window_width * 0.5, window_height)
            self.edited_img.size = (window_width * 0.5, window_height)

    def confirm_save(self):
        if self.original_image_path:
            layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            label = Label(text="是否要覆蓋現有檔案？", font_name="NotoSans")
            buttons_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
            yes_button = MDRaisedButton(text="是", size_hint=(None, None), height=dp(40), font_name="NotoSans")
            no_button = MDRaisedButton(text="否", size_hint=(None, None), height=dp(40), font_name="NotoSans")

            buttons_box.add_widget(yes_button)
            buttons_box.add_widget(no_button)
            layout.add_widget(label)
            layout.add_widget(buttons_box)

            popup = Popup(
                title="儲存", 
                content=layout, 
                size_hint=(None, None), 
                size=(400, 200), 
                auto_dismiss=True,
                title_font="NotoSans"
            )

            yes_button.bind(on_release=lambda x: (self.confirm_save_image(self.original_image_path), popup.dismiss()))
            no_button.bind(on_release=popup.dismiss)

            popup.open()

    def confirm_save_image(self, path):
        if self.temp_image_path:
            pil_image = PILImage.open(self.temp_image_path)
            pil_image.save(path)
            print(f'圖像已保存為 {path}')  # 移除Snackbar並改為在控制台打印

    def save_as_popup(self, folder_path):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        file_name_input = TextInput(hint_text="輸入檔名", multiline=False, font_name="NotoSans")
        save_button = MDRaisedButton(text="保存", size_hint=(None, None), height=dp(40), font_name="NotoSans")

        layout.add_widget(file_name_input)
        layout.add_widget(save_button)

        popup = Popup(title="另存新檔", content=layout, size_hint=(None, None), size=(400, 200), auto_dismiss=True,title_font="NotoSans")

        def save_to_location(instance):
            file_name = file_name_input.text
            if file_name:
                file_path = os.path.join(folder_path, file_name + '.png')
                self.save_image_to_location(file_path)
                popup.dismiss()

        save_button.bind(on_release=save_to_location)
        popup.open()

    def save_image_to_location(self, path):
        if self.temp_image_path:
            pil_image = PILImage.open(self.temp_image_path)
            pil_image.save(path)
            print(f'圖像已保存為 {path}')  # 移除Snackbar並改為在控制台打印

    def apply_adjustments(self, instance):
        if self.temp_image_path:
            pil_image = PILImage.open(self.temp_image_path)

            # 應用亮度
            enhancer = ImageEnhance.Brightness(pil_image)
            pil_image = enhancer.enhance(self.brightness_slider.value + 1)

            # 應用對比度
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(self.contrast_slider.value)

            # 應用飽和度
            enhancer = ImageEnhance.Color(pil_image)
            pil_image = enhancer.enhance(self.saturation_slider.value)

            # 保存當前調整值
            self.current_brightness = self.brightness_slider.value
            self.current_contrast = self.contrast_slider.value
            self.current_saturation = self.saturation_slider.value

            # 將PIL圖像轉回Kivy圖像並保存到臨時文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                pil_image.save(temp_file.name)
                self.temp_image_path = temp_file.name
            
            self.display_images(self.original_image_path, self.temp_image_path)
            self.adjustments_popup.dismiss()

    def clear_adjustments(self, instance):
        if self.temp_image_path:
            self.temp_image_path = self.original_image_path
            self.display_images(self.original_image_path, self.original_image_path)
            self.current_brightness = 0
            self.current_contrast = 1
            self.current_saturation = 1
            self.brightness_slider.value = self.current_brightness
            self.contrast_slider.value = self.current_contrast
            self.saturation_slider.value = self.current_saturation

    def apply_filter(self, filter_name):
            self.filter_menu.dismiss()
            if self.temp_image_path:
                pil_image = PILImage.open(self.temp_image_path)
                pil_image = pil_image.convert("RGB")  # Convert to RGB if not already

                if filter_name == "灰階":
                    pil_image = pil_image.convert("L").convert("RGB")
                elif filter_name == "負片":
                    pil_image = PILImage.fromarray(255 - cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR))
                elif filter_name == "銳化":
                    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                    pil_image = PILImage.fromarray(cv2.filter2D(np.array(pil_image), -1, kernel))
                elif filter_name == "二值化":
                    pil_image = PILImage.fromarray(cv2.threshold(cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2GRAY), 127, 255, cv2.THRESH_BINARY)[1])
                elif filter_name == "Canny邊緣檢測":
                    pil_image = PILImage.fromarray(cv2.Canny(cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2GRAY), 100, 200))
                elif filter_name == "雙邊過濾器":
                    pil_image = PILImage.fromarray(cv2.bilateralFilter(np.array(pil_image), 9, 75, 75))
                elif filter_name == "侵蝕":
                    kernel = np.ones((5, 5), np.uint8)
                    pil_image = PILImage.fromarray(cv2.erode(np.array(pil_image), kernel, iterations=1))
                elif filter_name == "中值過濾器":
                    pil_image = PILImage.fromarray(cv2.medianBlur(np.array(pil_image), 5))
                elif filter_name == "膨脹":
                    kernel = np.ones((5, 5), np.uint8)
                    pil_image = PILImage.fromarray(cv2.dilate(np.array(pil_image), kernel, iterations=1))
                elif filter_name == "伽瑪校正":
                    gamma = 2.0  # 示例伽瑪值
                    lookUpTable = np.empty((1, 256), np.uint8)
                    for i in range(256):
                        lookUpTable[0, i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
                    pil_image = PILImage.fromarray(cv2.LUT(np.array(pil_image), lookUpTable))
                elif filter_name == "均值過濾器":
                    pil_image = PILImage.fromarray(cv2.blur(np.array(pil_image), (5, 5)))
                elif filter_name == "翻轉":
                    pil_image = pil_image.transpose(PILImage.FLIP_LEFT_RIGHT)
                elif filter_name == "Beta校正":
                    beta = 50  # 示例beta值
                    pil_image = PILImage.fromarray(cv2.convertScaleAbs(np.array(pil_image), alpha=1, beta=beta))
                elif filter_name == "高斯過濾器":
                    pil_image = PILImage.fromarray(cv2.GaussianBlur(np.array(pil_image), (5, 5), 0))
                elif filter_name == "Sobel邊緣檢測":
                    gray = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2GRAY)
                    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
                    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
                    sobel = cv2.magnitude(sobelx, sobely)
                    pil_image = PILImage.fromarray(sobel.astype(np.uint8))
                elif filter_name == "椒鹽噪聲":
                    row, col, _ = np.array(pil_image).shape
                    s_vs_p = 0.5
                    amount = 0.004
                    out = np.copy(np.array(pil_image))
                    num_salt = np.ceil(amount * row * col * s_vs_p)
                    coords = [np.random.randint(0, i - 1, int(num_salt)) for i in out.shape]
                    out[coords[0], coords[1], :] = 1
                    num_pepper = np.ceil(amount * row * col * (1.0 - s_vs_p))
                    coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in out.shape]
                    out[coords[0], coords[1], :] = 0
                    pil_image = PILImage.fromarray(out)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    pil_image.save(temp_file.name)
                    self.temp_image_path = temp_file.name
            
                self.display_images(self.original_image_path, self.temp_image_path)

    def reset_image(self):
        if self.original_image_path:
            self.temp_image_path = self.original_image_path
            self.current_brightness = 0
            self.current_contrast = 1
            self.current_saturation = 1
            self.display_images(self.original_image_path, self.original_image_path)
            print("圖像已重置為原始狀態")  # 移除Snackbar並改為在控制台打印

if __name__ == "__main__":
    ImageProcessingApp().run()

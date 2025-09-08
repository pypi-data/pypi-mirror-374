import flet as ft
from smooth_criminal.flet_app.views import main_view

def main(page: ft.Page):
    main_view(page)

if __name__ == "__main__":
    ft.app(target=main)

import asyncio
import flet as ft

def info_panel(text: str, color="blue") -> ft.Container:
    return ft.Container(
        content=ft.Text(text, color=color, size=16),
        padding=10,
        bgcolor=ft.colors.SURFACE_VARIANT,
        border_radius=10
    )

def function_table() -> ft.DataTable:
    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Function")),
            ft.DataColumn(ft.Text("Decorator(s)")),
            ft.DataColumn(ft.Text("Runs")),
            ft.DataColumn(ft.Text("Avg Time (s)")),
            ft.DataColumn(ft.Text("Score")),
        ],
        rows=[]
    )

def action_buttons(refresh_fn, clear_fn, export_fn, graph_fn) -> ft.Row:
    return ft.Row([
        ft.ElevatedButton("🔄 Refresh", on_click=refresh_fn, icon=ft.Icons.REFRESH),
        ft.ElevatedButton("🧼 Limpiar historial", on_click=clear_fn, icon=ft.Icons.DELETE),
        ft.ElevatedButton("💾 Exportar CSV", on_click=lambda e: export_fn("csv"), icon=ft.Icons.DOWNLOAD),
        ft.ElevatedButton("💾 Exportar JSON", on_click=lambda e: export_fn("json"), icon=ft.Icons.DOWNLOAD),
        ft.ElevatedButton("💾 Exportar XLSX", on_click=lambda e: export_fn("xlsx"), icon=ft.Icons.DOWNLOAD),
        ft.ElevatedButton("💾 Exportar MD", on_click=lambda e: export_fn("md"), icon=ft.Icons.DOWNLOAD),
        ft.ElevatedButton("📈 Ver gráfico", on_click=graph_fn, icon=ft.Icons.INSERT_CHART)
    ], spacing=15)


def moonwalk_animation(page: ft.Page, duration: int = 800) -> None:
    """Desplaza un ícono de MJ por la pantalla y limpia al finalizar."""

    dancer = ft.Text("🕺", size=40)
    anim = ft.AnimatedContainer(
        content=dancer,
        width=40,
        height=40,
        left=-50,
        top=page.height / 2,
        animate_position=ft.animation.Animation(duration, "ease"),
    )
    page.overlay.append(anim)
    page.update()

    anim.left = page.width
    anim.update()

    async def _cleanup():
        await asyncio.sleep(duration / 1000)
        page.overlay.remove(anim)
        await page.update_async()

    page.run_task(_cleanup)

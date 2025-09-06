def main():
    """Función principal con GUI"""
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()  # oculta ventana raíz
        messagebox.showinfo("Demo POC", "¡Hola! La herramienta está lista para usarse.")
        root.destroy()
    except Exception as e:
        print("No se pudo abrir GUI:", e)

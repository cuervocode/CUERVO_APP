import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import random
import json
import os
import sys # <--- Necesario para el ejecutable

# --- FUNCIÓN PARA RUTAS DEL EJECUTABLE ---
def resource_path(relative_path):
    """ Obtiene la ruta de los archivos cuando están dentro del .exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- MAPEO DE ARCHIVOS JSON ---
BANCO_DATOS = {
    "DAM 1.3 Operaciones Navales": "DAM_1.3.json",
    "DAM 1.3.3 Operaciones de la Infantería de Marina": "DAM_1.3.3.json",
    "DAM 1.3.3.1.2 Táctica de Operaciones de Armas Combinadas de la BRIGIM": "DAM_1.3.3.1.2.json",
    "DAM 1.3.3.1.18 Concepto Operacional de IM (Defensa Exterior)": "DAM_1.3.3.1.18.json",
    "DAM 1.3-A Operaciones Conjuntas": "DAM_1.3-A.json",
    "DAM 1.5 Planeamiento Naval Operacional": "DAM_1.5.json"
}

class ExamenApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Evaluación Naval - Cuervo Edition")
        
        # --- LÍNEA PARA EL ICONO DE LA VENTANA (AJUSTADA) ---
        try:
            self.iconbitmap(resource_path("CUERVO_APP.ico"))
        except:
            pass
        
        self.geometry("700x850") 
        self.configure(fg_color="#CDD8E6")
        
        # 1. Variables de control
        self.minutos_configurados = 60
        self.tema_seleccionado = list(BANCO_DATOS.keys())[0]
        self.mostrar_feedback = tk.BooleanVar(value=False)
        self.cantidad_personalizada = None 
        
        # 2. Iniciar Interfaz
        self.mostrar_menu_seleccion()

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def obtener_total_preguntas(self, tema):
        try:
            if tema == "EXAMEN COMPLETO (TODOS LOS TEMAS)":
                total = 0
                for archivo in BANCO_DATOS.values():
                    # --- RUTA AJUSTADA ---
                    ruta_real = resource_path(archivo)
                    if os.path.exists(ruta_real):
                        with open(ruta_real, 'r', encoding='utf-8') as f:
                            total += len(json.load(f))
                return total
            else:
                archivo = BANCO_DATOS.get(tema)
                # --- RUTA AJUSTADA ---
                ruta_real = resource_path(archivo)
                if archivo and os.path.exists(ruta_real):
                    with open(ruta_real, 'r', encoding='utf-8') as f:
                        return len(json.load(f))
            return 0
        except: return 0

    def mostrar_menu_seleccion(self):
        self.limpiar_pantalla()
        
        ctk.CTkLabel(self, text="EVALUACIÓN NAVAL", font=("Noto Sans", 28, "bold"), text_color="#1A237E").pack(pady=(40, 5))
        label_edicion = ctk.CTkLabel(
            self, 
            text="Desarrollado por RPP  ", 
            font=("Noto Sans", 8, "italic"), 
            text_color="#1A237E",
            width=400,
            anchor="center"
        )
        label_edicion.pack(pady=(0, 30))

        f_config = ctk.CTkFrame(self, fg_color="#F0F4F8", corner_radius=15)
        f_config.pack(pady=10, padx=50, fill="x")

        ctk.CTkLabel(f_config, text="SELECCIONAR MANUAL:", font=("Noto Sans", 13, "bold"), text_color="black").pack(pady=(15, 0))
        
        opciones_dam = list(BANCO_DATOS.keys()) + ["EXAMEN COMPLETO (TODOS LOS TEMAS)"]
        self.menu_dam = ctk.CTkOptionMenu(
            f_config, values=opciones_dam, width=520, anchor="center", 
            fg_color="#1A237E", button_color="#1A237E",
            command=self.cambiar_tema_variable
        )
        self.menu_dam.set(self.tema_seleccionado)
        self.menu_dam.pack(pady=(10, 5), padx=20)

        total_inicial = self.obtener_total_preguntas(self.tema_seleccionado)
        self.lbl_info_preguntas = ctk.CTkLabel(
            f_config, 
            text=f"Total de preguntas en este banco: {total_inicial}  ", 
            font=("Noto Sans", 14, "italic"), 
            text_color="#546E7A",
            width=500,
            anchor="center"
        )
        self.lbl_info_preguntas.pack(pady=(0, 10))

        f_linea = ctk.CTkFrame(f_config, fg_color="transparent")
        f_linea.pack(pady=10)

        ctk.CTkLabel(f_linea, text="Preguntas:", font=("Noto Sans", 12, "bold"), text_color="black").pack(side="left", padx=5)
        self.entry_cant = ctk.CTkOptionMenu(
            f_linea, 
            values=["MAXIMO", "Otra cantidad..."], 
            width=150, 
            fg_color="#546E7A", 
            command=self.gestionar_cantidad_manual
        )
        self.entry_cant.set("MAXIMO")
        self.entry_cant.pack(side="left", padx=10)

        ctk.CTkLabel(f_linea, text="Minutos:", font=("Noto Sans", 12, "bold"), text_color="black").pack(side="left", padx=5)
        self.menu_tiempo = ctk.CTkOptionMenu(f_linea, values=["15", "30", "60", "120"], width=90, fg_color="#546E7A", command=self.ajustar_tiempo)
        self.menu_tiempo.set(f"{self.minutos_configurados} min")
        self.menu_tiempo.pack(side="left", padx=5)

        self.sw_feedback = ctk.CTkSwitch(f_config, text="Aviso de Correcto/Incorrecto", variable=self.mostrar_feedback, text_color="black")
        self.sw_feedback.pack(pady=20)

        ctk.CTkButton(self, text="COMENZAR EXAMEN", command=self.preparar_examen,
                      width=350, height=55, font=("Noto Sans", 18, "bold"), fg_color="#2E7D32").pack(pady=35)

    def cambiar_tema_variable(self, seleccion):
        self.tema_seleccionado = seleccion
        total = self.obtener_total_preguntas(seleccion)
        self.lbl_info_preguntas.configure(text=f"Total de preguntas en este banco: {total}  ")

    def gestionar_cantidad_manual(self, seleccion):
        if seleccion == "Otra cantidad...":
            dialogo = ctk.CTkInputDialog(text="Ingresa la cantidad de preguntas:", title="Cantidad Manual")
            valor = dialogo.get_input()
            if valor and valor.isdigit():
                self.cantidad_personalizada = int(valor)
                self.entry_cant.set(f"Manual: {valor}")
            else:
                messagebox.showwarning("Atención", "Ingresa un número válido.")
                self.entry_cant.set("MAXIMO")
        else:
            self.cantidad_personalizada = None

    def ajustar_tiempo(self, seleccion):
        self.minutos_configurados = int(seleccion.split()[0])

    def preparar_examen(self):
        tema = self.tema_seleccionado
        cant_sel = self.entry_cant.get()
        preguntas_totales = []

        try:
            if tema == "EXAMEN COMPLETO (TODOS LOS TEMAS)":
                for archivo in BANCO_DATOS.values():
                    # --- RUTA AJUSTADA ---
                    ruta_real = resource_path(archivo)
                    if os.path.exists(ruta_real):
                        with open(ruta_real, 'r', encoding='utf-8') as f:
                            preguntas_totales.extend(json.load(f))
            else:
                archivo = BANCO_DATOS.get(tema)
                # --- RUTA AJUSTADA ---
                with open(resource_path(archivo), 'r', encoding='utf-8') as f:
                    preguntas_totales = json.load(f)

            disponibles = len(preguntas_totales)
            
            if "Manual:" in cant_sel:
                deseadas = self.cantidad_personalizada
            elif cant_sel == "MAXIMO":
                deseadas = disponibles
            else:
                deseadas = disponibles

            if deseadas > disponibles:
                messagebox.showwarning(
                    "Ajuste de Cantidad", 
                    f"ATENCIÓN: El banco de '{tema}' solo tiene {disponibles} preguntas.\n\n"
                    f"Se procederá con el máximo disponible."
                )
                deseadas = disponibles 

            random.shuffle(preguntas_totales)
            self.preguntas_originales = preguntas_totales[:deseadas]
            self.iniciar_logica_examen(tema)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el banco: {e}")

    def iniciar_logica_examen(self, tema):
        self.categoria_actual = tema
        self.preguntas = list(self.preguntas_originales)
        self.indice_actual = 0
        self.omitidas = []
        self.respuestas_correctas = 0
        self.tiempo_restante = self.minutos_configurados * 60 
        self.configurar_interfaz_preguntas()
        self.after(10, self.actualizar_timer)
        self.after(50, self.cargar_pregunta)

    def configurar_interfaz_preguntas(self):
        self.limpiar_pantalla()
        color_fondo = "#CDD8E6"
        self.lbl_timer = ctk.CTkLabel(self, text="", font=("Noto Sans", 20, "bold"), text_color="#f83737")
        self.lbl_timer.pack(pady=(15, 5))

        self.main_frame = ctk.CTkFrame(self, fg_color=color_fondo)
        self.main_frame.pack(fill="both", expand=True, padx=40)
        self.main_frame.pack_propagate(False)

        self.lbl_pregunta = ctk.CTkLabel(self.main_frame, text="", font=("Noto Sans", 17, "bold"), 
                                         text_color="#000000", wraplength=550, height=150) 
        self.lbl_pregunta.pack(fill="x", pady=10)
        
        self.frame_opciones = ctk.CTkFrame(self.main_frame, fg_color=color_fondo)
        self.frame_opciones.pack(fill="both", expand=True, padx=20)
        
        self.var_opcion = tk.StringVar()

        ctk.CTkButton(self, text="CANCELAR Y SALIR", command=self.confirmar_salida, 
                      fg_color="#90A4AE", height=35, width=280).pack(side="bottom", pady=(0, 20))
        ctk.CTkButton(self, text="FINALIZAR AHORA", command=self.confirmar_finalizacion, 
                      fg_color="#546E7A", height=35, width=280).pack(side="bottom", pady=(0, 10))
        ctk.CTkButton(self, text="OMITIR PREGUNTA", command=self.omitir_pregunta, 
                      fg_color="#EF6C00", height=35, width=280).pack(side="bottom", pady=(0, 10))
        ctk.CTkButton(self, text="RESPONDER", command=self.verificar_respuesta, 
                      fg_color="#2E7D32", height=40, width=280, font=("Noto Sans", 13, "bold")).pack(side="bottom", pady=(0, 10))

    def cargar_pregunta(self):
        self.var_opcion.set("")
        for widget in self.frame_opciones.winfo_children(): widget.destroy()

        if self.indice_actual < len(self.preguntas):
            p = self.preguntas[self.indice_actual]
            self.lbl_pregunta.configure(text=f"[{self.categoria_actual}]\nPregunta {self.indice_actual + 1} de {len(self.preguntas)}\n\n{p['pregunta']}")
            opciones = list(p['opciones'])
            random.shuffle(opciones)
            for opc in opciones:
                ctk.CTkRadioButton(self.frame_opciones, text=opc, variable=self.var_opcion, value=opc,
                                   text_color="#000000", font=("Noto Sans", 14), fg_color="#1A237E").pack(fill="x", padx=30, pady=8)
            self.update()
        else:
            if self.omitidas:
                self.preguntas, self.omitidas, self.indice_actual = list(self.omitidas), [], 0
                messagebox.showinfo("Omitidas", "Revisando preguntas omitidas...")
                self.cargar_pregunta()
            else: self.finalizar_examen("Examen Completado")

    def verificar_respuesta(self):
        sel = self.var_opcion.get()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona una respuesta.")
            return

        p_act = self.preguntas[self.indice_actual]
        correcta = p_act.get('respuesta') or p_act.get('respuesta_correcta')

        if self.mostrar_feedback.get():
            if sel == correcta: messagebox.showinfo("Aviso", "¡CORRECTO!")
            else: messagebox.showerror("Aviso", "INCORRECTO")

        if sel == correcta: self.respuestas_correctas += 1
        self.indice_actual += 1
        self.cargar_pregunta()

    def omitir_pregunta(self):
        self.omitidas.append(self.preguntas[self.indice_actual])
        self.indice_actual += 1
        self.cargar_pregunta()

    def finalizar_examen(self, titulo):
        total = len(self.preguntas_originales)
        calif = (self.respuestas_correctas / total) * 10 if total > 0 else 0
        messagebox.showinfo(titulo, f"RESULTADOS: {self.categoria_actual}\n\nNota: {calif:.2f} / 10\nCorrectas: {self.respuestas_correctas} de {total}")
        self.mostrar_menu_seleccion()

    def actualizar_timer(self):
        if not hasattr(self, 'lbl_timer') or not self.lbl_timer.winfo_exists(): return 
        if self.tiempo_restante > 0:
            m, s = divmod(self.tiempo_restante, 60)
            self.lbl_timer.configure(text=f"TIEMPO RESTANTE: {m:02d}:{s:02d}")
            self.tiempo_restante -= 1
            self.after(1000, self.actualizar_timer)
        else: self.finalizar_examen("¡Tiempo Agotado!")

    def confirmar_salida(self):
        if messagebox.askyesno("Salir", "¿Cancelar examen?"): self.mostrar_menu_seleccion()

    def confirmar_finalizacion(self):
        if messagebox.askyesno("Finalizar", "¿Calificar ahora?"): self.finalizar_examen("Resultados")

if __name__ == "__main__":
    app = ExamenApp()
    app.mainloop()
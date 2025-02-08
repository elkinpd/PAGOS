import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os
from typing import Dict, List

class GestionPagosAtracos:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gestión de Pagos - GTA RP")
        self.root.geometry("1000x800")

        # Configuración de estilos
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=('Arial', 14, 'bold'))
        self.style.configure("Subtitle.TLabel", font=('Arial', 12, 'bold'))

        # Diccionario para almacenar los datos de los agentes
        self.agentes: Dict[str, List[dict]] = {}
        
        # Definición de tipos de atracos y sus pagos
        self.tipos_atracos = {
            "Tienditas": 75000,
            "Fleecas / Subterráneo": 100000,
            "Joyería": 100000,
            "Carnicería": 100000,
            "Humane": 250000,
            "Banco Central": 250000
        }

        # Cargar datos guardados si existen
        self.archivo_datos = "datos_pagos_gta.json"
        self.cargar_datos()
        
        self.crear_interfaz()

    def crear_interfaz(self):
        # Frame principal con scrollbar
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Canvas y scrollbar
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Empaquetado de elementos scroll
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Frame principal
        main_frame = ttk.Frame(self.scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Título principal
        ttk.Label(main_frame, text="Sistema de Gestión de Pagos - GTA RP", style="Title.TLabel").grid(row=0, column=0, columnspan=3, pady=10)

        # Frame izquierdo para gestión de agentes
        left_frame = ttk.LabelFrame(main_frame, text="Gestión de Agentes", padding="5")
        left_frame.grid(row=1, column=0, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Entrada para nuevo agente
        self.agente_var = tk.StringVar()
        ttk.Label(left_frame, text="Nombre del Agente:").grid(row=0, column=0, pady=5)
        self.entrada_agente = ttk.Entry(left_frame, textvariable=self.agente_var)
        self.entrada_agente.grid(row=0, column=1, pady=5)

        # Lista desplegable de agentes existentes
        ttk.Label(left_frame, text="Seleccionar Agente Existente:").grid(row=1, column=0, pady=5)
        self.combo_agentes = ttk.Combobox(left_frame, state="readonly")
        self.combo_agentes.grid(row=1, column=1, pady=5)
        
        # Botón para eliminar agente
        ttk.Button(left_frame, text="Eliminar Agente", command=self.eliminar_agente).grid(row=2, column=0, columnspan=2, pady=5)
        
        self.actualizar_lista_agentes()

        # Frame central para atracos
        center_frame = ttk.LabelFrame(main_frame, text="Registro de Atracos", padding="5")
        center_frame.grid(row=1, column=1, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Lista desplegable de tipos de atracos
        ttk.Label(center_frame, text="Tipo de Atraco:").grid(row=0, column=0, pady=5)
        self.combo_atracos = ttk.Combobox(center_frame, values=list(self.tipos_atracos.keys()), state="readonly")
        self.combo_atracos.grid(row=0, column=1, pady=5)

        # Campo para fecha
        ttk.Label(center_frame, text="Fecha:").grid(row=1, column=0, pady=5)
        self.fecha_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.entrada_fecha = ttk.Entry(center_frame, textvariable=self.fecha_var)
        self.entrada_fecha.grid(row=1, column=1, pady=5)

        # Comentarios
        ttk.Label(center_frame, text="Comentarios:").grid(row=2, column=0, pady=5)
        self.comentarios_text = tk.Text(center_frame, height=3, width=30)
        self.comentarios_text.grid(row=2, column=1, pady=5)

        # Botones de acción
        buttons_frame = ttk.Frame(center_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(buttons_frame, text="Registrar Participación", command=self.registrar_participacion).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Eliminar Último Registro", command=self.eliminar_ultimo_registro).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Guardar Datos", command=self.guardar_datos).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Limpiar Todos los Datos", command=self.limpiar_todos_datos).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Eliminar Todos los Registros de Robos", 
                  command=self.eliminar_todos_registros_robos).pack(side=tk.LEFT, padx=5)

        # Frame para búsqueda y filtros
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros y Búsqueda", padding="5")
        filter_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

        self.busqueda_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.busqueda_var).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Buscar", command=self.buscar_registros).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Limpiar Filtros", command=self.limpiar_filtros).pack(side=tk.LEFT, padx=5)

        # Área de resumen
        ttk.Label(main_frame, text="Resumen de Pagos", style="Subtitle.TLabel").grid(row=3, column=0, columnspan=3, pady=10)
        
        self.resumen_text = tk.Text(main_frame, height=15, width=80)
        self.resumen_text.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Estadísticas
        stats_frame = ttk.LabelFrame(main_frame, text="Estadísticas", padding="5")
        stats_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        self.stats_text = tk.Text(stats_frame, height=5, width=80)
        self.stats_text.pack(pady=5)

        self.mostrar_resumen()
        self.actualizar_estadisticas()

    def eliminar_todos_registros_robos(self):
        """Elimina todos los registros de robos de todos los agentes sin eliminar a los agentes"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar TODOS los registros de robos de todos los agentes? Esta acción no se puede deshacer."):
            # Mantener la lista de agentes pero limpiar sus registros
            for agente in self.agentes:
                self.agentes[agente] = []
            
            self.mostrar_resumen()
            self.actualizar_estadisticas()
            self.guardar_datos()
            messagebox.showinfo("Éxito", "Todos los registros de robos han sido eliminados")

    def eliminar_agente(self):
        """Elimina un agente y todos sus registros"""
        agente = self.combo_agentes.get()
        if not agente:
            messagebox.showerror("Error", "Debe seleccionar un agente para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar al agente {agente} y todos sus registros?"):
            del self.agentes[agente]
            self.actualizar_lista_agentes()
            self.mostrar_resumen()
            self.actualizar_estadisticas()
            self.guardar_datos()
            messagebox.showinfo("Éxito", f"Agente {agente} eliminado correctamente")

    def limpiar_todos_datos(self):
        """Limpia todos los datos de la aplicación"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar TODOS los datos? Esta acción no se puede deshacer."):
            self.agentes.clear()
            self.actualizar_lista_agentes()
            self.mostrar_resumen()
            self.actualizar_estadisticas()
            self.guardar_datos()
            messagebox.showinfo("Éxito", "Todos los datos han sido eliminados")

    def actualizar_lista_agentes(self):
        """Actualiza la lista desplegable de agentes"""
        self.combo_agentes['values'] = sorted(list(self.agentes.keys()))
        self.combo_agentes.set('')  # Limpiar la selección actual

    def registrar_participacion(self):
        """Registra la participación de un agente en un atraco"""
        agente = self.agente_var.get().strip()
        atraco_seleccionado = self.combo_atracos.get()
        fecha = self.fecha_var.get()
        comentarios = self.comentarios_text.get("1.0", tk.END).strip()

        if not agente and not self.combo_agentes.get():
            messagebox.showerror("Error", "Debe ingresar o seleccionar un agente")
            return
        
        if not atraco_seleccionado:
            messagebox.showerror("Error", "Debe seleccionar un tipo de atraco")
            return

        if not agente:
            agente = self.combo_agentes.get()

        if agente not in self.agentes:
            self.agentes[agente] = []
            self.actualizar_lista_agentes()

        # Registrar participación con más detalles
        monto = self.tipos_atracos[atraco_seleccionado]
        registro = {
            "tipo_atraco": atraco_seleccionado,
            "monto": monto,
            "fecha": fecha,
            "comentarios": comentarios,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.agentes[agente].append(registro)
        
        messagebox.showinfo("Éxito", f"Participación registrada para {agente}")
        self.mostrar_resumen()
        self.actualizar_estadisticas()
        self.guardar_datos()
        
        # Limpiar campos
        self.agente_var.set("")
        self.combo_atracos.set("")
        self.comentarios_text.delete("1.0", tk.END)

    def eliminar_ultimo_registro(self):
        """Elimina el último registro del agente seleccionado"""
        agente = self.combo_agentes.get()
        if not agente:
            messagebox.showerror("Error", "Debe seleccionar un agente")
            return
        
        if agente in self.agentes and self.agentes[agente]:
            if messagebox.askyesno("Confirmar", f"¿Desea eliminar el último registro de {agente}?"):
                self.agentes[agente].pop()
                self.mostrar_resumen()
                self.actualizar_estadisticas()
                self.guardar_datos()
                messagebox.showinfo("Éxito", "Registro eliminado")
        else:
            messagebox.showinfo("Info", "No hay registros para eliminar")

    def buscar_registros(self):
        """Filtra los registros según el término de búsqueda"""
        busqueda = self.busqueda_var.get().lower()
        self.mostrar_resumen(filtro=busqueda)

    def limpiar_filtros(self):
        """Limpia los filtros de búsqueda"""
        self.busqueda_var.set("")
        self.mostrar_resumen()

    def mostrar_resumen(self, filtro=""):
        """Muestra el resumen de pagos de todos los agentes"""
        self.resumen_text.delete(1.0, tk.END)
        for agente, participaciones in sorted(self.agentes.items()):
            if filtro and filtro not in agente.lower():
                continue
                
            total = sum(p["monto"] for p in participaciones)
            resumen = f"\nAgente: {agente}\n"
            resumen += "Participaciones:\n"
            
            for p in reversed(participaciones):  # Mostrar los más recientes primero
                if filtro and filtro not in str(p).lower():
                    continue
                resumen += f"- {p['fecha']}: {p['tipo_atraco']}: ${p['monto']:,}"
                if p['comentarios']:
                    resumen += f" - {p['comentarios']}"
                resumen += "\n"
                
            resumen += f"Total: ${total:,}\n"
            resumen += "-" * 60 + "\n"
            self.resumen_text.insert(tk.END, resumen)

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas generales"""
        total_global = sum(sum(p["monto"] for p in participaciones) 
                          for participaciones in self.agentes.values())
        total_atracos = sum(len(participaciones) for participaciones in self.agentes.values())
        promedio_por_atraco = total_global / total_atracos if total_atracos > 0 else 0

        stats = f"Estadísticas Globales:\n"
        stats += f"Total pagado: ${total_global:,}\n"
        stats += f"Total de atracos: {total_atracos}\n"
        stats += f"Promedio por atraco: ${promedio_por_atraco:,.2f}\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats)

    def guardar_datos(self):
        """Guarda los datos en un archivo JSON"""
        try:
            with open(self.archivo_datos, 'w', encoding='utf-8') as f:
                json.dump(self.agentes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")

    def cargar_datos(self):
        """Carga los datos desde el archivo JSON"""
        try:
            if os.path.exists(self.archivo_datos):
                with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                    self.agentes = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")

    def iniciar(self):
        """Inicia la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    app = GestionPagosAtracos()
    app.iniciar()
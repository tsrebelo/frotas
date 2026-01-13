import datetime
import csv
import json
from tkinter import ttk, messagebox
import customtkinter as ctk

# ==================== CONFIGURAÇÃO ====================
ctk.set_appearance_mode("dark")

# ==================== DECORADOR ====================
def log_operation(func):
    def wrapper(*args, **kwargs):
        now = datetime.datetime.now()
        print(f"[{now.strftime('%d-%m-%Y %H:%M:%S')}] Executando: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

# ==================== CLASSES DE VEÍCULOS ====================
class Vehicle:
    def __init__(self, brand, model, price, year):
        self.brand = brand
        self.model = model
        self.price = price
        self.year = year
        self.registration_date = datetime.datetime.now()
    
    def calculate_tax(self):
        return self.price * 0.23
    
    def __str__(self):
        return f"{self.brand} {self.model} - €{self.price:.2f} (Ano: {self.year})"
    
    def to_dict(self):
        return {
            'type': self.__class__.__name__,
            'brand': self.brand,
            'model': self.model,
            'price': self.price,
            'year': self.year,
            'tax': self.calculate_tax(),
            'registration_date': self.registration_date.strftime('%d-%m-%Y %H:%M:%S')
        }

class ElectricCar(Vehicle):
    def __init__(self, brand, model, price, year, battery_capacity, autonomy):
        super().__init__(brand, model, price, year)
        self.battery_capacity = battery_capacity
        self.autonomy = autonomy
    
    def calculate_tax(self):
        return super().calculate_tax() * 0.5
    
    def __str__(self):
        return f"{self.brand} {self.model} (Elétrico) - €{self.price:.2f} - Bateria: {self.battery_capacity}kWh - Autonomia: {self.autonomy}km"

class Truck(Vehicle):
    def __init__(self, brand, model, price, year, load_capacity, length):
        super().__init__(brand, model, price, year)
        self.load_capacity = load_capacity
        self.length = length
    
    def calculate_tax(self):
        return super().calculate_tax() * 1.3
    
    def __str__(self):
        return f"{self.brand} {self.model} (Camião) - €{self.price:.2f} - Carga: {self.load_capacity}t - Comprimento: {self.length}m"

# ==================== GESTÃO DA FROTA ====================
class Fleet:
    def __init__(self):
        self.vehicles = []
    
    @log_operation
    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)
        return True
    
    @log_operation
    def remove_vehicle(self, index):
        if 0 <= index < len(self.vehicles):
            return self.vehicles.pop(index)
        return None
    
    # Função lambda para aplicar desconto
    def apply_global_discount(self, percentage):
        adjust_price = lambda price, perc: price * (1 - perc/100)
        for vehicle in self.vehicles:
            vehicle.price = adjust_price(vehicle.price, percentage)
        return len(self.vehicles)
    
    # Compreensão de listas para filtros
    def filter_by_brand(self, brand):
        return [v for v in self.vehicles if v.brand.lower() == brand.lower()]
    
    def filter_by_year(self, min_year):
        return [v for v in self.vehicles if v.year >= min_year]
    
    def filter_by_type(self, vehicle_type):
        return [v for v in self.vehicles if v.__class__.__name__ == vehicle_type]
    
    # Exportação para ficheiros
    def export_inventory(self, filename, format_type='csv'):
        if not self.vehicles:
            return False, "Não há veículos para exportar!"
        
        try:
            if format_type == 'txt':
                self._export_txt(filename)
            elif format_type == 'csv':
                self._export_csv(filename)
            elif format_type == 'json':
                self._export_json(filename)
            else:
                return False, "Formato não suportado!"
            
            return True, f"Inventário exportado para '{filename}'!"
        except Exception as e:
            return False, f"Erro ao exportar: {str(e)}"
    
    def _export_txt(self, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            file.write("=" * 50 + "\n")
            file.write("INVENTÁRIO DA FROTA\n")
            file.write(f"Data de exportação: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n")
            file.write("=" * 50 + "\n\n")
            
            for i, vehicle in enumerate(self.vehicles, 1):
                file.write(f"VEÍCULO {i}:\n")
                file.write(f"  Tipo: {vehicle.__class__.__name__}\n")
                file.write(f"  Marca: {vehicle.brand}\n")
                file.write(f"  Modelo: {vehicle.model}\n")
                file.write(f"  Preço: €{vehicle.price:.2f}\n")
                file.write(f"  Imposto: €{vehicle.calculate_tax():.2f}\n")
                file.write(f"  Ano: {vehicle.year}\n")
                
                if isinstance(vehicle, ElectricCar):
                    file.write(f"  Capacidade da bateria: {vehicle.battery_capacity}kWh\n")
                    file.write(f"  Autonomia: {vehicle.autonomy}km\n")
                elif isinstance(vehicle, Truck):
                    file.write(f"  Capacidade de carga: {vehicle.load_capacity}t\n")
                    file.write(f"  Comprimento: {vehicle.length}m\n")
                
                file.write("\n" + "-" * 40 + "\n\n")
            
            # Resumo
            total_value = sum(v.price for v in self.vehicles)
            total_tax = sum(v.calculate_tax() for v in self.vehicles)
            
            file.write("=" * 50 + "\n")
            file.write("RESUMO DA FROTA\n")
            file.write(f"Total de veículos: {len(self.vehicles)}\n")
            file.write(f"Valor total da frota: €{total_value:.2f}\n")
            file.write(f"Imposto total: €{total_tax:.2f}\n")
            file.write("=" * 50 + "\n")
    
    def _export_csv(self, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            fields = ['type', 'brand', 'model', 'price', 'tax', 'year', 
                     'battery_capacity', 'autonomy', 'load_capacity', 
                     'length', 'registration_date']
            
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            
            for vehicle in self.vehicles:
                data = vehicle.to_dict()
                # Adicionar campos específicos
                if isinstance(vehicle, ElectricCar):
                    data['battery_capacity'] = vehicle.battery_capacity
                    data['autonomy'] = vehicle.autonomy
                elif isinstance(vehicle, Truck):
                    data['load_capacity'] = vehicle.load_capacity
                    data['length'] = vehicle.length
                writer.writerow(data)
    
    def _export_json(self, filename):
        data = {
            'export_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_vehicles': len(self.vehicles),
            'total_value': sum(v.price for v in self.vehicles),
            'total_tax': sum(v.calculate_tax() for v in self.vehicles),
            'vehicles': [vehicle.to_dict() for vehicle in self.vehicles]
        }
        
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    
    def get_summary(self):
        if not self.vehicles:
            return {'total': 0, 'total_value': 0, 'total_tax': 0, 'by_type': {}}
        
        summary = {
            'total': len(self.vehicles),
            'total_value': sum(v.price for v in self.vehicles),
            'total_tax': sum(v.calculate_tax() for v in self.vehicles),
            'by_type': {}
        }
        
        for vehicle in self.vehicles:
            vehicle_type = vehicle.__class__.__name__
            summary['by_type'][vehicle_type] = summary['by_type'].get(vehicle_type, 0) + 1
        
        return summary

# ==================== INTERFACE GRÁFICA ====================
class FleetManagementApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.fleet = Fleet()
        self.setup_ui()
        self.load_sample_data()
    
    def setup_ui(self):
        self.title("Sistema de Gestão de Frotas")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Container principal
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()
        self.show_dashboard()
    
    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self.main_container, width=200, corner_radius=10)
        sidebar.pack(side="left", fill="y", padx=(0, 10), pady=10)
        
        ctk.CTkLabel(sidebar, text="Gestor de Frotas", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 30))
        
        # Botões de navegação
        buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("🚗 Adicionar Veículo", self.show_add_vehicle),
            ("🗑️ Remover Veículo", self.show_remove_vehicle),
            ("💰 Aplicar Desconto", self.show_discount),
            ("📋 Inventário", self.show_inventory),
            ("📤 Exportar", self.show_export),
            ("⚙️ Definições", self.show_settings)
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(sidebar, text=text, command=command, height=40, corner_radius=8)
            btn.pack(pady=5, padx=10)
        
        ctk.CTkLabel(sidebar, text="Versão 1.0.0\n© 2024 Gestão de Frotas", font=ctk.CTkFont(size=10)).pack(side="bottom", pady=10)
    
    def create_main_content(self):
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.content_frame.pack(side="right", fill="both", expand=True, pady=10)
        
        self.content_title = ctk.CTkLabel(self.content_frame, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        self.content_title.pack(pady=(20, 10))
        
        self.content_container = ctk.CTkScrollableFrame(self.content_frame, corner_radius=10)
        self.content_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def create_status_bar(self):
        status_bar = ctk.CTkFrame(self, height=30)
        status_bar.pack(side="bottom", fill="x")
        
        self.status_label = ctk.CTkLabel(status_bar, text="Pronto", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left", padx=10)
        
        self.update_status()
    
    def update_status(self, message="Pronto"):
        self.status_label.configure(text=message)
    
    def clear_content(self):
        for widget in self.content_container.winfo_children():
            widget.destroy()
    
    # ==================== VIEWS ====================
    
    def show_dashboard(self):
        self.clear_content()
        self.content_title.configure(text="Dashboard")
        
        summary = self.fleet.get_summary()
        
        # Estatísticas
        stats_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        stats_data = [
            ("Total Veículos", f"{summary['total']}", "#4CC9F0"),
            ("Valor Total", f"€{summary['total_value']:,.2f}", "#4361EE"),
            ("Imposto Total", f"€{summary['total_tax']:,.2f}", "#3A0CA3"),
            ("Valor Médio", f"€{summary['total_value']/max(summary['total'], 1):,.2f}", "#7209B7")
        ]
        
        row_frame = ctk.CTkFrame(stats_frame)
        row_frame.pack(fill="x", padx=20, pady=20)
        
        for title, value, color in stats_data:
            card = ctk.CTkFrame(row_frame, height=100, corner_radius=10)
            card.pack(side="left", padx=10, expand=True, fill="both")
            
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14)).pack(pady=(15, 5))
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"), text_color=color).pack(pady=5)
        
        # Distribuição por tipo
        if summary['by_type']:
            dist_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
            dist_frame.pack(fill="x", pady=(0, 20))
            
            ctk.CTkLabel(dist_frame, text="Distribuição por Tipo", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
            
            for vehicle_type, count in summary['by_type'].items():
                type_frame = ctk.CTkFrame(dist_frame, height=40)
                type_frame.pack(fill="x", padx=20, pady=5)
                
                ctk.CTkLabel(type_frame, text=vehicle_type, font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
                
                progress = (count / summary['total']) * 100
                progress_bar = ctk.CTkProgressBar(type_frame)
                progress_bar.pack(side="left", padx=10, expand=True, fill="x")
                progress_bar.set(progress / 100)
                
                ctk.CTkLabel(type_frame, text=f"{count} ({progress:.1f}%)", font=ctk.CTkFont(size=14)).pack(side="right", padx=10)
        
        # Veículos recentes
        if self.fleet.vehicles:
            recent_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
            recent_frame.pack(fill="x")
            
            ctk.CTkLabel(recent_frame, text="Veículos Recentes", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
            
            for vehicle in self.fleet.vehicles[-5:]:
                vehicle_frame = ctk.CTkFrame(recent_frame, height=50)
                vehicle_frame.pack(fill="x", padx=20, pady=5)
                
                ctk.CTkLabel(vehicle_frame, text=str(vehicle), font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
                ctk.CTkLabel(vehicle_frame, text=f"Imposto: €{vehicle.calculate_tax():.2f}", font=ctk.CTkFont(size=12)).pack(side="right", padx=10)
    
    def show_add_vehicle(self):
        self.clear_content()
        self.content_title.configure(text="Adicionar Veículo")
        
        form_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        form_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        # Tipo de veículo
        ctk.CTkLabel(form_frame, text="Tipo de Veículo:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        self.vehicle_type = ctk.StringVar(value="Vehicle")
        type_combo = ctk.CTkComboBox(form_frame, values=["Vehicle", "ElectricCar", "Truck"], variable=self.vehicle_type, command=self.update_form_fields, width=200)
        type_combo.grid(row=0, column=1, padx=20, pady=20, sticky="w")
        
        # Campos comuns
        self.entries = {}
        fields = [("Marca:", "brand"), ("Modelo:", "model"), ("Preço (€):", "price"), ("Ano:", "year")]
        
        for i, (label, key) in enumerate(fields, 1):
            ctk.CTkLabel(form_frame, text=label, font=ctk.CTkFont(size=14)).grid(row=i, column=0, padx=20, pady=10, sticky="w")
            entry = ctk.CTkEntry(form_frame, width=200)
            entry.grid(row=i, column=1, padx=20, pady=10, sticky="w")
            self.entries[key] = entry
        
        # Campos específicos
        self.special_frame = ctk.CTkFrame(form_frame, corner_radius=10)
        self.special_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        
        # Botões
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=30)
        
        ctk.CTkButton(button_frame, text="Adicionar Veículo", command=self.add_vehicle, height=40, width=150).pack(side="left", padx=20)
        ctk.CTkButton(button_frame, text="Limpar Formulário", command=self.clear_form, height=40, width=150, fg_color="gray").pack(side="left", padx=20)
        
        self.update_form_fields()
    
    def update_form_fields(self):
        for widget in self.special_frame.winfo_children():
            widget.destroy()
        
        vehicle_type = self.vehicle_type.get()
        
        if vehicle_type == "ElectricCar":
            fields = [("Capacidade Bateria (kWh):", "battery"), ("Autonomia (km):", "autonomy")]
        elif vehicle_type == "Truck":
            fields = [("Capacidade Carga (ton):", "load"), ("Comprimento (m):", "length")]
        else:
            return
        
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(self.special_frame, text=label, font=ctk.CTkFont(size=14)).grid(row=i, column=0, padx=20, pady=10, sticky="w")
            entry = ctk.CTkEntry(self.special_frame, width=200)
            entry.grid(row=i, column=1, padx=20, pady=10, sticky="w")
            self.entries[key] = entry
    
    def add_vehicle(self):
        try:
            brand = self.entries['brand'].get()
            model = self.entries['model'].get()
            price = float(self.entries['price'].get())
            year = int(self.entries['year'].get())
            
            vehicle_type = self.vehicle_type.get()
            
            if vehicle_type == "Vehicle":
                vehicle = Vehicle(brand, model, price, year)
            elif vehicle_type == "ElectricCar":
                battery = float(self.entries['battery'].get())
                autonomy = float(self.entries['autonomy'].get())
                vehicle = ElectricCar(brand, model, price, year, battery, autonomy)
            elif vehicle_type == "Truck":
                load = float(self.entries['load'].get())
                length = float(self.entries['length'].get())
                vehicle = Truck(brand, model, price, year, load, length)
            
            self.fleet.add_vehicle(vehicle)
            messagebox.showinfo("Sucesso", f"Veículo adicionado!\n\n{vehicle}")
            self.clear_form()
            self.update_status(f"Adicionado {brand} {model}")
            self.show_dashboard()
            
        except ValueError:
            messagebox.showerror("Erro", "Por favor, introduza valores válidos!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
    
    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, 'end')
    
    def show_remove_vehicle(self):
        self.clear_content()
        self.content_title.configure(text="Remover Veículo")
        
        if not self.fleet.vehicles:
            ctk.CTkLabel(self.content_container, text="Não há veículos na frota!", font=ctk.CTkFont(size=16)).pack(pady=50)
            return
        
        # Tabela de veículos
        list_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        list_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        columns = ("#", "Tipo", "Marca", "Modelo", "Preço", "Ano", "Imposto")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("#", width=50)
        self.tree.column("Tipo", width=100)
        self.tree.column("Marca", width=100)
        self.tree.column("Modelo", width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Preencher tabela
        for i, vehicle in enumerate(self.fleet.vehicles, 1):
            self.tree.insert("", "end", values=(
                i,
                vehicle.__class__.__name__,
                vehicle.brand,
                vehicle.model,
                f"€{vehicle.price:.2f}",
                vehicle.year,
                f"€{vehicle.calculate_tax():.2f}"
            ))
        
        # Botão de remover
        button_frame = ctk.CTkFrame(self.content_container)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="Remover Veículo Selecionado", command=self.remove_selected, height=40, width=200, fg_color="#D32F2F").pack(pady=10)
    
    def remove_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um veículo para remover!")
            return
        
        item = self.tree.item(selection[0])
        index = int(item['values'][0]) - 1
        
        if messagebox.askyesno("Confirmar", f"Remover {item['values'][2]} {item['values'][3]}?"):
            vehicle = self.fleet.remove_vehicle(index)
            if vehicle:
                self.tree.delete(selection[0])
                self.update_status(f"Removido {vehicle.brand} {vehicle.model}")
                messagebox.showinfo("Sucesso", "Veículo removido!")
                
                # Renumerar itens
                for i, item_id in enumerate(self.tree.get_children(), 1):
                    values = list(self.tree.item(item_id, 'values'))
                    values[0] = i
                    self.tree.item(item_id, values=values)
    
    def show_discount(self):
        self.clear_content()
        self.content_title.configure(text="Aplicar Desconto/Imposto")
        
        discount_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        discount_frame.pack(fill="x", padx=100, pady=50)
        
        ctk.CTkLabel(discount_frame, text="Aplicar percentagem de desconto (positivo) ou imposto (negativo) a todos os veículos", font=ctk.CTkFont(size=14), wraplength=400).pack(pady=(30, 20))
        
        input_frame = ctk.CTkFrame(discount_frame)
        input_frame.pack(pady=20)
        
        ctk.CTkLabel(input_frame, text="Percentagem:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
        self.percentage_entry = ctk.CTkEntry(input_frame, width=100)
        self.percentage_entry.pack(side="left")
        ctk.CTkLabel(input_frame, text="%", font=ctk.CTkFont(size=14)).pack(side="left", padx=(5, 20))
        
        ctk.CTkLabel(discount_frame, text="Exemplo: +10% = 10% desconto, -5% = 5% imposto extra", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=10)
        
        button_frame = ctk.CTkFrame(discount_frame)
        button_frame.pack(pady=30)
        
        ctk.CTkButton(button_frame, text="Aplicar a Todos", command=self.apply_discount, height=40, width=200).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Pré-visualizar", command=self.preview_discount, height=40, width=200, fg_color="gray").pack(side="left", padx=10)
    
    def apply_discount(self):
        try:
            percentage = float(self.percentage_entry.get())
            
            if messagebox.askyesno("Confirmar", f"Aplicar {percentage}% {'desconto' if percentage > 0 else 'imposto extra'} a todos os veículos?"):
                count = self.fleet.apply_global_discount(percentage)
                messagebox.showinfo("Sucesso", f"Aplicado a {count} veículos!")
                self.update_status(f"Aplicado {percentage}% a todos")
                self.show_dashboard()
        except ValueError:
            messagebox.showerror("Erro", "Introduza uma percentagem válida!")
    
    def preview_discount(self):
        try:
            percentage = float(self.percentage_entry.get())
            
            preview_window = ctk.CTkToplevel(self)
            preview_window.title("Pré-visualização de Desconto")
            preview_window.geometry("600x400")
            
            columns = ("Marca", "Modelo", "Preço Antigo", "Preço Novo", "Variação")
            tree = ttk.Treeview(preview_window, columns=columns, show="headings", height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            scrollbar = ttk.Scrollbar(preview_window, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y")
            
            # Calcular novos preços
            adjust_price = lambda price, perc: price * (1 - perc/100)
            
            for vehicle in self.fleet.vehicles:
                new_price = adjust_price(vehicle.price, percentage)
                change = new_price - vehicle.price
                change_percent = (change / vehicle.price) * 100 if vehicle.price != 0 else 0
                
                tree.insert("", "end", values=(
                    vehicle.brand,
                    vehicle.model,
                    f"€{vehicle.price:.2f}",
                    f"€{new_price:.2f}",
                    f"{change_percent:+.1f}%"
                ))
            
            # Resumo
            total_old = sum(v.price for v in self.fleet.vehicles)
            total_new = sum(adjust_price(v.price, percentage) for v in self.fleet.vehicles)
            
            ctk.CTkLabel(preview_window, text=f"Variação total: €{total_new - total_old:+.2f}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
            
        except ValueError:
            messagebox.showerror("Erro", "Introduza uma percentagem válida!")
    
    def show_inventory(self):
        self.clear_content()
        self.content_title.configure(text="Inventário")
        
        inventory_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        inventory_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Filtros
        filters_frame = ctk.CTkFrame(inventory_frame)
        filters_frame.pack(fill="x", pady=20, padx=20)
        
        # Filtro por marca
        brand_frame = ctk.CTkFrame(filters_frame)
        brand_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(brand_frame, text="Filtrar por Marca:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
        self.brand_filter = ctk.CTkEntry(brand_frame, width=150)
        self.brand_filter.pack(side="left")
        ctk.CTkButton(brand_frame, text="Filtrar", command=lambda: self.filter_inventory('brand'), width=80).pack(side="left", padx=10)
        
        # Filtro por ano
        year_frame = ctk.CTkFrame(filters_frame)
        year_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(year_frame, text="Filtrar por Ano (mínimo):", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
        self.year_filter = ctk.CTkEntry(year_frame, width=150)
        self.year_filter.pack(side="left")
        ctk.CTkButton(year_frame, text="Filtrar", command=lambda: self.filter_inventory('year'), width=80).pack(side="left", padx=10)
        
        # Filtro por tipo
        type_frame = ctk.CTkFrame(filters_frame)
        type_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(type_frame, text="Filtrar por Tipo:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
        self.type_filter = ctk.StringVar(value="Todos")
        ctk.CTkComboBox(type_frame, values=["Todos", "Vehicle", "ElectricCar", "Truck"], variable=self.type_filter, width=150).pack(side="left")
        ctk.CTkButton(type_frame, text="Filtrar", command=lambda: self.filter_inventory('type'), width=80).pack(side="left", padx=10)
        
        ctk.CTkButton(filters_frame, text="Mostrar Todos", command=lambda: self.filter_inventory('all'), width=150, fg_color="gray").pack(pady=20)
        
        # Tabela de resultados
        self.results_frame = ctk.CTkFrame(inventory_frame)
        self.results_frame.pack(fill="both", expand=True, pady=20, padx=20)
        
        self.filter_inventory('all')
    
    def filter_inventory(self, filter_type):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        if filter_type == 'brand':
            brand = self.brand_filter.get()
            vehicles = self.fleet.filter_by_brand(brand) if brand else self.fleet.vehicles
        elif filter_type == 'year':
            try:
                year = int(self.year_filter.get())
                vehicles = self.fleet.filter_by_year(year)
            except:
                vehicles = self.fleet.vehicles
        elif filter_type == 'type':
            vehicle_type = self.type_filter.get()
            vehicles = self.fleet.vehicles if vehicle_type == "Todos" else self.fleet.filter_by_type(vehicle_type)
        else:
            vehicles = self.fleet.vehicles
        
        if not vehicles:
            ctk.CTkLabel(self.results_frame, text="Nenhum veículo encontrado", font=ctk.CTkFont(size=14)).pack(pady=50)
            return
        
        # Criar tabela
        columns = ("Marca", "Modelo", "Tipo", "Preço", "Ano", "Imposto")
        tree = ttk.Treeview(self.results_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.column("Marca", width=120)
        tree.column("Modelo", width=150)
        
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for vehicle in vehicles:
            tree.insert("", "end", values=(
                vehicle.brand,
                vehicle.model,
                vehicle.__class__.__name__,
                f"€{vehicle.price:.2f}",
                vehicle.year,
                f"€{vehicle.calculate_tax():.2f}"
            ))
        
        ctk.CTkLabel(self.results_frame, text=f"Encontrados {len(vehicles)} veículo(s)", font=ctk.CTkFont(size=12)).pack(pady=10)
    
    def show_export(self):
        self.clear_content()
        self.content_title.configure(text="Exportar Inventário")
        
        export_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        export_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        # Formato
        ctk.CTkLabel(export_frame, text="Formato de Exportação:", font=ctk.CTkFont(size=16)).pack(pady=(0, 20))
        
        self.export_format = ctk.StringVar(value="csv")
        formats = [("CSV (Excel)", "csv"), ("Texto (legível)", "txt"), ("JSON (estruturado)", "json")]
        
        for text, value in formats:
            ctk.CTkRadioButton(export_frame, text=text, variable=self.export_format, value=value).pack(pady=5)
        
        # Nome do ficheiro
        file_frame = ctk.CTkFrame(export_frame)
        file_frame.pack(pady=20)
        
        ctk.CTkLabel(file_frame, text="Nome do Ficheiro:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
        self.filename = ctk.CTkEntry(file_frame, width=200)
        self.filename.pack(side="left")
        self.filename.insert(0, f"frota_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Botões
        button_frame = ctk.CTkFrame(export_frame)
        button_frame.pack(pady=30)
        
        ctk.CTkButton(button_frame, text="Exportar", command=self.export_data, height=40, width=200).pack(pady=10)
        ctk.CTkButton(button_frame, text="Pré-visualizar", command=self.preview_export, height=40, width=200, fg_color="gray").pack(pady=10)
    
    def export_data(self):
        filename = self.filename.get()
        format_type = self.export_format.get()
        
        if not filename.endswith(f'.{format_type}'):
            filename += f'.{format_type}'
        
        success, message = self.fleet.export_inventory(filename, format_type)
        
        if success:
            messagebox.showinfo("Sucesso", message)
            self.update_status(f"Exportado para {filename}")
        else:
            messagebox.showerror("Erro", message)
    
    def preview_export(self):
        if not self.fleet.vehicles:
            messagebox.showinfo("Info", "Não há veículos para pré-visualizar!")
            return
        
        preview_window = ctk.CTkToplevel(self)
        preview_window.title("Pré-visualização de Exportação")
        preview_window.geometry("800x500")
        
        text_widget = ctk.CTkTextbox(preview_window, font=ctk.CTkFont(family="Courier", size=12))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        preview_text = "PRÉ-VISUALIZAÇÃO DE EXPORTAÇÃO\n"
        preview_text += "=" * 50 + "\n\n"
        
        for i, vehicle in enumerate(self.fleet.vehicles[:5], 1):
            preview_text += f"Veículo {i}:\n"
            preview_text += f"  Tipo: {vehicle.__class__.__name__}\n"
            preview_text += f"  Marca: {vehicle.brand}\n"
            preview_text += f"  Modelo: {vehicle.model}\n"
            preview_text += f"  Preço: €{vehicle.price:.2f}\n"
            preview_text += f"  Imposto: €{vehicle.calculate_tax():.2f}\n"
            preview_text += f"  Ano: {vehicle.year}\n"
            
            if isinstance(vehicle, ElectricCar):
                preview_text += f"  Bateria: {vehicle.battery_capacity}kWh\n"
                preview_text += f"  Autonomia: {vehicle.autonomy}km\n"
            elif isinstance(vehicle, Truck):
                preview_text += f"  Carga: {vehicle.load_capacity}t\n"
                preview_text += f"  Comprimento: {vehicle.length}m\n"
            
            preview_text += "\n"
        
        if len(self.fleet.vehicles) > 5:
            preview_text += f"... e mais {len(self.fleet.vehicles) - 5} veículos\n\n"
        
        summary = self.fleet.get_summary()
        preview_text += "=" * 50 + "\n"
        preview_text += f"Total veículos: {summary['total']}\n"
        preview_text += f"Valor total: €{summary['total_value']:.2f}\n"
        preview_text += f"Imposto total: €{summary['total_tax']:.2f}\n"
        preview_text += "=" * 50
        
        text_widget.insert("1.0", preview_text)
        text_widget.configure(state="disabled")
    
    def show_settings(self):
        self.clear_content()
        self.content_title.configure(text="Definições")
        
        settings_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        settings_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        # Aparência
        appearance_frame = ctk.CTkFrame(settings_frame)
        appearance_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(appearance_frame, text="Aparência", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 10))
        
        ctk.CTkLabel(appearance_frame, text="Tema:", font=ctk.CTkFont(size=14)).pack(pady=5)
        theme = ctk.StringVar(value=ctk.get_appearance_mode())
        ctk.CTkComboBox(appearance_frame, values=["dark", "light", "system"], variable=theme, command=lambda v: ctk.set_appearance_mode(v), width=150).pack(pady=5)
        
        # Informação do sistema
        info_frame = ctk.CTkFrame(settings_frame)
        info_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(info_frame, text="Informação do Sistema", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 10))
        
        info_text = f"""
        Sistema de Gestão de Frotas v1.0.0
        Veículos no sistema: {len(self.fleet.vehicles)}
        Última atualização: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Funcionalidades:
        • Gestão de veículos (adicionar/remover)
        • Cálculo de impostos (IVA 23%)
        • Aplicação de descontos
        • Filtros e pesquisa
        • Exportação para múltiplos formatos
        """
        
        ctk.CTkLabel(info_frame, text=info_text, font=ctk.CTkFont(size=12), justify="left").pack(pady=10)
        
        # Botão para dados de exemplo
        ctk.CTkButton(settings_frame, text="Carregar Dados de Exemplo", command=self.load_sample_data, height=40, fg_color="gray").pack(pady=20)
    
    def load_sample_data(self):
        self.fleet.vehicles.clear()
        
        sample_vehicles = [
            Vehicle("Toyota", "Corolla", 25000, 2022),
            Vehicle("Ford", "Focus", 22000, 2021),
            ElectricCar("Tesla", "Model 3", 45000, 2023, 75, 500),
            ElectricCar("Nissan", "Leaf", 32000, 2022, 40, 270),
            Truck("Mercedes", "Actros", 85000, 2020, 18, 12.5),
            Truck("Volvo", "FH", 92000, 2021, 20, 13.2),
            Vehicle("BMW", "3 Series", 42000, 2023),
            ElectricCar("Hyundai", "Kona Electric", 38000, 2022, 64, 450),
            Vehicle("Volkswagen", "Golf", 28000, 2021),
            Truck("MAN", "TGX", 78000, 2019, 16, 11.8)
        ]
        
        for vehicle in sample_vehicles:
            self.fleet.add_vehicle(vehicle)
        
        self.update_status("Dados de exemplo carregados")
        messagebox.showinfo("Dados de Exemplo", "10 veículos de exemplo carregados com sucesso!")

# ==================== EXERCÍCIOS DE PREPARAÇÃO ====================
def preparation_exercises():
    print("\n" + "=" * 50)
    print("EXERCÍCIOS DE PREPARAÇÃO")
    print("=" * 50)
    
    # 1. Lambda e Map
    print("\n1. Processamento com Lambda e Map:")
    prices = [10000, 25000, 40000]
    print(f"Preços originais: {prices}")
    prices_with_vat = list(map(lambda p: p * 1.23, prices))
    print(f"Preços com IVA (23%): {prices_with_vat}")
    
    # 2. Compreensão de Listas
    print("\n2. Compreensão de Listas:")
    kms = [150, 2000, 50000, 120000, 500]
    print(f"Quilometragens: {kms}")
    low_mileage = [km for km in kms if km < 1000]
    print(f"Veículos pouco usados (<1000km): {low_mileage}")
    
    # 3. Persistência de Dados
    print("\n3. Persistência de Dados:")
    with open("frota_exportada.txt", 'w', encoding='utf-8') as f:
        for obj in ["Carro", "Mota", "Camião", "Autocarro"]:
            f.write(obj + "\n")
    print("Lista de objetos guardada em 'frota_exportada.txt'")
    
    print("=" * 50)

# ==================== EXECUÇÃO PRINCIPAL ====================
def main():
    preparation_exercises()
    app = FleetManagementApp()
    app.mainloop()

if __name__ == "__main__":
    main()
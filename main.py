import datetime
import csv
import json
from tkinter import ttk, messagebox
import customtkinter as ctk

ctk.set_appearance_mode("dark")

def log_operation(func):
    def wrapper(*args, **kwargs):
        now = datetime.datetime.now()
        print(f"[{now.strftime('%d-%m-%Y %H:%M:%S')}] Executing: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

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
        return f"{self.brand} {self.model} - €{self.price:.2f} (Year: {self.year})"
    
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
        base_tax = super().calculate_tax()
        return base_tax * 0.5
    
    def __str__(self):
        return f"{self.brand} {self.model} (Electric) - €{self.price:.2f} - Battery: {self.battery_capacity}kWh - Autonomy: {self.autonomy}km"
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'battery_capacity': self.battery_capacity,
            'autonomy': self.autonomy,
            'tax_discount': '50%'
        })
        return data


class Truck(Vehicle):
    def __init__(self, brand, model, price, year, load_capacity, length):
        super().__init__(brand, model, price, year)
        self.load_capacity = load_capacity
        self.length = length
    
    def calculate_tax(self):
        base_tax = super().calculate_tax()
        return base_tax * 1.3
    
    def __str__(self):
        return f"{self.brand} {self.model} (Truck) - €{self.price:.2f} - Load: {self.load_capacity}t - Length: {self.length}m"
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'load_capacity': self.load_capacity,
            'length': self.length,
            'extra_tax': '30%'
        })
        return data

class Fleet:
    """Class to manage fleet vehicles"""
    def __init__(self):
        self.vehicles = []
    
    @log_operation
    def add_vehicle(self, vehicle):
        """Add a vehicle to the fleet"""
        self.vehicles.append(vehicle)
        return True
    
    @log_operation
    def remove_vehicle(self, index):
        if 0 <= index < len(self.vehicles):
            return self.vehicles.pop(index)
        return None
    
    def apply_global_discount(self, percentage):
        adjust_price = lambda price, perc: price * (1 - perc/100)
        
        for vehicle in self.vehicles:
            vehicle.price = adjust_price(vehicle.price, percentage)
        return len(self.vehicles)
    
    def filter_by_brand(self, brand):
        return [v for v in self.vehicles if v.brand.lower() == brand.lower()]
    
    def filter_by_year(self, min_year):
        return [v for v in self.vehicles if v.year >= min_year]
    
    def filter_by_type(self, vehicle_type):
        return [v for v in self.vehicles if v.__class__.__name__ == vehicle_type]
    
    def export_inventory(self, filename, format_type='csv'):
        if not self.vehicles:
            return False, "No vehicles to export!"
        
        try:
            if format_type == 'txt':
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write("=" * 50 + "\n")
                    file.write("FLEET INVENTORY\n")
                    file.write(f"Export date: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n")
                    file.write("=" * 50 + "\n\n")
                    
                    for i, vehicle in enumerate(self.vehicles, 1):
                        file.write(f"VEHICLE {i}:\n")
                        file.write(f"  Type: {vehicle.__class__.__name__}\n")
                        file.write(f"  Brand: {vehicle.brand}\n")
                        file.write(f"  Model: {vehicle.model}\n")
                        file.write(f"  Price: €{vehicle.price:.2f}\n")
                        file.write(f"  Tax: €{vehicle.calculate_tax():.2f}\n")
                        file.write(f"  Year: {vehicle.year}\n")
                        
                        if isinstance(vehicle, ElectricCar):
                            file.write(f"  Battery capacity: {vehicle.battery_capacity}kWh\n")
                            file.write(f"  Autonomy: {vehicle.autonomy}km\n")
                        elif isinstance(vehicle, Truck):
                            file.write(f"  Load capacity: {vehicle.load_capacity}t\n")
                            file.write(f"  Length: {vehicle.length}m\n")
                        
                        file.write("\n" + "-" * 40 + "\n\n")
                    
                    file.write("=" * 50 + "\n")
                    file.write("FLEET SUMMARY\n")
                    file.write(f"Total vehicles: {len(self.vehicles)}\n")
                    file.write(f"Total fleet value: €{sum(v.price for v in self.vehicles):.2f}\n")
                    file.write(f"Total tax: €{sum(v.calculate_tax() for v in self.vehicles):.2f}\n")
                    file.write("=" * 50 + "\n")
            
            elif format_type == 'csv':
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    fields = ['type', 'brand', 'model', 'price', 'tax', 'year', 
                             'battery_capacity', 'autonomy', 'load_capacity', 
                             'length', 'registration_date']
                    
                    writer = csv.DictWriter(file, fieldnames=fields)
                    writer.writeheader()
                    
                    for vehicle in self.vehicles:
                        writer.writerow(vehicle.to_dict())
            
            elif format_type == 'json':
                data = {
                    'export_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_vehicles': len(self.vehicles),
                    'total_value': sum(v.price for v in self.vehicles),
                    'total_tax': sum(v.calculate_tax() for v in self.vehicles),
                    'vehicles': [vehicle.to_dict() for vehicle in self.vehicles]
                }
                
                with open(filename, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)
            
            else:
                return False, "Unsupported format!"
            
            return True, f"Inventory exported successfully to '{filename}'!"
        
        except Exception as e:
            return False, f"Error exporting inventory: {str(e)}"
    
    def get_summary(self):
        """Get fleet summary statistics"""
        if not self.vehicles:
            return {
                'total': 0,
                'total_value': 0,
                'total_tax': 0,
                'by_type': {}
            }
        
        summary = {
            'total': len(self.vehicles),
            'total_value': sum(v.price for v in self.vehicles),
            'total_tax': sum(v.calculate_tax() for v in self.vehicles),
            'by_type': {}
        }
        
        for vehicle in self.vehicles:
            vehicle_type = vehicle.__class__.__name__
            if vehicle_type not in summary['by_type']:
                summary['by_type'][vehicle_type] = 0
            summary['by_type'][vehicle_type] += 1
        
        return summary

class FleetManagementApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        
        self.fleet = Fleet()
        self.setup_ui()
        self.load_sample_data()
    
    def setup_ui(self):

        self.title("Fleet Management System")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.create_sidebar()

        self.create_main_content()

        self.create_status_bar()
    
    def create_sidebar(self):

        sidebar = ctk.CTkFrame(self.main_container, width=200, corner_radius=10)
        sidebar.pack(side="left", fill="y", padx=(0, 10), pady=10)
        
        title_label = ctk.CTkLabel(
            sidebar, 
            text="Fleet Manager", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        buttons_info = [
            ("📊 Dashboard", self.show_dashboard),
            ("🚗 Add Vehicle", self.show_add_vehicle),
            ("🗑️ Remove Vehicle", self.show_remove_vehicle),
            ("💰 Apply Discount", self.show_discount),
            ("🔍 Filter Vehicles", self.show_filter),
            ("📤 Export", self.show_export),
            ("📋 Inventory", self.show_inventory),
            ("⚙️ Settings", self.show_settings)
        ]
        
        for text, command in buttons_info:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                height=40,
                corner_radius=8,
                font=ctk.CTkFont(size=14)
            )
            btn.pack(pady=5, padx=10)

        version_label = ctk.CTkLabel(
            sidebar, 
            text="Version 1.0.0\n© 2024 Fleet Management",
            font=ctk.CTkFont(size=10)
        )
        version_label.pack(side="bottom", pady=10)
    
    def create_main_content(self):
        
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.content_frame.pack(side="right", fill="both", expand=True, pady=10)
        
        self.content_title = ctk.CTkLabel(
            self.content_frame, 
            text="Dashboard", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.content_title.pack(pady=(20, 10))

        self.content_container = ctk.CTkScrollableFrame(self.content_frame, corner_radius=10)
        self.content_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.show_dashboard()
    
    def create_status_bar(self):

        status_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
        status_bar.pack(side="bottom", fill="x")
        
        self.status_label = ctk.CTkLabel(
            status_bar, 
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10)

        self.vehicle_count_label = ctk.CTkLabel(
            status_bar, 
            text="Vehicles: 0",
            font=ctk.CTkFont(size=12)
        )
        self.vehicle_count_label.pack(side="right", padx=10)

        self.update_status()
    
    def update_status(self, message="Ready"):

        self.status_label.configure(text=message)
        summary = self.fleet.get_summary()
        self.vehicle_count_label.configure(text=f"Vehicles: {summary['total']}")
    
    def clear_content(self):

        for widget in self.content_container.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):

        self.clear_content()
        self.content_title.configure(text="Dashboard")
        
        summary = self.fleet.get_summary()

        stats_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        stats_frame.pack(fill="x", pady=(0, 20))

        stats_data = [
            ("Total Vehicles", f"{summary['total']}", "#4CC9F0"),
            ("Total Value", f"€{summary['total_value']:,.2f}", "#4361EE"),
            ("Total Tax", f"€{summary['total_tax']:,.2f}", "#3A0CA3"),
            ("Avg. Value", f"€{summary['total_value']/max(summary['total'], 1):,.2f}", "#7209B7")
        ]
        
        row_frame = ctk.CTkFrame(stats_frame)
        row_frame.pack(fill="x", padx=20, pady=20)
        
        for i, (title, value, color) in enumerate(stats_data):
            card = ctk.CTkFrame(row_frame, width=200, height=100, corner_radius=10)
            card.pack(side="left", padx=10, expand=True, fill="both")

            title_label = ctk.CTkLabel(
                card, 
                text=title,
                font=ctk.CTkFont(size=14)
            )
            title_label.pack(pady=(15, 5))
            
            value_label = ctk.CTkLabel(
                card, 
                text=value,
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color=color
            )
            value_label.pack(pady=5)

        if summary['by_type']:
            dist_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
            dist_frame.pack(fill="x", pady=(0, 20))
            
            dist_label = ctk.CTkLabel(
                dist_frame,
                text="Vehicle Distribution by Type",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            dist_label.pack(pady=(15, 10))
            
            for vehicle_type, count in summary['by_type'].items():
                type_frame = ctk.CTkFrame(dist_frame, height=40)
                type_frame.pack(fill="x", padx=20, pady=5)
                
                type_label = ctk.CTkLabel(
                    type_frame,
                    text=vehicle_type,
                    font=ctk.CTkFont(size=14)
                )
                type_label.pack(side="left", padx=10)
                
                progress = (count / summary['total']) * 100
                progress_bar = ctk.CTkProgressBar(type_frame)
                progress_bar.pack(side="left", padx=10, expand=True, fill="x")
                progress_bar.set(progress / 100)
                
                count_label = ctk.CTkLabel(
                    type_frame,
                    text=f"{count} ({progress:.1f}%)",
                    font=ctk.CTkFont(size=14)
                )
                count_label.pack(side="right", padx=10)

        if self.fleet.vehicles:
            recent_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
            recent_frame.pack(fill="x")
            
            recent_label = ctk.CTkLabel(
                recent_frame,
                text="Recent Vehicles",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            recent_label.pack(pady=(15, 10))

            for vehicle in self.fleet.vehicles[-5:]:
                vehicle_frame = ctk.CTkFrame(recent_frame, height=50)
                vehicle_frame.pack(fill="x", padx=20, pady=5)
                
                vehicle_info = ctk.CTkLabel(
                    vehicle_frame,
                    text=str(vehicle),
                    font=ctk.CTkFont(size=12)
                )
                vehicle_info.pack(side="left", padx=10)
                
                tax_label = ctk.CTkLabel(
                    vehicle_frame,
                    text=f"Tax: €{vehicle.calculate_tax():.2f}",
                    font=ctk.CTkFont(size=12)
                )
                tax_label.pack(side="right", padx=10)
    
    def show_add_vehicle(self):

        self.clear_content()
        self.content_title.configure(text="Add New Vehicle")
        
        form_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        form_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        type_label = ctk.CTkLabel(
            form_frame,
            text="Vehicle Type:",
            font=ctk.CTkFont(size=14)
        )
        type_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.vehicle_type_var = ctk.StringVar(value="Vehicle")
        type_options = ["Vehicle", "ElectricCar", "Truck"]
        type_combo = ctk.CTkComboBox(
            form_frame,
            values=type_options,
            variable=self.vehicle_type_var,
            command=self.on_vehicle_type_change,
            width=200
        )
        type_combo.grid(row=0, column=1, padx=20, pady=20, sticky="w")
        
        fields = [
            ("Brand:", "brand_entry"),
            ("Model:", "model_entry"),
            ("Price (€):", "price_entry"),
            ("Year:", "year_entry")
        ]
        
        self.entries = {}
        for i, (label_text, entry_name) in enumerate(fields, 1):
            label = ctk.CTkLabel(form_frame, text=label_text, font=ctk.CTkFont(size=14))
            label.grid(row=i, column=0, padx=20, pady=10, sticky="w")
            
            entry = ctk.CTkEntry(form_frame, width=200)
            entry.grid(row=i, column=1, padx=20, pady=10, sticky="w")
            self.entries[entry_name] = entry
        
        self.special_fields_frame = ctk.CTkFrame(form_frame, corner_radius=10)
        self.special_fields_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=30)
        
        add_button = ctk.CTkButton(
            button_frame,
            text="Add Vehicle",
            command=self.add_vehicle_submit,
            height=40,
            width=150
        )
        add_button.pack(side="left", padx=20)
        
        clear_button = ctk.CTkButton(
            button_frame,
            text="Clear Form",
            command=self.clear_add_form,
            height=40,
            width=150,
            fg_color="gray"
        )
        clear_button.pack(side="left", padx=20)
        
        self.on_vehicle_type_change(self.vehicle_type_var.get())
    
    def on_vehicle_type_change(self, choice):

        for widget in self.special_fields_frame.winfo_children():
            widget.destroy()
        
        if choice == "ElectricCar":
            fields = [
                ("Battery Capacity (kWh):", "battery_entry"),
                ("Autonomy (km):", "autonomy_entry")
            ]
        elif choice == "Truck":
            fields = [
                ("Load Capacity (tons):", "load_entry"),
                ("Length (meters):", "length_entry")
            ]
        else:
            return
        
        for i, (label_text, entry_name) in enumerate(fields):
            label = ctk.CTkLabel(self.special_fields_frame, text=label_text, font=ctk.CTkFont(size=14))
            label.grid(row=i, column=0, padx=20, pady=10, sticky="w")
            
            entry = ctk.CTkEntry(self.special_fields_frame, width=200)
            entry.grid(row=i, column=1, padx=20, pady=10, sticky="w")
            self.entries[entry_name] = entry
    
    def add_vehicle_submit(self):

        try:
            brand = self.entries['brand_entry'].get()
            model = self.entries['model_entry'].get()
            price = float(self.entries['price_entry'].get())
            year = int(self.entries['year_entry'].get())
            
            vehicle_type = self.vehicle_type_var.get()
            
            if vehicle_type == "Vehicle":
                vehicle = Vehicle(brand, model, price, year)
            elif vehicle_type == "ElectricCar":
                battery = float(self.entries['battery_entry'].get())
                autonomy = float(self.entries['autonomy_entry'].get())
                vehicle = ElectricCar(brand, model, price, year, battery, autonomy)
            elif vehicle_type == "Truck":
                load_capacity = float(self.entries['load_entry'].get())
                length = float(self.entries['length_entry'].get())
                vehicle = Truck(brand, model, price, year, load_capacity, length)
            else:
                messagebox.showerror("Error", "Invalid vehicle type!")
                return
            
            success = self.fleet.add_vehicle(vehicle)
            
            if success:
                messagebox.showinfo("Success", f"Vehicle added successfully!\n\n{vehicle}")
                self.clear_add_form()
                self.update_status(f"Added {brand} {model}")
                self.show_dashboard()
        
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def clear_add_form(self):

        for entry in self.entries.values():
            entry.delete(0, 'end')
    
    def show_remove_vehicle(self):

        self.clear_content()
        self.content_title.configure(text="Remove Vehicle")
        
        if not self.fleet.vehicles:
            no_vehicles_label = ctk.CTkLabel(
                self.content_container,
                text="No vehicles in the fleet!",
                font=ctk.CTkFont(size=16)
            )
            no_vehicles_label.pack(pady=50)
            return

        list_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        list_frame.pack(fill="both", expand=True, padx=20, pady=20)

        columns = ("#", "Type", "Brand", "Model", "Price", "Year", "Tax")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("#", width=50)
        self.tree.column("Type", width=100)
        self.tree.column("Brand", width=100)
        self.tree.column("Model", width=150)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for i, vehicle in enumerate(self.fleet.vehicles, 1):
            vehicle_type = vehicle.__class__.__name__
            values = (
                i,
                vehicle_type,
                vehicle.brand,
                vehicle.model,
                f"€{vehicle.price:.2f}",
                vehicle.year,
                f"€{vehicle.calculate_tax():.2f}"
            )
            self.tree.insert("", "end", values=values)
        
        button_frame = ctk.CTkFrame(self.content_container)
        button_frame.pack(pady=20)
        
        remove_button = ctk.CTkButton(
            button_frame,
            text="Remove Selected Vehicle",
            command=self.remove_selected_vehicle,
            height=40,
            width=200,
            fg_color="#D32F2F",
            hover_color="#B71C1C"
        )
        remove_button.pack(pady=10)
    
    def remove_selected_vehicle(self):

        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a vehicle to remove!")
            return
        
        item = self.tree.item(selection[0])
        index = int(item['values'][0]) - 1
        
        confirm = messagebox.askyesno(
            "Confirm Removal",
            f"Are you sure you want to remove vehicle {index + 1}?\n\n{item['values'][2]} {item['values'][3]}"
        )
        
        if confirm:
            removed_vehicle = self.fleet.remove_vehicle(index)
            if removed_vehicle:
                self.tree.delete(selection[0])
                self.update_status(f"Removed {removed_vehicle.brand} {removed_vehicle.model}")
                messagebox.showinfo("Success", "Vehicle removed successfully!")
                
                for i, item_id in enumerate(self.tree.get_children(), 1):
                    values = list(self.tree.item(item_id, 'values'))
                    values[0] = i
                    self.tree.item(item_id, values=values)
    
    def show_discount(self):

        self.clear_content()
        self.content_title.configure(text="Apply Global Discount/Tax")
        
        discount_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        discount_frame.pack(fill="x", padx=100, pady=50)
        
        instructions = ctk.CTkLabel(
            discount_frame,
            text="Apply a percentage discount (positive) or tax increase (negative) to all vehicles",
            font=ctk.CTkFont(size=14),
            wraplength=400
        )
        instructions.pack(pady=(30, 20))
        
        input_frame = ctk.CTkFrame(discount_frame)
        input_frame.pack(pady=20)
        
        percentage_label = ctk.CTkLabel(
            input_frame,
            text="Percentage:",
            font=ctk.CTkFont(size=14)
        )
        percentage_label.pack(side="left", padx=(0, 10))
        
        self.percentage_entry = ctk.CTkEntry(input_frame, width=100)
        self.percentage_entry.pack(side="left")
        
        percent_label = ctk.CTkLabel(
            input_frame,
            text="%",
            font=ctk.CTkFont(size=14)
        )
        percent_label.pack(side="left", padx=(5, 20))

        example_label = ctk.CTkLabel(
            discount_frame,
            text="Example: +10% = 10% discount, -5% = 5% tax increase",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        example_label.pack(pady=10)
        
        button_frame = ctk.CTkFrame(discount_frame)
        button_frame.pack(pady=30)
        
        apply_button = ctk.CTkButton(
            button_frame,
            text="Apply to All Vehicles",
            command=self.apply_discount_submit,
            height=40,
            width=200
        )
        apply_button.pack(side="left", padx=10)
        
        preview_button = ctk.CTkButton(
            button_frame,
            text="Preview Changes",
            command=self.preview_discount,
            height=40,
            width=200,
            fg_color="gray"
        )
        preview_button.pack(side="left", padx=10)
    
    def apply_discount_submit(self):

        try:
            percentage = float(self.percentage_entry.get())
            
            confirm = messagebox.askyesno(
                "Confirm",
                f"Are you sure you want to apply {percentage}% {'discount' if percentage > 0 else 'tax increase'} to all vehicles?"
            )
            
            if confirm:
                count = self.fleet.apply_global_discount(percentage)
                messagebox.showinfo("Success", f"Applied to {count} vehicles!")
                self.update_status(f"Applied {percentage}% to all vehicles")
                self.show_dashboard()
        
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid percentage!")
    
    def preview_discount(self):

        try:
            percentage = float(self.percentage_entry.get())

            adjust_price = lambda price, perc: price * (1 - perc/100)
            
            preview_window = ctk.CTkToplevel(self)
            preview_window.title("Discount Preview")
            preview_window.geometry("600x400")

            columns = ("Brand", "Model", "Old Price", "New Price", "Change")
            tree = ttk.Treeview(preview_window, columns=columns, show="headings", height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            scrollbar = ttk.Scrollbar(preview_window, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y")

            for vehicle in self.fleet.vehicles:
                new_price = adjust_price(vehicle.price, percentage)
                change = new_price - vehicle.price
                change_percent = (change / vehicle.price) * 100 if vehicle.price != 0 else 0
                
                values = (
                    vehicle.brand,
                    vehicle.model,
                    f"€{vehicle.price:.2f}",
                    f"€{new_price:.2f}",
                    f"{change_percent:+.1f}%"
                )
                tree.insert("", "end", values=values)
            
            total_old = sum(v.price for v in self.fleet.vehicles)
            total_new = sum(adjust_price(v.price, percentage) for v in self.fleet.vehicles)
            total_change = total_new - total_old
            
            summary_label = ctk.CTkLabel(
                preview_window,
                text=f"Total change: €{total_change:+.2f} ({total_new - total_old:+.1f}%)",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            summary_label.pack(pady=10)
        
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid percentage!")
    
    def show_filter(self):

        self.clear_content()
        self.content_title.configure(text="Filter Vehicles")
        
        filter_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        filter_frame.pack(fill="both", expand=True, padx=20, pady=20)

        options_frame = ctk.CTkFrame(filter_frame)
        options_frame.pack(fill="x", pady=20, padx=20)
        
        brand_frame = ctk.CTkFrame(options_frame)
        brand_frame.pack(fill="x", pady=10)
        
        brand_label = ctk.CTkLabel(
            brand_frame,
            text="Filter by Brand:",
            font=ctk.CTkFont(size=14)
        )
        brand_label.pack(side="left", padx=(0, 10))
        
        self.brand_filter_entry = ctk.CTkEntry(brand_frame, width=150)
        self.brand_filter_entry.pack(side="left")
        
        brand_button = ctk.CTkButton(
            brand_frame,
            text="Filter",
            command=lambda: self.apply_filter("brand"),
            width=80
        )
        brand_button.pack(side="left", padx=10)

        year_frame = ctk.CTkFrame(options_frame)
        year_frame.pack(fill="x", pady=10)
        
        year_label = ctk.CTkLabel(
            year_frame,
            text="Filter by Year (min):",
            font=ctk.CTkFont(size=14)
        )
        year_label.pack(side="left", padx=(0, 10))
        
        self.year_filter_entry = ctk.CTkEntry(year_frame, width=150)
        self.year_filter_entry.pack(side="left")
        
        year_button = ctk.CTkButton(
            year_frame,
            text="Filter",
            command=lambda: self.apply_filter("year"),
            width=80
        )
        year_button.pack(side="left", padx=10)
        
        type_frame = ctk.CTkFrame(options_frame)
        type_frame.pack(fill="x", pady=10)
        
        type_label = ctk.CTkLabel(
            type_frame,
            text="Filter by Type:",
            font=ctk.CTkFont(size=14)
        )
        type_label.pack(side="left", padx=(0, 10))
        
        type_options = ["All", "Vehicle", "ElectricCar", "Truck"]
        self.type_filter_var = ctk.StringVar(value="All")
        type_combo = ctk.CTkComboBox(
            type_frame,
            values=type_options,
            variable=self.type_filter_var,
            width=150
        )
        type_combo.pack(side="left")
        
        type_button = ctk.CTkButton(
            type_frame,
            text="Filter",
            command=lambda: self.apply_filter("type"),
            width=80
        )
        type_button.pack(side="left", padx=10)

        self.results_frame = ctk.CTkFrame(filter_frame)
        self.results_frame.pack(fill="both", expand=True, pady=20, padx=20)

        self.display_filtered_vehicles(self.fleet.vehicles)
    
    def apply_filter(self, filter_type):
        """Apply filter and display results"""
        if filter_type == "brand":
            brand = self.brand_filter_entry.get()
            if brand:
                filtered = self.fleet.filter_by_brand(brand)
            else:
                filtered = self.fleet.vehicles
        elif filter_type == "year":
            try:
                min_year = int(self.year_filter_entry.get())
                filtered = self.fleet.filter_by_year(min_year)
            except ValueError:
                filtered = self.fleet.vehicles
        elif filter_type == "type":
            vehicle_type = self.type_filter_var.get()
            if vehicle_type == "All":
                filtered = self.fleet.vehicles
            else:
                filtered = self.fleet.filter_by_type(vehicle_type)
        else:
            filtered = self.fleet.vehicles
        
        self.display_filtered_vehicles(filtered)
    
    def display_filtered_vehicles(self, vehicles):

        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        if not vehicles:
            no_results_label = ctk.CTkLabel(
                self.results_frame,
                text="No vehicles found matching the criteria",
                font=ctk.CTkFont(size=14)
            )
            no_results_label.pack(pady=50)
            return
        
        columns = ("Brand", "Model", "Type", "Price", "Year", "Tax")
        tree = ttk.Treeview(self.results_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.column("Brand", width=120)
        tree.column("Model", width=150)
        
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
        for vehicle in vehicles:
            vehicle_type = vehicle.__class__.__name__
            values = (
                vehicle.brand,
                vehicle.model,
                vehicle_type,
                f"€{vehicle.price:.2f}",
                vehicle.year,
                f"€{vehicle.calculate_tax():.2f}"
            )
            tree.insert("", "end", values=values)
        
        count_label = ctk.CTkLabel(
            self.results_frame,
            text=f"Found {len(vehicles)} vehicle(s)",
            font=ctk.CTkFont(size=12)
        )
        count_label.pack(pady=10)
    
    def show_export(self):

        self.clear_content()
        self.content_title.configure(text="Export Inventory")
        
        export_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        export_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        options_frame = ctk.CTkFrame(export_frame)
        options_frame.pack(pady=30)
        
        format_label = ctk.CTkLabel(
            options_frame,
            text="Export Format:",
            font=ctk.CTkFont(size=16)
        )
        format_label.pack(pady=(0, 20))
        
        self.format_var = ctk.StringVar(value="csv")
        
        formats = [
            ("CSV (Excel compatible)", "csv"),
            ("Text (Human readable)", "txt"),
            ("JSON (Structured data)", "json")
        ]
        
        for text, value in formats:
            radio = ctk.CTkRadioButton(
                options_frame,
                text=text,
                variable=self.format_var,
                value=value,
                font=ctk.CTkFont(size=14)
            )
            radio.pack(pady=5)
        
        file_frame = ctk.CTkFrame(export_frame)
        file_frame.pack(pady=20)
        
        file_label = ctk.CTkLabel(
            file_frame,
            text="File Name:",
            font=ctk.CTkFont(size=14)
        )
        file_label.pack(side="left", padx=(0, 10))
        
        self.filename_entry = ctk.CTkEntry(file_frame, width=200)
        self.filename_entry.pack(side="left")
        self.filename_entry.insert(0, f"fleet_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        button_frame = ctk.CTkFrame(export_frame)
        button_frame.pack(pady=30)
        
        export_button = ctk.CTkButton(
            button_frame,
            text="Export Inventory",
            command=self.export_inventory_submit,
            height=40,
            width=200
        )
        export_button.pack(pady=10)
        
        preview_button = ctk.CTkButton(
            button_frame,
            text="Preview Export",
            command=self.preview_export,
            height=40,
            width=200,
            fg_color="gray"
        )
        preview_button.pack(pady=10)
    
    def export_inventory_submit(self):
        
        filename = self.filename_entry.get()
        format_type = self.format_var.get()

        if not filename.endswith(f'.{format_type}'):
            filename += f'.{format_type}'
        
        success, message = self.fleet.export_inventory(filename, format_type)
        
        if success:
            messagebox.showinfo("Success", message)
            self.update_status(f"Exported to {filename}")
        else:
            messagebox.showerror("Error", message)
    
    def preview_export(self):

        if not self.fleet.vehicles:
            messagebox.showinfo("Info", "No vehicles to preview!")
            return
        
        preview_window = ctk.CTkToplevel(self)
        preview_window.title("Export Preview")
        preview_window.geometry("800x500")
        
        text_widget = ctk.CTkTextbox(preview_window, font=ctk.CTkFont(family="Courier", size=12))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
    
        preview_text = "EXPORT PREVIEW\n"
        preview_text += "=" * 50 + "\n\n"
        
        for i, vehicle in enumerate(self.fleet.vehicles[:10], 1):
            preview_text += f"Vehicle {i}:\n"
            preview_text += f"  Type: {vehicle.__class__.__name__}\n"
            preview_text += f"  Brand: {vehicle.brand}\n"
            preview_text += f"  Model: {vehicle.model}\n"
            preview_text += f"  Price: €{vehicle.price:.2f}\n"
            preview_text += f"  Tax: €{vehicle.calculate_tax():.2f}\n"
            preview_text += f"  Year: {vehicle.year}\n"
            
            if isinstance(vehicle, ElectricCar):
                preview_text += f"  Battery: {vehicle.battery_capacity}kWh\n"
                preview_text += f"  Autonomy: {vehicle.autonomy}km\n"
            elif isinstance(vehicle, Truck):
                preview_text += f"  Load Capacity: {vehicle.load_capacity}t\n"
                preview_text += f"  Length: {vehicle.length}m\n"
            
            preview_text += "\n"
        
        if len(self.fleet.vehicles) > 10:
            preview_text += f"... and {len(self.fleet.vehicles) - 10} more vehicles\n\n"
        
        summary = self.fleet.get_summary()
        preview_text += "=" * 50 + "\n"
        preview_text += f"Total vehicles: {summary['total']}\n"
        preview_text += f"Total value: €{summary['total_value']:.2f}\n"
        preview_text += f"Total tax: €{summary['total_tax']:.2f}\n"
        preview_text += "=" * 50
        
        text_widget.insert("1.0", preview_text)
        text_widget.configure(state="disabled")
    
    def show_inventory(self):
        
        self.show_filter()
    
    def show_settings(self):

        self.clear_content()
        self.content_title.configure(text="Settings")
        
        settings_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        settings_frame.pack(fill="both", expand=True, padx=50, pady=50)

        appearance_frame = ctk.CTkFrame(settings_frame)
        appearance_frame.pack(fill="x", pady=20)
        
        appearance_label = ctk.CTkLabel(
            appearance_frame,
            text="Appearance",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        appearance_label.pack(pady=(0, 10))
        
        theme_label = ctk.CTkLabel(
            appearance_frame,
            text="Theme:",
            font=ctk.CTkFont(size=14)
        )
        theme_label.pack(pady=5)
        
        theme_options = ["dark", "light", "system"]
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        
        theme_combo = ctk.CTkComboBox(
            appearance_frame,
            values=theme_options,
            variable=self.theme_var,
            command=self.change_theme,
            width=150
        )
        theme_combo.pack(pady=5)
        
        info_frame = ctk.CTkFrame(settings_frame)
        info_frame.pack(fill="x", pady=20)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="System Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        info_label.pack(pady=(0, 10))
        
        info_text = f"""
        Fleet Management System v1.0.0
        Total vehicles in system: {len(self.fleet.vehicles)}
        Last update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Features:
        • Vehicle management (add/remove)
        • Tax calculation (VAT 23%)
        • Discount application
        • Filtering and search
        • Export to multiple formats
        """
        
        info_display = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_display.pack(pady=10)

        reset_button = ctk.CTkButton(
            settings_frame,
            text="Load Sample Data",
            command=self.load_sample_data,
            height=40,
            fg_color="gray"
        )
        reset_button.pack(pady=20)
    
    def change_theme(self, theme):
        ctk.set_appearance_mode(theme)
    
    def change_color_theme(self, theme):
        ctk.set_default_color_theme(theme)
    
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
        
        self.update_status("Loaded sample data")
        messagebox.showinfo("Sample Data", "10 sample vehicles loaded successfully!")

def preparation_exercises():
    
    print("\n" + "=" * 50)
    print("PREPARATION EXERCISES")
    print("=" * 50)
    
    print("\n1. Lambda and Map Processing:")
    prices = [10000, 25000, 40000]
    print(f"Original prices: {prices}")

    prices_with_vat = list(map(lambda price: price * 1.23, prices))
    print(f"Prices with VAT (23%): {prices_with_vat}")
    
    print("\n2. List Comprehension:")
    kms = [150, 2000, 50000, 120000, 500]
    print(f"Mileages: {kms}")
    
    low_mileage = [km for km in kms if km < 1000]
    print(f"Low mileage vehicles (<1000km): {low_mileage}")

    print("\n3. Data Persistence:")
    objects = ["Car", "Motorcycle", "Truck", "Bus"]
    filename = "fleet_exported.txt"
    
    with open(filename, 'w', encoding='utf-8') as file:
        for obj in objects:
            file.write(obj + "\n")
    
    print(f"Object list saved to '{filename}'")
    print("=" * 50)

def main():
    
    preparation_exercises()
    
    app = FleetManagementApp()
    app.mainloop()


if __name__ == "__main__":
    main()
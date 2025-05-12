import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyodbc
from datetime import datetime
import csv
import logging

from utils import str_to_set, set_to_str
from x_plus import calculate_xplus
from key_finder import find_k1, find_k2, find_k3, find_all_keys, find_ks1, find_ks2, find_ks3,find_ks4, find_ks5, find_ks6
from fc_generator import find_f1, find_f2, find_f3
from db import insert_log, get_all_logs, delete_log, get_combined_logs, get_connection

class KeyFindingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ứng dụng tìm khóa lược đồ quan hệ")
        self.geometry("850x600")
        self.configure(bg="#f5f5f5")
        
        self.u_set = set()
        self.f_list = []

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TLabel", font=("Arial", 11), background="#f5f5f5", foreground="#333333")
        self.style.configure("TButton", font=("Arial", 10), padding=6, background="#4CAF50", foreground="white")
        self.style.map("TButton", background=[('active', '#45a049')], foreground=[('active', '#ffffff')])
        self.style.configure("TEntry", font=("Arial", 11), padding=4)
        self.style.configure("TLabelframe", font=("Arial", 11, "bold"), background="#f5f5f5")
        self.style.configure("TLabelframe.Label", background="#f5f5f5", foreground="#333333")
        self.style.configure("TNotebook", background="#e0e0e0")
        self.style.configure("TNotebook.Tab", font=("Arial", 10), padding=[8, 4])
        self.style.configure("Treeview", font=("Arial", 10))
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        self.style.map("Treeview", background=[('selected', '#d0e8ff')])

        self.create_menu()
        self.create_main_interface()

    def create_menu(self):
        menu_bar = tk.Menu(self, bg="#4CAF50", fg="white", activebackground="#45a049", activeforeground="white")
        self.config(menu=menu_bar)
        
        file_menu = tk.Menu(menu_bar, tearoff=0, bg="white", fg="black")
        menu_bar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(label="🆕 Mới", command=lambda: self.reset_data())
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Thoát", command=self.quit)
        
        tools_menu = tk.Menu(menu_bar, tearoff=0, bg="white", fg="black")
        menu_bar.add_cascade(label="🛠 Công cụ", menu=tools_menu)
        tools_menu.add_command(label="📜 Xem lịch sử", command=self.show_history)
        tools_menu.add_command(label="🔗 Kết nối CSDL", command=self.test_db_connection)
        
        help_menu = tk.Menu(menu_bar, tearoff=0, bg="white", fg="black")
        menu_bar.add_cascade(label="❓ Trợ giúp", menu=help_menu)
        help_menu.add_command(label="📖 Hướng dẫn", command=self.show_help)
        help_menu.add_command(label="ℹ Giới thiệu", command=self.show_about)

    def create_main_interface(self):
        main_frame = ttk.Frame(self, padding=8, style="Main.TFrame")
        main_frame.pack(fill="both", expand=True)
        self.style.configure("Main.TFrame", background="#f5f5f5")

        panel1 = ttk.LabelFrame(main_frame, text="🌌 Tập thuộc tính vũ trụ", padding=8)
        panel1.pack(fill="x", padx=8, pady=8)

        ttk.Label(panel1, text="Nhập U =", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.txtU = ttk.Entry(panel1, font=("Arial", 11), width=35)
        self.txtU.grid(row=0, column=1, sticky="ew", padx=8, pady=4)
        self.txtU.bind("<KeyRelease>", self.on_u_change)
        
        ttk.Label(panel1, text="U =", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.txtUDisplay = ttk.Entry(panel1, font=("Arial", 11), state="readonly", width=35)
        self.txtUDisplay.grid(row=1, column=1, sticky="ew", padx=8, pady=4)

        self.tabControl = ttk.Notebook(main_frame)
        self.tab1 = ttk.Frame(self.tabControl)
        self.tab2 = ttk.Frame(self.tabControl)
        self.tab3 = ttk.Frame(self.tabControl)

        self.tabControl.add(self.tab1, text='📥 Tìm X+')
        self.tabControl.add(self.tab2, text='🔑 Tìm Khóa')
        self.tabControl.add(self.tab3, text='📊 Tìm Fc')
        self.tabControl.pack(expand=1, fill="both", padx=8, pady=8)

        self.init_tab1(self.tab1)
        self.init_tab2(self.tab2)
        self.init_tab3(self.tab3)

        self.btnSaveToDB = ttk.Button(main_frame, text="💾 Lưu vào SQL Server", command=self.log_to_db, style="Accent.TButton")
        self.btnSaveToDB.pack(pady=8)
        self.style.configure("Accent.TButton", background="#2196F3", font=("Arial", 10, "bold"))
        self.style.map("Accent.TButton", background=[('active', '#1976D2')])

        self.status_var = tk.StringVar()
        self.status_var.set("✅ Sẵn sàng")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, background="#e0e0e0", padding=4)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_u_change(self, event=None):
        u_str = self.txtU.get().strip()
        self.u_set = str_to_set(u_str)

        self.txtUDisplay.config(state="normal")
        self.txtUDisplay.delete(0, tk.END)
        self.txtUDisplay.insert(0, set_to_str(self.u_set))
        self.txtUDisplay.config(state="readonly")

    def init_tab1(self, parent):
        input_frame = ttk.LabelFrame(parent, text="➕ Nhập phụ thuộc hàm", padding=8)
        input_frame.pack(fill="x", padx=8, pady=8)
        
        ttk.Label(input_frame, text="X =", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=8, pady=4)
        self.txtX = ttk.Entry(input_frame, font=("Arial", 11), width=18)
        self.txtX.grid(row=0, column=1, padx=8, pady=4)
        
        ttk.Label(input_frame, text="Y =", font=("Arial", 11, "bold")).grid(row=0, column=2, padx=8, pady=4)
        self.txtY = ttk.Entry(input_frame, font=("Arial", 11), width=18)
        self.txtY.grid(row=0, column=3, padx=8, pady=4)
        
        self.btnAddRelation = ttk.Button(input_frame, text="➕ Thêm F", command=self.on_add_relation)
        self.btnAddRelation.grid(row=0, column=4, padx=8, pady=4)

        f_display_frame = ttk.LabelFrame(parent, text="📋 Tập phụ thuộc hàm F", padding=8)
        f_display_frame.pack(fill="both", expand=True, padx=8, pady=8)

        text_frame = ttk.Frame(f_display_frame)
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.txtF = tk.Text(text_frame, font=("Arial", 11), height=12, width=50, bg="#ffffff", relief="flat", borderwidth=1)
        
        scrollbar_y = ttk.Scrollbar(text_frame, orient="vertical", command=self.txtF.yview)
        scrollbar_y.pack(side="right", fill="y")
        
        self.txtF.pack(fill="both", expand=True)
        self.txtF.config(yscrollcommand=scrollbar_y.set)

        xplus_frame = ttk.LabelFrame(parent, text="🔍 Tìm X+", padding=8)
        xplus_frame.pack(fill="x", padx=8, pady=8)

        ttk.Label(xplus_frame, text="Nhập X =", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=8, pady=4)
        self.txtFindX = ttk.Entry(xplus_frame, font=("Arial", 11), width=18)
        self.txtFindX.grid(row=0, column=1, padx=8, pady=4)

        ttk.Label(xplus_frame, text="X+ =", font=("Arial", 11, "bold")).grid(row=0, column=2, padx=8, pady=4)
        self.txtXPlus = ttk.Entry(xplus_frame, font=("Arial", 11), width=25, state="readonly")
        self.txtXPlus.grid(row=0, column=3, padx=8, pady=4)

        self.btnFindXPlus = ttk.Button(xplus_frame, text="🔎 Tìm X+", command=self.on_find_xplus)
        self.btnFindXPlus.grid(row=0, column=4, padx=8, pady=4)

    def init_tab2(self, parent):
        keys_frame = ttk.LabelFrame(parent, text="🔑 Tìm các khóa", padding=8)
        keys_frame.pack(fill="both", expand=True, padx=8, pady=8)

        ttk.Label(keys_frame, text="K1 =", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=8, pady=6, sticky="w")
        self.txtK1 = ttk.Entry(keys_frame, font=("Arial", 11), width=35, state="readonly")
        self.txtK1.grid(row=0, column=1, padx=8, pady=6)
        ttk.Button(keys_frame, text="🔍 Tìm K1", command=self.on_find_k1).grid(row=0, column=2, padx=8, pady=6)

        ttk.Label(keys_frame, text="K2 =", font=("Arial", 11, "bold")).grid(row=1, column=0, padx=8, pady=6, sticky="w")
        self.txtK2 = ttk.Entry(keys_frame, font=("Arial", 11), width=35, state="readonly")
        self.txtK2.grid(row=1, column=1, padx=8, pady=6)
        ttk.Button(keys_frame, text="🔍 Tìm K2", command=self.on_find_k2).grid(row=1, column=2, padx=8, pady=6)

        ttk.Label(keys_frame, text="K3 =", font=("Arial", 11, "bold")).grid(row=2, column=0, padx=8, pady=6, sticky="w")
        self.txtK3 = ttk.Entry(keys_frame, font=("Arial", 11), width=35, state="readonly")
        self.txtK3.grid(row=2, column=1, padx=8, pady=6)
        ttk.Button(keys_frame, text="🔍 Tìm K3", command=self.on_find_k3).grid(row=2, column=2, padx=8, pady=6)

        ttk.Label(keys_frame, text="KS1 =", font=("Arial", 11, "bold")).grid(row=3, column=0, padx=8, pady=6, sticky="w")
        self.txtKS1 = ttk.Entry(keys_frame, font=("Arial", 11), width=35, state="readonly")
        self.txtKS1.grid(row=3, column=1, padx=8, pady=6)
        ttk.Button(keys_frame, text="🔍 Tìm KS1", command=self.on_find_ks1).grid(row=3, column=2, padx=8, pady=6)

        ttk.Label(keys_frame, text="KS2 =", font=("Arial", 11, "bold")).grid(row=4, column=0, padx=8, pady=6, sticky="w")
        self.txtKS2 = ttk.Entry(keys_frame, font=("Arial", 11), width=35, state="readonly")
        self.txtKS2.grid(row=4, column=1, padx=8, pady=6)
        ttk.Button(keys_frame, text="🔍 Tìm KS2", command=self.on_find_ks2).grid(row=4, column=2, padx=8, pady=6)

        ttk.Label(keys_frame, text="KS3 =", font=("Arial", 11, "bold")).grid(row=5, column=0, padx=8, pady=6, sticky="w")
        self.txtKS3 = ttk.Entry(keys_frame, font=("Arial", 11), width=35, state="readonly")
        self.txtKS3.grid(row=5, column=1, padx=8, pady=6)
        ttk.Button(keys_frame, text="🔍 Tìm KS3", command=self.on_find_ks3).grid(row=5, column=2, padx=8, pady=6)

        ttk.Label(keys_frame, text="KS4 =", font=("Arial", 11, "bold")).grid(row=6, column=0, padx=8, pady=6, sticky="w")
        self.txtKS4 = ttk.Entry(keys_frame, font=("Arial", 11), width=35, state="readonly")
        self.txtKS4.grid(row=6, column=1, padx=8, pady=6)
        ttk.Button(keys_frame, text="🔍 Tìm KS4", command=self.on_find_ks4).grid(row=6, column=2, padx=8, pady=6)

        ttk.Label(keys_frame, text="KS5 =", font=("Arial", 11, "bold")).grid(row=7, column=0, padx=8, pady=6, sticky="w")
        self.txtKS5 = ttk.Entry(keys_frame, font=("Arial", 11), width=35, state="readonly")
        self.txtKS5.grid(row=7, column=1, padx=8, pady=6)
        ttk.Button(keys_frame, text="🔍 Tìm KS5", command=self.on_find_ks5).grid(row=7, column=2, padx=8, pady=6)

        ttk.Label(keys_frame, text="KS6 =", font=("Arial", 11, "bold")).grid(row=8, column=0, padx=8, pady=6, sticky="w")
        self.txtKS6 = ttk.Entry(keys_frame, font=("Arial", 11), width=35, state="readonly")
        self.txtKS6.grid(row=8, column=1, padx=8, pady=6)
        ttk.Button(keys_frame, text="🔍 Tìm KS6", command=self.on_find_ks6).grid(row=8, column=2, padx=8, pady=6)

    def init_tab3(self, parent):
        fc_frame = ttk.LabelFrame(parent, text="📊 Tập phụ thuộc hàm tối thiểu", padding=8)
        fc_frame.pack(fill="both", expand=True, padx=8, pady=8)

        ttk.Label(fc_frame, text="F1 =", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="nw", padx=8, pady=6)
        text_frame_f1 = ttk.Frame(fc_frame)
        text_frame_f1.grid(row=0, column=1, padx=8, pady=6, sticky="ew")
        
        self.txtF1 = tk.Text(text_frame_f1, font=("Arial", 11), height=4, width=50, bg="#ffffff", relief="flat", borderwidth=1)
        scrollbar_y_f1 = ttk.Scrollbar(text_frame_f1, orient="vertical", command=self.txtF1.yview)
        scrollbar_y_f1.pack(side="right", fill="y")
        self.txtF1.pack(fill="both", expand=True)
        self.txtF1.config(yscrollcommand=scrollbar_y_f1.set)
        
        ttk.Button(fc_frame, text="🔍 Tìm F1", command=self.on_find_f1).grid(row=0, column=2, padx=8, pady=6)

        ttk.Label(fc_frame, text="F2 =", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky="nw", padx=8, pady=6)
        text_frame_f2 = ttk.Frame(fc_frame)
        text_frame_f2.grid(row=1, column=1, padx=8, pady=6, sticky="ew")
        
        self.txtF2 = tk.Text(text_frame_f2, font=("Arial", 11), height=4, width=50, bg="#ffffff", relief="flat", borderwidth=1)
        scrollbar_y_f2 = ttk.Scrollbar(text_frame_f2, orient="vertical", command=self.txtF2.yview)
        scrollbar_y_f2.pack(side="right", fill="y")
        self.txtF2.pack(fill="both", expand=True)
        self.txtF2.config(yscrollcommand=scrollbar_y_f2.set)
        
        ttk.Button(fc_frame, text="🔍 Tìm F2", command=self.on_find_f2).grid(row=1, column=2, padx=8, pady=6)

        ttk.Label(fc_frame, text="F3 =", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky="nw", padx=8, pady=6)
        text_frame_f3 = ttk.Frame(fc_frame)
        text_frame_f3.grid(row=2, column=1, padx=8, pady=6, sticky="ew")
        
        self.txtF3 = tk.Text(text_frame_f3, font=("Arial", 11), height=4, width=50, bg="#ffffff", relief="flat", borderwidth=1)
        scrollbar_y_f3 = ttk.Scrollbar(text_frame_f3, orient="vertical", command=self.txtF3.yview)
        scrollbar_y_f3.pack(side="right", fill="y")
        self.txtF3.pack(fill="both", expand=True)
        self.txtF3.config(yscrollcommand=scrollbar_y_f3.set)
        
        ttk.Button(fc_frame, text="🔍 Tìm F3", command=self.on_find_f3).grid(row=2, column=2, padx=8, pady=6)

    def on_add_relation(self):
        x_str = self.txtX.get().strip()
        y_str = self.txtY.get().strip()

        if not x_str or not y_str:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ X và Y")
            return
        
        x_set = str_to_set(x_str)
        y_set = str_to_set(y_str)

        if not x_set.issubset(self.u_set) or not y_set.issubset(self.u_set):
            messagebox.showwarning("Dữ liệu không hợp lệ", 
                                "X và Y phải là tập con của U")
            return
        
        self.f_list.append((x_set, y_set))

        self.txtF.insert(tk.END, f"{set_to_str(x_set)} → {set_to_str(y_set)}\n")

        self.txtX.delete(0, tk.END)
        self.txtY.delete(0, tk.END)

        self.status_var.set(f"✅ Đã thêm phụ thuộc hàm: {set_to_str(x_set)} → {set_to_str(y_set)}")
        
    def on_find_xplus(self):
        if not self.u_set:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập U trước")
            return
        
        if not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập F trước")
            return
        
        x_str = self.txtFindX.get().strip()
        if not x_str:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập X để tìm X+")
            return
        
        x_set = str_to_set(x_str)
    
        if not x_set.issubset(self.u_set):
            messagebox.showwarning("Dữ liệu không hợp lệ", "X phải là tập con của U")
            return
        
        xplus = calculate_xplus(x_set, self.f_list, self.u_set)
    
        self.txtXPlus.config(state="normal")
        self.txtXPlus.delete(0, tk.END)
        self.txtXPlus.insert(0, set_to_str(xplus))
        self.txtXPlus.config(state="readonly")
    
        self.status_var.set(f"✅ X+ của {set_to_str(x_set)} là {set_to_str(xplus)}")

    def on_find_k1(self):
        if not self.u_set or not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập U và F.")
            return
        k1 = find_k1(self.u_set, self.f_list)
        self.txtK1.config(state="normal")
        self.txtK1.delete(0, tk.END)
        self.txtK1.insert(0, set_to_str(k1))
        self.txtK1.config(state="readonly")
        self.status_var.set("✅ Đã tìm K1 thành công")

    def on_find_k2(self):
        if not self.u_set or not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập U và F.")
            return
        k2 = find_k2(self.u_set, self.f_list)
        self.txtK2.config(state="normal")
        self.txtK2.delete(0, tk.END)
        self.txtK2.insert(0, set_to_str(k2))
        self.txtK2.config(state="readonly")
        self.status_var.set("✅ Đã tìm K2 thành công")

    def on_find_k3(self):
        if not self.u_set or not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập U và F.")
            return
        k3 = find_k3(self.u_set, self.f_list)
        self.txtK3.config(state="normal")
        self.txtK3.delete(0, tk.END)
        self.txtK3.insert(0, set_to_str(k3))
        self.txtK3.config(state="readonly")
        self.status_var.set("✅ Đã tìm K3 thành công")

    def on_find_ks1(self):
        if not self.u_set or not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập U và F.")
            return
        
        # Calculate the new KS1 value
        new_ks1 = find_ks1(self.u_set, self.f_list)
        if not new_ks1:
            self.status_var.set("❌ Không tìm thấy KS1")
            return

        # Get the current KS1 value from the Entry widget
        self.txtKS1.config(state="normal")
        current_ks1 = self.txtKS1.get().strip()
        
        # Combine current and new KS1 values, avoiding duplicates
        if current_ks1:
            # Split current KS1 into a set to remove duplicates
            current_keys = set(current_ks1.split(';')) if current_ks1 else set()
            new_keys = set(new_ks1.split(';'))
            # Update the set with new keys
            combined_keys = current_keys.union(new_keys)
            # Convert back to a semicolon-separated string
            updated_ks1 = ';'.join(sorted(combined_keys))
        else:
            updated_ks1 = new_ks1

        # Update the Entry widget with the combined value
        self.txtKS1.delete(0, tk.END)
        self.txtKS1.insert(0, updated_ks1)
        self.txtKS1.config(state="readonly")
        self.status_var.set("✅ Đã tìm và cập nhật KS1 thành công")

    def on_find_ks2(self):
        if not self.u_set or not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập U và F.")
            return
        
        new_ks2 = find_ks2(self.u_set, self.f_list)
        if not new_ks2:
            self.status_var.set("❌ Không tìm thấy KS2")
            return

        self.txtKS2.config(state="normal")
        current_ks2 = self.txtKS2.get().strip()
        
        if current_ks2:
            current_keys = set(current_ks2.split(';')) if current_ks2 else set()
            new_keys = set(new_ks2.split(';'))
            combined_keys = current_keys.union(new_keys)
            updated_ks2 = ';'.join(sorted(combined_keys))
        else:
            updated_ks2 = new_ks2

        self.txtKS2.delete(0, tk.END)
        self.txtKS2.insert(0, updated_ks2)
        self.txtKS2.config(state="readonly")
        self.status_var.set("✅ Đã tìm và cập nhật KS2 thành công")

    def on_find_ks3(self):
        if not self.u_set or not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập U và F.")
            return
        
        new_ks3 = find_ks3(self.u_set, self.f_list)
        if not new_ks3:
            self.status_var.set("❌ Không tìm thấy KS3")
            return

        self.txtKS3.config(state="normal")
        current_ks3 = self.txtKS3.get().strip()
        
        if current_ks3:
            current_keys = set(current_ks3.split(';')) if current_ks3 else set()
            new_keys = set(new_ks3.split(';'))
            combined_keys = current_keys.union(new_keys)
            updated_ks3 = ';'.join(sorted(combined_keys))
        else:
            updated_ks3 = new_ks3

        self.txtKS3.delete(0, tk.END)
        self.txtKS3.insert(0, updated_ks3)
        self.txtKS3.config(state="readonly")
        self.status_var.set("✅ Đã tìm và cập nhật KS3 thành công")

    def on_find_ks4(self):
        if not self.u_set or not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập U và F.")
            return
        
        new_ks4 = find_ks4(self.u_set, self.f_list)
        if not new_ks4:
            self.status_var.set("❌ Không tìm thấy KS4")
            return

        self.txtKS4.config(state="normal")
        current_ks4 = self.txtKS4.get().strip()
        
        if current_ks4:
            current_keys = set(current_ks4.split(';')) if current_ks4 else set()
            new_keys = set(new_ks4.split(';'))
            combined_keys = current_keys.union(new_keys)
            updated_ks4 = ';'.join(sorted(combined_keys))
        else:
            updated_ks4 = new_ks4

        self.txtKS4.delete(0, tk.END)
        self.txtKS4.insert(0, updated_ks4)
        self.txtKS4.config(state="readonly")
        self.status_var.set("✅ Đã tìm và cập nhật KS4 thành công")

    def on_find_ks5(self):
        if not self.u_set or not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập U và F.")
            return
        
        new_ks5 = find_ks5(self.u_set, self.f_list)
        if not new_ks5:
            self.status_var.set("❌ Không tìm thấy KS5")
            return

        self.txtKS5.config(state="normal")
        current_ks5 = self.txtKS5.get().strip()
        
        if current_ks5:
            current_keys = set(current_ks5.split(';')) if current_ks5 else set()
            new_keys = set(new_ks5.split(';'))
            combined_keys = current_keys.union(new_keys)
            updated_ks5 = ';'.join(sorted(combined_keys))
        else:
            updated_ks5 = new_ks5

        self.txtKS5.delete(0, tk.END)
        self.txtKS5.insert(0, updated_ks5)
        self.txtKS5.config(state="readonly")
        self.status_var.set("✅ Đã tìm và cập nhật KS5 thành công")

    def on_find_ks6(self):
        if not self.u_set or not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập U và F.")
            return
        
        new_ks6 = find_ks6(self.u_set, self.f_list)
        if not new_ks6:
            self.status_var.set("❌ Không tìm thấy KS6")
            return

        self.txtKS6.config(state="normal")
        current_ks6 = self.txtKS6.get().strip()
        
        if current_ks6:
            current_keys = set(current_ks6.split(';')) if current_ks6 else set()
            new_keys = set(new_ks6.split(';'))
            combined_keys = current_keys.union(new_keys)
            updated_ks6 = ';'.join(sorted(combined_keys))
        else:
            updated_ks6 = new_ks6

        self.txtKS6.delete(0, tk.END)
        self.txtKS6.insert(0, updated_ks6)
        self.txtKS6.config(state="readonly")
        self.status_var.set("✅ Đã tìm và cập nhật KS6 thành công")

    def on_find_f1(self):
        if not self.u_set or not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập U và F")
            return
        
        f1 = find_f1(self.f_list)
    
        self.txtF1.delete(1.0, tk.END)
        for vt, vp in f1:
            self.txtF1.insert(tk.END, f"{set_to_str(vt)} → {set_to_str(vp)}\n")
        
        self.status_var.set("✅ Đã tìm F1 thành công")

    def on_find_f2(self):
        if not self.u_set or not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập U và F")
            return
        
        f2 = find_f2(self.f_list, self.u_set)
    
        self.txtF2.delete(1.0, tk.END)
        for vt, vp in f2:
            self.txtF2.insert(tk.END, f"{set_to_str(vt)} → {set_to_str(vp)}\n")
        
        self.status_var.set("✅ Đã tìm F2 thành công")

    def on_find_f3(self):
        if not self.u_set or not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập U và F")
            return
        
        f3 = find_f3(self.f_list, self.u_set)
    
        self.txtF3.delete(1.0, tk.END)
        for vt, vp in f3:
            self.txtF3.insert(tk.END, f"{set_to_str(vt)} → {set_to_str(vp)}\n")
        
        self.status_var.set("✅ Đã tìm F3 thành công")

    def find_all_keys_ui(self):
        if not self.u_set or not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập U và F")
            return
        
        keys = find_all_keys(self.u_set, self.f_list)
    
        if keys:
            result = "Các khóa tìm thấy:\n\n"
            for i, key in enumerate(keys, 1):
                result += f"{i}. {set_to_str(key)}\n"
        else:
            result = "Không tìm thấy khóa nào"
        
        messagebox.showinfo("Tất cả các khóa", result)
        self.status_var.set(f"✅ Đã tìm thấy {len(keys)} khóa")

    def log_to_db(self):
        if not self.u_set:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập thuộc tính U")
            return

        if not self.f_list:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tập phụ thuộc hàm F")
            return

        data = {
            'u_set': set_to_str(self.u_set),
            'f_list': '\n'.join([f"{set_to_str(vt)} → {set_to_str(vp)}" for vt, vp in self.f_list]),
            'x_input': self.txtFindX.get().strip() or None,
            'x_plus': self.txtXPlus.get().strip() or None,
            'k1': self.txtK1.get().strip() or None,
            'k2': self.txtK2.get().strip() or None,
            'k3': self.txtK3.get().strip() or None,
            'ks1': self.txtKS1.get().strip() or None,
            'ks2': self.txtKS2.get().strip() or None,
            'ks3': self.txtKS3.get().strip() or None,
            'ks4': self.txtKS4.get().strip() or None,
            'ks5': self.txtKS5.get().strip() or None,
            'ks6': self.txtKS6.get().strip() or None,
            'f1': self.txtF1.get("1.0", "end").strip() or None,
            'f2': self.txtF2.get("1.0", "end").strip() or None,
            'f3': self.txtF3.get("1.0", "end").strip() or None,
        }

        try:
            insert_log(data)
            messagebox.showinfo("Thành công", "Đã lưu dữ liệu vào SQL Server")
            self.status_var.set("✅ Đã lưu dữ liệu vào cơ sở dữ liệu")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu dữ liệu: {e}")
            self.status_var.set("❌ Lỗi khi lưu dữ liệu")

    def show_history(self):
        try:
            logs = get_combined_logs()
            if not logs:
                messagebox.showinfo("Lịch sử", "Không có dữ liệu lịch sử.")
                return

            # Sort logs by created_at in descending order
            logs.sort(key=lambda x: x['created_at'], reverse=True)

            history_window = tk.Toplevel(self)
            history_window.title("📜 Lịch sử")
            history_window.geometry("1200x550")
            history_window.configure(bg="#f5f5f5")

            # Include schema_log_id in columns
            columns = ("created_at", "schema_log_id", "u_set", "f_list", "x_input", "x_plus", "k1", "k2", "k3", "ks1","ks2", "ks3", "ks4", "ks5", "ks6","f1", "f2", "f3")
            self.tree = ttk.Treeview(history_window, columns=columns, show='headings', selectmode='browse')

            column_widths = {
                "created_at": 140,
                "schema_log_id": 100,
                "u_set": 90,
                "f_list": 180,
                "x_input": 90,
                "x_plus": 90,
                "k1": 90,
                "k2": 90,
                "k3": 90,
                "ks1": 140,
                "ks2": 140,
                "ks3": 140,
                "ks4": 140,
                "ks5": 140,
                "ks6": 140,
                "f1": 180,
                "f2": 180,
                "f3": 180
            }
            for col in columns:
                header = col.upper().replace('_', ' ')
                self.tree.heading(col, text=header)
                self.tree.column(col, anchor="center", width=column_widths[col])

            self.tree.tag_configure('oddrow', background='#f0f0f0')
            self.tree.tag_configure('evenrow', background='#ffffff')

            # Store logs with their Treeview IDs for easier lookup
            self.log_map = {}
            for i, log in enumerate(logs):
                tag = 'oddrow' if i % 2 else 'evenrow'
                created_at_str = log['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                item_id = self.tree.insert("", "end", values=(
                    created_at_str,
                    log.get('schema_log_id', ''),  # Include schema_log_id
                    log.get('U', ''),  # Use 'U' as it comes from the database
                    log.get('f_list', ''),
                    log.get('x_input', ''),
                    log.get('x_plus', ''),
                    log.get('k1', ''),
                    log.get('k2', ''),
                    log.get('k3', ''),
                    log.get('ks1', ''),
                    log.get('ks2', ''),
                    log.get('ks3', ''),
                    log.get('ks4', ''),
                    log.get('ks5', ''),
                    log.get('f1', ''),
                    log.get('f2', ''),
                    log.get('f3', '')
                ), tags=(tag,))
                self.log_map[item_id] = log

            scrollbar_y = ttk.Scrollbar(history_window, orient="vertical", command=self.tree.yview)
            scrollbar_x = ttk.Scrollbar(history_window, orient="horizontal", command=self.tree.xview)
            self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

            self.tree.pack(side="top", fill="both", expand=True, padx=8, pady=8)
            scrollbar_y.pack(side="right", fill="y")
            scrollbar_x.pack(side="bottom", fill="x")

            # Bind double-click to show log details
            self.tree.bind('<Double-1>', lambda event: self.show_log_detail(history_window))

            button_frame = ttk.Frame(history_window)
            button_frame.pack(fill="x", pady=5)
            ttk.Button(button_frame, text="🔄 Làm mới", command=lambda: [history_window.destroy(), self.show_history()]).pack(side="left", padx=5)
            ttk.Button(button_frame, text="📋 Xem chi tiết", command=lambda: self.show_log_detail(history_window)).pack(side="left", padx=5)
            ttk.Button(button_frame, text="📤 Xuất CSV", command=lambda: self.export_history(logs)).pack(side="left", padx=5)

        except ImportError:
            messagebox.showerror("Lỗi", "Module pyodbc không được cài đặt. Vui lòng cài đặt bằng lệnh: pip install pyodbc")
        except Exception as e:
            logging.error(f"Error in show_history: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể hiển thị lịch sử: {str(e)}")

    def show_log_detail(self, history_window):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một bản ghi để xem chi tiết")
            return
        
        selected_item = selection[0]
        log = self.log_map.get(selected_item)
        if not log:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu chi tiết cho bản ghi này")
            return
        
        created_at_str = log['created_at'].strftime("%Y-%m-%d %H:%M:%S")
        
        detail_window = tk.Toplevel(self)
        detail_window.title(f"📋 Chi tiết - Thời gian: {created_at_str}")
        detail_window.geometry("450x600")
        detail_window.configure(bg="#f5f5f5")

        main_frame = ttk.Frame(detail_window)
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        canvas = tk.Canvas(main_frame, bg="#f5f5f5")
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)

        def get_text_height(content, default=4, max_height=10):
            if not content:
                return default
            lines = content.count('\n') + 1 if isinstance(content, str) else default
            return min(max(lines, default), max_height)

        ttk.Label(frame, text=f"⏰ Thời gian tạo: {created_at_str}", font=("Arial", 11, "bold")).pack(anchor="w", pady=4)
        if 'schema_log_id' in log:
            ttk.Label(frame, text=f"🆔 Schema Log ID: {log['schema_log_id']}", font=("Arial", 11)).pack(anchor="w", pady=4)
        ttk.Label(frame, text=f"🌌 Tập U: {log['U'] or 'N/A'}", font=("Arial", 11)).pack(anchor="w", pady=4)

        ttk.Label(frame, text="📋 Tập F:", font=("Arial", 11, "bold")).pack(anchor="w", pady=4)
        txt_f = tk.Text(frame, height=get_text_height(log['f_list']), width=50, font=("Arial", 11), bg="#ffffff", relief="flat", borderwidth=1)
        txt_f.insert(tk.END, log['f_list'] or 'N/A')
        txt_f.config(state="disabled")
        txt_f.pack(fill="x", pady=4)

        if log.get('x_input'):
            ttk.Label(frame, text=f"➡️ X Input: {log['x_input']}", font=("Arial", 11)).pack(anchor="w", pady=4)
        if log.get('x_plus'):
            ttk.Label(frame, text=f"🔍 X+: {log['x_plus']}", font=("Arial", 11)).pack(anchor="w", pady=4)

        if log.get('k1'):
            ttk.Label(frame, text=f"🔑 K1: {log['k1']}", font=("Arial", 11)).pack(anchor="w", pady=4)
        if log.get('k2'):
            ttk.Label(frame, text=f"🔑 K2: {log['k2']}", font=("Arial", 11)).pack(anchor="w", pady=4)
        if log.get('k3'):
            ttk.Label(frame, text=f"🔑 K3: {log['k3']}", font=("Arial", 11)).pack(anchor="w", pady=4)
        if log.get('ks1'):
            ttk.Label(frame, text=f"🔑 KS1: {log['ks1']}", font=("Arial", 11)).pack(anchor="w", pady=4)
        if log.get('ks2'):
            ttk.Label(frame, text=f"🔑 KS2: {log['ks2']}", font=("Arial", 11)).pack(anchor="w", pady=4)
        if log.get('ks3'):
            ttk.Label(frame, text=f"🔑 KS3: {log['ks3']}", font=("Arial", 11)).pack(anchor="w", pady=4)
        if log.get('ks4'):
            ttk.Label(frame, text=f"🔑 KS4: {log['ks4']}", font=("Arial", 11)).pack(anchor="w", pady=4)
        if log.get('ks5'):
            ttk.Label(frame, text=f"🔑 KS5: {log['ks5']}", font=("Arial", 11)).pack(anchor="w", pady=4)
        if log.get('ks6'):
            ttk.Label(frame, text=f"🔑 KS6: {log['ks6']}", font=("Arial", 11)).pack(anchor="w", pady=4)

        if log.get('f1'):
            ttk.Label(frame, text="📊 F1:", font=("Arial", 11, "bold")).pack(anchor="w", pady=4)
            txt_f1 = tk.Text(frame, height=get_text_height(log['f1']), width=50, font=("Arial", 11), bg="#ffffff", relief="flat", borderwidth=1)
            txt_f1.insert(tk.END, log['f1'])
            txt_f1.config(state="disabled")
            txt_f1.pack(fill="x", pady=4)

        if log.get('f2'):
            ttk.Label(frame, text="📊 F2:", font=("Arial", 11, "bold")).pack(anchor="w", pady=4)
            txt_f2 = tk.Text(frame, height=get_text_height(log['f2']), width=50, font=("Arial", 11), bg="#ffffff", relief="flat", borderwidth=1)
            txt_f2.insert(tk.END, log['f2'])
            txt_f2.config(state="disabled")
            txt_f2.pack(fill="x", pady=4)

        if log.get('f3'):
            ttk.Label(frame, text="📊 F3:", font=("Arial", 11, "bold")).pack(anchor="w", pady=4)
            txt_f3 = tk.Text(frame, height=get_text_height(log['f3']), width=50, font=("Arial", 11), bg="#ffffff", relief="flat", borderwidth=1)
            txt_f3.insert(tk.END, log['f3'])
            txt_f3.config(state="disabled")
            txt_f3.pack(fill="x", pady=4)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", pady=8)
        ttk.Button(button_frame, text="🗑 Xóa bản ghi", command=lambda: self.delete_log_and_close(log['created_at'], detail_window, history_window)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🔙 Đóng", command=detail_window.destroy).pack(side="left", padx=5)

        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

    def delete_log_and_close(self, created_at, detail_window, history_window):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa bản ghi này?"):
            try:
                if delete_log(created_at):
                    messagebox.showinfo("Thành công", "Đã xóa bản ghi")
                    detail_window.destroy()
                    history_window.destroy()
                    self.show_history()
                else:
                    messagebox.showerror("Lỗi", "Không thể xóa bản ghi")
            except Exception as e:
                logging.error(f"Error deleting log: {str(e)}")
                messagebox.showerror("Lỗi", f"Lỗi khi xóa bản ghi: {str(e)}")

    def export_history(self, logs):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Lưu tệp CSV"
            )
            if not file_path:
                return

            # Include schema_log_id in fieldnames
            fieldnames = ["created_at", "schema_log_id", "u_set", "f_list", "x_input", "x_plus", "k1", "k2", "k3", "ks1", "ks2", "ks3", "ks4", "ks5", "ks6", "f1", "f2", "f3"]

            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
                # Write header with descriptive names
                writer.writerow({
                    "created_at": "Thời gian tạo",
                    "schema_log_id": "Schema Log ID",
                    "u_set": "Tập U",
                    "f_list": "Tập F",
                    "x_input": "X Input",
                    "x_plus": "X+",
                    "k1": "K1",
                    "k2": "K2",
                    "k3": "K3",
                    "ks1": "KS1",
                    "ks2": "KS2",
                    "ks3": "KS3",
                    "ks4": "KS4",
                    "ks5": "KS5",
                    "ks6": "KS6",
                    "f1": "F1",
                    "f2": "F2",
                    "f3": "F3"
                })
                for log in logs:
                    log_copy = log.copy()
                    # Format the timestamp
                    log_copy['created_at'] = log_copy['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                    # Rename 'U' to 'u_set' to match fieldnames
                    if 'U' in log_copy:
                        log_copy['u_set'] = log_copy.pop('U')
                    # Replace None with empty string and ensure strings
                    for key in log_copy:
                        log_copy[key] = '' if log_copy[key] is None else str(log_copy[key])
                    writer.writerow(log_copy)

            messagebox.showinfo("Thành công", f"Đã xuất lịch sử ra {file_path}")
            self.status_var.set("✅ Đã xuất lịch sử ra CSV")
        except PermissionError:
            logging.error("Lỗi quyền truy cập: Không thể ghi vào tệp CSV")
            messagebox.showerror("Lỗi", "Không có quyền ghi vào tệp. Vui lòng kiểm tra quyền truy cập hoặc chọn vị trí khác.")
        except Exception as e:
            logging.error(f"Lỗi khi xuất CSV: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi khi xuất CSV: {str(e)}")

    def test_db_connection(self):
        try:
            conn = get_connection()
            if conn:
                conn.close()
                messagebox.showinfo("Kết nối thành công", "Đã kết nối được đến SQL Server")
            else:
                messagebox.showerror("Lỗi kết nối", "Không thể kết nối đến SQL Server")
        except ImportError:
            messagebox.showerror("Lỗi", "Module pyodbc không được cài đặt. Vui lòng cài đặt bằng lệnh: pip install pyodbc")
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", f"Lỗi: {str(e)}")

    def reset_data(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tất cả dữ liệu đã nhập?"):
            self.txtU.delete(0, tk.END)
            self.txtUDisplay.config(state="normal")
            self.txtUDisplay.delete(0, tk.END)
            self.txtUDisplay.config(state="readonly")
            self.u_set = set()
        
            self.txtF.delete(1.0, tk.END)
            self.f_list = []
        
            self.txtX.delete(0, tk.END)
            self.txtY.delete(0, tk.END)
        
            self.txtFindX.delete(0, tk.END)
            self.txtXPlus.config(state="normal")
            self.txtXPlus.delete(0, tk.END)
            self.txtXPlus.config(state="readonly")
        
            self.txtK1.config(state="normal")
            self.txtK1.delete(0, tk.END)
            self.txtK1.config(state="readonly")
        
            self.txtK2.config(state="normal")
            self.txtK2.delete(0, tk.END)
            self.txtK2.config(state="readonly")
        
            self.txtK3.config(state="normal")
            self.txtK3.delete(0, tk.END)
            self.txtK3.config(state="readonly")
        
            self.txtKS1.config(state="normal")
            self.txtKS1.delete(0, tk.END)
            self.txtKS1.config(state="readonly")

            self.txtKS2.config(state="normal")
            self.txtKS2.delete(0, tk.END)
            self.txtKS2.config(state="readonly")
        
            self.txtKS3.config(state="normal")
            self.txtKS3.delete(0, tk.END)
            self.txtKS3.config(state="readonly")

            self.txtKS4.config(state="normal")
            self.txtKS4.delete(0, tk.END)
            self.txtKS4.config(state="readonly")
        
            self.txtKS5.config(state="normal")
            self.txtKS5.delete(0, tk.END)
            self.txtKS5.config(state="readonly")
        
            self.txtKS6.config(state="normal")
            self.txtKS6.delete(0, tk.END)
            self.txtKS6.config(state="readonly")

            self.txtF1.delete(1.0, tk.END)
            self.txtF2.delete(1.0, tk.END)
            self.txtF3.delete(1.0, tk.END)
        
            self.status_var.set("✅ Đã xóa tất cả dữ liệu")

    def show_help(self):
        help_text = """
        📖 HƯỚNG DẪN SỬ DỤNG PHẦN MỀM TÌM KHÓA LƯỢC ĐỒ QUAN HỆ
    
        1. 🌌 Nhập tập thuộc tính vũ trụ U:
           - Nhập các ký tự đại diện cho thuộc tính, ví dụ: ABCDEF
       
        2. ➕ Thêm phụ thuộc hàm:
           - Nhập X (vế trái), ví dụ: AB
           - Nhập Y (vế phải), ví dụ: CD
           - Nhấn "Thêm phụ thuộc hàm"
       
        3. 🔍 Tìm X+:
           - Nhập X cần tìm bao đóng
           - Nhấn "Tìm X+"
       
        4. 🔑 Tìm khóa:
           - Nhấn "Tìm K1", "Tìm K2", "Tìm K3", "Tìm KS1", "Tìm KS2", "Tìm KS3", "Tìm KS4", "Tìm KS5", "Tìm KS6" để tìm khóa theo từng thuật toán
           - KS1 trả về tất cả các khóa ứng viên
           - KS2 trả về các khóa ứng viên có số thuộc tính tối thiểu và ít phụ thuộc
           - KS3 ưu tiên các khóa chứa nhiều thuộc tính ở vế trái và cân bằng
           - KS4 tối ưu hóa độ bao phủ của tập phụ thuộc hàm
           - KS5 dựa trên phân tích đồ thị phụ thuộc với năng lượng thấp
           - KS6 kết hợp bao phủ và năng lượng để tối ưu hóa
           - Các khóa được phân tách bằng dấu chấm phẩy
       
        5. 📊 Tìm tập phụ thuộc hàm tối thiểu:
           - Nhấn "Tìm F1", "Tìm F2", "Tìm F3" để tìm tập phụ thuộc hàm tối thiểu
       
        6. 💾 Lưu kết quả:
           - Nhấn "Lưu vào SQL Server" để lưu kết quả vào cơ sở dữ liệu
       
        7. 📜 Xem lịch sử:
           - Vào menu "Công cụ" > "Xem lịch sử" để xem các kết quả đã lưu
           - Nhấn vào một bản ghi để xem chi tiết
           - Nhấn "Xuất CSV" để lưu lịch sử ra file CSV
        """
    
        help_window = tk.Toplevel(self)
        help_window.title("📖 Hướng dẫn sử dụng")
        help_window.geometry("650x550")
        help_window.configure(bg="#f5f5f5")
    
        txt_help = tk.Text(help_window, font=("Arial", 11), wrap="word", bg="#ffffff", relief="flat", borderwidth=1)
        txt_help.pack(fill="both", expand=True, padx=8, pady=8)
        txt_help.insert(tk.END, help_text)
        txt_help.config(state="disabled")
    
        scrollbar = ttk.Scrollbar(txt_help, command=txt_help.yview)
        txt_help.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def show_about(self):
        about_text = """
        ℹ ỨNG DỤNG TÌM KHÓA LƯỢC ĐỒ QUAN HỆ
    
        Chức năng chính:
        - 🔍 Tìm bao đóng của tập thuộc tính
        - 🔑 Tìm khóa của lược đồ quan hệ
        - 📊 Tìm tập phụ thuộc hàm tối thiểu
        - 💾 Lưu và xem lịch sử các kết quả
    
        Đây là một ứng dụng minh họa cho các thuật toán cơ sở dữ liệu.
        """
    
        messagebox.showinfo("ℹ Giới thiệu", about_text)

if __name__ == "__main__":
    logging.basicConfig(filename='app.log', level=logging.DEBUG, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    app = KeyFindingApp()
    app.mainloop()

import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import re
from datetime import datetime
import platform
import json

try:
    from ttkthemes import ThemedTk
except ImportError:
    ThemedTk = None

try:
    import azure.azure_tcl_theme
    _azure_theme_available = True
except ImportError:
    _azure_theme_available = False

SETTINGS_FILE = "namefluxer_settings.json"

class FileRenamerApp:
    def __init__(self, master):
        self.master = master
        master.title("NameFluxer - Renomeador Inteligente")
        master.geometry("1000x800")
        master.resizable(True, True)

        if platform.system() == "Windows":
            master.state('zoomed')
        else:
            try:
                master.attributes('-zoom', True)
            except tk.TclError:
                pass

        style = ttk.Style()

        if _azure_theme_available:
            try:
                azure.azure_tcl_theme.set_theme(self.master, "light")
                style.theme_use('azure')
            except Exception as e:
                if ThemedTk:
                    style.theme_use('forest-light')
                else:
                    style.theme_use('clam')
        elif ThemedTk:
            try:
                style.theme_use('forest-light')
            except tk.TclError:
                try:
                    style.theme_use('arc')
                except tk.TclError:
                    style.theme_use('clam')
        else:
            try:
                style.theme_use('arc')
            except tk.TclError:
                style.theme_use('clam')

        self.primary_color = '#4A90E2'
        self.secondary_color = '#6C757D'
        self.background_color = '#F8F9FA'
        self.light_gray = '#E9ECEF'

        style.configure('.', background=self.background_color, font=('Segoe UI', 10))
        style.configure('TFrame', background=self.background_color)
        style.configure('TLabelframe', background=self.background_color, borderwidth=1, relief='flat')
        style.configure('TLabelframe.Label', font=('Segoe UI', 11, 'bold'), foreground=self.primary_color)
        style.configure('TLabel', background=self.background_color, foreground='#333333', font=('Segoe UI', 10))
        style.configure('TEntry', font=('Segoe UI', 10), fieldbackground='white', foreground='#333333')
        style.configure('TCheckbutton', background=self.background_color, font=('Segoe UI', 10))
        style.configure('TMenubutton', background='white', foreground='#333333', font=('Segoe UI', 10), borderwidth=1, relief='solid')
        style.map('TMenubutton', background=[('active', self.light_gray)])
        style.configure('Accent.TButton',
                        background=self.primary_color,
                        foreground='white',
                        font=('Segoe UI', 11, 'bold'),
                        borderwidth=0,
                        focusthickness=3,
                        focuscolor='none',
                        padding=[10, 5])
        style.map('Accent.TButton',
                  background=[('active', '#357ABD')])
        style.configure('Secondary.TButton',
                        background=self.light_gray,
                        foreground='#333333',
                        font=('Segoe UI', 10),
                        borderwidth=0,
                        focusthickness=3,
                        focuscolor='none',
                        padding=[8, 3])
        style.map('Secondary.TButton',
                  background=[('active', '#DDE3E9')])

        self.directory_path = tk.StringVar()
        self.output_pattern_var = tk.StringVar(value="")
        self.sequential_var = tk.BooleanVar(value=False)
        self.start_num_var = tk.IntVar(value=1)
        self.digits_var = tk.IntVar(value=3)
        self.recursive_var = tk.BooleanVar(value=False)

        self.replace_old_var = tk.StringVar()
        self.replace_new_var = tk.StringVar()

        self.remove_pattern_var = tk.StringVar()

        self.case_option = tk.StringVar(value="Manter")
        self.space_option = tk.StringVar(value="Manter")

        self.custom_date_var = tk.StringVar(value=datetime.now().strftime("%Y%m%d"))
        self.use_custom_date_var = tk.BooleanVar(value=False)
        self.date_input_format_option = tk.StringVar(value="YYYYMMDD")
        self.date_output_format_option = tk.StringVar(value="YYYYMMDD")

        self.ignore_ext_case_var = tk.BooleanVar(value=True)
        self.overwrite_conflict_var = tk.BooleanVar(value=False)
        self.add_increment_on_conflict_var = tk.BooleanVar(value=True)

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(pady=15, padx=15, expand=True, fill="both")

        tab1 = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab1, text="1. Geral")
        self.setup_general_tab(tab1)

        tab2 = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab2, text="2. Transformações")
        self.setup_transform_tab(tab2)

        tab3 = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab3, text="3. Padrão & Avançado")
        self.setup_advanced_tab(tab3)

        tab4 = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab4, text="Instruções")
        self.setup_instructions_tab(tab4)

        action_frame = ttk.Frame(master, style='TFrame')
        action_frame.pack(pady=10, padx=15, fill="x")

        ttk.Button(action_frame, text="✨ Prévia das Mudanças", command=lambda: self.run_renamer(preview=True), style='Accent.TButton').pack(side="left", expand=True, fill="x", padx=5)
        ttk.Button(action_frame, text="🚀 Renomear Agora!", command=lambda: self.run_renamer(preview=False), style='Accent.TButton').pack(side="right", expand=True, fill="x", padx=5)

        self.log_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=60, height=15, state='disabled',
                                                 font=('Consolas', 9), bg='#ffffff', fg='#333333', relief='flat', borderwidth=1, highlightbackground=self.light_gray)
        self.log_text.pack(pady=10, padx=15, fill="both", expand=True)

        self.add_all_tooltips()
        self.load_settings()
        self.show_welcome_message()

    def _add_tooltip_for_widget(self, widget, text):
        def enter(event):
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root + 20}+{event.y_root + 20}")
            label = tk.Label(self.tooltip, text=text, background="#FFFFCC", relief="solid", borderwidth=1,
                             wraplength=280, font=("Segoe UI", 9))
            label.pack(padx=5, pady=3)
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def add_all_tooltips(self):
        self._add_tooltip_for_widget(self.directory_path_entry, "Selecione a pasta onde os arquivos serão renomeados.")
        self._add_tooltip_for_widget(self.output_pattern_entry, "Defina o novo nome usando placeholders: {original_name}, {sequence}, {date}, {ext}. Você pode adicionar prefixos/sufixos diretamente aqui. Ex: 'MinhaFoto_{sequence}_{date}.{ext}'")
        self._add_tooltip_for_widget(self.sequential_cb, "Adiciona um número sequencial ao nome do arquivo (ex: '001', '002').")
        self._add_tooltip_for_widget(self.start_num_entry, "Número de início para a sequência (ex: 1, 10).")
        self._add_tooltip_for_widget(self.digits_entry, "Número de dígitos para a sequência (ex: 3 para 001, 002).")
        self._add_tooltip_for_widget(self.recursive_cb, "Renomeia arquivos em todas as subpastas do diretório selecionado.")
        self._add_tooltip_for_widget(self.replace_old_entry, "Texto a ser encontrado e substituído no nome do arquivo.")
        self._add_tooltip_for_widget(self.replace_new_entry, "Texto pelo qual o 'Encontrar' será trocado.")
        self._add_tooltip_for_widget(self.remove_pattern_entry, "Expressão Regular (Regex) para remover partes do nome. Ex: `\\(.*?\\)` para remover texto entre parênteses.")
        self._add_tooltip_for_widget(self.case_option_menu, "Converte o nome do arquivo para maiúsculas, minúsculas ou capitaliza a primeira letra.")
        self._add_tooltip_for_widget(self.space_option_menu, "Gerencia espaços no nome do arquivo: remove todos ou substitui por sublinhados.")
        self._add_tooltip_for_widget(self.use_custom_date_cb, "Ativar esta opção para usar uma data personalizada no nome do arquivo. Utilize o placeholder {date} no padrão de nome final.")
        self._add_tooltip_for_widget(self.custom_date_entry, "Defina a data personalizada a ser usada. O formato deve corresponder ao 'Formato de Entrada'.")
        self._add_tooltip_for_widget(self.date_input_format_menu, "Escolha o formato em que a data foi digitada na caixa 'Data'.")
        self._add_tooltip_for_widget(self.date_output_format_menu, "Escolha o formato da data como ela aparecerá no nome do arquivo.")
        self._add_tooltip_for_widget(self.ignore_ext_case_cb, "Considera 'JPG' e 'jpg' a mesma extensão ao gerar o novo nome.")
        self._add_tooltip_for_widget(self.overwrite_conflict_cb, "Se o novo nome já existir, o arquivo antigo será sobrescrito. Use com cautela!")
        self._add_tooltip_for_widget(self.add_increment_on_conflict_cb, "Se o novo nome já existir, adiciona um sufixo '(1)', '(2)' ao arquivo (ex: 'foto (1).jpg').")

    def setup_general_tab(self, tab):
        frame = ttk.LabelFrame(tab, text="Configurações Básicas")
        frame.pack(pady=20, padx=20, fill="x")
        frame.grid_columnconfigure(1, weight=1)

        ttk.Label(frame, text="1. Selecione a Pasta:").grid(row=0, column=0, sticky="w", pady=10, padx=10)
        self.directory_path_entry = ttk.Entry(frame, textvariable=self.directory_path, state="readonly")
        self.directory_path_entry.grid(row=0, column=1, sticky="ew", padx=10)
        ttk.Button(frame, text="📁 Procurar...", command=self.browse_directory, style='Secondary.TButton').grid(row=0, column=2, padx=10)

        ttk.Label(frame, text="2. Padrão de Nome Final:").grid(row=1, column=0, sticky="w", pady=10, padx=10)
        self.output_pattern_entry = ttk.Entry(frame, textvariable=self.output_pattern_var)
        self.output_pattern_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=10)
        ttk.Label(frame, text="Placeholders disponíveis: {original_name}, {sequence}, {date}, {ext}").grid(row=2, column=0, columnspan=3, sticky="w", padx=10, pady=5)
        ttk.Label(frame, text="Exemplos: 'Foto_{sequence}_{date}.{ext}', 'Doc-{original_name}', '{original_name}-rev.{ext}'").grid(row=3, column=0, columnspan=3, sticky="w", padx=10, pady=5)

        ttk.Label(frame, text="3. Numeração Sequencial:").grid(row=4, column=0, sticky="w", pady=10, padx=10)
        self.sequential_cb = ttk.Checkbutton(frame, text="Ativar Numeração", variable=self.sequential_var)
        self.sequential_cb.grid(row=4, column=1, sticky="w", padx=10)

        num_options_frame = ttk.Frame(frame, style='TFrame')
        num_options_frame.grid(row=4, column=2, sticky="w", padx=10)
        ttk.Label(num_options_frame, text="Início:").pack(side="left", padx=(0,5))
        self.start_num_entry = ttk.Entry(num_options_frame, textvariable=self.start_num_var, width=5)
        self.start_num_entry.pack(side="left", padx=(0,10))
        self.start_num_entry.bind("<FocusOut>", self.validate_numeric_input)
        ttk.Label(num_options_frame, text="Dígitos:").pack(side="left", padx=(0,5))
        self.digits_entry = ttk.Entry(num_options_frame, textvariable=self.digits_var, width=5)
        self.digits_entry.pack(side="left")
        self.digits_entry.bind("<FocusOut>", self.validate_numeric_input)

        ttk.Label(frame, text="4. Data Personalizada:").grid(row=5, column=0, sticky="w", pady=10, padx=10)
        self.use_custom_date_cb = ttk.Checkbutton(frame, text="Usar Data Personalizada", variable=self.use_custom_date_var)
        self.use_custom_date_cb.grid(row=5, column=1, sticky="w", padx=10)

        date_options_frame = ttk.Frame(frame, style='TFrame')
        date_options_frame.grid(row=5, column=2, sticky="w", padx=10)
        
        ttk.Label(date_options_frame, text="Data:").pack(side="left", padx=(0,5))
        self.custom_date_entry = ttk.Entry(date_options_frame, textvariable=self.custom_date_var, width=12)
        self.custom_date_entry.pack(side="left", padx=(0,5))
        self.custom_date_entry.bind("<FocusOut>", self.validate_date_input)

        ttk.Label(date_options_frame, text="Entrada:").pack(side="left", padx=(0,5))
        self.date_input_format_menu = tk.OptionMenu(date_options_frame, self.date_input_format_option, "YYYYMMDD", "YYYY-MM-DD", "DDMMYYYY", "DD-MM-YYYY")
        self.date_input_format_menu.pack(side="left")
        self.date_input_format_menu.config(font=('Segoe UI', 9), bg='white', fg='#333333', activebackground=self.light_gray, activeforeground='#333333', relief='flat', borderwidth=1)
        self.date_input_format_option.trace_add("write", lambda *args: self.update_date_format_labels())

        ttk.Label(date_options_frame, text="Saída:").pack(side="left", padx=(10,5))
        self.date_output_format_menu = tk.OptionMenu(date_options_frame, self.date_output_format_option, "YYYYMMDD", "YYYY-MM-DD", "DDMMYYYY", "DD-MM-YYYY")
        self.date_output_format_menu.pack(side="left")
        self.date_output_format_menu.config(font=('Segoe UI', 9), bg='white', fg='#333333', activebackground=self.light_gray, activeforeground='#333333', relief='flat', borderwidth=1)

        self.input_date_label = ttk.Label(date_options_frame, text="", foreground='#6C757D')
        self.input_date_label.pack(side="left", padx=(5,0))
        self.update_date_format_labels()

        ttk.Label(frame, text="5. Subpastas:").grid(row=6, column=0, sticky="w", pady=10, padx=10)
        self.recursive_cb = ttk.Checkbutton(frame, text="Incluir arquivos em subpastas (Recursivo)", variable=self.recursive_var)
        self.recursive_cb.grid(row=6, column=1, columnspan=2, sticky="w", padx=10)

    def update_date_format_labels(self, *args):
        format_map_display = {
            "YYYYMMDD": "AAAA-MM-DD (ex: 20250609)",
            "YYYY-MM-DD": "AAAA-MM-DD (ex: 2025-06-09)",
            "DDMMYYYY": "DDMMYYYY (ex: 09062025)",
            "DD-MM-YYYY": "DD-MM-YYYY (ex: 09-06-2025)"
        }
        current_input_format = self.date_input_format_option.get()
        self.input_date_label.config(text=f"Formato: {format_map_display.get(current_input_format, '')}")

    def validate_numeric_input(self, event=None):
        try:
            value = self.start_num_var.get()
            if not isinstance(value, int) or value <= 0:
                self.start_num_var.set(1)
                messagebox.showwarning("Entrada Inválida", "O número inicial deve ser um inteiro positivo.")
                self.log("Aviso: Número inicial inválido, redefinido para 1.")
                return False
        except tk.TclError:
            self.start_num_var.set(1)
            messagebox.showwarning("Entrada Inválida", "O número inicial deve ser um número inteiro.")
            self.log("Aviso: Número inicial inválido, redefinido para 1.")
            return False
        
        try:
            value = self.digits_var.get()
            if not isinstance(value, int) or value <= 0:
                self.digits_var.set(3)
                messagebox.showwarning("Entrada Inválida", "O número de dígitos deve ser um inteiro positivo.")
                self.log("Aviso: Número de dígitos inválido, redefinido para 3.")
                return False
        except tk.TclError:
            self.digits_var.set(3)
            messagebox.showwarning("Entrada Inválida", "O número de dígitos deve ser um número inteiro.")
            self.log("Aviso: Número de dígitos inválido, redefinido para 3.")
            return False
        return True

    def validate_date_input(self, event=None):
        if not self.use_custom_date_var.get():
            self.custom_date_entry.config(foreground='black')
            return True
        
        date_str = self.custom_date_var.get()
        input_format_key = self.date_input_format_option.get()

        format_map = {
            "YYYYMMDD": "%Y%m%d",
            "YYYY-MM-DD": "%Y-%m-%d",
            "DDMMYYYY": "%d%m%Y",
            "DD-MM-YYYY": "%d-%m-%Y"
        }
        
        python_format = format_map.get(input_format_key)

        if not python_format:
            self.log(f"Erro de Validação: Formato de entrada de data '{input_format_key}' inválido.")
            self.custom_date_entry.config(foreground='red')
            messagebox.showerror("Erro de Formato", "Formato de entrada de data selecionado é inválido.")
            return False

        try:
            datetime.strptime(date_str, python_format)
            self.custom_date_entry.config(foreground='black')
            return True
        except ValueError:
            self.log(f"Erro de Validação: Data '{date_str}' não corresponde ao formato de entrada '{input_format_key}'.")
            self.custom_date_entry.config(foreground='red')
            messagebox.showwarning("Formato de Data Inválido", f"A data '{date_str}' não corresponde ao formato de entrada '{input_format_key}'. Por favor, corrija.")
            return False

    def setup_transform_tab(self, tab):
        frame = ttk.LabelFrame(tab, text="Transformações de Texto no Nome")
        frame.pack(pady=20, padx=20, fill="x")
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(3, weight=1)

        ttk.Label(frame, text="1. Substituir Texto:").grid(row=0, column=0, sticky="w", pady=10, padx=10)
        ttk.Label(frame, text="Encontrar:").grid(row=1, column=0, sticky="w", padx=10)
        self.replace_old_entry = ttk.Entry(frame, textvariable=self.replace_old_var)
        self.replace_old_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        ttk.Label(frame, text="Substituir por:").grid(row=1, column=2, sticky="w", padx=(10,0))
        self.replace_new_entry = ttk.Entry(frame, textvariable=self.replace_new_var)
        self.replace_new_entry.grid(row=1, column=3, sticky="ew", pady=5, padx=5)

        ttk.Label(frame, text="2. Remover Padrão (Regex):").grid(row=2, column=0, sticky="w", pady=10, padx=10)
        self.remove_pattern_entry = ttk.Entry(frame, textvariable=self.remove_pattern_var)
        self.remove_pattern_entry.grid(row=3, column=0, columnspan=4, sticky="ew", padx=10, pady=5)
        ttk.Label(frame, text="Ex: `\\(.*?\\)` (remove texto entre parênteses) | `\\d{4}` (remove números de 4 dígitos)").grid(row=4, column=0, columnspan=4, sticky="w", padx=10, pady=5)

        ttk.Label(frame, text="3. Converter Case:").grid(row=5, column=0, sticky="w", pady=10, padx=10)
        self.case_option_menu = tk.OptionMenu(frame, self.case_option, "Manter", "Maiúsculas", "Minúsculas", "Capitalizar")
        self.case_option_menu.grid(row=5, column=1, sticky="ew", pady=5, padx=5)
        self.case_option_menu.config(font=('Segoe UI', 10), bg='white', fg='#333333', activebackground=self.light_gray, activeforeground='#333333', relief='flat', borderwidth=1)

        ttk.Label(frame, text="4. Gerenciar Espaços:").grid(row=6, column=0, sticky="w", pady=10, padx=10)
        self.space_option_menu = tk.OptionMenu(frame, self.space_option, "Manter", "Remover Todos", "Substituir por '_'")
        self.space_option_menu.grid(row=6, column=1, sticky="ew", pady=5, padx=5)
        self.space_option_menu.config(font=('Segoe UI', 10), bg='white', fg='#333333', activebackground=self.light_gray, activeforeground='#333333', relief='flat', borderwidth=1)

    def setup_advanced_tab(self, tab):
        frame = ttk.LabelFrame(tab, text="Opções Avançadas e Conflitos")
        frame.pack(pady=20, padx=20, fill="x")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        ttk.Label(frame, text="1. Tratamento de Extensão:").grid(row=0, column=0, sticky="w", pady=10, padx=10)
        self.ignore_ext_case_cb = ttk.Checkbutton(frame, text="Considerar extensão maiúscula/minúscula como a mesma (ex: .JPG == .jpg)", variable=self.ignore_ext_case_var)
        self.ignore_ext_case_cb.grid(row=1, column=0, columnspan=2, sticky="w", padx=10)

        ttk.Label(frame, text="2. Conflito de Nomes (Quando o nome final já existe):").grid(row=2, column=0, sticky="w", pady=10, padx=10)
        self.add_increment_on_conflict_cb = ttk.Checkbutton(frame, text="Adicionar um número incremental ao final (ex: 'arquivo (1).ext') - Recomendado", variable=self.add_increment_on_conflict_var)
        self.add_increment_on_conflict_cb.grid(row=3, column=0, columnspan=2, sticky="w", padx=10)
        self.overwrite_conflict_cb = ttk.Checkbutton(frame, text="Sobrescrever arquivo existente (⚠️ CUIDADO!)", variable=self.overwrite_conflict_var)
        self.overwrite_conflict_cb.grid(row=4, column=0, columnspan=2, sticky="w", padx=10)
        self.overwrite_conflict_cb.bind("<Button-1>", self.warn_overwrite)

        ttk.Label(frame, text="3. Restrições de Nome de Arquivo:").grid(row=5, column=0, sticky="w", pady=10, padx=10)
        ttk.Label(frame, text='Caracteres que serão removidos automaticamente: / \\ : * ? " < > |').grid(row=6, column=0, columnspan=2, sticky="w", padx=10)

    def setup_instructions_tab(self, tab):
        instructions_frame = ttk.Frame(tab, style='TFrame')
        instructions_frame.pack(pady=20, padx=20, fill="both", expand=True)

        ttk.Label(instructions_frame, text="Guia Rápido de Uso do NameFluxer:", font=('Segoe UI', 14, 'bold'), foreground=self.primary_color).pack(pady=10)
        
        instructions_text_content = """
Bem-vindo(a) ao **NameFluxer**, sua ferramenta inteligente para renomear arquivos em massa!

---

**Passos Básicos para Renomear:**

1.  **Aba "1. Geral"**:
    * **Selecione a Pasta**: Clique em "📁 **Procurar...**" para escolher o diretório que contém os arquivos que você deseja renomear.
    * **Padrão de Nome Final**: Digite o novo padrão de nome para seus arquivos. Você pode usar os seguintes placeholders para incluir informações dinâmicas:
        * **{original_name}**: O nome original do arquivo (sem a extensão).
        * **{sequence}**: Um número sequencial (ex: 001, 002...). Ative a "Numeração Sequencial" e defina o início e o número de dígitos.
        * **{date}**: Uma data. Ative "Usar Data Personalizada" para definir a data e seus formatos de entrada/saída.
        * **{ext}**: A extensão original do arquivo (ex: .jpg, .pdf).
    * **Exemplos de Padrões**:
        * `MinhaFoto_{sequence}_{date}.{ext}`
        * `Documento-Projeto-{original_name}.{ext}`
        * `Relatório_{date}-v2.{ext}`
    * **Subpastas**: Marque "Incluir arquivos em subpastas (Recursivo)" se quiser renomear arquivos em todas as pastas dentro do diretório selecionado.

---

**Aba "2. Transformações" (Opcional):**

* **Substituir Texto**: Encontre e substitua partes específicas do nome do arquivo (ex: trocar "antigo" por "novo").
* **Remover Padrão (Regex)**: Use Expressões Regulares (Regex) para remover padrões complexos (ex: `\\(.*?\\)` para remover texto entre parênteses).
* **Converter Case**: Altere a caixa das letras do nome do arquivo (Maiúsculas, Minúsculas, Capitalizar).
* **Gerenciar Espaços**: Remova todos os espaços ou substitua-os por sublinhados (`_`).

---

**Aba "3. Padrão & Avançado":**

* **Tratamento de Extensão**: "Considerar extensão maiúscula/minúscula como a mesma" normaliza as extensões (ex: .JPG e .jpg são tratados como .jpg).
* **Conflito de Nomes**:
    * **Adicionar um número incremental ao final (Recomendado)**: Se o nome final gerado já existir (ex: `foto.jpg`), o programa adicionará um sufixo numérico para evitar conflitos (ex: `foto (1).jpg`, `foto (2).jpg`). **Esta é a opção mais segura e recomendada.**
    * **Sobrescrever arquivo existente (⚠️ CUIDADO!)**: Selecionar esta opção fará com que qualquer arquivo existente com o novo nome seja **permanentemente perdido**. Use com extrema cautela!
* **Restrições de Nome de Arquivo**: Caracteres inválidos em nomes de arquivo (`/ \ : * ? " < > |`) serão automaticamente removidos para garantir compatibilidade.

---

**Ações Finais:**

* **✨ Prévia das Mudanças**: Clique neste botão para ver uma lista de como os arquivos seriam renomeados, sem realmente fazer as alterações. Verifique o painel de log abaixo.
* **🚀 Renomear Agora!**: Clique para aplicar todas as transformações e renomear os arquivos.

---

**Painel de Log**: Na parte inferior da janela, o painel de log exibe todas as ações, avisos e erros durante a prévia ou renomeação.
        """
        
        instructions_st = scrolledtext.ScrolledText(instructions_frame, wrap=tk.WORD, width=90, height=25,
                                                   font=('Segoe UI', 10), bg='#ffffff', fg='#333333', relief='flat', borderwidth=1, highlightbackground=self.light_gray)
        instructions_st.pack(pady=10, fill="both", expand=True)
        
        instructions_st.insert(tk.END, instructions_text_content)
        instructions_st.config(state='disabled')
        
        instructions_st.tag_configure('bold', font=('Segoe UI', 10, 'bold'))
        instructions_st.tag_configure('warning', foreground='red', font=('Segoe UI', 10, 'bold'))

        instructions_st.tag_add('bold', '8.27', '8.44')
        instructions_st.tag_add('bold', '8.47', '8.58')
        instructions_st.tag_add('bold', '8.61', '8.69')
        instructions_st.tag_add('bold', '8.72', '8.79')

        instructions_st.tag_add('bold', '42.4', '42.39')
        instructions_st.tag_add('bold', '43.20', '43.37')
        instructions_st.tag_add('bold', '44.4', '44.33')
        instructions_st.tag_add('warning', '44.35', '44.49')
        instructions_st.tag_add('bold', '45.41', '45.58')

        instructions_st.tag_add('bold', '52.4', '52.26')
        instructions_st.tag_add('bold', '54.4', '54.21')

    def warn_overwrite(self, event=None):
        if not self.overwrite_conflict_var.get():
            response = messagebox.askyesno(
                "Atenção: Sobrescrever Arquivos!",
                "Marcar esta opção fará com que arquivos com o mesmo nome sejam PERDIDOS sem aviso. Deseja continuar?",
                icon='warning'
            )
            if not response:
                self.overwrite_conflict_var.set(False)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_path.set(directory)
            self.log("Diretório selecionado: " + directory)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def sanitize_filename(self, filename):
        invalid_chars = r'[\\/:*?"<>|]'
        return re.sub(invalid_chars, '', filename)

    def generate_new_filename(self, original_name_no_ext, original_ext, sequence_num=None):
        pattern = self.output_pattern_var.get()
        new_name_no_ext_processed = original_name_no_ext

        old_text = self.replace_old_var.get()
        new_text = self.replace_new_var.get()
        if old_text:
            new_name_no_ext_processed = new_name_no_ext_processed.replace(old_text, new_text)

        pattern_to_remove = self.remove_pattern_var.get()
        if pattern_to_remove:
            try:
                new_name_no_ext_processed = re.sub(pattern_to_remove, '', new_name_no_ext_processed)
            except re.error:
                self.log(f"Aviso: Padrão Regex inválido '{pattern_to_remove}'. Ignorando.")

        space_option = self.space_option.get()
        if space_option == "Remover Todos":
            new_name_no_ext_processed = new_name_no_ext_processed.replace(" ", "")
        elif space_option == "Substituir por '_'":
            new_name_no_ext_processed = new_name_no_ext_processed.replace(" ", "_")

        case_option = self.case_option.get()
        if case_option == "Maiúsculas":
            new_name_no_ext_processed = new_name_no_ext_processed.upper()
        elif case_option == "Minúsculas":
            new_name_no_ext_processed = new_name_no_ext_processed.lower()
        elif case_option == "Capitalizar":
            new_name_no_ext_processed = new_name_no_ext_processed.capitalize()

        formatted_sequence = ""
        if sequence_num is not None:
            try:
                digits = self.digits_var.get()
                if digits > 0:
                    formatted_sequence = f"{sequence_num:0{digits}d}"
                else:
                    formatted_sequence = str(sequence_num)
            except Exception:
                formatted_sequence = str(sequence_num)

        formatted_date = ""
        if self.use_custom_date_var.get():
            date_str = self.custom_date_var.get()
            input_format_key = self.date_input_format_option.get()
            output_format_key = self.date_output_format_option.get()

            format_map = {
                "YYYYMMDD": "%Y%m%d",
                "YYYY-MM-DD": "%Y-%m-%d",
                "DDMMYYYY": "%d%m%Y",
                "DD-MM-YYYY": "%d-%m-%Y"
            }

            input_python_format = format_map.get(input_format_key)
            output_python_format = format_map.get(output_format_key)

            if not input_python_format or not output_python_format:
                self.log(f"Erro interno: Formato de data inválido. Placeholder {{date}} será ignorado.")
                formatted_date = ""
            else:
                try:
                    dt_obj = datetime.strptime(date_str, input_python_format)
                    formatted_date = dt_obj.strftime(output_python_format)
                except ValueError:
                    self.log(f"Aviso: Data '{date_str}' não corresponde ao formato de entrada '{input_python_format}'. O placeholder {{date}} será ignorado ou aparecerá vazio.")
                    formatted_date = ""
                except Exception as e:
                    self.log(f"Erro inesperado ao processar data: {e}. O placeholder {{date}} será ignorado.")
                    formatted_date = ""

        processed_pattern = pattern

        if self.sequential_var.get() and "{sequence}" not in processed_pattern:
            if "{ext}" in processed_pattern:
                ext_pos = processed_pattern.rfind("{ext}")
                processed_pattern = processed_pattern[:ext_pos] + "_{sequence}" + processed_pattern[ext_pos:]
            else:
                processed_pattern += "_{sequence}"

        if self.use_custom_date_var.get() and "{date}" not in processed_pattern:
            if "{ext}" in processed_pattern:
                ext_pos = processed_pattern.rfind("{ext}")
                if "{sequence}" in processed_pattern:
                    seq_pos = processed_pattern.rfind("{sequence}")
                    if seq_pos < ext_pos:
                        insert_at = seq_pos + len("{sequence}")
                        processed_pattern = processed_pattern[:insert_at] + "_{date}" + processed_pattern[insert_at:]
                    else:
                        processed_pattern = processed_pattern[:ext_pos] + "_{date}" + processed_pattern[ext_pos:]
                else:
                    processed_pattern = processed_pattern[:ext_pos] + "_{date}" + processed_pattern[ext_pos:]
            else:
                processed_pattern += "_{date}"

        final_name_parts = {
            "{original_name}": new_name_no_ext_processed,
            "{sequence}": formatted_sequence,
            "{date}": formatted_date,
            "{ext}": original_ext.lower() if self.ignore_ext_case_var.get() else original_ext
        }

        new_full_name_base = processed_pattern
        for placeholder, value in final_name_parts.items():
            new_full_name_base = new_full_name_base.replace(placeholder, str(value))

        new_full_name_base = self.sanitize_filename(new_full_name_base)

        return new_full_name_base

    def run_renamer(self, preview):
        directory = self.directory_path.get()
        sequential = self.sequential_var.get()
        start_num = self.start_num_var.get()
        recursive = self.recursive_var.get()

        if self.use_custom_date_var.get() and not self.validate_date_input():
            self.log("Operação cancelada devido a formato de data inválido.")
            return

        if not self.validate_numeric_input():
            self.log("Operação cancelada devido a valores numéricos inválidos.")
            return

        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')

        if not directory:
            messagebox.showerror("Erro", "Por favor, selecione um diretório.")
            self.log("Erro: Diretório não selecionado.")
            return

        output_pattern = self.output_pattern_var.get().strip()
        if not output_pattern:
             messagebox.showerror("Erro", "O 'Padrão de Nome Final' não pode ser vazio. Use '{original_name}.{ext}' se não quiser alterar o nome, apenas manter a extensão.")
             self.log("Erro: Padrão de saída vazio.")
             return

        has_transformation = any([
            self.replace_old_var.get(),
            self.replace_new_var.get(),
            self.remove_pattern_var.get(),
            self.case_option.get() != "Manter",
            self.space_option.get() != "Manter",
            self.sequential_var.get(),
            self.use_custom_date_var.get(),
            output_pattern.lower() not in ["{original_name}.{ext}", "{original_name}{ext}"]
        ])

        if not has_transformation:
            messagebox.showinfo("Informação", "Nenhuma opção de transformação foi selecionada e o padrão de nome final não altera o nome base. Nenhuma alteração será feita nos nomes dos arquivos.")
            self.log("Nenhuma transformação especificada. Arquivos não serão alterados.")
            return

        if self.overwrite_conflict_var.get() and not preview:
            response = messagebox.askyesno(
                "CONFIRMAR SOBRESCRITA",
                "Você ativou a opção de SOBRESCRITA. Arquivos com nomes idênticos SERÃO PERDIDOS. Deseja continuar?",
                icon='warning'
            )
            if not response:
                self.log("Operação cancelada pelo usuário devido à opção de sobrescrita.")
                return

        self.log(f"Iniciando {'prévia' if preview else 'renomeação'}...")
        self.log(f"Diretório: {directory}")
        self.log(f"Padrão de Nome Final: '{output_pattern}'")
        self.log(f"Recursivo: {'Sim' if recursive else 'Não'}")
        self.log("-" * 40)

        files_info = []
        if not os.path.isdir(directory):
            self.log(f"Erro: O diretório '{directory}' não existe ou não é válido.")
            messagebox.showerror("Erro", f"O diretório '{directory}' não existe ou não é válido.")
            return

        for root, _, files in os.walk(directory):
            for filename in files:
                full_path_old = os.path.join(root, filename)
                name, ext = os.path.splitext(filename)
                files_info.append((full_path_old, name, ext))
            if not recursive:
                break

        if not files_info:
            self.log("Nenhum arquivo encontrado para renomear.")
            messagebox.showinfo("Informação", "Nenhum arquivo encontrado no diretório especificado.")
            return

        counter = start_num
        renamed_map_preview = {}
        results_list = []
        renamed_count = 0

        for old_path, original_name_no_ext, original_ext in files_info:
            new_basename_base = self.generate_new_filename(
                original_name_no_ext, original_ext, counter if sequential else None
            )

            if sequential:
                counter += 1

            new_path_candidate = os.path.join(os.path.dirname(old_path), new_basename_base)

            final_new_path = new_path_candidate
            conflict_type = None

            if new_path_candidate in renamed_map_preview and renamed_map_preview[new_path_candidate] != old_path:
                conflict_type = "interno"
                self.log(f"Conflito INTERNO detectado para '{os.path.basename(old_path)}': outro arquivo ('{os.path.basename(renamed_map_preview[new_path_candidate])}') também renomeia para '{os.path.basename(new_path_candidate)}'.")
            elif os.path.exists(new_path_candidate) and new_path_candidate != old_path:
                conflict_type = "existente"
                self.log(f"Conflito com ARQUIVO EXISTENTE no disco para '{os.path.basename(old_path)}': '{os.path.basename(new_path_candidate)}' já existe.")

            if conflict_type:
                if self.overwrite_conflict_var.get():
                    self.log(f" -> Sobrescrevendo o arquivo existente em '{os.path.basename(new_path_candidate)}' (opção ativada).")
                elif self.add_increment_on_conflict_var.get():
                    increment = 1
                    original_name_no_ext_candidate, original_ext_candidate = os.path.splitext(new_basename_base)
                    while True:
                        temp_new_name = f"{original_name_no_ext_candidate} ({increment}){original_ext_candidate}"
                        temp_new_path = os.path.join(os.path.dirname(old_path), temp_new_name)
                        if not os.path.exists(temp_new_path) and temp_new_path not in renamed_map_preview:
                            final_new_path = temp_new_path
                            self.log(f" -> Conflito resolvido com incremento: '{os.path.basename(final_new_path)}'")
                            break
                        increment += 1
                else:
                    self.log(f" -> Sem opção de resolução de conflito. Ignorando renomeação de '{os.path.basename(old_path)}'.")
                    continue

            if old_path == final_new_path:
                self.log(f"Ignorando '{os.path.basename(old_path)}': Nome inalterado após todas as transformações.")
                continue

            renamed_map_preview[final_new_path] = old_path

            results_list.append((old_path, final_new_path))

        if not results_list:
            self.log("Nenhuma renomeação válida será realizada com as opções atuais.")
            messagebox.showinfo("Informação", "Nenhum arquivo será renomeado com as opções atuais.")
            return

        for old_path, new_path in results_list:
            self.log(f"'{os.path.basename(old_path)}' -> '{os.path.basename(new_path)}'")
            if not preview:
                try:
                    os.rename(old_path, new_path)
                    renamed_count += 1
                except OSError as e:
                    self.log(f"Erro ao renomear '{os.path.basename(old_path)}' para '{os.path.basename(new_path)}': {e}")
                except Exception as e:
                    self.log(f"Ocorreu um erro inesperado ao renomear '{os.path.basename(old_path)}': {e}")

        self.log("-" * 40)
        if preview:
            self.log("Modo de prévia ativado. Nenhum arquivo foi realmente renomeado.")
            self.log(f"Total de arquivos que seriam afetados: {len(results_list)}")
            messagebox.showinfo("Prévia Concluída", f"Prévia gerada com sucesso. Total de arquivos a serem renomeados: {len(results_list)}. Verifique o log abaixo.")
        else:
            self.log(f"Renomeação concluída. Total de arquivos renomeados: {renamed_count}")
            self.log(f"Total de arquivos processados (incluindo ignorados/conflitos): {len(files_info)}")
            messagebox.showinfo("Renomeação Concluída", f"Operação finalizada. Total de arquivos renomeados: {renamed_count}.")

    def show_welcome_message(self):
        settings = self.load_settings()
        if not settings.get("dont_show_welcome_again", False):
            welcome_window = tk.Toplevel(self.master)
            welcome_window.title("Bem-vindo ao NameFluxer!")
            welcome_window.transient(self.master)
            welcome_window.grab_set()
            welcome_window.focus_set()
            
            message_frame = ttk.Frame(welcome_window, padding="20")
            message_frame.pack(fill="both", expand=True)

            ttk.Label(message_frame, text="Como Usar o NameFluxer:", font=('Segoe UI', 12, 'bold')).pack(pady=10)
            
            instructions_text = """
1.  **Selecione a Pasta**: Use o botão "Procurar..." na aba "Geral" para escolher o diretório com seus arquivos.
2.  **Defina o Padrão de Nome Final**: Na mesma aba, use o campo "Padrão de Nome Final" para criar o novo nome.
    * Use placeholders como: **{original_name}**, **{sequence}**, **{date}**, **{ext}**.
3.  **Transformações Opcionais**:
    * Na aba "Transformações", você pode substituir texto, remover padrões (Regex), mudar o case e gerenciar espaços.
4.  **Conflito de Nomes**:
    * **Adicionar um número incremental ao final (Recomendado)**: Esta opção, na aba "Padrão & Avançado", é crucial! Ela garante que, se um nome novo já existir (ex: `foto.jpg`), o NameFluxer criará `foto (1).jpg`, `foto (2).jpg`, etc., evitando perda de arquivos.
    * **Atenção**: Evite usar a opção "Sobrescrever arquivo existente" a menos que você saiba exatamente o que está fazendo, pois ela pode causar perda permanente de dados!
5.  **Prévia e Renomeação**:
    * Clique em "✨ Prévia das Mudanças" para ver o que será alterado.
    * Clique em "🚀 Renomear Agora!" para aplicar as mudanças.
            """
            ttk.Label(message_frame, text=instructions_text, justify=tk.LEFT, wraplength=450).pack(pady=5)

            dont_show_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(message_frame, text="Não mostrar esta mensagem novamente", variable=dont_show_var).pack(pady=10)

            def close_welcome():
                settings["dont_show_welcome_again"] = dont_show_var.get()
                self.save_settings(settings)
                welcome_window.destroy()

            ttk.Button(message_frame, text="Entendi!", command=close_welcome, style='Accent.TButton').pack(pady=10)
            
            welcome_window.protocol("WM_DELETE_WINDOW", close_welcome)
            self.master.wait_window(welcome_window)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_settings(self, settings):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenamerApp(root)
    root.mainloop()
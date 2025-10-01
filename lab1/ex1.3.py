# ex1_gui.py
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def read_fasta(filename):
    with open(filename, "r", encoding="utf-8") as f:
        seq_lines = []
        for line in f:
            line = line.strip()
            if not line or line.startswith(">"):
                continue
            seq_lines.append(line)
    return "".join(seq_lines).upper()

def fasta_composition(filename):
    seq = read_fasta(filename)
    if not seq:
        raise ValueError("Empty sequence in FASTA.")
    length = len(seq)
    alphabet = sorted(set(seq))
    composition = {}
    for char in alphabet:
        count = seq.count(char)
        percentage = (count / length) * 100
        composition[char] = round(percentage, 2)
    return seq, alphabet, composition

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FASTA Composition")
        self.geometry("520x420")
        self.resizable(False, False)

        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        self.path_var = tk.StringVar(value="")
        ttk.Label(top, text="FASTA file:").pack(side="left")
        ttk.Entry(top, textvariable=self.path_var, width=50).pack(side="left", padx=6)
        ttk.Button(top, text="Browse...", command=self.browse).pack(side="left")

        mid = ttk.Frame(self, padding=(10,0))
        mid.pack(fill="x", pady=10)
        self.len_var = tk.StringVar(value="Length: -")
        self.alpha_var = tk.StringVar(value="Alphabet: -")
        ttk.Label(mid, textvariable=self.len_var).pack(anchor="w")
        ttk.Label(mid, textvariable=self.alpha_var).pack(anchor="w", pady=2)

        table_frame = ttk.Frame(self, padding=(10,0))
        table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("symbol","percent"), show="headings", height=10)
        self.tree.heading("symbol", text="Symbol")
        self.tree.heading("percent", text="Percent (%)")
        self.tree.column("symbol", width=120, anchor="center")
        self.tree.column("percent", width=120, anchor="e")
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        bottom = ttk.Frame(self, padding=10)
        bottom.pack(fill="x")
        ttk.Button(bottom, text="Analyze", command=self.analyze).pack(side="left")
        ttk.Button(bottom, text="Quit", command=self.destroy).pack(side="right")

        default_path = os.path.join(os.getcwd(), "sequence.fasta")
        if os.path.exists(default_path):
            self.path_var.set(default_path)
            self.analyze()

    def browse(self):
        path = filedialog.askopenfilename(
            title="Select FASTA file",
            filetypes=[("FASTA files", "*.fasta *.fa *.fna *.faa *.ffn *.frn"), ("All files", "*.*")]
        )
        if path:
            self.path_var.set(path)
            self.analyze()

    def analyze(self):
        path = self.path_var.get().strip()
        if not path:
            messagebox.showwarning("No file", "Please choose a FASTA file.")
            return
        try:
            seq, alphabet, composition = fasta_composition(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read/parse FASTA:\n{e}")
            return

        self.len_var.set(f"Length: {len(seq)}")
        self.alpha_var.set("Alphabet: " + " ".join(alphabet))

        for row in self.tree.get_children():
            self.tree.delete(row)
        for k in alphabet:
            self.tree.insert("", "end", values=(k, f"{composition[k]:.2f}"))

if __name__ == "__main__":
    App().mainloop()

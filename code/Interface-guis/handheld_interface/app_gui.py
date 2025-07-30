import tkinter as tk
from tkinter import ttk

class MetadataEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Metadata Editor")
        
        # Create and pack the main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create the entry fields
        self.entries = {}
        for i in range(5):
            ttk.Label(main_frame, text=f"Line {i+1}:").grid(row=i, column=0, sticky=tk.W, pady=5)
            self.entries[f"line{i+1}"] = ttk.Entry(main_frame, width=40)
            self.entries[f"line{i+1}"].grid(row=i, column=1, sticky=tk.W, padx=5)
            
        # Create buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.save_metadata).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=root.quit).pack(side=tk.LEFT, padx=5)
        
    def save_metadata(self):
        metadata = {
            key: entry.get() for key, entry in self.entries.items()
        }
        print("Metadata saved:", metadata)

if __name__ == "__main__":
    root = tk.Tk()
    app = MetadataEditor(root)
    root.mainloop()

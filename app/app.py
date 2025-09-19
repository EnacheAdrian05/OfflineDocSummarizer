import tkinter as Tk
import tkinter.font as TkFont
from colors import Color
import sys, os
from tkinter import filedialog
from threading import Thread

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_func.gen_summary import generate_summary, read_file
from database.db import insert_document, find_by_hash, update_summary, file_hash

documents_dir = os.path.join(os.path.expanduser("~"), "Documents")


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def browse_files():
    filename = filedialog.askopenfilename(
        initialdir=documents_dir,
        filetypes=[("PDF files", "*.pdf"), ("Text files", "*.txt"), ("Word files", "*.docx")],
        title="Select a Document"
    )
    if filename:
        entry.config(state="normal")
        entry.delete(0, Tk.END)
        entry.insert(0, filename)
        entry.config(state="readonly")

        insert_document(filename)

        if summarize_button['state'] == 'disabled':
            summarize_button.config(state="normal")
            
            
def on_summarize_hover(e):
    if summarize_button['state'] == 'normal':
        summarize_button.config(bg=Color.SUBMIT_HOVER.value, cursor="hand2")
        
    else:
        summarize_button.config(cursor="no")
        

def on_summarize_leave(e):
    summarize_button.config(bg=Color.SUBMIT_BG.value, cursor="")
    
    
def get_summary():
    if summarize_button['state'] == 'normal':
        summarize_button.config(state="disabled")  
        summary_text.config(state="normal")
        summary_text.delete(1.0, Tk.END)
        summary_text.insert(Tk.END, "Generating summary...")
        summary_text.config(state="disabled")

        file_path = entry.get()
        hash_val = file_hash(file_path)

        if not hash_val:
            summary_text.config(state="normal")
            summary_text.delete(1.0, Tk.END)
            summary_text.insert(Tk.END, "Error: could not read file.")
            summary_text.config(state="disabled")
            summarize_button.config(state="normal")
            return

        def worker():
            doc = find_by_hash(hash_val)
            if doc and doc[2]:
                result = doc[2]
                
            else:
                text = read_file(file_path)
                
                result = generate_summary(text) if text else None
                if result:
                    update_summary(hash_val, result)
                    
            window.after(0, lambda: show_summary(result))

        Thread(target=worker, daemon=True).start()


def show_summary(result):
    summary_text.config(state="normal")
    summary_text.delete(1.0, Tk.END)
    
    if result:
        summary_text.insert(Tk.END, result)
        
    else:
        summary_text.insert(Tk.END, "Failed to generate summary.")
        
    summary_text.config(state="disabled")
    summarize_button.config(state="normal")

            
if __name__ == "__main__":
    window = Tk.Tk()
    window.title("Document Summarizer")
    window.configure(bg=Color.BACKGROUND.value)
    window.resizable(False, False)
    window.iconbitmap(resource_path("icon.ico"))

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = int(screen_width * 0.8)
    window_height = int(screen_height * 0.8)
        
    center = ((screen_width - window_width) // 2, (screen_height - window_height) // 4)
    window.geometry(f"{window_width}x{window_height}+{center[0]}+{center[1]}")

    font_big = TkFont.Font(family="Arial", size=14)
    font_small = TkFont.Font(family="Arial", size=10)

    left_container = Tk.Frame(window, bg=Color.BACKGROUND.value)
    left_container.grid(row=0, column=0, sticky="ns", padx=(20, 10))

    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=0)
    window.grid_columnconfigure(1, weight=1)
    left_container.grid_rowconfigure(0, weight=1)
    left_container.grid_rowconfigure(2, weight=1)
    left_container.grid_columnconfigure(0, weight=1)
    

    left_frame = Tk.Frame(left_container, bg=Color.BACKGROUND.value)
    left_frame.grid(row=1, column=0, pady=0, padx=(20, 10))

    browse_button = Tk.Button(left_frame, width=25, text="Browse Files", bg=Color.BUTTON_BG.value, fg=Color.BUTTON_FG.value, command=browse_files)
    browse_button.grid(row=0, column=0, sticky="n", pady=50)

    entry = Tk.Entry(left_frame, width=50, bg=Color.ENTRY_BG.value, fg=Color.ENTRY_FG.value, bd=2, relief="groove")
    entry.grid(row=1, column=0, sticky="ew", pady=5)

    summarize_button = Tk.Button(left_frame, width=25, text="Summarize!", bg=Color.SUBMIT_BG.value, fg=Color.SUBMIT_FG.value)
    summarize_button.grid(row=2, column=0, sticky="n", pady=50)

    left_frame.grid_columnconfigure(0, weight=1)

    right_frame = Tk.Frame(window, bg=Color.BORDER.value, bd=2, relief="sunken")
    right_frame.grid(row=0, column=1, padx=(10, 20), pady=10)

    summary_container = Tk.Frame(right_frame, bg=Color.BORDER.value)
    summary_container.pack(expand=True)

    summary_text = Tk.Text(summary_container, width=window_width // 20, height=10,  
                        bg=Color.ENTRY_BG.value, fg=Color.ENTRY_FG.value, wrap="word")
    
    summary_text.pack(padx=15, pady=15)
    summary_text.insert(Tk.END, "Summary will appear here...")

    entry.config(font=font_small, state="readonly")
    browse_button.config(font=font_big, width=20)
    summarize_button.config(font=font_big, width=20, state="disabled", cursor="no")
    summary_text.config(font=font_big, state="disabled")


    browse_button.bind("<Enter>", lambda e: browse_button.config(bg=Color.BUTTON_HOVER.value, cursor="hand2"))
    browse_button.bind("<Leave>", lambda e: browse_button.config(bg=Color.BUTTON_BG.value, cursor=""))

    summarize_button.bind("<Enter>", on_summarize_hover)
    summarize_button.bind("<Leave>", on_summarize_leave)
    summarize_button.bind("<Button-1>", lambda e: get_summary())

    window.mainloop()

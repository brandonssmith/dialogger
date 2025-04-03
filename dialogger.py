import whisper
from pydub import AudioSegment
import datetime
import os
import soundfile as sf
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import torch

class DialoggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dialogger - Audio to SRT Converter")
        self.root.geometry("800x600")
        
        # Configure style
        style = ttk.Style()
        style.configure('TButton', padding=5)
        style.configure('TLabel', padding=5)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Dialogger", font=('Helvetica', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=20)
        
        # Input file selection
        ttk.Label(main_frame, text="Input Audio File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        input_entry = ttk.Entry(main_frame, textvariable=self.input_path, width=50)
        input_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input).grid(row=1, column=2, padx=5)
        
        # Output file selection
        ttk.Label(main_frame, text="Output SRT File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_path = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_path, width=50)
        output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=2, column=2, padx=5)
        
        # Model selection
        ttk.Label(main_frame, text="Whisper Model:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(main_frame, textvariable=self.model_var, state="readonly")
        model_combo['values'] = ('tiny', 'base', 'small', 'medium', 'large')
        model_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Device selection
        ttk.Label(main_frame, text="Processing Device:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.device_var = tk.StringVar(value="cuda" if torch.cuda.is_available() else "cpu")
        device_combo = ttk.Combobox(main_frame, textvariable=self.device_var, state="readonly")
        device_combo['values'] = ('cpu', 'cuda')
        device_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Convert button
        convert_btn = ttk.Button(main_frame, text="Convert to SRT", command=self.start_conversion)
        convert_btn.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=6, column=0, columnspan=3, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Preview section
        preview_frame = ttk.LabelFrame(main_frame, text="Subtitle Preview", padding="5")
        preview_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=10, width=70)
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=(
                ("Audio files", "*.mp3 *.wav *.m4a *.ogg"),
                ("All files", "*.*")
            )
        )
        if filename:
            self.input_path.set(filename)
            # Set default output path
            if not self.output_path.get():
                default_output = os.path.splitext(filename)[0] + ".srt"
                self.output_path.set(default_output)
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save SRT File",
            defaultextension=".srt",
            filetypes=(("SRT files", "*.srt"), ("All files", "*.*"))
        )
        if filename:
            self.output_path.set(filename)
    
    def start_conversion(self):
        input_file = self.input_path.get()
        output_file = self.output_path.get()
        
        if not input_file or not output_file:
            messagebox.showerror("Error", "Please select both input and output files.")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist.")
            return
        
        # Start conversion in a separate thread
        thread = threading.Thread(target=self.convert, args=(input_file, output_file))
        thread.daemon = True
        thread.start()
    
    def convert(self, input_file, output_file):
        try:
            # Start progress bar
            self.progress['mode'] = 'indeterminate'
            self.progress.start()
            self.status_var.set("Loading Whisper model...")
            self.root.update()
            
            # Load Whisper model
            model = whisper.load_model(self.model_var.get(), device=self.device_var.get())
            
            self.status_var.set("Converting audio...")
            self.root.update()
            
            # Convert audio to SRT
            results = convert_audio_to_srt(
                input_file,
                output_file,
                model,
                self.device_var.get(),
                self.update_preview
            )
            
            # Update preview
            self.update_preview(results)
            
            messagebox.showinfo("Success", "Conversion completed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            # Stop progress bar
            self.progress.stop()
            self.progress['mode'] = 'determinate'
            self.progress['value'] = 0
            self.status_var.set("Ready")
    
    def update_preview(self, results):
        preview_text = ""
        for i, segment in enumerate(results[:5], 1):  # Show first 5 segments as preview
            start_time = datetime.timedelta(seconds=segment["start"])
            end_time = datetime.timedelta(seconds=segment["end"])
            start_str = str(start_time).replace(".", ",")[:11]
            end_str = str(end_time).replace(".", ",")[:11]
            preview_text += f"{i}\n{start_str} --> {end_str}\n{segment['text']}\n\n"
        
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, preview_text)

def convert_audio_to_srt(audio_file_path, output_srt_path, model, device, preview_callback=None):
    # Transcribe audio
    result = model.transcribe(
        audio_file_path,
        language="en",
        word_timestamps=True,
        fp16=device == "cuda"  # Use fp16 for GPU
    )
    
    # Create SRT content
    srt_content = ""
    for i, segment in enumerate(result["segments"], 1):
        start_time = datetime.timedelta(seconds=segment["start"])
        end_time = datetime.timedelta(seconds=segment["end"])
        
        # Format timestamps for SRT
        start_str = str(start_time).replace(".", ",")[:11]
        end_str = str(end_time).replace(".", ",")[:11]
        
        # Add subtitle entry
        srt_content += f"{i}\n"
        srt_content += f"{start_str} --> {end_str}\n"
        srt_content += f"{segment['text'].strip()}\n\n"
        
        # Update preview if callback is provided
        if preview_callback:
            preview_callback(result["segments"])
    
    # Write to SRT file
    with open(output_srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    
    return result["segments"]

def main():
    root = tk.Tk()
    app = DialoggerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
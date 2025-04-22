import customtkinter as ctk
import pandas as pd
import os
import openai
from dotenv import load_dotenv
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Load API key
dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path)
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key
client = openai.OpenAI()

# Chat completion helper
def get_chat_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I couldn't fetch a response."

# Plot helper
def plot_calories(frame):
    import pandas.errors as pd_errors
    if not os.path.exists("wrkoutData.csv"):
        print("No workout data found!")
        return
    try:
        df = pd.read_csv("wrkoutData.csv", on_bad_lines='warn')
    except pd_errors.ParserError as e:
        print(f"Error reading CSV: {e}\nCheck for malformed rows.")
        return
    if 'Date' not in df.columns or 'Calories Burned' not in df.columns:
        print("CSV missing required columns.")
        return
    df["Day"] = pd.to_datetime(df["Date"], errors='coerce').dt.day_name()
    weekly = df.groupby("Day")["Calories Burned"].sum().reindex([
        "Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"
    ])
    fig = Figure(figsize=(5, 3), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(weekly.index, weekly.values, marker='o')
    ax.set_title("Calories Burned Per Day")
    ax.set_xlabel("Day")
    ax.set_ylabel("Calories")
    for w in frame.winfo_children(): w.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# Data persistence
def load_user_data():
    if os.path.exists("user_data.json"):
        return json.load(open("user_data.json"))
    return {}

def save_user_data(goal, level):
    with open("user_data.json", "w") as f:
        json.dump({"goal": goal, "experience_level": level}, f)

class WorkoutApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("mAI Coach - Personal Trainer")
        self.geometry("900x700")
        self.resizable(True, True)
        try: self.state("zoomed")
        except: pass

        # Shared state
        self.messages = [{"role":"system","content":"You are mAI Coach, a personal training assistant."}]
        self.user_data = load_user_data()

        # Main container
        container = ctk.CTkFrame(self, corner_radius=12)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Create tab view
        tabs = ctk.CTkTabview(container)
        tabs.pack(fill="both", expand=True)
        tabs.add("Dashboard")
        tabs.add("Chat")

        # === Dashboard Tab ===
        dash = tabs.tab("Dashboard")
        # Profile display or inputs
        if self.user_data.get("goal") and self.user_data.get("experience_level"):
            ctk.CTkLabel(dash, text=f"Goal: {self.user_data['goal']}").grid(row=0, column=0, sticky="w", padx=10, pady=(10,5))
            ctk.CTkLabel(dash, text=f"Experience: {self.user_data['experience_level']}").grid(row=1, column=0, sticky="w", padx=10, pady=(0,10))
            ctk.CTkButton(dash, text="Change Profile", command=lambda: self.show_profile_inputs(dash)).grid(row=2, column=0, padx=10, pady=(0,20))
        else:
            self.show_profile_inputs(dash)
        # Workout logging inputs
        labels = ["Workout Name","Type","Duration (min)","Calories Burned"]
        self.inputs = []
        for i, text in enumerate(labels, start=3):
            ctk.CTkLabel(dash, text=f"{text}:").grid(row=i, column=0, sticky="w", padx=10, pady=5)
            var = ctk.StringVar()
            ctk.CTkEntry(dash, textvariable=var, width=220).grid(row=i, column=1, sticky="w", pady=5)
            self.inputs.append(var)
        ctk.CTkButton(dash, text="Log Workout", command=self.log_workout).grid(row=7, column=0, padx=10, pady=(10,0))
        ctk.CTkButton(dash, text="Show Calories Burned", command=lambda: plot_calories(self.plot_frame)).grid(row=7, column=1, padx=10, pady=(10,0))
        self.plot_frame = ctk.CTkFrame(dash, corner_radius=8)
        self.plot_frame.grid(row=8, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        dash.grid_rowconfigure(8, weight=1)

        # === Chat Tab ===
        chat = tabs.tab("Chat")
        chat.grid_rowconfigure(0, weight=1)
        chat.grid_columnconfigure(0, weight=1)
        # Chat history
        self.chat_box = ctk.CTkTextbox(chat)
        self.chat_box.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.chat_box.tag_config("user", foreground="#7FDBFF")
        self.chat_box.tag_config("ai", foreground="#FFD600")
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", "Hello, I'm mAI Coach, your personal training assistant!\n\n", "ai")
        self.chat_box.configure(state="disabled")
        # User entry
        self.user_entry = ctk.CTkTextbox(chat, height=100)
        self.user_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,10))
        ctk.CTkButton(chat, text="Send", command=self.send_chat).grid(row=1, column=1, padx=10, pady=(0,10))

    def show_profile_inputs(self, parent):
        # Remove existing profile widgets
        for widget in parent.grid_slaves(row=0): widget.destroy()
        for widget in parent.grid_slaves(row=1): widget.destroy()
        for widget in parent.grid_slaves(row=2): widget.destroy()
        # Profile input fields
        self.goal_var = ctk.StringVar(value=self.user_data.get("goal", ""))
        self.exp_var = ctk.StringVar(value=self.user_data.get("experience_level", ""))
        ctk.CTkLabel(parent, text="Goal:").grid(row=0, column=0, sticky="w", padx=10, pady=(10,5))
        ctk.CTkEntry(parent, textvariable=self.goal_var, width=220).grid(row=0, column=1, pady=(10,5))
        ctk.CTkLabel(parent, text="Experience:").grid(row=1, column=0, sticky="w", padx=10, pady=(0,5))
        ctk.CTkEntry(parent, textvariable=self.exp_var, width=220).grid(row=1, column=1, pady=(0,5))
        ctk.CTkButton(parent, text="Save Profile", command=self.save_profile).grid(row=2, column=0, columnspan=2, pady=(0,20))

    def save_profile(self):
        save_user_data(self.goal_var.get(), self.exp_var.get())
        self.user_data = load_user_data()
        self.destroy()
        WorkoutApp().mainloop()

    def log_workout(self):
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        name, typ, dur, cal = [v.get() for v in self.inputs]
        df = pd.DataFrame({
            "Name": [name],
            "Type": [typ],
            "Duration": [dur],
            "Calories Burned": [cal],
            "Date": [today]
        })
        df.to_csv("wrkoutData.csv", mode="a", index=False,
                  header=not os.path.exists("wrkoutData.csv"))

    def send_chat(self):
        msg = self.user_entry.get("1.0", "end-1c").strip()
        if not msg:
            return
        self.messages.append({"role": "user", "content": msg})
        response = get_chat_response(self.messages)
        self.messages.append({"role":"assistant","content":response})
        for tag, text in [("user", f"You: {msg}\n"), ("ai", f"mAI Coach: {response}\n\n")]:
            self.chat_box.configure(state="normal")
            self.chat_box.insert("end", text, tag)
            self.chat_box.configure(state="disabled")
        self.user_entry.delete("1.0", "end")

if __name__ == "__main__":
    app = WorkoutApp()
    app.mainloop()
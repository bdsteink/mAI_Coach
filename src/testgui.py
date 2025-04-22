from tkinter import *
import pandas as pd
import os
import openai
from dotenv import load_dotenv
import json
import matplotlib.pylot as plt
from matplotlib.backends_tkagg import FigureCanvasTkAgg

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")  # Get key from environment variable

print(f"API Key: {api_key}")

openai.api_key = api_key

client = openai.OpenAI()

# Function to generate mAI Coach reponse based on user input
def get_chat_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting reponse: {e}")
        return "Sorry, I couldn't fetch a response at the moment."


# Function to plot calories burned per day
def plot_calories():
    # Read workout data from CSV
    if os.path.exists("wrkoutData.csv"):
        df = pd.read_csv("wrkoutData.csv")
    else:
        print("No workout data found!")
        return

    # Extract the day of the week and calories burned
    df["Day of the Week"] = pd.to_datetime(df["Date"]).dt.day_name()  # Assuming you have a Date column
    df_grouped = df.groupby("Day of the Week")["Calories Burned"].sum().reindex([
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ])

    # Create the plot
    fig, ax = plt.subplots()
    ax.plot(df_grouped.index, df_grouped.values, marker='o', color='b', label="Calories Burned")
    
    ax.set_xlabel("Day of the Week")
    ax.set_ylabel("Calories Burned")
    ax.set_title("Calories Burned Per Day")
    ax.legend()

    # Display the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=widget.window)  # widget.window is your Tkinter window
    canvas.draw()
    canvas.get_tk_widget().grid(row=8, column=1, columnspan=2)


# Function to load user data, goal/experience
def load_user_data():
    if os.path.exists("user_data.json"):
        with open ("user_data.json", "r") as file:
            user_data = json.load(file)
            return user_data
    return None


# Function to save user data, goal/experience
def save_user_data(goal, experience_level):
    user_data = {"goal": goal, "experience_level": experience_level}
    with open("user_data.json", "w") as file:
        json.dump(user_data,file)


class Widget:
    def __init__(self):
        self.window = Tk()
        self.window.title("mAI Coach - Personal Trainer")

       # frame1 = Frame(self.window)

        self.messages = [
            {"role": "system", "content": "You are a personal trainer named mAI Coach, helping users with workouts and motivation."},
        ]
       
        # Goal label and entry box
        lblGoal = Label(self.window, text="Goal (e.g., Build muscle, Lose weight):")
        self.goal = StringVar()
        entryGoal = Entry(self.window, textvariable = self.goal)
        lblGoal.grid(row = 0, column = 1)
        entryGoal.grid(row = 0, column = 2)


        # Experience label and entry box
        lblExp = Label(self.window, text="Experience Level (e.g., Beginner, Intermediate, Advanced):")
        self.expLvl = StringVar()
        entryExp = Entry(self.window, textvariable= self.expLvl)
        lblExp.grid(row = 1, column = 1)
        entryExp.grid(row = 1, column = 2)


        # Button to save the goal and experience level
        saveButton = Button(self.window, text="Save Goal & Experience Level", command=self.save_goal_and_level)
        saveButton.grid(row=2, column = 1, columnspan = 2)


        # Button to change goal/expLevel
        changeButton = Button(self.window, text="Change Goal & Experience Level", command=self.change_goal_and_level)
        changeButton.grid(row=3, column = 1, columnspan = 2)


        # Workout Name label and entry box
        lblWName = Label(self.window, text = "Workout Name:")
        self.wrkName = StringVar()
        entryWName = Entry(self.window, textvariable = self.wrkName)
        lblWName.grid(row = 4, column = 1)
        entryWName.grid(row= 4, column= 2)


        # Workout Type label and entry box
        lblWType = Label(self.window, text = "Workout Type:")
        self.wrkType = StringVar()
        entryWType = Entry(self.window, textvariable = self.wrkType)
        lblWType.grid(row = 5, column = 1)
        entryWType.grid(row= 5, column= 2)


        # Duration label and entry box
        lblDuration = Label(self.window, text = "Duration:")
        self.duration = IntVar()
        entryDuration = Entry(self.window, textvariable = self.duration)
        lblDuration.grid(row = 6, column = 1)
        entryDuration.grid(row = 6, column = 2)


        # Calories Burned label and entry box
        lblCalBrn = Label(self.window, text = "Calories Burned:")

        self.calBrn = IntVar()

        entryCalBrn = Entry(self.window, textvariable = self.calBrn)

        lblCalBrn.grid(row = 7, column = 1)
        entryCalBrn.grid(row= 7, column= 2)


        # Save button to save workout data to CSV
        saveWorkoutButton = Button(self.window, text= "Log Workout", command = self.save_to_csv)
        saveWorkoutButton.grid(row = 8, column = 1)


        # Button to plot calories burned per day
        plotButton = Button(self.window, text="Show Calories Burned", command=plot_calories)
        plotButton.grid(row=8, column=2)


        # Chat history area (text widget)
        self.chat_history = Text(self.window, height = 20, width = 100, state = DISABLED, wrap = WORD)
        self.chat_history.grid(row = 9, column = 1, columnspan=2)


        # User input label and entry box
        lblUserInput = Label(self.window, text="Ask something")
        self.user_input = StringVar()
        entryUserInput = Entry(self.window, textvariable=self.user_input)
        lblUserInput.grid(row = 10, column = 1)
        entryUserInput.grid(row = 10, column = 2)


        # Button to send user's message to mAI Coach
        sendButton = Button(self.window, text="Send", command = self.send_message)
        sendButton.grid(row = 11, column = 1)


        self.window.mainloop()


    # Function to save the goal and experience level
    def save_goal_and_level(self):
        save_user_data(self.goal.get(), self.expLvl.get())
        print("Goal and Experience Level saved!")


    # Function to allow user to change goal / experience level
    def change_goal_and_level(self):
        self.goal.set("")
        self.expLvl.set("")


    # Function to send messages to mAI Coach
    def send_message(self):
        user_message = self.user_input.get()
        if not user_message:
            return
        
        # User message to conversation history
        self.messages.append({"role": "user", "content": user_message})

        # Retrieve mAI Coach Response
        mAI_response = get_chat_response(self.messages)

        # Add mAI Coach response to history
        self.messages.append({"role": "assistant", "content": mAI_response})

        # Update the conversation on the GUI
        self.chat_history.config(state=NORMAL)
        self.chat_history.insert(END, f"You: {user_message}\n")
        self.chat_history.insert(END, f"mAI Coach: {mAI_response}\n\n")
        self.chat_history.config(state=DISABLED)

        self.user_input.set("")

    # method to save the data into csv
    def save_to_csv(self):
        
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')

        wrkOut_Data = {

            "Name": [self.wrkName.get()],
            "Type": [self.wrkType.get()],
            "Duration":[self.duration.get()],
            "Calories Burned": [self.calBrn.get()],
            "Date": [today]

        }

        df = pd.DataFrame(wrkOut_Data)

        df.to_csv("wrkoutData.csv", mode="a", index = False, header= not pd.io.common.file_exists("wrkoutData.csv"))

        print("Saved to wrkoutData.csv")
Widget()

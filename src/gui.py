from tkinter import *
import pandas as pd
import os
import openai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")  # Get key from environment variable

openai.api_key = api_key

def get_workout(goal, experience_level):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a personal trainer helping users with workouts."},
            {"role": "user", "content": f"Create a workout plan for a {experience_level} user who wants to {goal}."}
        ]
    )
    return response["choices"][0]["message"]["content"]




class Widget:
    def __init__(self):
        self.window = Tk()
        self.window.title("TEST")

       # frame1 = Frame(self.window)

       
        # Duration label and entry box
        lblDuration = Label(self.window, text = "Duration:")
        
        self.duration = IntVar()

        entryDuration = Entry(self.window, textvariable = self.duration)
        
        lblDuration.grid(row = 1, column = 1)
        entryDuration.grid(row = 1, column = 2)


        # Workout Name label and entry box
        lblWName = Label(self.window, text = "Workout Name:")

        self.wrkName = StringVar()

        entryWName = Entry(self.window, textvariable = self.wrkName)

        lblWName.grid(row = 2, column = 1)
        entryWName.grid(row= 2, column= 2)


        # Workout Type label and entry box
        lblWType = Label(self.window, text = "Workout Type:")

        self.wrkType = StringVar()

        entryWType = Entry(self.window, textvariable = self.wrkType)

        lblWType.grid(row = 3, column = 1)
        entryWType.grid(row= 3, column= 2)


        # Calories Burned label and entry box
        lblCalBrn = Label(self.window, text = "Calories Burned:")

        self.calBrn = IntVar()

        entryCalBrn = Entry(self.window, textvariable = self.calBrn)

        lblCalBrn.grid(row = 4, column = 1)
        entryCalBrn.grid(row= 4, column= 2)



        saveButton = Button(self.window, text= "Save", command = self.save_to_csv)
        saveButton.grid(row = 6, column = 1)

        self.window.mainloop()



    # method to save the data into csv
    def save_to_csv(self):

        

        wrkOut_Data = {

            "Name": [self.wrkName.get()],
            "Type": [self.wrkType.get()],
            "Duration":[self.duration.get()],
            "Calories Burned": [self.calBrn.get()]

        }

        df = pd.DataFrame(wrkOut_Data)

        df.to_csv("wrkoutData.csv", mode="a", index = False, header= not pd.io.common.file_exists("wrkoutData.csv"))

        print("Saved to wrkoutData.csv")
Widget()

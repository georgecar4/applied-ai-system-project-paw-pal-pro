# Title and Summary: What your project does and why it matters.

# Architecture Overview: A short explanation of your system diagram.

Owner has many Pets, each Pet has many Tasks (composition, "0..*"). Scheduler, TaskStorage, and ChatAssistant all operate on an Owner (dependency arrows, ..>/-->) rather than owning it — they're service/utility classes, not data containers.

# Setup Instructions: Step-by-step directions to run your code.

1. start VS code and open the project folder
2. you get ollama runing on the PC via terminal
3. you put $env:OLLAMA_MODEL = "qwen3.5:4b" in the terminal of VS code to get it runing on the app
4. streamlit run app.py  will get the app running on the browser.
5. you can use a the side to go from the main app to the schedule or the chat bot
6. you can make apointments manualy
7. one you you have the owner and the pet setup you can add a task or retrive info from the chat bot.


# Sample Interactions: Include at least 2-3 examples of inputs and the resulting AI outputs to demonstrate the system is functional.
input: hi 
output:HELLOOOO THERE MY FRIEND! 🐾🎉💕

Aww, hellooo! How's your favorite human today? I'm so excited to help you out with all those pet care tasks and tricks! What kind of pets are we talking about, and how can I sprinkle some magic into your day? ✨🐶🐱

2. input: can you give me the names of all the pets

output: WOOHOO! 🎉 Here are your furry friends:

    Nacho (dog, age 4) has 2 tasks scheduled! 🐾🐕
    Wiskers (cat, age 3) has 1 task coming up! 🐱✨
    Lala (cat, age 2) also has a cute task too! 💕🐾

So many pets and so much love! What kind of tasks are they doing, would you like to see the schedule or make anything new? I'm ready to help with all your pet care magic! 🎊🦴
 
 3. input: give me the task for nacho

 output: OMG YES NACHO'S TASKS! 🐾🎉✨

Here they are all lined up and ready to go:

    Bath at 03:00 on November 14th, 2026 (pending!) 🛁💦
    Walk at 13:00 on November 14th, 2026 (pending!) 🚶‍♂️🐕

Those two tasks are all Nacho needs to take care of! And they're both marked as pending which means they're super fresh and ready for action! 💕 What's going great with Nacho today? Or maybe you wanna make some new magic happen? I'm so pumped to help! 🌟🐾



# Design Decisions: Why you built it this way, and what trade-offs you made.

i built this app a shop owner or a reseptionist in mind. thats why the chat cant add an owner or an animal because the client has to be approved. the chat bot main purpose is so the owner has a quick access to the data.



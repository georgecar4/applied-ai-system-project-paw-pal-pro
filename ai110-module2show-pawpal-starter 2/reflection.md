# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
# system where an Owner can manage multiple pets, and each Pet stores its personal details, care tasks, and appointments. The Task class allows users to track, complete, and reschedule tasks, while the Appointment class manages scheduling and canceling services

- What classes did you include, and what responsibilities did you assign to each?

# 1. Owner: Stores the owner's name, email, and list of pets. It allows the owner to add pets and view their pets.

# 2. Pet: Stores a pet's name, species, age, tasks, and appointments. It allows users to update the pet's information and view its details.

# 3. Task: Represents a task associated with pet care, including its title, due date, and completion status. It allows users to mark tasks as complete or reschedule them.

# 4. Appointment: Stores appointment details, including the date, time, and service. It allows users to schedule or cancel appointments.

**b. Design changes**

- Did your design change during implementation?
 # yes
- If yes, describe at least one change and why you made it.

# adding the scheduler at the top

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
# The scheduler currently detects conflicts by comparing the date and exact start time of tasks. This approach is simple to implement and easy to understand, but it does not detect overlapping tasks with different start times.For example, two tasks beginning at 8:00 AM and 8:15 AM will not be identified as a conflict, even if the first task takes 30 minutes.
- Why is that tradeoff reasonable for this scenario?
# this is a ok trade off because; fleshing out durations for every scenario will involve things like size of the pet and thats out of the scope of this project. 

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
# i used it to ask questions about the assignment and to help me with the code 
- What kinds of prompts or questions were most helpful?
# in one istance i copied the error that Scheduler class was not being imported and Ai fixed it. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
# it wanted me to compleately to change app.py 
- How did you evaluate or verify what the AI suggested?
# that is part of the assighment thats not something i should compeately rewrite.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
# tried to clash times in the apointments 
- Why were these tests important?
# you dont want too have two people book an apointment at the same time

**b. Confidence**

- How confident are you that your scheduler works correctly?
# pretty confident, i tried different senarios and it was able to do them and it passed the pytest
- What edge cases would you test next if you had more time?
# if it was a global app i would test difrent time zones

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
# that it was able to build the schedule from all the componets given 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
# if i had more time i would give each task a time frame so the appointments could be better spaced
# i would also add a comment section for specific pets

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
# i learned the imprtance of a UML diagram and how it can change 


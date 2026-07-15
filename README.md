# Introduction to Web Applications - Exam Project
**Fantasy Adventure Guild: The Mystic Grove**

* **Name:** Gualtiero
* **Surname:** Bocaccio
* **Student ID (Matricola):** s324660


## Deployed Application
The application is live and deployed on PythonAnywhere:
**[https://gualty.pythonanywhere.com/](https://gualty.pythonanywhere.com/)**

---

## Simulated Time and Day Settings
* **Simulated Day:** Tuesday
* **Simulated Time:** 10:00

---

## Test Accounts (Credentials)
*Note: Please use the **Email** to log in, not the username.*

### 1. Guild Master (Administrator)
Can create new quests, schedule sessions, modify/cancel empty sessions, and view participation statistics.
* **Email:** `master@guild.com`
* **Password:** `master123`

### 2. Guild Council (Prova Finale Extra Requirement)
Has access to a dedicated dashboard to view platform statistics, adventurer lists, and overall guild activity.
* **Email:** `council@guild.com`
* **Password:** `council123`

### 3. Adventurers (Registered Users)
Can explore quests, filter sessions, and manage their enrollments. I have prepared specific accounts to demonstrate the different time constraints and edge cases. 

All adventurer accounts share the same password: **`password`**

* **Willow** (`willow@sunlitgrove.net`)
  * *Test Case: Modifiable Enrollment.* Enrolled in a session on Wednesday at 11:00. Because this is more than 8 hours away from the simulated time (Tuesday 10:00), Willow can still modify or cancel this participation in her profile.
* **Sylas** (`sylas@deepwoods.com`)
  * *Test Case: Blocked by 8-hour limit.* Enrolled in a session on Tuesday at 16:00. This is in the future, but strictly within the 8-hour lockdown window. Modifications are disabled.
* **Zephyr** (`zephyr@windsong.com`)
  * *Test Case: Past Session & Fully Booked Role (1/2).* Enrolled as a Warrior for the Monday 10:00 session. This session is already in the past (unmodifiable). He takes 2 places.
* **Lyra** (`lyra@moonglow.com`)
  * *Test Case: Past Session & Fully Booked Role (2/2).* Enrolled as a Warrior for the same Monday 10:00 session, taking the remaining 2 places. Together with Zephyr, they make the Warrior role **fully booked** (4/4 places) for that specific session.

---

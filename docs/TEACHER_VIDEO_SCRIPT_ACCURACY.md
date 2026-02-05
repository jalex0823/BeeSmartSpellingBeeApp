# Teacher Video Script — Accuracy Check

This document verifies each section of the teacher demo script against the current app behavior. Use it to keep the script true and accurate when recording or updating the video.

---

## 1️⃣ Hook & Intro (Script 1)

**Script:** *"This is BeeSmart Spelling Bee. In the next few minutes, I'll show you how teachers set up an account and use the tools built specifically for the classroom — from managing students to running fair, shared quizzes."*

**Status:** ✅ **Accurate.** The app supports teacher signup, Teacher Key, managed roster, and Groups for shared quizzes.

---

## 2️⃣ Creating the Teacher Account (Scripts 2–4)

### Script 2

**Script:** *"Teachers register with just a name, email address, and password. During sign-up, you choose the teacher role and submit the form. The setup is quick, so you can focus on your class, not configuration."*

**Status:** ⚠️ **Minor tweak for accuracy.**

- **Actual behavior:** Registration requires **username**, **display name** (how they appear), **password**, and **role** (Teacher is an option). **Email is optional** (used for password recovery).
- **Suggested script (optional):**  
  *"Teachers register with a username, display name, and password. You can add an optional email for password recovery. During sign-up, you choose the teacher role and submit the form. The setup is quick, so you can focus on your class, not configuration."*  
- If you keep the current wording, "name" can be understood as display name; just note that **email is optional**, not required.

### Script 3

**Script:** *"After signing up, BeeSmart gives you a Teacher Key. This is a unique code made up of letters and numbers. You'll see it in your dashboard or confirmation screen."*

**Status:** ✅ **Accurate.** A unique Teacher Key is generated for teachers (and parents). It is shown in a modal after signup (`show_key_modal`) and is always visible in the teacher dashboard strip.

### Script 4

**Script:** *"You share this Teacher Key with students. It links them to your class automatically. You can write it on the board, post it in Google Classroom, or send it by email."*

**Status:** ✅ **Accurate.** Students can link to the teacher by entering the Teacher Key during registration, or use it on the "Join Teacher/Class" page to select their name from the roster (no registration).

---

## 3️⃣ Teacher Dashboard (Scripts 5–6)

### Script 5

**Script:** *"This is the teacher dashboard — your home base. Everything starts here. You can see your class, student activity, and performance all in one place."*

**Status:** ✅ **Accurate.** The teacher dashboard shows the class (Class Roster + My Students), activity, and aggregate stats (quizzes, accuracy, points, buzz dust).

### Script 6

**Script:** *"At a glance, you'll see who's active, how many quizzes have been taken, and overall class performance. You can also click into any student to review quiz history, scores, and learning trends."*

**Status:** ✅ **Accurate.** The dashboard table shows Active/Inactive, quiz counts, accuracy, points, and last active. Each student has a **View Details** link to `/teacher/student/<id>`, which shows recent quiz sessions, scores, accuracy, and **Struggling Words** (learning trends).

---

## 4️⃣ Groups vs. Roster (Script 7)

**Script:** *"In BeeSmart, there are two classroom tools that work together: Groups and the managed roster. Groups are for shared quizzes. The roster is for managing students and tracking progress — without student registration."*

**Status:** ✅ **Accurate.** Groups = one word list, one code, shared quiz. Managed roster = teacher-created profiles, optional PIN, Join by Teacher Key; no student signup required.

---

## 5️⃣ Groups — Same Quiz for Everyone (Scripts 8–10)

### Script 8

**Script:** *"Use Groups when you want every student to take the exact same quiz. You create one word list, and BeeSmart generates a short group code."*

**Status:** ✅ **Accurate.** `/api/groups/create` accepts a name and word list; the app generates a short code (e.g. `BEE1A2B`).

### Script 9

**Script:** *"Students join the group using that code and their name. Everyone gets the same words in the same order, which keeps assessments fair and consistent."*

**Status:** ⚠️ **Clarify "same order".**

- **Actual behavior:** Everyone gets the **same word list**. Word **order** is **randomized per student** when they start the quiz (so each student may see the words in a different order).
- **Suggested script (optional):**  
  *"Students join the group using that code and their name. Everyone gets the same words for the quiz, which keeps the assessment fair and consistent."*  
- If you want to say "same order" in the video, the app would need a change to support a fixed order for group quizzes (e.g. no shuffle when in group mode).

### Script 10

**Script:** *"You can see who has joined, who has finished, and when the quiz is complete, you can export the results for grading."*

**Status:** ✅ **Accurate.** `GET /api/groups/<code>` returns `players` (joined), `joined_count`, and `finished_count`. `GET /api/groups/<code>/export` returns CSV (Rank, Name, Score, Correct, Total, Accuracy %, Completed, Completed At).

---

## 6️⃣ Managed Student Roster (Scripts 11–14)

### Script 11

**Script:** *"The managed roster saves the most time. Teachers create student profiles ahead of time — either by adding them manually or importing a class list from Excel or CSV."*

**Status:** ✅ **Accurate.** Teacher can add students one-by-one or import via CSV/XLSX; download template (CSV/Excel) is available from the dashboard.

### Script 12

**Script:** *"You can add names, student IDs, grade levels, and even require a 4-digit PIN. Students don't create accounts at all."*

**Status:** ✅ **Accurate.** Roster supports display name, optional student ID, grade, and optional 4-digit PIN. Roster-only flow requires no student account; optional auto-issued logins are available.

### Script 13

**Script:** *"Students simply tap Join Teacher or Class, enter your Teacher Key, select their name from the roster, enter a PIN if required, and start working."*

**Status:** ✅ **Accurate.** Join flow: `/join` → enter Teacher Key → select student from roster → optional PIN → start quiz.

### Script 14

**Script:** *"All quiz results and progress are automatically tracked to that student profile, making it easy to monitor growth over time."*

**Status:** ✅ **Accurate.** Quiz sessions and results are stored with `roster_student_id` when the student joins by Teacher Key; progress is tied to that roster profile.

---

## 7️⃣ Wrap-Up & Outro (Scripts 15–16)

**Script 15 & 16:** *"So for teachers, the flow is simple: create your account, get your Teacher Key, and manage your class from one dashboard. Use Groups for shared quizzes, and the roster for effortless student tracking without sign-ups."* / *"That's BeeSmart for teachers — a simple way to manage students, track progress, and run fair, shared quizzes. Thanks for taking a few minutes to see how BeeSmart supports your classroom. We appreciate you watching."*

**Status:** ✅ **Accurate.** No code changes needed.

---

## Summary of Recommended Changes

| Item | Recommendation |
|------|----------------|
| **Script 2** | Optionally say "username, display name, and password" and that email is optional. |
| **Script 9** | Say "same words" (drop "in the same order") unless you add fixed order for group quizzes. |
| **Code** | Group join bug fixed: `init_quiz_state(len(word_list))` is now called after `set_wordbank(...)` so the group quiz initializes correctly. |

All other script lines match current app behavior.

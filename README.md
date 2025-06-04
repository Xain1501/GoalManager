# 🗂️ Goal Manager (CLI-Based)

This is a Python-based **Goal Management System** that allows you to create, manage, and track progress on your goals and sub-goals through a simple command-line interface. The system stores your goals persistently using JSON files, allowing you to pick up where you left off.

---

## 📦 Features

- ✅ Add major goals and nested sub-goals
- 🗓️ Set optional due dates
- 📓 Add notes, issues, and resources to goals
- 🔄 Mark goals and sub-goals as complete/incomplete
- 📊 Track progress with percentage indicators
- 📁 View detailed information on any goal
- 🗑️ Delete goals (and their sub-goals)
- 🕒 View completion history in chronological order
- 💾 Data persistence via `goals_data.json` file

---

## 🛠️ How It Works

### 🧱 Class: `Goal`
Represents a single goal or sub-goal.

Attributes:
- `id`: Unique ID of the goal
- `title`: Name of the goal
- `due_date`: Optional due date
- `completed`: Completion status
- `completion_date`: Date when goal was completed
- `notes`, `issues`, `resources`: Lists of associated details
- `sub_goals`: List of nested sub-goals
- `parent_id`: ID of the parent goal (if it's a sub-goal)

Methods:
- `to_dict()`: Converts goal to dictionary for saving
- `from_dict()`: Loads goal from dictionary

---

### 🧠 Class: `GoalManager`
Handles the logic and storage of all goals.

Key Functions:
- `add_goal(title, due_date=None, parent_id=None)`
- `delete_goal(goal_id)`
- `edit_goal(goal_id, new_title, new_due_date)`
- `mark_complete(goal_id)` / `unmark_complete(goal_id)`
- `add_note(goal_id, note)` / `add_issue(goal_id, issue)` / `add_resource(goal_id, resource)`
- `show_progress()` – View progress percentages
- `show_completion_history()` – View all completed goals by date
- `view_details(goal_id)` – See full goal details

The manager also handles goal IDs, parent-child relationships, and recursive updates of parent goal statuses.

---

## 📁 File: `goals_data.json`
Used to **save and load** all goal-related data between program sessions.

---

## 🖥️ CLI Interface

### Main Menu Options:
1. Add major goal  
2. Add sub-goal  
3. View goal details  
4. Mark goal complete/uncomplete  
5. Edit goal  
6. Delete goal  
7. Add note / issue / resource  
8. Show progress  
9. Show completion history  
0. Exit

Inputs are validated and dates must be in `YYYY-MM-DD` format or left blank.

---

## ▶️ How to Run

1. Make sure you have Python 3 installed.
2. Save the code in a file (e.g., `goal_manager.py`)
3. Run the program:

```bash
python goal_manager.py

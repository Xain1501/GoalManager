import json
from datetime import date, datetime

SAVE_FILE = "goals_data.json"

class Goal:
    def __init__(self, title, due_date=None, parent_id=None):
        self.id = None
        self.title = title
        self.due_date = due_date
        self.completed = False
        self.completion_date = None
        self.notes = []
        self.issues = []
        self.resources = []
        self.sub_goals = []
        self.parent_id = parent_id

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date,
            "completed": self.completed,
            "completion_date": self.completion_date,
            "notes": self.notes,
            "issues": self.issues,
            "resources": self.resources,
            "sub_goals": [sg.to_dict() for sg in self.sub_goals],
            "parent_id": self.parent_id,
        }

    @staticmethod
    def from_dict(d):
        g = Goal(d["title"], d["due_date"], d["parent_id"])
        g.id = d["id"]
        g.completed = d["completed"]
        g.completion_date = d["completion_date"]
        g.notes = d["notes"]
        g.issues = d["issues"]
        g.resources = d["resources"]
        g.sub_goals = [Goal.from_dict(sg) for sg in d["sub_goals"]]
        return g

class GoalManager:
    def __init__(self):
        self.goals = []
        self.next_id = 1

    def load(self):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                self.next_id = data["next_id"]
                self.goals = [Goal.from_dict(g) for g in data["goals"]]
        except (FileNotFoundError, json.JSONDecodeError):
            self.goals = []
            self.next_id = 1

    def save(self):
        data = {
            "next_id": self.next_id,
            "goals": [g.to_dict() for g in self.goals]
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def add_goal(self, title, due_date=None, parent_id=None):
        goal = Goal(title, due_date, parent_id)
        goal.id = self.next_id
        self.next_id += 1
        if parent_id is None:
            self.goals.append(goal)
        else:
            parent = self.find_goal(parent_id)
            if parent:
                parent.sub_goals.append(goal)
            else:
                print("Parent goal not found.")
                return None
        return goal.id

    def find_goal(self, goal_id, goals=None):
        if goals is None:
            goals = self.goals
        for g in goals:
            if g.id == goal_id:
                return g
            found = self.find_goal(goal_id, g.sub_goals)
            if found:
                return found
        return None

    def find_parent(self, goal_id, goals=None, parent=None):
        if goals is None:
            goals = self.goals
        for g in goals:
            if g.id == goal_id:
                return parent
            found = self.find_parent(goal_id, g.sub_goals, g)
            if found:
                return found
        return None

    def delete_goal(self, goal_id):
        parent = self.find_parent(goal_id)
        if parent is None:
            # top-level goal
            for i, g in enumerate(self.goals):
                if g.id == goal_id:
                    del self.goals[i]
                    return True
            return False
        else:
            for i, sg in enumerate(parent.sub_goals):
                if sg.id == goal_id:
                    del parent.sub_goals[i]
                    return True
            return False

    def mark_complete(self, goal_id):
        goal = self.find_goal(goal_id)
        if not goal:
            print("Goal not found.")
            return False
        if goal.sub_goals:
            if not all(sg.completed for sg in goal.sub_goals):
                print("Cannot complete this goal until all its sub-goals are completed.")
                return False
        goal.completed = True
        goal.completion_date = str(date.today())
        self._check_parent_completion(goal.parent_id)
        return True

    def _check_parent_completion(self, parent_id):
        if parent_id is None:
            return
        parent = self.find_goal(parent_id)
        if parent and all(sg.completed for sg in parent.sub_goals):
            parent.completed = True
            parent.completion_date = str(date.today())
            self._check_parent_completion(parent.parent_id)

    def unmark_complete(self, goal_id):
        goal = self.find_goal(goal_id)
        if not goal:
            print("Goal not found.")
            return False
        # Unmark this goal and recursively unmark parents
        goal.completed = False
        goal.completion_date = None
        self._unmark_parent(goal.parent_id)
        return True

    def _unmark_parent(self, parent_id):
        if parent_id is None:
            return
        parent = self.find_goal(parent_id)
        if parent:
            parent.completed = False
            parent.completion_date = None
            self._unmark_parent(parent.parent_id)

    def edit_goal(self, goal_id, new_title=None, new_due_date=None):
        goal = self.find_goal(goal_id)
        if not goal:
            print("Goal not found.")
            return False
        if new_title:
            goal.title = new_title
        if new_due_date is not None:
            goal.due_date = new_due_date
        return True

    def add_note(self, goal_id, note):
        goal = self.find_goal(goal_id)
        if goal:
            goal.notes.append(note)
            return True
        return False

    def add_issue(self, goal_id, issue):
        goal = self.find_goal(goal_id)
        if goal:
            goal.issues.append(issue)
            return True
        return False

    def add_resource(self, goal_id, resource):
        goal = self.find_goal(goal_id)
        if goal:
            goal.resources.append(resource)
            return True
        return False

    def get_progress_percentage(self, goal):
        if not goal.sub_goals:
            return 100 if goal.completed else 0
        total = len(goal.sub_goals)
        sub_percents = [self.get_progress_percentage(sg) for sg in goal.sub_goals]
        return sum(sub_percents) / total

    def show_progress(self):
        if not self.goals:
            print("No goals found.")
            return
        for g in self.goals:
            perc = self.get_progress_percentage(g)
            print(f"Goal [{g.id}]: {g.title} - Due: {g.due_date or 'No due date'}")
            print(f"  Progress: {perc:.1f}% - Completed: {'Yes' if g.completed else 'No'}")
            self._print_subgoals_progress(g.sub_goals, indent=4)
            print("-" * 40)

    def _print_subgoals_progress(self, subgoals, indent=0):
        for sg in subgoals:
            perc = self.get_progress_percentage(sg)
            print(" " * indent + f"Subgoal [{sg.id}]: {sg.title} - Due: {sg.due_date or 'No due date'}")
            print(" " * indent + f"  Progress: {perc:.1f}% - Completed: {'Yes' if sg.completed else 'No'}")
            self._print_subgoals_progress(sg.sub_goals, indent + 4)

    def show_completion_history(self):
        completed_goals = []
        def gather_completed(goal, major_title=None):
            if goal.completed:
                completed_goals.append((goal.completion_date, goal.title, major_title or goal.title))
            for sg in goal.sub_goals:
                gather_completed(sg, major_title or goal.title)
        for g in self.goals:
            gather_completed(g)

        if not completed_goals:
            print("No completed goals yet.")
            return

        completed_goals.sort(key=lambda x: x[0])
        print("Completion History (date - goal - major goal):")
        for date_, title, major in completed_goals:
            print(f"{date_} - {title} (Part of: {major})")

    def view_details(self, goal_id):
        goal = self.find_goal(goal_id)
        if not goal:
            print("Goal not found.")
            return
        print(f"Goal [{goal.id}]: {goal.title}")
        print(f"Due Date: {goal.due_date or 'No due date'}")
        print(f"Completed: {'Yes' if goal.completed else 'No'}")
        if goal.completed:
            print(f"Completion Date: {goal.completion_date}")
        if goal.notes:
            print("Notes:")
            for i, note in enumerate(goal.notes, 1):
                print(f"  {i}. {note}")
        if goal.issues:
            print("Issues:")
            for i, issue in enumerate(goal.issues, 1):
                print(f"  {i}. {issue}")
        if goal.resources:
            print("Resources:")
            for i, res in enumerate(goal.resources, 1):
                print(f"  {i}. {res}")
        if goal.sub_goals:
            print("Sub-Goals:")
            for sg in goal.sub_goals:
                print(f"  [{sg.id}] {sg.title} - Completed: {'Yes' if sg.completed else 'No'}")

def input_date(prompt):
    while True:
        d = input(prompt + " (YYYY-MM-DD or leave blank): ").strip()
        if not d:
            return None
        try:
            datetime.strptime(d, "%Y-%m-%d")
            return d
        except ValueError:
            print("Invalid date format.")

def main_menu(manager):
    while True:
        print("\n--- GOAL MANAGER ---")
        print("1. Add major goal")
        print("2. Add sub-goal")
        print("3. View goal details")
        print("4. Mark goal complete/uncomplete")
        print("5. Edit goal")
        print("6. Delete goal")
        print("7. Add note / issue / resource")
        print("8. Show progress")
        print("9. Show completion history")
        print("0. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            title = input("Enter major goal title: ")
            due = input_date("Enter due date")
            manager.add_goal(title, due)

        elif choice == "2":
            pid = input("Enter parent goal ID: ")
            if not pid.isdigit():
                print("Invalid ID.")
                continue
            title = input("Enter sub-goal title: ")
            due = input_date("Enter due date")
            manager.add_goal(title, due, int(pid))

        elif choice == "3":
            gid = input("Enter goal ID to view details: ")
            if gid.isdigit():
                manager.view_details(int(gid))
            else:
                print("Invalid ID.")

        elif choice == "4":
            gid = input("Enter goal ID to toggle completion: ")
            if gid.isdigit():
                gid = int(gid)
                goal = manager.find_goal(gid)
                if goal:
                    if goal.completed:
                        manager.unmark_complete(gid)
                        print("Marked as incomplete.")
                    else:
                        manager.mark_complete(gid)
                        print("Marked as complete.")
                else:
                    print("Goal not found.")
            else:
                print("Invalid ID.")

        elif choice == "5":
            gid = input("Enter goal ID to edit: ")
            if not gid.isdigit():
                print("Invalid ID.")
                continue
            gid = int(gid)
            new_title = input("Enter new title (leave blank to keep current): ").strip()
            new_due = input_date("Enter new due date")
            manager.edit_goal(gid, new_title if new_title else None, new_due)

        elif choice == "6":
            gid = input("Enter goal ID to delete: ")
            if gid.isdigit() and manager.delete_goal(int(gid)):
                print("Goal deleted.")
            else:
                print("Goal not found or could not delete.")

        elif choice == "7":
            gid = input("Enter goal ID: ")
            if not gid.isdigit():
                print("Invalid ID.")
                continue
            gid = int(gid)
            print("1. Add note\n2. Add issue\n3. Add resource")
            sub_choice = input("Choose: ")
            content = input("Enter content: ")
            if sub_choice == "1":
                manager.add_note(gid, content)
            elif sub_choice == "2":
                manager.add_issue(gid, content)
            elif sub_choice == "3":
                manager.add_resource(gid, content)
            else:
                print("Invalid choice.")

        elif choice == "8":
            manager.show_progress()

        elif choice == "9":
            manager.show_completion_history()

        elif choice == "0":
            manager.save()
            print("Progress saved. Exiting.")
            break

        else:
            print("Invalid option.")

# Entry point
if __name__ == "__main__":
    gm = GoalManager()
    gm.load()
    main_menu(gm)
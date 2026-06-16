import tkinter as tk
from tkinter import ttk, messagebox
from database import initialize_db
from tracker import (
    register_user, login_user,
    add_subject, get_subjects,
    log_session, get_sessions,
    set_goal, get_goal,
    get_streak, get_today_summary
)

# ── MAIN APP ──────────────────────────────────────────

class StudyTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Study Tracker")
        self.geometry("600x500")
        self.resizable(False, False)
        self.user_id = None
        initialize_db()
        self.show_login()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear()
        LoginScreen(self)

    def show_register(self):
        self.clear()
        RegisterScreen(self)

    def show_dashboard(self):
        self.clear()
        Dashboard(self)

    def show_log_session(self):
        self.clear()
        LogSessionScreen(self)

    def show_subjects(self):
        self.clear()
        SubjectScreen(self)

    def show_goals(self):
        self.clear()
        GoalScreen(self)

    def show_history(self):
        self.clear()
        HistoryScreen(self)

    def show_charts(self):
        from charts import show_charts
        show_charts(self.user_id)

# ── LOGIN ─────────────────────────────────────────────

class LoginScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Student Study Tracker", font=("Arial", 20, "bold")).pack(pady=30)
        tk.Label(self, text="Username").pack()
        self.username = tk.Entry(self, width=30)
        self.username.pack(pady=5)

        tk.Label(self, text="Password").pack()
        self.password = tk.Entry(self, show="*", width=30)
        self.password.pack(pady=5)

        tk.Button(self, text="Login", width=20, command=self.login).pack(pady=10)
        tk.Button(self, text="Register", width=20, command=app.show_register).pack()

    def login(self):
        u = self.username.get().strip()
        p = self.password.get().strip()
        if not u or not p:
            messagebox.showerror("Error", "Fill in all fields.")
            return
        user_id = login_user(u, p)
        if user_id:
            self.app.user_id = user_id
            self.app.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

# ── REGISTER ──────────────────────────────────────────

class RegisterScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Create Account", font=("Arial", 18, "bold")).pack(pady=30)
        tk.Label(self, text="Username").pack()
        self.username = tk.Entry(self, width=30)
        self.username.pack(pady=5)

        tk.Label(self, text="Password").pack()
        self.password = tk.Entry(self, show="*", width=30)
        self.password.pack(pady=5)

        tk.Button(self, text="Register", width=20, command=self.register).pack(pady=10)
        tk.Button(self, text="Back to Login", width=20, command=app.show_login).pack()

    def register(self):
        u = self.username.get().strip()
        p = self.password.get().strip()
        if not u or not p:
            messagebox.showerror("Error", "Fill in all fields.")
            return
        success = register_user(u, p)
        if success:
            messagebox.showinfo("Success", "Account created! Please login.")
            self.app.show_login()
        else:
            messagebox.showerror("Error", "Username already exists.")

# ── DASHBOARD ─────────────────────────────────────────

class Dashboard(tk.Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.pack(fill="both", expand=True)

        today_mins = get_today_summary(app.user_id)
        goal_mins = get_goal(app.user_id)
        streak = get_streak(app.user_id)

        tk.Label(self, text="Dashboard", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self, text=f"Today's Study Time: {today_mins} mins", font=("Arial", 12)).pack(pady=5)
        tk.Label(self, text=f"Daily Goal: {goal_mins} mins", font=("Arial", 12)).pack(pady=5)
        tk.Label(self, text=f"Current Streak: {streak} day(s) 🔥", font=("Arial", 12)).pack(pady=5)

        tk.Button(self, text="Log Study Session", width=25, command=app.show_log_session).pack(pady=8)
        tk.Button(self, text="Manage Subjects", width=25, command=app.show_subjects).pack(pady=5)
        tk.Button(self, text="Set Daily Goal", width=25, command=app.show_goals).pack(pady=5)
        tk.Button(self, text="View History", width=25, command=app.show_history).pack(pady=5)
        tk.Button(self, text="View Charts", width=25, command=app.show_charts).pack(pady=5)
        tk.Button(self, text="Logout", width=25, command=app.show_login).pack(pady=10)

# ── LOG SESSION ───────────────────────────────────────

class LogSessionScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Log Study Session", font=("Arial", 18, "bold")).pack(pady=20)

        subjects = get_subjects(app.user_id)
        if not subjects:
            tk.Label(self, text="No subjects found. Add subjects first.", fg="red").pack(pady=10)
            tk.Button(self, text="Go to Subjects", command=app.show_subjects).pack(pady=5)
            tk.Button(self, text="Back", command=app.show_dashboard).pack()
            return

        self.subject_map = {name: sid for sid, name in subjects}
        subject_names = list(self.subject_map.keys())

        tk.Label(self, text="Subject").pack()
        self.subject_var = tk.StringVar(value=subject_names[0])
        ttk.Combobox(self, textvariable=self.subject_var, values=subject_names, state="readonly", width=27).pack(pady=5)

        tk.Label(self, text="Duration (minutes)").pack()
        self.duration = tk.Entry(self, width=30)
        self.duration.pack(pady=5)

        tk.Label(self, text="Notes (optional)").pack()
        self.notes = tk.Entry(self, width=30)
        self.notes.pack(pady=5)

        tk.Button(self, text="Save Session", width=20, command=self.save).pack(pady=10)
        tk.Button(self, text="Back", width=20, command=app.show_dashboard).pack()

    def save(self):
        subject_name = self.subject_var.get()
        subject_id = self.subject_map[subject_name]
        duration = self.duration.get().strip()
        notes = self.notes.get().strip()

        if not duration.isdigit() or int(duration) <= 0:
            messagebox.showerror("Error", "Enter a valid duration in minutes.")
            return

        log_session(self.app.user_id, subject_id, int(duration), notes)
        messagebox.showinfo("Success", "Session logged!")
        self.app.show_dashboard()

# ── SUBJECTS ──────────────────────────────────────────

class SubjectScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Manage Subjects", font=("Arial", 18, "bold")).pack(pady=20)

        tk.Label(self, text="New Subject Name").pack()
        self.subject_entry = tk.Entry(self, width=30)
        self.subject_entry.pack(pady=5)
        tk.Button(self, text="Add Subject", width=20, command=self.add).pack(pady=5)

        tk.Label(self, text="Your Subjects:", font=("Arial", 11, "bold")).pack(pady=10)
        self.listbox = tk.Listbox(self, width=40, height=10)
        self.listbox.pack()
        self.load_subjects()

        tk.Button(self, text="Back", width=20, command=app.show_dashboard).pack(pady=10)

    def load_subjects(self):
        self.listbox.delete(0, tk.END)
        for _, name in get_subjects(self.app.user_id):
            self.listbox.insert(tk.END, name)

    def add(self):
        name = self.subject_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter a subject name.")
            return
        add_subject(self.app.user_id, name)
        self.subject_entry.delete(0, tk.END)
        self.load_subjects()

# ── GOALS ─────────────────────────────────────────────

class GoalScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Set Daily Goal", font=("Arial", 18, "bold")).pack(pady=20)
        current = get_goal(app.user_id)
        tk.Label(self, text=f"Current Goal: {current} mins/day", font=("Arial", 12)).pack(pady=5)

        tk.Label(self, text="New Goal (minutes per day)").pack()
        self.goal_entry = tk.Entry(self, width=30)
        self.goal_entry.pack(pady=5)

        tk.Button(self, text="Save Goal", width=20, command=self.save).pack(pady=10)
        tk.Button(self, text="Back", width=20, command=app.show_dashboard).pack()

    def save(self):
        val = self.goal_entry.get().strip()
        if not val.isdigit() or int(val) <= 0:
            messagebox.showerror("Error", "Enter a valid number of minutes.")
            return
        set_goal(self.app.user_id, int(val))
        messagebox.showinfo("Success", "Goal saved!")
        self.app.show_dashboard()

# ── HISTORY ───────────────────────────────────────────

class HistoryScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Study History", font=("Arial", 18, "bold")).pack(pady=20)

        cols = ("Date", "Subject", "Duration (mins)", "Notes")
        tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=130)
        tree.pack(padx=10)

        for row in get_sessions(app.user_id):
            tree.insert("", tk.END, values=row)

        tk.Button(self, text="Back", width=20, command=app.show_dashboard).pack(pady=10)
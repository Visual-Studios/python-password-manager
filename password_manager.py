import tkinter as tk
from tkinter import messagebox
import json
import os
from cryptography.fernet import Fernet

class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("500x400")

        # Generate or load encryption key
        if not os.path.exists("key.key"):
            self.key = Fernet.generate_key()
            with open("key.key", "wb") as key_file:
                key_file.write(self.key)
        else:
            with open("key.key", "rb") as key_file:
                self.key = key_file.read()
        
        self.fernet = Fernet(self.key)
        
        self.setup_ui()

    def setup_ui(self):
        heading = tk.Label(self.root, text="Password Manager", font=("Arial", 16, "bold"), fg="#333")
        heading.grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(self.root, text="Website:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5)
        self.website_entry = tk.Entry(self.root, width=30)
        self.website_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Username:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5)
        self.username_entry = tk.Entry(self.root, width=30)
        self.username_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Password:", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5)
        self.password_entry = tk.Entry(self.root, width=30)
        self.password_entry.grid(row=3, column=1, padx=10, pady=5)

        save_btn = tk.Button(self.root, text="Save", command=self.save_password, width=15, bg="#4CAF50", fg="white")
        save_btn.grid(row=4, column=0, padx=10, pady=5)

        view_btn = tk.Button(self.root, text="View Saved Passwords", command=self.view_passwords, width=15, bg="#2196F3", fg="white")
        view_btn.grid(row=4, column=1, padx=10, pady=5)

        self.view_frame = tk.Frame(self.root)
        self.view_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def save_password(self):
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not website or not username or not password:
            messagebox.showerror("Error", "Please fill out all fields")
            return

        new_data = {website: {"username": username, "password": self.fernet.encrypt(password.encode()).decode()}}

        if os.path.exists("passwords.json"):
            with open("passwords.json", "r") as f:
                data = json.load(f)
        else:
            data = {}

        data.update(new_data)

        with open("passwords.json", "w") as f:
            json.dump(data, f, indent=4)

        self.website_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        messagebox.showinfo("Success", "Password saved successfully")

    def delete_password(self, website):
        if os.path.exists("passwords.json"):
            with open("passwords.json", "r") as f:
                data = json.load(f)

            if website in data:
                del data[website]

                with open("passwords.json", "w") as f:
                    json.dump(data, f, indent=4)

                messagebox.showinfo("Success", f"Password for {website} deleted successfully")
                self.view_passwords()
            else:
                messagebox.showerror("Error", f"No entry found for {website}")
        else:
            messagebox.showerror("Error", "No passwords saved yet")

    def view_passwords(self):
        for widget in self.view_frame.winfo_children():
            widget.destroy()

        if os.path.exists("passwords.json"):
            with open("passwords.json", "r") as f:
                data = json.load(f)

            for i, (website, info) in enumerate(data.items()):
                decrypted_password = self.fernet.decrypt(info["password"].encode()).decode()
                tk.Label(self.view_frame, text=f"Website: {website}", font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w")
                tk.Label(self.view_frame, text=f"Username: {info['username']}", font=("Arial", 10)).grid(row=i, column=1, sticky="w")
                tk.Label(self.view_frame, text=f"Password: {decrypted_password}", font=("Arial", 10)).grid(row=i, column=2, sticky="w")
                tk.Button(self.view_frame, text="Delete", command=lambda w=website: self.delete_password(w)).grid(row=i, column=3, sticky="w")
        else:
            messagebox.showerror("Error", "No passwords saved yet")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManager(root)
    root.mainloop()


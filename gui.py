import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import face_recognition
import os
from PIL import Image, ImageTk
from database import create_connection, mark_attendance

class AttendanceApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Smart Attendance System")
        
        # Database connection
        self.conn = create_connection()
        
        # Load known faces
        self.known_encodings = []
        self.known_names = []
        self.load_known_faces()
        
        # GUI Components
        self.setup_gui()
        self.cap = cv2.VideoCapture(0)
        self.is_running = False
        self.update_video()
    
    def load_known_faces(self):
        for img_name in os.listdir("known_faces"):
            img_path = os.path.join("known_faces", img_name)
            image = face_recognition.load_image_file(img_path)
            encoding = face_recognition.face_encodings(image)[0]
            self.known_encodings.append(encoding)
            self.known_names.append(os.path.splitext(img_name)[0])
    
    def setup_gui(self):
        # Video frame
        self.video_frame = ttk.LabelFrame(self.window, text="Live Feed")
        self.video_frame.pack(padx=10, pady=10)
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack()
        
        # Controls
        self.control_frame = ttk.Frame(self.window)
        self.control_frame.pack(pady=10)
        
        self.btn_start = ttk.Button(
            self.control_frame, 
            text="Start Attendance", 
            command=self.start_attendance
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = ttk.Button(
            self.control_frame, 
            text="Stop Attendance", 
            command=self.stop_attendance
        )
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        self.btn_register = ttk.Button(
            self.control_frame, 
            text="Register New User", 
            command=self.register_user
        )
        self.btn_register.pack(side=tk.LEFT, padx=5)
        
        # Attendance log
        self.log_frame = ttk.LabelFrame(self.window, text="Attendance Log")
        self.log_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(
            self.log_frame, 
            columns=("Name", "Date", "Time"), 
            show="headings"
        )
        self.tree.heading("Name", text="Name")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Time", text="Time")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Load initial logs
        self.refresh_logs()
    
    def start_attendance(self):
        self.is_running = True
    
    def stop_attendance(self):
        self.is_running = False
    
    def register_user(self):
        # Add code to capture and save a new face
        messagebox.showinfo("Info", "Use create_dataset.py to register new users.")
    
    def update_video(self):
        if self.is_running:
            ret, frame = self.cap.read()
            if ret:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Face detection and recognition
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    matches = face_recognition.compare_faces(
                        self.known_encodings, face_encoding, tolerance=0.5
                    )
                    name = "Unknown"
                    
                    if True in matches:
                        first_match_index = matches.index(True)
                        name = self.known_names[first_match_index]
                        mark_attendance(self.conn, name)
                        self.refresh_logs()
                    
                    # Scale coordinates
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    
                    # Draw bounding box
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, name, (left, top - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                
                # Display frame in GUI
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
        
        self.window.after(10, self.update_video)
    
    def refresh_logs(self):
        # Clear existing logs
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Fetch data from database
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, date, time FROM attendance ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        
        for row in rows:
            self.tree.insert("", tk.END, values=row)
    
    def on_close(self):
        self.cap.release()
        self.conn.close()
        self.window.destroy()

if __name__ == "__main__":
    window = tk.Tk()
    app = AttendanceApp(window)
    window.protocol("WM_DELETE_WINDOW", app.on_close)
    window.mainloop()
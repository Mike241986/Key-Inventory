import tkinter as tk
from tkinter import messagebox
import pickle

class Room:
    def __init__(self, room_number, num_keys=4, residents=None):
        self.room_number = room_number
        self.num_keys = num_keys
        if residents is None:
            residents = {}
        self.residents = residents

    def check_in(self, resident_name):
        if len(self.residents) >= 2:
            raise Exception("Room already has two residents.")
        if resident_name in self.residents:
            raise Exception("Resident already checked in.")
        self.residents[resident_name] = {'room_key_loss': 0, 'entrance_key_loss': 0}  # Initialize key loss counters
        self.num_keys -= 1

    def check_out(self, resident_name):
        if resident_name not in self.residents:
            raise Exception("Resident not found in this room.")
        del self.residents[resident_name]
        self.num_keys += 1

    def key_loss(self, resident_name, key_type):
        if resident_name not in self.residents:
            raise Exception("Resident not found in this room.")
        if key_type not in ['room_key', 'entrance_key']:
            raise ValueError("Invalid key type. Use 'room_key' or 'entrance_key'.")
        if key_type == 'room_key':
            self.residents[resident_name]['room_key_loss'] += 1
            self.num_keys -= 1  # Reduce the number of keys in the room
        elif key_type == 'entrance_key':
            self.residents[resident_name]['entrance_key_loss'] += 1
        


    def fine_check(self, resident_name):
        if resident_name not in self.residents:
            raise Exception("Resident not found in this room.")
        room_key_loss = self.residents[resident_name]['room_key_loss']
        entrance_key_loss = self.residents[resident_name]['entrance_key_loss']
        if room_key_loss < 2:
            room_fine = room_key_loss * 10
        else:
            room_fine = room_key_loss * 10 + (room_key_loss-1) *10  # $10 fine per first room key loss, $20 for second
        if entrance_key_loss < 2:
            entrance_fine = entrance_key_loss * 20
        else:
            entrance_fine = entrance_key_loss * 20 + (entrance_key_loss-1)*20  # $20 fine per entrance key loss, $40 for second
        return {'room_fine': room_fine, 'entrance_fine': entrance_fine, 'room_key_loss': room_key_loss, 'entrance_key_loss':entrance_key_loss}

class Dorm:
    def __init__(self):
        self.rooms = {}
        self.load_data("dorm_data.pkl")  # Automatically load data on initialization

    def add_room(self, room_number, num_keys=4):
        self.rooms[room_number] = Room(room_number, num_keys)

    def inventory_check(self):
        inventory = []
        for room_number, room in self.rooms.items():
            total_keys = room.num_keys + len(room.residents)  # Total keys including those with residents
            needed_keys = 4 - total_keys
            if needed_keys > 0:
                inventory.append((room_number, room.num_keys, needed_keys))
        return inventory

    def fine_check_all(self):
        fines = {}
        for room_number, room in self.rooms.items():
            for resident_name in room.residents:
                fine_info = room.fine_check(resident_name)
                fines[f'{room_number}-{resident_name}'] = fine_info
        return fines

    def list_rooms_and_residents(self):
        room_list = []
        for room_number, room in self.rooms.items():
            residents = list(room.residents.keys())
            room_list.append((room_number, residents))
        return room_list

    def save_data(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.rooms, file)

    def load_data(self, filename):
        try:
            with open(filename, 'rb') as file:
                self.rooms = pickle.load(file)
        except FileNotFoundError:
            self.rooms = {}

class DormGUI:
    def __init__(self, root, dorm):
        self.root = root
        self.dorm = dorm
        self.root.title("Dorm Key Inventory System")

        # Room Number Entry
        self.room_label = tk.Label(root, text="Room Number")
        self.room_label.pack()
        self.room_entry = tk.Entry(root)
        self.room_entry.pack()

        # Resident Name Entry
        self.resident_label = tk.Label(root, text="Resident Name")
        self.resident_label.pack()
        self.resident_entry = tk.Entry(root)
        self.resident_entry.pack()

        # Buttons
        self.check_in_button = tk.Button(root, text="Check In", command=self.check_in)
        self.check_in_button.pack()
        self.check_out_button = tk.Button(root, text="Check Out", command=self.check_out)
        self.check_out_button.pack()
        self.room_key_loss_button = tk.Button(root, text="Report Room Key Loss", command=lambda: self.key_loss('room_key'))
        self.room_key_loss_button.pack()
        self.entrance_key_loss_button = tk.Button(root, text="Report Entrance Key Loss", command=lambda: self.key_loss('entrance_key'))
        self.entrance_key_loss_button.pack()
        self.inventory_button = tk.Button(root, text="Inventory Check", command=self.inventory_check)
        self.inventory_button.pack()
        self.fine_button = tk.Button(root, text="Check Fines", command=self.fine_check)
        self.fine_button.pack()
        self.list_rooms_button = tk.Button(root, text="List Rooms and Residents", command=self.list_rooms_and_residents)
        self.list_rooms_button.pack()
        self.save_button = tk.Button(root, text="Save Data", command=self.save_data)
        self.save_button.pack()
        self.load_button = tk.Button(root, text="Load Data", command=self.load_data)
        self.load_button.pack()

        # Manual Room Setup
        self.add_room_label = tk.Label(root, text="Add Room")
        self.add_room_label.pack()

        self.new_room_label = tk.Label(root, text="Room Number")
        self.new_room_label.pack()
        self.new_room_entry = tk.Entry(root)
        self.new_room_entry.pack()

        self.new_room_keys_label = tk.Label(root, text="Number of Keys")
        self.new_room_keys_label.pack()
        self.new_room_keys_entry = tk.Entry(root)
        self.new_room_keys_entry.pack()

        self.add_room_button = tk.Button(root, text="Add Room", command=self.add_room)
        self.add_room_button.pack()

    def get_room(self):
        room_number = self.room_entry.get()
        if room_number not in self.dorm.rooms:
            messagebox.showerror("Error", "Room not found. Please add the room first.")
            return None
        return self.dorm.rooms[room_number]

    def check_in(self):
        try:
            room = self.get_room()
            if room is None:
                return
            resident_name = self.resident_entry.get()
            room.check_in(resident_name)
            self.dorm.save_data("dorm_data.pkl")  # Save data after check-in
            messagebox.showinfo("Success", "Check-in successful")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def check_out(self):
        try:
            room = self.get_room()
            if room is None:
                return
            resident_name = self.resident_entry.get()
            room.check_out(resident_name)
            self.dorm.save_data("dorm_data.pkl")  # Save data after check-out
            messagebox.showinfo("Success", "Check-out successful")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def key_loss(self, key_type):
        try:
            room = self.get_room()
            if room is None:
                return
            resident_name = self.resident_entry.get()
            if key_type not in ['room_key', 'entrance_key']:
                raise ValueError("Invalid key type. Use 'room_key' or 'entrance_key'.")
            room.key_loss(resident_name, key_type)
            self.dorm.save_data("dorm_data.pkl")  # Save data after reporting key loss
            messagebox.showinfo("Success", f"{key_type.capitalize()} loss reported")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def inventory_check(self):
        rooms_with_less_keys = self.dorm.inventory_check()
        inventory_info = "\n".join([f"Room {room_number}: {num_keys} keys, needs {needed_keys} more" for room_number, num_keys, needed_keys in rooms_with_less_keys])
        messagebox.showinfo("Inventory Check", f"Rooms with less than 4 keys:\n{inventory_info}")

    def fine_check(self):
        fines = self.dorm.fine_check_all()
        fined_residents = {resident: fine for resident, fine in fines.items() if fine['room_fine'] > 0 or fine['entrance_fine'] > 0}
        if not fined_residents:
            messagebox.showinfo("Fine Check", "No residents have fines.")
        else:
            fine_info = "\n".join([f"{resident}: Room key - ${fine['room_fine']} ({fine['room_key_loss']}), Entrance key - ${fine['entrance_fine']} ({fine['entrance_key_loss']})" for resident, fine in fined_residents.items()])
            messagebox.showinfo("Fine Check", f"Residents with fines:\n{fine_info}")

    def list_rooms_and_residents(self):
        rooms = self.dorm.list_rooms_and_residents()
        rooms_info = "\n".join([f"Room {room_number}: {', '.join(residents)}" for room_number, residents in rooms])
        messagebox.showinfo("Rooms and Residents", f"Rooms with residents:\n{rooms_info}")

    def save_data(self):
        self.dorm.save_data("dorm_data.pkl")
        messagebox.showinfo("Success", "Data saved successfully")

    def load_data(self):
        self.dorm.load_data("dorm_data.pkl")
        messagebox.showinfo("Success", "Data loaded successfully")

    def add_room(self):
        try:
            room_number = self.new_room_entry.get()
            num_keys = int(self.new_room_keys_entry.get())
            self.dorm.add_room(room_number, num_keys)
            self.dorm.save_data("dorm_data.pkl")  # Save data after adding room
            messagebox.showinfo("Success", f"Room {room_number} added with {num_keys} keys")
        except ValueError:
            messagebox.showerror("Error", "Number of keys must be an integer")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    dorm = Dorm()
    gui = DormGUI(root, dorm)
    root.mainloop()


def main():
	print("Welcome to the LMS Management System!")
	print("Sample users: Admin One (id=1), Admin Two (id=2)")
	print("Type 'help' for commands.")
	db = load_db()
	users = db["users"]
	while True:
		cmd = input("\nEnter command: ").strip().lower()
		if cmd == "help":
			print("""
Commands:
  add_user <adder_id> <name> <role>         - Add a user (admin/superuser only)
  set_superuser <admin_id> <target_id> <on|off> - Admin sets superuser flag
  remove_user <remover_id> <target_id>      - Remove a user (admin/superuser only)
  list                                      - List all users
  exit                                      - Exit program
""")
		elif cmd.startswith("add_user"):
			try:
				_, adder_id, name, role = cmd.split()
				adder_id = int(adder_id)
				user = add_user(users, name, role, adder_id)
				save_db(db)
				print(f"Added: {user}")
			except Exception as e:
				print(f"Error: {e}")
		elif cmd.startswith("set_superuser"):
			try:
				_, admin_id, target_id, flag = cmd.split()
				admin_id = int(admin_id)
				target_id = int(target_id)
				value = True if flag == "on" else False
				user = set_superuser(users, target_id, admin_id, value)
				save_db(db)
				print(f"Superuser flag updated: {user}")
			except Exception as e:
				print(f"Error: {e}")
		elif cmd.startswith("remove_user"):
			try:
				_, remover_id, target_id = cmd.split()
				remover_id = int(remover_id)
				target_id = int(target_id)
				user = remove_user(users, target_id, remover_id)
				save_db(db)
				print(f"Removed: {user}")
			except Exception as e:
				print(f"Error: {e}")
		elif cmd == "list":
			for user in users:
				print(user)
		elif cmd == "exit":
			print("Exiting.")
			break
		else:
			print("Unknown command. Type 'help' for options.")

if __name__ == "__main__":
	main()
import random

def random_phone():
	return f"9{random.randint(100000000, 999999999)}"

def generate_sample_data():
	data = {"users": []}
	admin_names = ["Alice Johnson", "Robert Smith"]
	teacher_names = [
		"Emily Clark", "Michael Brown", "Jessica Lee", "David Wilson", "Sarah Miller",
		"James Anderson", "Laura Thomas", "Daniel Moore", "Sophia Taylor", "Matthew Harris",
		"Olivia Martin", "Benjamin White", "Emma Thompson", "William Garcia", "Ava Martinez"
	]
	student_first_names = [
		"Liam", "Noah", "Oliver", "Elijah", "James", "William", "Benjamin", "Lucas", "Henry", "Alexander",
		"Mason", "Michael", "Ethan", "Daniel", "Jacob", "Logan", "Jackson", "Levi", "Sebastian", "Mateo",
		"Jack", "Owen", "Theodore", "Aiden", "Samuel", "Joseph", "John", "David", "Wyatt", "Matthew",
		"Luke", "Asher", "Carter", "Julian", "Grayson", "Leo", "Jayden", "Gabriel", "Isaac", "Lincoln",
		"Anthony", "Hudson", "Dylan", "Ezra", "Thomas", "Charles", "Christopher", "Jaxon", "Maverick", "Josiah"
	]
	student_last_names = [
		"Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
		"Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
	]
	sections = ['A', 'B', 'C']
	classes = [f"Class {i}" for i in range(1, 11)]
	# Add 2 admins
	for i, name in enumerate(admin_names, 1):
		data["users"].append({
			"id": i,
			"name": name,
			"role": "admin",
			"superuser": True,
			"phone": random_phone()
		})
	# Add 15 teachers with subjects
	subjects = [
		"Math", "English", "Science", "History", "Geography", "Physics", "Chemistry", "Biology",
		"Computer Science", "Physical Education", "Art", "Music", "Economics", "Civics", "French"
	]
	for i, (name, subject) in enumerate(zip(teacher_names, subjects), 3):
		data["users"].append({
			"id": i,
			"name": name,
			"role": "teacher",
			"superuser": False,
			"phone": random_phone(),
			"subject": subject
		})
	# Add 1000 students, distributed in 10 classes and 2-3 sections each
	student_id = 18
	for class_num in range(1, 11):
		for section in sections:
			# About 33-34 students per section, adjust for 1000 total
			students_in_section = 34 if (class_num-1)*3+sections.index(section) < 1000%30 else 33
			for _ in range(students_in_section):
				fname = random.choice(student_first_names)
				lname = random.choice(student_last_names)
				name = f"{fname} {lname}"
				data["users"].append({
					"id": student_id,
					"name": name,
					"role": "student",
					"superuser": False,
					"phone": random_phone(),
					"class": f"Class {class_num}",
					"section": section
				})
				student_id += 1
				if student_id > 1017:  # 2 admins + 15 teachers + 1000 students = 1017
					break
			if student_id > 1017:
				break
		if student_id > 1017:
			break
	save_db(data)
	print("Sample data generated: 2 admins, 15 teachers, 1000 students with classes, sections, phones, and subjects.")
def add_user(users, name, role, added_by):
	# Only admin or superuser can add users
	adder = find_user_by_id(users, added_by)
	if not adder or (adder["role"] != "admin" and not adder["superuser"]):
		raise PermissionError("Only admin or superuser can add users.")
	if role == "admin" and adder["role"] != "admin":
		raise PermissionError("Only admin can add another admin.")
	new_id = get_next_user_id(users)
	user = {
		"id": new_id,
		"name": name,
		"role": role,
		"superuser": True if role == "admin" else False
	}
	users.append(user)
	return user

def set_superuser(users, target_id, set_by, value=True):
	setter = find_user_by_id(users, set_by)
	target = find_user_by_id(users, target_id)
	if not setter or setter["role"] != "admin":
		raise PermissionError("Only admin can set superuser flag.")
	if not target or target["role"] == "admin":
		raise ValueError("Cannot change superuser status of admin.")
	target["superuser"] = value
	return target

def remove_user(users, target_id, removed_by):
	remover = find_user_by_id(users, removed_by)
	target = find_user_by_id(users, target_id)
	if not remover or (remover["role"] != "admin" and not remover["superuser"]):
		raise PermissionError("Only admin or superuser can remove users.")
	if target["role"] == "admin":
		raise PermissionError("Cannot remove admin user.")
	if remover["role"] != "admin" and target["id"] == remover["id"]:
		raise PermissionError("Superuser cannot remove themselves.")
	users.remove(target)
	return target
import json
import os

DB_FILE = "lms_db.json"

def load_db():
	if not os.path.exists(DB_FILE):
		return {"users": []}
	with open(DB_FILE, "r") as f:
		return json.load(f)

def save_db(data):
	with open(DB_FILE, "w") as f:
		json.dump(data, f, indent=2)

def get_next_user_id(users):
	if not users:
		return 1
	return max(user["id"] for user in users) + 1

def find_user_by_id(users, user_id):
	for user in users:
		if user["id"] == user_id:
			return user
	return None

def find_user_by_name(users, name):
	for user in users:
		if user["name"].lower() == name.lower():
			return user
	return None
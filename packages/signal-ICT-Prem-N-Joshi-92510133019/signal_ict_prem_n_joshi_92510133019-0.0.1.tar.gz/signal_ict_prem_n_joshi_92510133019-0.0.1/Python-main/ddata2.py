import sqlite3

# Connect to (or create) database
conn = sqlite3.connect('student_record.db')
cursor = conn.cursor()

# Drop the table if it already exists to avoid schema conflicts
cursor.execute('DROP TABLE IF EXISTS student_record')

# Create the table with correct columns
cursor.execute('''
CREATE TABLE IF NOT EXISTS student_record (
    Enrollment INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    Subject1 TEXT NOT NULL,
    Mark1 INTEGER NOT NULL,
    Subject2 TEXT NOT NULL,
    Mark2 INTEGER NOT NULL,
    Subject3 TEXT NOT NULL,
    Mark3 INTEGER NOT NULL,
    Subject4 TEXT NOT NULL,
    Mark4 INTEGER NOT NULL           
)
''')

# List of student records
student_record = [
    (92301733016, 'ASHUTOSH KUMAR SINGH', 'PWP', 95, 'COA', 85, 'ICE', 99, 'C++', 86),
    (92301733017, 'HARSH VISHALBHAI TRIVEDI', 'PWP', 85, 'COA', 89, 'ICE', 94, 'C++', 89),
    (92301733027, 'VIRAJ PRAKASHBHAI VAGHASIYA', 'PWP', 90, 'COA', 84, 'ICE', 91, 'C++', 89),
    (92301733046, 'SHIVAM ATULKUMAR BHATT', 'PWP', 93, 'COA', 89, 'ICE', 69, 'C++', 88),
    (92301733058, 'DEVENDRASINH DOLATSINH JADEJA', 'PWP', 75, 'COA', 89, 'ICE', 97, 'C++', 87)
]

# Insert student records
cursor.executemany('''
INSERT INTO student_record (
    Enrollment, name, Subject1, Mark1,
    Subject2, Mark2, Subject3, Mark3,
    Subject4, Mark4
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', student_record)

# Commit the changes
conn.commit()

# Fetch and display all records
cursor.execute('SELECT * FROM student_record')
rows = cursor.fetchall()

print("All Student Records:")
for row in rows:
    print(row)

# Fetch students with any mark > 90
cursor.execute('''
SELECT name, 
    CASE 
        WHEN Mark1 > 90 THEN Subject1
        WHEN Mark2 > 90 THEN Subject2
        WHEN Mark3 > 90 THEN Subject3
        WHEN Mark4 > 90 THEN Subject4
    END as HighSubject,
    CASE 
        WHEN Mark1 > 90 THEN Mark1
        WHEN Mark2 > 90 THEN Mark2
        WHEN Mark3 > 90 THEN Mark3
        WHEN Mark4 > 90 THEN Mark4
    END as HighMark
FROM student_record
WHERE Mark1 > 90 OR Mark2 > 90 OR Mark3 > 90 OR Mark4 > 90
''')

high_marks = cursor.fetchall()
print("\nStudents with Marks greater than 90:")
for student in high_marks:
    print(student)

# Delete a student record
cursor.execute('''
DELETE FROM student_record 
WHERE name = "DEVENDRASINH DOLATSINH JADEJA"
''')
conn.commit()

# Update mark for Ashutosh Kumar (PWP)
cursor.execute('''
UPDATE student_record 
SET Mark1 = 98 
WHERE name = 'ASHUTOSH KUMAR SINGH' AND Subject1 = 'PWP'
''')

# Fetch updated mark
cursor.execute('''
SELECT name, Mark1 
FROM student_record 
WHERE name = "ASHUTOSH KUMAR SINGH"
''')
updated_mark = cursor.fetchone()
print(f"\nUpdated Mark for {updated_mark[0]} in PWP: {updated_mark[1]}")

# Verify deletion
cursor.execute('''
SELECT * FROM student_record 
WHERE name = "DEVENDRASINH DOLATSINH JADEJA"
''')
deleted = cursor.fetchone()
if deleted is None:
    print("\nDEVENDRASINH DOLATSINH JADEJA has been successfully deleted.")

# Calculate the average of all students' average marks
cursor.execute('''
SELECT AVG((Mark1 + Mark2 + Mark3 + Mark4) / 4.0) 
FROM student_record
''')
avg = cursor.fetchone()[0]
print(f"\nAverage mark of students: {avg:.2f}")

# Close connection
conn.close()
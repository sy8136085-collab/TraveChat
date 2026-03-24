import sqlite3

conn = sqlite3.connect('qa.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS qa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    source TEXT
)
''')

# Example data daal dete hain testing ke liye (baad mein delete / replace kar dena)
sample_data = [
    ("Goa mein best beach kaunsi hai?", "Baga Beach sabse popular hai crowd aur nightlife ke liye. Candolim calm hai.", "https://example.com/goa-beaches"),
    ("Kashmir kab jana best hai?", "April-June (summer) aur December-February (snow) best time hai.", "https://travel.com/kashmir"),
    ("Dubai visa kitne din ka milta hai?", "Tourist visa normally 30 ya 60 days ka milta hai Indians ko.", None),
]

c.executemany("INSERT INTO qa (question, answer, source) VALUES (?, ?, ?)", sample_data)

conn.commit()
conn.close()

print("qa.db ban gayi + 3 sample entries daal diye!")
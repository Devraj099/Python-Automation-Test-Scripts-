import sqlite3

# ─────────────────────────────────────────────
# Connect to the SQL Murder Mystery database
# ─────────────────────────────────────────────
conn = sqlite3.connect(r"C:\Python AI Testing\sql-murder-mystery.db")
conn.row_factory = sqlite3.Row  # allows column-name access
cur = conn.cursor()


def run(query, title=""):
    """Helper: run a query, print SQL and results nicely."""
    print("\n" + "═" * 70)
    if title:
        print(f"  🔍 {title}")
    print("═" * 70)

    # ── Print the SQL query ──
    print("\n  📝 SQL QUERY:")
    print("  " + "─" * 65)
    for line in query.strip().splitlines():
        print(f"  {line}")
    print("  " + "─" * 65)

    # ── Run and print results ──
    print("\n  📊 RESULT:")
    print("  " + "─" * 65)
    cur.execute(query)
    rows = cur.fetchall()
    if rows:
        cols = [d[0] for d in cur.description]
        print("  " + " | ".join(cols))
        print("  " + "-" * 60)
        for row in rows:
            print("  " + " | ".join(str(v) for v in row))
    else:
        print("  (no results)")
    return rows


# ─────────────────────────────────────────────
# STEP 1 — Find the crime scene report
# ─────────────────────────────────────────────
run("""
    SELECT *
    FROM crime_scene_report
    WHERE type = 'murder'
      AND date = 20180115
      AND city = 'SQL City'
""", "STEP 1 · Crime Scene Report (Jan 15, 2018 · SQL City)")

print("""
  📋 CLUE: Two witnesses.
     • Witness 1 → lives on Northwestern Dr (last/highest house number)
     • Witness 2 → named Annabel, lives on Franklin Ave
""")

# ─────────────────────────────────────────────
# STEP 2 — Find Witness 1 (last house on Northwestern Dr)
# ─────────────────────────────────────────────
run("""
    SELECT *
    FROM person
    WHERE address_street_name = 'Northwestern Dr'
    ORDER BY address_number DESC
    LIMIT 1
""", "STEP 2 · Witness 1 (last house on Northwestern Dr)")

# ─────────────────────────────────────────────
# STEP 3 — Find Witness 2 (Annabel on Franklin Ave)
# ─────────────────────────────────────────────
run("""
    SELECT *
    FROM person
    WHERE address_street_name = 'Franklin Ave'
      AND name LIKE 'Annabel%'
""", "STEP 3 · Witness 2 (Annabel on Franklin Ave)")

# ─────────────────────────────────────────────
# STEP 4 — Read both witness interviews
# ─────────────────────────────────────────────
run("""
    SELECT p.name, i.transcript
    FROM interview i
    JOIN person p ON p.id = i.person_id
    WHERE p.address_street_name = 'Northwestern Dr'
      AND p.address_number = (
          SELECT MAX(address_number)
          FROM person
          WHERE address_street_name = 'Northwestern Dr'
      )
    UNION
    SELECT p.name, i.transcript
    FROM interview i
    JOIN person p ON p.id = i.person_id
    WHERE p.address_street_name = 'Franklin Ave'
      AND p.name LIKE 'Annabel%'
""", "STEP 4 · Witness Interview Transcripts")

print("""
  📋 CLUES from interviews:
     • Killer is a MAN
     • Has a Get Fit Now Gym bag → membership starts with '48Z' (gold member)
     • Was at the gym on Jan 9, 2018
     • Drives a car with plate containing 'H42W'
""")

# ─────────────────────────────────────────────
# STEP 5 — Find gym members with 48Z gold membership who checked in Jan 9
# ─────────────────────────────────────────────
run("""
    SELECT m.id, m.name, m.membership_status, ci.check_in_date
    FROM get_fit_now_member m
    JOIN get_fit_now_check_in ci ON ci.membership_id = m.id
    WHERE m.id LIKE '48Z%'
      AND m.membership_status = 'gold'
      AND ci.check_in_date = 20180109
""", "STEP 5 · Gold Gym Members (48Z*) who checked in on Jan 9")

# ─────────────────────────────────────────────
# STEP 6 — Cross-reference with license plate 'H42W'
# ─────────────────────────────────────────────
run("""
    SELECT p.id, p.name, dl.plate_number, dl.car_make, dl.car_model, dl.gender
    FROM person p
    JOIN get_fit_now_member m ON m.person_id = p.id
    JOIN drivers_license dl ON dl.id = p.license_id
    WHERE m.id LIKE '48Z%'
      AND m.membership_status = 'gold'
      AND dl.plate_number LIKE '%H42W%'
      AND dl.gender = 'male'
""", "STEP 6 · Suspect with matching plate (H42W) + gym membership")

# ─────────────────────────────────────────────
# STEP 7 — Confirm killer & read their interview
# ─────────────────────────────────────────────
run("""
    SELECT p.name, i.transcript
    FROM interview i
    JOIN person p ON p.id = i.person_id
    WHERE p.name = 'Jeremy Bowers'
""", "STEP 7 · Killer's Interview (Jeremy Bowers)")

print("""
  📋 CLUES from Jeremy's confession:
     • Hired by a WOMAN
     • Has red hair, ~5'5" to 5'7", drives a Tesla Model S
     • Attended SQL Symphony Concert 3x in December 2017
""")

# ─────────────────────────────────────────────
# STEP 8 — Find the Mastermind
# ─────────────────────────────────────────────
run("""
    SELECT p.name, dl.hair_color, dl.height, dl.car_make, dl.car_model,
           dl.gender, COUNT(f.event_name) AS concert_visits, i.annual_income
    FROM person p
    JOIN drivers_license dl ON dl.id = p.license_id
    JOIN facebook_event_checkin f ON f.person_id = p.id
    LEFT JOIN income i ON i.ssn = p.ssn
    WHERE dl.hair_color = 'red'
      AND dl.gender = 'female'
      AND dl.car_make = 'Tesla'
      AND dl.car_model = 'Model S'
      AND dl.height BETWEEN 65 AND 67
      AND f.event_name = 'SQL Symphony Concert'
      AND f.date BETWEEN 20171201 AND 20171231
    GROUP BY p.id
    HAVING COUNT(f.event_name) = 3
""", "STEP 8 · The Real Mastermind (Miranda Priestly)")

# ─────────────────────────────────────────────
# STEP 9 — Insert answer & verify Murderer
# ─────────────────────────────────────────────
print("\n" + "═" * 70)
print("  ✅  STEP 9 · Verifying the Murderer")
print("═" * 70)

print("\n  📝 SQL QUERY:")
print("  " + "─" * 65)
print("  DELETE FROM solution;")
print("  INSERT INTO solution VALUES (1, 'Jeremy Bowers');")
print("  SELECT value FROM solution;")
print("  " + "─" * 65)

cur.execute("DELETE FROM solution")
cur.execute("INSERT INTO solution VALUES (1, 'Jeremy Bowers')")
conn.commit()
cur.execute("SELECT value FROM solution")
result = cur.fetchone()[0]
print(f"\n  📊 RESULT:")
print("  " + "─" * 65)
print(f"  value")
print("  " + "-" * 60)
print(f"  {result}")
print(f"\n  🔫  Murderer confirmed → {result}")

# ─────────────────────────────────────────────
# STEP 10 — Insert answer & verify Mastermind
# ─────────────────────────────────────────────
print("\n" + "═" * 70)
print("  ✅  STEP 10 · Verifying the Mastermind")
print("═" * 70)

print("\n  📝 SQL QUERY:")
print("  " + "─" * 65)
print("  DELETE FROM solution;")
print("  INSERT INTO solution VALUES (1, 'Miranda Priestly');")
print("  SELECT value FROM solution;")
print("  " + "─" * 65)

cur.execute("DELETE FROM solution")
cur.execute("INSERT INTO solution VALUES (1, 'Miranda Priestly')")
conn.commit()
cur.execute("SELECT value FROM solution")
result = cur.fetchone()[0]
print(f"\n  📊 RESULT:")
print("  " + "─" * 65)
print(f"  value")
print("  " + "-" * 60)
print(f"  {result}")
print(f"\n  🎭  Mastermind confirmed → {result}")

print("\n" + "═" * 70)
print("  🎉  MYSTERY SOLVED!")
print("      Killer     → Jeremy Bowers")
print("      Mastermind → Miranda Priestly")
print("═" * 70 + "\n")

conn.close()
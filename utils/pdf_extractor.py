import re
import pandas as pd
import pdfplumber

def extract_text_from_pdf(pdf_path, output_txt="extracted_data.txt"):
    """
    Extracts all text from a PDF file and writes it to a text file.
    Returns the lines of text as a list.
    """
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    
    # Save the extracted text to a file.
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    with open(output_txt, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    return lines

# Regular expression patterns.
STUDENT_REGEX = re.compile(r"SEAT NO\.\:\s+(\S+)\s+NAME\s+\:\s+(.*?)\s+MOTHER")
SEM_REGEX = re.compile(r"SEM\.\:(\d+)")
SGPA_REGEX = re.compile(r"THIRD YEAR SGPA\s*\:\s*([\d\.]+|--),\s*TOTAL CREDITS EARNED\s*\:\s*(\d+)")
SUBJECT_REGEX = re.compile(
    r"^(\S+)\s+(.+?)\s+(\S+)\s+"
    r"(\S+)\s+(\S+)\s+"
    r"(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+"
    r"(\S+)\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d+)"
)

def parse_mark_field(mark_field):
    """Converts a mark field like '022/030' to an integer (returns None for '---')."""
    mark_field = mark_field.strip()
    if mark_field == "---":
        return None
    parts = mark_field.split('/')
    return int(parts[0]) if parts[0].isdigit() else None

def parse_subject_line(line):
    """
    Uses the SUBJECT_REGEX to parse a subject line.
    Returns a dictionary of subject details or None if the line does not match.
    """
    match = SUBJECT_REGEX.match(line.strip())
    if not match:
        # Debug: print if line seems to be a subject line.
        if re.match(r"^\d", line.strip()):
            print(f"DEBUG: Line did not match subject pattern: {line}")
        return None

    return {
        "Subject Code": match.group(1).strip().rstrip("*"),
        "Subject Name": match.group(2).strip().rstrip(" *"),
        "ISE": None if match.group(3) == "---" else match.group(3),
        "ESE": None if match.group(4) == "---" else match.group(4),
        "TOTAL": None if match.group(5) == "---" else match.group(5),
        "TW": None if match.group(6) == "---" else match.group(6),
        "PR": None if match.group(7) == "---" else match.group(7),
        "OR": None if match.group(8) == "---" else match.group(8),
        "TUT": None if match.group(9) == "---" else match.group(9),
        "Tot%": match.group(10) if match.group(10) != "---" else None,
        "Crd": int(match.group(11)) if match.group(11).isdigit() else None,
        "Grd": match.group(12) if match.group(12) != "---" else None,
        "GP": int(match.group(13)) if match.group(13).isdigit() else None,
        "CP": int(match.group(14)) if match.group(14).isdigit() else None
    }

def parse_student_blocks(lines):
    """
    Processes the list of text lines and groups data into student blocks.
    Each student block contains header info and a list of subject records.
    """
    students = []
    current_student = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Student header: extract Seat No and Name.
        stu_match = STUDENT_REGEX.search(line)
        if stu_match:
            if current_student:
                students.append(current_student)
            current_student = {
                "Seat No": stu_match.group(1).strip(),
                "Name": stu_match.group(2).strip(),
                "Sem": None,
                "SGPA": None,
                "Credits": None,
                "Subjects": []
            }
            continue

        # Semester line: update current student's semester.
        sem_match = SEM_REGEX.search(line)
        if sem_match and current_student:
            current_student["Sem"] = sem_match.group(1).strip()
            continue

        # SGPA line: update current student's SGPA and credits.
        sgpa_match = SGPA_REGEX.search(line)
        if sgpa_match and current_student:
            sgpa_val = sgpa_match.group(1).strip()
            if sgpa_val == "--":
                sgpa_val = ""
            current_student["SGPA"] = sgpa_val
            current_student["Credits"] = sgpa_match.group(2).strip()
            continue

        # Subject line: parse and append subject data.
        subj_data = parse_subject_line(line)
        if subj_data and current_student:
            subj_data["Sem"] = current_student["Sem"]
            current_student["Subjects"].append(subj_data)

    if current_student:
        students.append(current_student)
    
    return students

def build_final_rows(students):
    """
    Converts the student blocks into a list of rows.
    For each student, the header (Seat No, Name, SGPA, Credits) is only shown on the first row.
    """
    final_rows = []
    for student in students:
        first = True
        if student["Subjects"]:
            for subject in student["Subjects"]:
                row = {
                    "Seat No": student["Seat No"] if first else "",
                    "Name": student["Name"] if first else "",
                    "Sem": subject.get("Sem", ""),
                    "Subject Code": subject.get("Subject Code", ""),
                    "Subject Name": subject.get("Subject Name", ""),
                    "ISE": subject.get("ISE", ""),
                    "ESE": subject.get("ESE", ""),
                    "TOTAL": subject.get("TOTAL", ""),
                    "TW": subject.get("TW", ""),
                    "PR": subject.get("PR", ""),
                    "OR": subject.get("OR", ""),
                    "TUT": subject.get("TUT", ""),
                    "Tot%": subject.get("Tot%", ""),
                    "Crd": subject.get("Crd", ""),
                    "Grd": subject.get("Grd", ""),
                    "GP": subject.get("GP", ""),
                    "CP": subject.get("CP", ""),
                    "SGPA": student["SGPA"] if first else "",
                    "Credits": student["Credits"] if first else ""
                }
                final_rows.append(row)
                first = False
        else:
            final_rows.append({
                "Seat No": student["Seat No"],
                "Name": student["Name"],
                "Sem": "",
                "Subject Code": "",
                "Subject Name": "",
                "ISE": "",
                "ESE": "",
                "TOTAL": "",
                "TW": "",
                "PR": "",
                "OR": "",
                "TUT": "",
                "Tot%": "",
                "Crd": "",
                "Grd": "",
                "GP": "",
                "CP": "",
                "SGPA": student["SGPA"],
                "Credits": student["Credits"]
            })
    return final_rows

def extract_data(pdf_path):
    """
    Main wrapper function to extract data from the PDF.
    Returns a list of dictionaries ready for DataFrame creation.
    """
    lines = extract_text_from_pdf(pdf_path)
    students = parse_student_blocks(lines)
    final_rows = build_final_rows(students)
    return final_rows

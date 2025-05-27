import json

def process_lesson_names():
    # Read the lessons.json file
    with open('lessons.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Extract and process lesson names
    lesson_names = []
    for lesson in data['lessons']:
        # Remove "Bài:" from the name and add to list
        name = lesson['name']
        if "Bài:" in name:
            name = name.replace("Bài:", "").strip()
        lesson_names.append(name)
    
    # Write only the names to a new file
    with open('lesson_names.txt', 'w', encoding='utf-8') as file:
        for name in lesson_names:
            file.write(name + '\n')
    
    print(f"Processing complete! Found {len(lesson_names)} lesson names.")
    print("Check lesson_names.txt for results.")

if __name__ == "__main__":
    process_lesson_names() 
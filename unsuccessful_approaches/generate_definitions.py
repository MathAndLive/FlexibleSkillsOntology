import csv
from time import sleep
from openai import OpenAI

reader = csv.reader(open(r"soft_skills_top184.csv", encoding="utf-8-sig"))
top_skills = [row[0] for row in reader]

top_skills_definitions = {}

client = OpenAI(
    api_key="Ваша информация тут",
    base_url="Ваша информация тут"
)

for skill in top_skills[1:]:
    response = None
    try:
        print(f"Processing skill: {skill}")
        response = client.chat.completions.create(
            model='gemini-2.5-flash',
            messages=[
                {'role': 'system',
                 'content': 'Тебе нужно написать 5 определений для данного навыка. Пиши максимально подробно и понятно. Я буду вставлять это в SBERT, чтобы понять, есть ли требование к навыку в вакансии. Тебе нужно отвечать без лишних слов, только определения, так как я твои ответы сразу использую в коде. Не нужно писать цифры в начала, форматировать слова.'},
                {'role': 'user', 'content': f'Навык: {skill}.'},
            ]
        )
    except Exception as e:
        print(f"Error: {e}")
        sleep(5)
        while response is None or not response.choices or not response.choices[0].message.content:
            print("Server error, retrying...")
            try:
                response = client.chat.completions.create(
                    model='gemini-2.5-flash',
                    messages=[
                        {'role': 'system',
                         'content': 'Тебе нужно написать 5 определений для данного навыка. Пиши максимально подробно и понятно. Я буду вставлять это в SBERT, чтобы понять, есть ли требование к навыку в вакансии. Тебе нужно отвечать без лишних слов, только определения, так как я твои ответы сразу использую в коде. Не нужно писать цифры в начала, форматировать слова.'},
                        {'role': 'user', 'content': f'Навык: {skill}.'},
                    ]
                )
            except Exception as e:
                print(f"Error: {e}")
                sleep(5)
                continue

    definitions = response.choices[0].message.content.split('\n')
    top_skills_definitions[skill] = definitions

with open('top_soft_skills_definitions.csv', 'w', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    for skill, definitions in top_skills_definitions.items():
        writer.writerow([skill, *definitions])

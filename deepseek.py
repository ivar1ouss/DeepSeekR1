from tkinter import *
from tkinter import scrolledtext, messagebox
import os
from dotenv import load_dotenv
import openai

# Инициализация главного окна
window = Tk()
window.title("DeepSeek")
window.geometry("800x650")  # Увеличили высоту для статусной строки
window.resizable(False, False)

# Загрузка API-ключа
load_dotenv()
api_key = os.getenv("IO_SECRET_KEY")

# Настройка клиента OpenAI
client = openai.OpenAI(
    api_key=api_key,
    base_url="https://api.intelligence.io.solutions/api/v1/",
)

Label(text="DeepSeek Chat", font=("Arial", 20, "bold")).pack(pady=10)
# Настройка стилей
BG_COLOR = "#f0f0f0"
TEXT_COLOR = "#333333"
FONT = ("Arial", 12)
STATUS_FONT = ("Arial", 10)

# Элементы интерфейса
chat_history = scrolledtext.ScrolledText(
    window,
    wrap=WORD,
    width=70,
    height=25,
    bg="white",
    fg=TEXT_COLOR,
    font=FONT
)
chat_history.pack(pady=20, padx=20)
chat_history.insert(END, "DeepSeek: Привет! Чем могу помочь?\n")
chat_history.config(state=DISABLED)

input_frame = Frame(window, bg=BG_COLOR)
input_frame.pack(pady=10)

user_input = Entry(
    input_frame,
    width=60,
    font=FONT,
    bg="white",
    fg=TEXT_COLOR
)
user_input.pack(side=LEFT, padx=5)
user_input.focus()

# Создаем статусную строку
status_frame = Frame(window, bg=BG_COLOR, height=30)
status_frame.pack(fill=X, padx=20, pady=(0, 20))

status_label = Label(
    status_frame,
    text="Статус бота: готов к работе",
    bg=BG_COLOR,
    fg="#555555",
    font=STATUS_FONT,
    anchor="w"
)
status_label.pack(fill=X, padx=5)


def update_status(text):
    """Обновляет текст в статусной строке"""
    status_label.config(text=text)
    window.update()  # Обновляем интерфейс сразу


def extract_final_response(full_response):
    """Извлекает только последнюю содержательную строку из ответа"""
    lines = full_response.split('\n')
    for line in reversed(lines):
        line = line.strip()
        if line and (any(c.isalpha() for c in line)):
            return line
    return full_response.strip()


def send_message():
    question = user_input.get().strip()
    if not question:
        return

    chat_history.config(state=NORMAL)
    chat_history.insert(END, f"\nВы: {question}\n")
    chat_history.see(END)
    user_input.delete(0, END)

    try:
        response = get_deepseek_response(question)
        clean_response = extract_final_response(response)
        chat_history.insert(END, f"DeepSeek: {clean_response}\n")
        update_status("Статус бота: ждет запрос")
    except Exception as e:
        chat_history.insert(END, f"Ошибка: {str(e)}\n")
        update_status(f"Ошибка: {str(e)}")

    chat_history.config(state=DISABLED)
    chat_history.see(END)


def get_deepseek_response(question):
    """Функция для получения ответа от DeepSeek-Llama-70B через API"""
    update_status("Статус бота: генерирует ответ...")
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
        messages=[
            {
                "role": "system",
                "content": "Отвечай ТОЛЬКО на русском языке и только ответ на поставленный вопрос. "
            },
            {"role": "user", "content": question},
        ],
        temperature=0.7,
        stream=False,
        max_completion_tokens=100
    )
    return response.choices[0].message.content


send_button = Button(
    input_frame,
    text="Отправить",
    command=send_message,
    bg="#4CAF50",
    fg="white",
    font=FONT
)
send_button.pack(side=LEFT, padx=5)

# Горячая клавиша Enter
window.bind("<Return>", lambda event: send_message())

window.mainloop()
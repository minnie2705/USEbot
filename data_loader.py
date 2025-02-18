from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import mysql.connector

def load_data():
    # Настройка Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Запуск в фоновом режиме
    options.add_argument('--disable-gpu')

    # Используем webdriver-manager для автоматической установки ChromeDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    # Подключение к базе данных MySQL
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='MinMin123',
        database='user_base'
    )
    cursor = connection.cursor()

    # URL страницы с заданиями
    url = 'https://soc-ege.sdamgia.ru/test?a=show_result&stat_id=34299589&retriable=1'
    driver.get(url)

    # Дождитесь загрузки страницы и извлеките содержимое
    driver.implicitly_wait(10)  # Подождать до 10 секунд

    # Получение HTML-страницы после полной загрузки
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Извлечение заданий, правильных ответов и пояснений
    questions = soup.find_all('div', class_='prob_maindiv')
    print(f"Found {len(questions)} questions.")  # Отладочная информация
    for question in questions:
        question_text_div = question.find('div', class_='pbody')
        correct_answer_div = question.find('div', text='Правильный ответ:').find_next('div')  # Предполагаем, что правильный ответ находится здесь
        explanation_div = question.find('div', text='Пояснение.').find_next('div')  # Предполагаем, что пояснение находится здесь

        if question_text_div and correct_answer_div and explanation_div:
            question_text = question_text_div.text.strip()
            correct_answer = correct_answer_div.text.strip()
            explanation = explanation_div.text.strip()

            combined_answer = f"Пояснение: {explanation}\nПравильный ответ: {correct_answer}"

            print(f"Loading question: {question_text}")  # Вывод отладочной информации
            print(f"Combined Answer: {combined_answer}")  # Вывод отладочной информации

            # Сохранение в базу данных
            query = "INSERT INTO examples (question, answer) VALUES (%s, %s)"
            try:
                cursor.execute(query, (question_text, combined_answer))
                connection.commit()
                print("Data inserted successfully")  # Вывод отладочной информации
            except mysql.connector.Error as err:
                print(f"Error: {err}")
                connection.rollback()
        else:
            print("Question, explanation or answer not found, skipping this entry.")  # Отладочная информация

    cursor.close()
    connection.close()
    driver.quit()
    print("Data loading complete")  # Вывод отладочной информации

if __name__ == '__main__':
    load_data()

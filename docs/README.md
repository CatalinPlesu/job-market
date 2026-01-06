# Документация проекта / Documentație Proiect

Этот каталог содержит документацию для магистерской диссертации.  
Acest director conține documentația pentru teza de master.

## Файлы / Fișiere

### 1. AVIZ.md
**Язык / Limba:** Румынский / Română

Официальный документ AVIZ (заключение/одобрение) для магистерской диссертации в соответствии с требованиями Технического Университета Молдовы.

Document oficial AVIZ (aviz/aprobare) pentru teza de master conform cerințelor Universității Tehnice a Moldovei.

**Содержание / Conținut:**
- Информация о студенте и координаторе (с заполнителями)
- Актуальность темы
- Характеристика диссертации
- Анализ прототипа
- Оценка результатов
- Корректность материалов
- Качество графических материалов
- Практическая ценность
- Рекомендации
- Характеристика студента и предложенная оценка

### 2. ABSTRACT_RU.md
**Язык / Limba:** Русский / Rusă

Подробная аннотация исследовательской работы на русском языке, описывающая текущее состояние проекта, цели, задачи, архитектуру и достижения системы.

Rezumat detaliat al lucrării de cercetare în limba rusă, care descrie starea actuală a proiectului, obiectivele, sarcinile, arhitectura și realizările sistemului.

**Содержание / Conținut:**
- Введение и актуальность темы
- Цели и задачи исследования
- Поставленная проблема
- Архитектура разработанной системы
- Описание всех модулей (scraping, LLM, база данных, аналитика, frontend)
- Интеллектуальные алгоритмы и оптимизации
- Технологические инновации
- Результаты и достижения
- Практическая ценность
- Перспективы развития
- Заключение

## Инструкции по заполнению / Instrucțiuni de completare

### Для AVIZ.md:

Необходимо заменить следующие заполнители:

1. `[Nume și Prenume Student]` - Имя и Фамилия студента
2. `[Grupa]` - Номер группы студента
3. `[Funcția, titlul științific]` - Должность и научное звание координатора
4. `[Semnătura, data]` - Подпись и дата
5. `[Nume, Prenume Coordonator]` - Имя и Фамилия координатора

### Для ABSTRACT_RU.md:

Необходимо заменить следующие заполнители:

1. `[Фамилия и Имя Студента]` - Фамилия и Имя студента
2. `[Номер Группы]` - Номер группы
3. `[Фамилия и Имя Научного Руководителя]` - Фамилия и Имя научного руководителя

## О проекте / Despre proiect

**Название / Titlu:**
Автоматизированная система анализа и классификации вакансий с рынка труда Республики Молдова с использованием больших языковых моделей (LLM) / Sistem automat de analiză și clasificare a vacanselor de pe piața muncii din Republica Moldova utilizând modele de limbaj (LLM)

**Технологии / Tehnologii:**
- Backend: Python (requests, aiohttp, BeautifulSoup4, SQLAlchemy)
- Frontend: JavaScript (Mithril.js, DaisyUI, Tailwind CSS, Chart.js)
- База данных / Bază de date: SQLite
- LLM: OpenAI API (OpenRouter)

**Основные источники данных / Surse principale de date:**
- Rabota.md
- Jobber.md
- Delucru.md

## Структура проекта / Structura proiectului

```
job-market/
├── docs/                       # Документация / Documentație
│   ├── README.md              # Этот файл / Acest fișier
│   ├── AVIZ.md                # AVIZ на румынском / AVIZ în română
│   └── ABSTRACT_RU.md         # Аннотация на русском / Rezumat în rusă
├── src/                       # Исходный код / Cod sursă
├── config/                    # Конфигурация / Configurare
├── frontend/                  # Веб-интерфейс / Interfață web
├── analysis_engine/           # Модули аналитики / Module de analiză
└── databases/                 # Базы данных / Baze de date
```

## Контакты / Contacte

**Университет / Universitate:** Технический Университет Молдовы / Universitatea Tehnică a Moldovei  
**Факультет / Facultate:** Компьютеры, Информатика и Микроэлектроника / Calculatoare, Informatică și Microelectronică  
**Департамент / Departament:** Информатика и Инженерия Систем / Informatică și Ingineria Sistemelor

---

*Документация создана в январе 2026 года / Documentația creată în ianuarie 2026*

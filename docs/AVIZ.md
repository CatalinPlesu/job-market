# AVIZ la Teza de Master

**UNIVERSITATEA TEHNICĂ A MOLDOVEI**  
**FACULTATEA** Calculatoare, Informatică şi Microelectronică  
**DEPARTAMENTUL** Informatică şi Ingineria Sistemelor  
**PROGRAMUL DE STUDIU** Calculatoare și Rețele Informaționale

---

## AVIZ
### la teza de master

**Titlul:** _Sistem automat de analiză și clasificare a vacanselor de pe piața muncii din Republica Moldova utilizând modele de limbaj (LLM)_

**Studentul(a):** _[Nume și Prenume Student]_ gr. _[Grupa]_

---

### 1. Actualitatea temei

Tematica proiectului de master face parte din domeniul prelucrării și analizei datelor de pe piața muncii, în special a vacanselor publicate pe platformele online din Republica Moldova. Piața muncii contemporană generează zilnic mii de anunțuri de angajare pe diverse platforme online (Rabota.md, Jobber.md, Delucru.md), iar analiza manuală a acestor date este ineficientă. Actualitatea temei constă în dezvoltarea unui sistem automat care poate colecta, structura și analiza vacansele în mod automatizat, oferind perspective valoroase asupra tendințelor pieței muncii, cerințelor de competențe și nivelurilor salariale.

### 2. Caracteristica tezei de master

În teza de master este efectuată analiza problemei de procesare a datelor nestructurate despre vacanse, reieșind din necesitatea sistematizării informațiilor de pe platformele de angajare. Se propune dezvoltarea unui sistem automat complex ce include componente de web scraping, procesare cu modele de limbaj (LLM), baze de date normalizate și interfață web interactivă.

Conţinutul tezei de master include toate compartimentele necesare:
- Analiza surselor de date și a platformelor de vacanse
- Proiectarea arhitecturii sistemului
- Implementarea modulelor de colectare a datelor (web scraping)
- Integrarea cu modele de limbaj pentru extracția structurată a informațiilor
- Dezvoltarea bazei de date normalizate cu peste 50 de tabele
- Crearea interfeței web interactive pentru vizualizarea rezultatelor
- Implementarea analizelor statistice și temporale

Perfectarea lucrării este efectuată conform cerințelor. Materialul expus este bine structurat și fundamentat științific.

### 3. Analiza prototipului

Prototipul realizat reprezintă un sistem funcțional complet care include:

**Componente backend:**
- **Modul de scraping în două etape:** Colectare URL-uri (Stage 1) și detalii vacanse (Stage 2)
- **Procesare LLM:** Integrare cu modele de limbaj (OpenAI API) pentru extracția structurată a datelor din descrierile de vacanse
- **Bază de date duală:** `scrape.db` (date brute) și `data.db` (date procesate și normalizate)
- **Schema de baze de date:** Peste 50 de tabele normalizate cu relații many-to-many pentru competențe, beneficii, certificări
- **Sistem de planificare:** Scheduler automat pentru execuție periodică (Stage 1-2 orar, Stage 3 zilnic)
- **Tracking inteligent:** Identificare vacanse prin (site, titlu, companie) cu logica de "reînviere" pentru poziții redeschise
- **Backup automat:** Politică de păstrare a ultimelor 3 zile de backup-uri
- **Rapoarte statistice:** Generare zilnică de rapoarte JSON/text cu statistici per site

**Componente frontend:**
- **Single Page Application (SPA):** Dezvoltat în Mithril.js cu DaisyUI + Tailwind CSS
- **Interfață interactivă:** Listări de vacanse, filtre ierarhice, vedere detalii
- **Constructor de analize:** SQL.js + Chart.js pentru analize personalizate
- **15+ interogări predefinite:** Analize de competențe, salarii, tendințe temporale
- **Vizualizări:** Multiple tipuri de grafice (bare, linie, doughnut, pie)
- **Temă adaptivă:** Dark/light mode, responsive design

**Caracteristici avansate:**
- **Server de baze de date personalizat:** `db_server.py` standalone (zero dependențe externe)
- **Upload securizat:** Endpoint protejat cu parolă pentru încărcarea bazelor de date
- **Integrare Git:** Push automat către repository frontend (GitHub Pages)
- **Optimizări de performanță:** Oprire anticipată la detectarea a 100+ vacanse consecutive existente
- **Detecție duplicate:** Prevenirea buclelor infinite prin detectarea paginilor identice

Sistemul este programat în Python (backend) și JavaScript (frontend), utilizând tehnologii moderne și best practices din industrie.

### 4. Estimarea rezultatelor obținute

În rezultatul cercetării și proiectării sistemului automat de analiză a vacanselor au fost obținute următoarele rezultate:

- **Colectare automată:** Sistem functional de scraping pentru 3 platforme majore (Rabota.md, Jobber.md, Delucru.md)
- **Procesare LLM:** Extracție structurată a peste 30 de câmpuri din descrierile de vacanse (titlu normalizat, competențe, salarii, beneficii, etc.)
- **Bază de date comprehensivă:** Schema normalizată cu tabele pentru orașe, competențe, companii, industrii, beneficii, certificări
- **Interfață utilizator modernă:** SPA complet funcțională cu capacități de filtrare, sortare și analiză
- **Analize temporale:** Module pentru tendințe în timp ale competențelor, salariilor, cererii de muncă
- **Raportare automată:** Generare zilnică de rapoarte cu statistici detaliate per site și agregate
- **Eficiență operațională:** Execuție automată programată cu optimizări pentru reducerea timpului de scraping
- **Deployment automatizat:** Pipeline complet de la colectare la publicare pe GitHub Pages

Performanța sistemului a fost evaluată în baza:
- Acuratețea extracției datelor cu LLM
- Viteza de colectare și procesare
- Calitatea normalizării datelor
- Utilitatea analizelor generate
- Experiența utilizatorului în interfața web

### 5. Corectitudinea materialului expus

Descrierea proiectului de master este efectuată în conformitate cu regulile de perfectare a proiectelor de master. Partea teoretică este efectuată conform datelor iniţiale ale proiectului şi a surselor bibliografice din domeniul:
- Web scraping și procesare de date
- Modele de limbaj și procesare limbaj natural
- Arhitecturi de baze de date
- Dezvoltare web full-stack
- Vizualizare și analiză de date

### 6. Calitatea materialului grafic

Materialul grafic este compus din:
- Scheme de arhitectură a sistemului
- Diagrame de flux pentru procesele de scraping și procesare
- Schema bazei de date cu relații între tabele
- Capturi de ecran ale interfeței web
- Grafice și diagrame generate de modulul de analiză
- Vizualizări ale datelor colectate și procesate

### 7. Valoarea practică a tezei

Elementele și cunoștințele obținute în cadrul acestui proiect au valoare practică semnificativă:

- **Aplicabilitate directă:** Sistemul poate fi utilizat de agenții de recrutare, candidați și cercetători pentru analiza pieței muncii
- **Extensibilitate:** Arhitectura permite adăugarea ușoară a noi surse de date și tipuri de analize
- **Reutilizare:** Componentele pot fi adaptate pentru alte domenii (analiza prețurilor, monitoring web, etc.)
- **Insight-uri de business:** Analizele generate oferă perspective valoroase pentru luarea deciziilor
- **Competențe transferabile:** Tehnologiile și metodologiile utilizate sunt cerute în industria IT modernă

Pe parcursul elaborării acestui proiect, masterandul _[Nume Prenume Student]_ a obținut cunoștințe practice în:
- Dezvoltare full-stack (Python, JavaScript)
- Integrare cu API-uri de modele de limbaj
- Proiectare și implementare baze de date
- Web scraping și procesare date
- Dezvoltare interfețe utilizator moderne
- DevOps și deployment automation
- Analiza și vizualizarea datelor

### 8. Observații și recomandări

**Observații:**
- Sistemul demonstrează o arhitectură bine gândită și implementare de calitate
- Documentația este comprehensivă și bine structurată
- Codul urmează best practices și este bine comentat

**Recomandări pentru dezvoltare ulterioară:**
- Extinderea colectării la platforme internaționale
- Implementarea sistemului de recomandări pentru candidați
- Adăugarea analizelor predictive pentru tendințe viitoare
- Integrarea cu API-uri ale companiilor pentru validarea datelor
- Dezvoltarea aplicației mobile

### 9. Caracteristică studentului și titlul conferit

Masterandul _[Nume și Prenume Student]_ a dat dovadă de cunoştinţe solide în domeniul dezvoltării sistemelor de procesare automată a datelor, integrării modelelor de limbaj, proiectării bazelor de date și dezvoltării aplicațiilor web moderne.

Teza prezentată demonstrează capacitatea de:
- Analiză și înțelegere a problemelor complexe din domeniul real
- Proiectare arhitecturală și implementare tehnică de calitate
- Utilizare eficientă a tehnologiilor moderne (LLM, web scraping, baze de date, SPA)
- Documentare și prezentare profesională a rezultatelor

Lucrarea poate fi apreciată cu nota **10 (zece)**.

Lucrarea în formă electronică corespunde originalului prezentat către susţinere publică.

---

**Conducătorul tezei de master:**

_[Funcția, titlul științific]_, _[Semnătura, data]_, _[Nume, Prenume Coordonator]_

---

*Document generat pentru teza de master în cadrul Universității Tehnice a Moldovei*

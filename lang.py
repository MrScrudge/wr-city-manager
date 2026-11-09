"""UI languages for W&R City Manager: Ukrainian (source strings), English, German.
tr('Ukrainian text') -> text in the current language; unknown strings fall back to Ukrainian."""
LANGS = [('uk', 'УКР'), ('en', 'ENG'), ('de', 'DEU')]
L = 'uk'


def set_lang(code):
    global L
    L = code if code in dict(LANGS) else 'uk'


def tr(s):
    return s if L == 'uk' else _T.get(s, {}).get(L, s)


def res_name(key, uk_names):
    if L == 'uk':
        return uk_names.get(key, key)
    return RES.get(key, {}).get(L) or uk_names.get(key, key)


# Ukrainian source -> {en, de}
_T = {
    'Міста': dict(en='Cities', de='Städte'),
    'Планувальник': dict(en='Planner', de='Planer'),
    'Карта': dict(en='Map', de='Karte'),
    'Калькулятор населення': dict(en='Population calculator', de='Bevölkerungsrechner'),
    'Скільки жителів порахувати': dict(en='How many residents to calculate', de='Für wie viele Einwohner berechnen'),
    'Формула розрахунку': dict(en='Calculation formula', de='Berechnungsformel'),
    'Змінити норми на 1000 жителів': dict(en='Edit the rates per 1000 residents', de='Raten pro 1000 Einwohner ändern'),
    'Скинути до нуля': dict(en='Reset to zero', de='Auf null zurücksetzen'),
    'жителів': dict(en='residents', de='Einwohner'),
    'Кількість = Населення ÷ 1000 × Норма на 1000 жителів (за рік) ÷ Період':
        dict(en='Amount = Population ÷ 1000 × Rate per 1000 residents (per year) ÷ Period',
             de='Menge = Einwohner ÷ 1000 × Rate pro 1000 Einwohner (pro Jahr) ÷ Zeitraum'),
    'Період: рік — 1, місяць — 12, трудодень — 365.': dict(en='Period: year — 1, month — 12, workday — 365.',
                                                          de='Zeitraum: Jahr — 1, Monat — 12, Arbeitstag — 365.'),
    'Зараз': dict(en='Now', de='Jetzt'),
    'Норма на 1000 (за рік)': dict(en='Rate per 1000 (per year)', de='Rate pro 1000 (pro Jahr)'),
    'Результат': dict(en='Result', de='Ergebnis'),
    'Норми на 1000 жителів': dict(en='Rates per 1000 residents', de='Raten pro 1000 Einwohner'),
    'Норми на 1000 жителів (на рік)': dict(en='Rates per 1000 residents (per year)', de='Raten pro 1000 Einwohner (pro Jahr)'),
    'Впиши свої числа: калькулятор і міста порахують за ними. Нуль — ресурс не показується.':
        dict(en='Enter your own numbers: the calculator and the cities use them. Zero — the resource is not shown.',
             de='Eigene Werte eintragen: Rechner und Städte nutzen sie. Null — die Ressource wird nicht angezeigt.'),
    'Продукти та товари': dict(en='Food and goods', de='Lebensmittel und Waren'),
    'Типові норми': dict(en='Default rates', de='Standardwerte'),
    'Ресурси на 1000 жителів': dict(en='Resources per 1000 residents', de='Ressourcen pro 1000 Einwohner'),
    '«–» або подвійний клік по заголовку — згорнути': dict(en='«–» or double-click the title to collapse',
                                                          de='«–» oder Doppelklick auf den Titel zum Einklappen'),
    'Мова': dict(en='Language', de='Sprache'),
    '+ Додати місто': dict(en='+ Add city', de='+ Stadt hinzufügen'),
    'Показати на одну зміну': dict(en='Show for one shift', de='Für eine Schicht anzeigen'),
    'Населення всіх міст:': dict(en='Population of all cities:', de='Einwohner aller Städte:'),
    'Населення:': dict(en='Population:', de='Einwohner:'),
    'Населення': dict(en='Population', de='Einwohner'),
    'С': dict(en='S', de='M'),
    'В': dict(en='H', de='H'),
    'Разом:': dict(en='Total:', de='Gesamt:'),
    'Разом': dict(en='Total', de='Gesamt'),
    '(1 зміна)': dict(en='(1 shift)', de='(1 Schicht)'),
    'Середня освіта': dict(en='Secondary education', de='Mittlere Bildung'),
    'Вища освіта': dict(en='Higher education', de='Hochschulbildung'),
    'Середня освіта: {c}    Вища освіта: {b}    Загалом: {t}': dict(
        en='Secondary: {c}    Higher: {b}    Overall: {t}', de='Mittlere: {c}    Höhere: {b}    Insgesamt: {t}'),
    'Усі міста: середня + вища освіта, одна чи три зміни': dict(
        en='All cities: secondary + higher education, one or three shifts', de='Alle Städte: mittlere + höhere Bildung, eine oder drei Schichten'),
    'Видалити місто': dict(en='Delete city', de='Stadt löschen'),
    "Видалити «{n}» разом з усіма об'єктами?": dict(en='Delete «{n}» with all its buildings?', de='«{n}» mit allen Gebäuden löschen?'),
    'Місто {n}': dict(en='City {n}', de='Stadt {n}'),
    "Об'єкт": dict(en='Building', de='Gebäude'),
    'К-сть': dict(en='Qty', de='Anz.'),
    'Продукт. %': dict(en='Prod. %', de='Prod. %'),
    'Виробництво': dict(en='Production', de='Produktion'),
    'Потреби': dict(en='Needs', de='Bedarf'),
    'С (3 зміни)': dict(en='Secondary (3 shifts)', de='Mittlere (3 Schichten)'),
    'В (3 зміни)': dict(en='Higher (3 shifts)', de='Höhere (3 Schichten)'),
    "+ Додати об'єкт": dict(en='+ Add building', de='+ Gebäude hinzufügen'),
    'Змінити іконку': dict(en='Change icon', de='Symbol ändern'),
    "Прибрати об'єкт": dict(en='Remove building', de='Gebäude entfernen'),
    'Натисни, щоб вказати': dict(en='Click to set', de='Klicken zum Festlegen'),
    '/ рік': dict(en='/ year', de='/ Jahr'),
    'Додатково ▸': dict(en='Extra ▸', de='Extras ▸'),
    'Додатково: будинки, зупинки, поля': dict(en='Extra: housing, stops, fields', de='Extras: Wohnhäuser, Haltestellen, Felder'),
    'Житлові будинки': dict(en='Housing', de='Wohngebäude'),
    'Працівників С на будинок': dict(en='Secondary workers per building', de='Arbeiter (mittl.) pro Gebäude'),
    'Працівників В на будинок': dict(en='Higher-ed. workers per building', de='Arbeiter (höh.) pro Gebäude'),
    'Будинків для С': dict(en='Buildings for secondary', de='Gebäude für mittlere'),
    'Будинків для В': dict(en='Buildings for higher-ed.', de='Gebäude für höhere'),
    'Зупинки': dict(en='Bus stops', de='Haltestellen'),
    'Жителів на зупинку': dict(en='Residents per stop', de='Einwohner pro Haltestelle'),
    'Потрібно зупинок': dict(en='Stops needed', de='Benötigte Haltestellen'),
    'Поля': dict(en='Fields', de='Felder'),
    'Рослин потрібно / рік': dict(en='Plants needed / year', de='Pflanzen benötigt / Jahr'),
    'з потреб міста': dict(en="from the city's needs", de='aus dem Bedarf der Stadt'),
    "Взяти «Рослини» з потреб об'єктів цього міста": dict(en="Take «Plants» from this city's building needs",
                                                         de='«Pflanzen» aus dem Bedarf der Gebäude dieser Stadt übernehmen'),
    'Врожай поля без добрив': dict(en='Field yield without fertilizer', de='Feldertrag ohne Dünger'),
    'Врожай поля з добривами': dict(en='Field yield with fertilizer', de='Feldertrag mit Dünger'),
    'Полів без добрив': dict(en='Fields without fertilizer', de='Felder ohne Dünger'),
    'Полів з добривами': dict(en='Fields with fertilizer', de='Felder mit Dünger'),
    '{t} (на рік)': dict(en='{t} (per year)', de='{t} (pro Jahr)'),
    '+ Ресурс': dict(en='+ Resource', de='+ Ressource'),
    'Готово': dict(en='Done', de='Fertig'),
    'Іконка будівлі': dict(en='Building icon', de='Gebäudesymbol'),
    'пошук англійською: school, factory, power…': dict(en='search: school, factory, power…', de='Suche (englisch): school, factory, power…'),
    'Продукти та товари — норма на 1000 жителів (на рік)': dict(en='Food and goods — rate per 1000 residents (per year)',
                                                              de='Lebensmittel und Waren — Bedarf pro 1000 Einwohner (pro Jahr)'),
    '+ Рядок': dict(en='+ Row', de='+ Zeile'),
    '+ Усі міста': dict(en='+ All cities', de='+ Alle Städte'),
    'Місто або населення': dict(en='City or population', de='Stadt oder Einwohner'),
    'місто зі списку або число': dict(en='city from the list or a number', de='Stadt aus der Liste oder Zahl'),
    'Разом (рядки вище)': dict(en='Total (rows above)', de='Summe (Zeilen oben)'),
    'Усі міста з вкладки «Міста»': dict(en='All cities from «Cities»', de='Alle Städte aus «Städte»'),
    'Додатково: електроенергія, вода, стічні води, сміття, тепло': dict(en='Extra: electricity, water, sewage, waste, heat',
                                                                       de='Extras: Strom, Wasser, Abwasser, Müll, Wärme'),
    'Комунальні — норма на 1000 жителів (на рік)': dict(en='Utilities — rate per 1000 residents (per year)',
                                                       de='Versorgung — Bedarf pro 1000 Einwohner (pro Jahr)'),
    'Населення береться з рядків таблиці продуктів вище.': dict(en='Population is taken from the rows of the goods table above.',
                                                               de='Einwohner werden aus den Zeilen der Warentabelle oben übernommen.'),
    'Вручну': dict(en='Manual', de='Manuell'),
    'Згорнути': dict(en='Collapse', de='Einklappen'),
    'Розгорнути': dict(en='Expand', de='Ausklappen'),
    'Закріпити поверх усіх вікон': dict(en='Keep on top of all windows', de='Immer im Vordergrund'),
    'Закріплено поверх усіх вікон — натисни, щоб відкріпити': dict(en='Kept on top — click to unpin',
                                                                   de='Im Vordergrund — klicken zum Lösen'),
    'Закрити': dict(en='Close', de='Schließen'),
    '{t} — на рік, 1 будівля при 100%': dict(en='{t} — per year, 1 building at 100%', de='{t} — pro Jahr, 1 Gebäude bei 100%'),
    'Піпетка: обведи у грі вікно будівлі — програма зчитає виробництво й потреби': dict(
        en='Pipette: outline the building window in the game — production and needs are read automatically',
        de='Pipette: Gebäudefenster im Spiel umranden — Produktion und Bedarf werden ausgelesen'),
    'Обведи мишкою вікно будівлі в грі. Esc — скасувати.': dict(en='Drag around the building window in the game. Esc to cancel.',
                                                               de='Gebäudefenster im Spiel mit der Maus umranden. Esc zum Abbrechen.'),
    'Піпетка — що знайдено': dict(en='Pipette — what was found', de='Pipette — Ergebnis'),
    'Виробництво за трудодень': dict(en='Production per workday', de='Produktion pro Arbeitstag'),
    'Потреби за трудодень': dict(en='Consumption per workday', de='Verbrauch pro Arbeitstag'),
    '→ {v} / рік': dict(en='→ {v} / year', de='→ {v} / Jahr'),
    'Рік = значення × 365 днів. Продуктивність % і кількість будівель задаються в таблиці. Вода й електрика за замовчуванням не враховуються.': dict(
        en='Year = value × 365 days. Productivity % and the number of buildings are set in the table. Water and electricity are not counted by default.',
        de='Jahr = Wert × 365 Tage. Produktivität % und Anzahl der Gebäude werden in der Tabelle eingestellt. Wasser und Strom werden standardmäßig nicht gezählt.'),
    'Записати в рядок': dict(en='Write to row', de='In die Zeile übernehmen'),
    'Скасувати': dict(en='Cancel', de='Abbrechen'),
    'Нічого не знайдено. Обведи вікно разом з рядками виробництва і споживання.': dict(
        en='Nothing found. Include the production and consumption lines in the outline.',
        de='Nichts gefunden. Die Zeilen für Produktion und Verbrauch mit umranden.'),
    'Модуль розпізнавання ще не встановлений. Закрий програму і запусти «W&R City Manager.bat» — він доставить його.': dict(
        en='The recognition module is not installed yet. Close the program and start «W&R City Manager.bat» — it will install it.',
        de='Das Erkennungsmodul ist noch nicht installiert. Programm schließen und «W&R City Manager.bat» starten — es installiert es.'),
    'Не вдалося прочитати: {e}': dict(en='Could not read: {e}', de='Lesen fehlgeschlagen: {e}'),
    'Інструкція': dict(en='Instructions', de='Anleitung'),
    'Перевірити': dict(en='Check', de='Prüfen'),
    'Норма зафіксована': dict(en='Fixed rate', de='Fester Wert'),
    'Записано в «{n}» (на рік, 1 будівля при 100%)': dict(en='Written to «{n}» (per year, 1 building at 100%)',
                                                         de='In «{n}» übernommen (pro Jahr, 1 Gebäude bei 100%)'),
    'Місто': dict(en='City', de='Stadt'),
    'Спочатку створи місто на вкладці «Міста».': dict(en='First create a city on the «Cities» tab.',
                                                     de='Lege zuerst eine Stadt im Reiter «Städte» an.'),
    'за трудодень': dict(en='per workday', de='pro Arbeitstag'),
    'за місяць': dict(en='per month', de='pro Monat'),
    'за рік': dict(en='per year', de='pro Jahr'),
    '/ день': dict(en='/ day', de='/ Tag'),
    '/ місяць': dict(en='/ month', de='/ Monat'),
    "Мої об'єкти": dict(en='My buildings', de='Meine Gebäude'),
    "Мої об'єкти — значення на 1 будівлю": dict(en='My buildings — values for 1 building', de='Meine Gebäude — Werte für 1 Gebäude'),
    "С і В — люди на 3 зміни для 1 будівлі. Зміни тут оновлюють цей об'єкт у всіх містах.": dict(
        en='S and H — people for 3 shifts for 1 building. Changes here update this building in every city.',
        de='M und H — Personal für 3 Schichten pro Gebäude. Änderungen hier gelten für dieses Gebäude in allen Städten.'),
    '1 зміна': dict(en='1 shift', de='1 Schicht'),
    '3 зміни': dict(en='3 shifts', de='3 Schichten'),
    'Назва': dict(en='Name', de='Name'),
    'Люди': dict(en='Staff', de='Personal'),
    'Трудівники (1 зміна)': dict(en='Workers (1 shift)', de='Arbeiter (1 Schicht)'),
    'Інженери (1 зміна)': dict(en='Engineers (1 shift)', de='Ingenieure (1 Schicht)'),
    '{t} — за 1 трудодень, 1 будівля при 100%': dict(en='{t} — per workday, 1 building at 100%', de='{t} — pro Arbeitstag, 1 Gebäude bei 100%'),
    'Вводь число за одну зміну — як «за 1 трудодень» у вікні гри. За місяць і рік програма порахує сама.': dict(
        en='Enter the number for one shift — as «per workday» in the game window. Month and year are calculated for you.',
        de='Zahl für eine Schicht eingeben — wie «pro Arbeitstag» im Spielfenster. Monat und Jahr rechnet das Programm selbst.'),
    "Об'єкт «{n}» уже є.": dict(en='«{n}» already exists.', de='«{n}» gibt es schon.'),
    "Прибрати «{n}» зі списку об'єктів?": dict(en='Remove «{n}» from the list of buildings?', de='«{n}» aus der Gebäudeliste entfernen?'),
    "Новий об'єкт {n}": dict(en='New building {n}', de='Neues Gebäude {n}'),
    'С (1 зміна)': dict(en='S (1 shift)', de='M (1 Schicht)'),
    'В (1 зміна)': dict(en='H (1 shift)', de='H (1 Schicht)'),
    'Пошук…': dict(en='Search…', de='Suchen…'),
    'Сортувати за назвою': dict(en='Sort by name', de='Nach Name sortieren'),
    'Сортувати за кількістю людей': dict(en='Sort by number of people', de='Nach Personenzahl sortieren'),
    'Натисни ще раз — зворотний порядок, ще раз — мій порядок': dict(
        en='Click again — reverse order, once more — my own order', de='Nochmal klicken — umgekehrt, nochmal — eigene Reihenfolge'),
    'Іконка об\'єкта': dict(en='Building icon', de='Gebäudesymbol'),
    'Натисни, щоб змінити іконку': dict(en='Click to change the icon', de='Klicken, um das Symbol zu ändern'),
    'Будівлі гри': dict(en='Game buildings', de='Spielgebäude'),
    'Ресурси гри': dict(en='Game resources', de='Spielressourcen'),
    'Своя картинка PNG…': dict(en='Own PNG picture…', de='Eigenes PNG-Bild…'),
    'Стандартна іконка': dict(en='Default icon', de='Standardsymbol'),
    'Подвійний клік — вибрати': dict(en='Double-click to choose', de='Doppelklick zum Auswählen'),
    'Не вдалося відкрити картинку.': dict(en='Could not open the picture.', de='Bild konnte nicht geöffnet werden.'),
    'Зберегти в таблицю (Excel)': dict(en='Save as a spreadsheet (Excel)', de='Als Tabelle speichern (Excel)'),
    'Зберегти таблицю': dict(en='Save spreadsheet', de='Tabelle speichern'),
    'Збережено: {p}': dict(en='Saved: {p}', de='Gespeichert: {p}'),
    'Не вдалося зберегти: {e}': dict(en='Could not save: {e}', de='Speichern fehlgeschlagen: {e}'),
    'Модуль Excel не встановлено — збережено як CSV (теж відкривається в Excel): {p}': dict(
        en='The Excel module is not installed — saved as CSV (Excel opens it too): {p}',
        de='Das Excel-Modul ist nicht installiert — als CSV gespeichert (öffnet sich auch in Excel): {p}'),
    'Баланс ресурсів': dict(en='Resource balance', de='Ressourcenbilanz'),
    'Ресурс': dict(en='Resource', de='Ressource'),
    'Різниця': dict(en='Difference', de='Differenz'),
    'Період': dict(en='Period', de='Zeitraum'),
    'Разом (3 зміни)': dict(en='Total (3 shifts)', de='Gesamt (3 Schichten)'),
    'Разом (1 зміна)': dict(en='Total (1 shift)', de='Gesamt (1 Schicht)'),
    'Усього по місту': dict(en='City total', de='Stadt gesamt'),
    'Комунальні': dict(en='Utilities', de='Versorgung'),
    'Відкрити': dict(en='Open', de='Öffnen'),
    'сховати / показати': dict(en='hide / show', de='ausblenden / einblenden'),
    'Видалено «{n}».': dict(en='Deleted «{n}».', de='«{n}» gelöscht.'),
    'Ctrl+Z — повернути.': dict(en='Ctrl+Z — bring it back.', de='Strg+Z — zurückholen.'),
    'Нічого скасовувати.': dict(en='Nothing to undo.', de='Nichts rückgängig zu machen.'),
    'Повернуто «{n}».': dict(en='«{n}» is back.', de='«{n}» ist zurück.'),
    'З добривами — натисни, щоб без добрив': dict(en='With fertilizer — click for without', de='Mit Dünger — klicken für ohne'),
    'Без добрив — натисни, щоб з добривами': dict(en='Without fertilizer — click for with', de='Ohne Dünger — klicken für mit'),
    'Жителів на 1 посадку': dict(en='Residents per boarding place', de='Einwohner pro Einstiegsort'),
    'Підприємств': dict(en='Enterprises', de='Betriebe'),
    '1–2 зупинки на посадку і 1–2 на підприємство': dict(en='1–2 stops per boarding place and 1–2 per enterprise',
                                                        de='1–2 Haltestellen pro Einstiegsort und 1–2 pro Betrieb'),
    'Посадок': dict(en='Boarding places', de='Einstiegsorte'),
    'Додатково: будинки, зупинки': dict(en='Extra: housing, bus stops', de='Extras: Wohnhäuser, Haltestellen'),
    '{t} — за рік, 1 поле': dict(en='{t} — per year, 1 field', de='{t} — pro Jahr, 1 Feld'),
    'Для поля вводь урожай і добрива за рік.': dict(en='For a field enter the harvest and fertilizer per year.',
                                                   de='Für ein Feld Ernte und Dünger pro Jahr eingeben.'),
    'Усі міста': dict(en='All cities', de='Alle Städte'),
    'Зберегти карту': dict(en='Save map', de='Karte speichern'),
    'Для вкладки «Планувальник» потрібен модуль PySide6 WebEngine. Закрий програму і запусти «W&R City Manager.bat» — він доставить його.': dict(
        en='The «Planner» tab needs the PySide6 WebEngine module. Close the program and start «W&R City Manager.bat» — it will install it.',
        de='Der Reiter «Planer» braucht das Modul PySide6 WebEngine. Programm schließen und «W&R City Manager.bat» starten — es installiert es.'),
    "Зміни тут оновлюють цей об'єкт у всіх містах.": dict(en='Changes here update this building in every city.',
                                                         de='Änderungen hier gelten für dieses Gebäude in allen Städten.'),
}

# resource names (game resource ids)
RES = {
    'airplanes': dict(en='Aircraft', de='Flugzeuge'), 'alcohol': dict(en='Alcohol', de='Alkohol'),
    'alumina': dict(en='Alumina', de='Tonerde'), 'aluminium': dict(en='Aluminium', de='Aluminium'),
    'asphalt': dict(en='Asphalt', de='Asphalt'), 'bauxite': dict(en='Bauxite', de='Bauxit'),
    'bitumen': dict(en='Bitumen', de='Bitumen'), 'boards': dict(en='Boards', de='Bretter'),
    'bricks': dict(en='Bricks', de='Ziegel'), 'cement': dict(en='Cement', de='Zement'),
    'chemicals': dict(en='Chemicals', de='Chemikalien'), 'clothes': dict(en='Clothes', de='Kleidung'),
    'coal': dict(en='Coal', de='Kohle'), 'colorwater': dict(en='? (white drop)', de='? (weißer Tropfen)'),
    'concrete': dict(en='Concrete', de='Beton'), 'ecomponents': dict(en='Electronic components', de='Elektronische Bauteile'),
    'eletric': dict(en='Electricity', de='Strom'), 'eletronics': dict(en='Electronics', de='Elektronik'),
    'explosives': dict(en='Explosives', de='Sprengstoff'), 'fabric': dict(en='Fabric', de='Stoff'),
    'fertiliser': dict(en='Fertilizer', de='Kunstdünger'), 'fertiliser_liquid': dict(en='Liquid fertilizer', de='Flüssigdünger'),
    'food': dict(en='Bread', de='Brot'), 'fuel': dict(en='Fuel', de='Treibstoff'), 'gravel': dict(en='Gravel', de='Schotter'),
    'heat': dict(en='Heat', de='Wärme'), 'helicopters': dict(en='Helicopters', de='Hubschrauber'),
    'iron': dict(en='Iron ore', de='Eisenerz'), 'livestock': dict(en='Livestock', de='Vieh'),
    'mcomponents': dict(en='Mechanical components', de='Mechanische Bauteile'), 'meat': dict(en='Meat', de='Fleisch'),
    'nuclearfuel': dict(en='Nuclear fuel', de='Kernbrennstoff'),
    'nuclearfuelburned': dict(en='Spent nuclear fuel', de='Abgebrannter Kernbrennstoff'),
    'oil': dict(en='Oil', de='Öl'), 'plants': dict(en='Crops', de='Getreide'), 'plastics': dict(en='Plastics', de='Kunststoff'),
    'prefabpanels': dict(en='Prefab panels', de='Fertigteilplatten'), 'rawbauxite': dict(en='Raw bauxite', de='Rohbauxit'),
    'rawcoal': dict(en='Raw coal', de='Rohkohle'), 'rawgravel': dict(en='Raw gravel', de='Rohkies'),
    'rawiron': dict(en='Raw iron ore', de='Roheisenerz'),
    'service_material': dict(en='Maintenance & repair', de='Wartung und Reparatur'),
    'ships': dict(en='Ships', de='Schiffe'), 'steel': dict(en='Steel', de='Stahl'), 'trains': dict(en='Trains', de='Züge'),
    'uf6': dict(en='Uranium hexafluoride', de='Uranhexafluorid'), 'uranium': dict(en='Uranium', de='Uran'),
    'usagewater': dict(en='Sewage', de='Abwasser'), 'vehicles': dict(en='Vehicles', de='Fahrzeuge'),
    'waste_aluminium': dict(en='Aluminium waste', de='Aluminiumabfall'), 'waste_ash': dict(en='Ash', de='Asche'),
    'waste_bio': dict(en='Bio waste', de='Bioabfall'), 'waste_burnable': dict(en='Burnable waste', de='Brennbarer Abfall'),
    'waste_gravel': dict(en='Gravel waste', de='Schotterabfall'), 'waste_mixed': dict(en='Waste', de='Müll'),
    'waste_other': dict(en='Other waste', de='Sonstiger Abfall'), 'waste_plastic': dict(en='Plastic waste', de='Kunststoffabfall'),
    'waste_steel': dict(en='Steel waste', de='Stahlabfall'), 'waste_toxic': dict(en='Toxic waste', de='Giftmüll'),
    'water': dict(en='Water', de='Wasser'), 'wood': dict(en='Wood', de='Holz'),
    'workers': dict(en='Graduates / workers', de='Absolventen / Arbeiter'), 'yellowcake': dict(en='Yellowcake', de='Yellowcake'),
}


# the user's building templates: Ukrainian name -> (English, German); English as in the game where it has that building
OBJ = {
    'Танковий завод': ('Tank factory', 'Panzerfabrik'),
    'Трамвайний завод': ('Tram factory', 'Straßenbahnfabrik'),
    'Цегельний завод': ('Brick factory', 'Ziegelei'),
    'Панельний завод': ('Panel factory', 'Plattenwerk'),
    'Цементний завод': ('Cement plant', 'Zementwerk'),
    'Гравійний завод': ('Gravel processing plant', 'Schotterwerk'),
    'Завод переробки буд сміття': ('Construction waste recycling plant', 'Bauschutt-Recyclinganlage'),
    'Завод з переробки пластику': ('Plastic recycling plant', 'Kunststoff-Recyclinganlage'),
    'Завод з переробки сталі': ('Steel recycling plant', 'Stahl-Recyclinganlage'),
    'Завод з переробки Алюмінію': ('Aluminium recycling plant', 'Aluminium-Recyclinganlage'),
    'Завод з переробки н відходів': ('Waste sorting plant', 'Müllsortieranlage'),
    'Сміттєспалювальна електростанція': ('Waste incineration power plant', 'Müllverbrennungskraftwerk'),
    'Сміттєспалювальна теплостанція': ('Waste incineration heating plant', 'Müllverbrennungs-Heizwerk'),
    'Хлібзавод': ('Food factory', 'Lebensmittelfabrik'),
    'Переробка техніки': ('Vehicle recycling', 'Fahrzeugverwertung'),
    'ТЕС': ('Coal power plant', 'Kohlekraftwerk'),
    'Теплоцентраль': ('Heating plant', 'Heizwerk'),
    'Лісопильний завод': ('Sawmill', 'Sägewerk'),
    'Алкогольний завод': ('Alcohol factory', 'Alkoholfabrik'),
    'Завод електродеталей': ('Electrical components factory', 'Elektrobauteilefabrik'),
    'Завод Електроніки': ('Electronics factory', 'Elektronikfabrik'),
    'Свердловина': ('Water well', 'Brunnen'),
    'Кінотеатр': ('Cinema', 'Kino'),
    'Спорт (Зал і поля)': ('Sports (hall and fields)', 'Sport (Halle und Plätze)'),
    'Радіостанція': ('Radio station', 'Radiosender'),
    'Сто велике': ('Technical services (large)', 'Technischer Dienst (groß)'),
    'Держбезпека': ('Secret police', 'Staatssicherheit'),
    'Залізнична буд. кантора': ('Railway construction office', 'Bahnbaubüro'),
    'Міська Адміністрація': ('City hall', 'Rathaus'),
    'Асфальт та Бетон': ('Asphalt and concrete', 'Asphalt und Beton'),
    'Хімічний завод': ('Chemical plant', 'Chemiewerk'),
    'Уран': ('Uranium processing plant', 'Uranaufbereitung'),
    'Ткацька фабрика': ('Fabric factory', 'Textilfabrik'),
    'ЛІсгосп': ('Forestry', 'Forstbetrieb'),
    'Мясокомбінат': ('Meat processing plant (2)', 'Fleischfabrik (2)'),
    'Мясрадгосп': ('Livestock farm (2)', 'Viehzuchtbetrieb (2)'),
    'Вугільнозбагачувальний завод': ('Coal processing plant', 'Kohleaufbereitung'),
    'Пластмасовий завод': ('Plastic factory', 'Kunststofffabrik'),
    'Завод Ядерного Палива': ('Nuclear fuel factory', 'Kernbrennstofffabrik'),
    'Нафтопереробний Завод': ('Oil refinery', 'Ölraffinerie'),
    'Алюмініювий Завод': ('Aluminium plant', 'Aluminiumwerk'),
    'Заврд Бетонних Панелей': ('Prefab panel factory', 'Betonfertigteilwerk'),
    'Бетоний Завод': ('Concrete plant', 'Betonwerk'),
    'Асфальтний Завод': ('Asphalt plant', 'Asphaltwerk'),
    'Малий Торговельний Центр': ('Small shopping center', 'Kleines Einkaufszentrum'),
    'Великий Торговельний Центр': ('Large shopping center', 'Großes Einkaufszentrum'),
    'Кафе-бар': ('Café bar', 'Café-Bar'),
    'Афитеатр': ('Amphitheater', 'Amphitheater'),
    'Будинок Культури': ('House of culture', 'Kulturhaus'),
    'Телестанція': ('TV station', 'Fernsehsender'),
    'Критий басейн': ('Indoor swimming pool', 'Hallenbad'),
    'Спортзал менший': ('Sports hall (small)', 'Sporthalle (klein)'),
    'Спортзал більший': ('Sports hall (large)', 'Sporthalle (groß)'),
    'Поліклініка': ('Clinic', 'Poliklinik'),
    'Лікарня менша': ('Hospital (small)', 'Krankenhaus (klein)'),
    'Лікарня більша': ('Hospital (large)', 'Krankenhaus (groß)'),
    'Дитбудинок більший': ('Orphanage (large)', 'Waisenhaus (groß)'),
    'Дитбудинок менший': ('Orphanage (small)', 'Waisenhaus (klein)'),
    'Садок більший': ('Kindergarten (large)', 'Kindergarten (groß)'),
    'Дитсадок середній': ('Kindergarten (medium)', 'Kindergarten (mittel)'),
    'Дитсадок менший': ('Kindergarten (small)', 'Kindergarten (klein)'),
    'Медичний університет': ('Medical university', 'Medizinische Universität'),
    'Технічний Університет більший': ('Technical university (large)', 'Technische Universität (groß)'),
    'Технічний Університет менший': ('Technical university (small)', 'Technische Universität (klein)'),
    'Пожежна частина велика': ('Fire station (large)', 'Feuerwache (groß)'),
    'Пожежна частина середня': ('Fire station (medium)', 'Feuerwache (mittel)'),
    'Пожежна частина маленька': ('Fire station (small)', 'Feuerwache (klein)'),
    'Штаб Партії великий': ('Party headquarters (large)', 'Parteizentrale (groß)'),
    'Штаб Партії маленький': ('Party headquarters (small)', 'Parteizentrale (klein)'),
    'Відділок Поліції великий': ('Police station (large)', 'Polizeiwache (groß)'),
    'Відділок Поліції малий': ('Police station (small)', 'Polizeiwache (klein)'),
    'Школа велика': ('School (large)', 'Schule (groß)'),
    'Школа середня': ('School (medium)', 'Schule (mittel)'),
    'Школа маленька': ('School (small)', 'Schule (klein)'),
    'Суд великий': ('Court (large)', 'Gericht (groß)'),
    'Суд малий': ('Court (small)', 'Gericht (klein)'),
    "В'язниця велика": ('Prison (large)', 'Gefängnis (groß)'),
    "В'язниця мала": ('Prison (small)', 'Gefängnis (klein)'),
    'Держбезпека велика': ('Secret police (large)', 'Staatssicherheit (groß)'),
    'Держбезпека мала': ('Secret police (small)', 'Staatssicherheit (klein)'),
    'Готель': ('Hotel', 'Hotel'),
    'СТО середнє': ('Technical services (medium)', 'Technischer Dienst (mittel)'),
    'СТО мале': ('Technical services (small)', 'Technischer Dienst (klein)'),
    'Станція Водопідготовка мала': ('Water treatment plant (small)', 'Wasseraufbereitung (klein)'),
    'Станція Водопідготовка велика': ('Water treatment plant (large)', 'Wasseraufbereitung (groß)'),
    'Очисні споруди малі': ('Sewage treatment plant (small)', 'Kläranlage (klein)'),
    'Очисні споруди великі': ('Sewage treatment plant (large)', 'Kläranlage (groß)'),
    'Спирто-горіличаний завод': ('Distillery', 'Brennerei'),
    "М'ясорадгосп": ('Livestock farm', 'Viehzuchtbetrieb'),
    "М'ясокомбінат": ('Meat processing plant', 'Fleischfabrik'),
}


def obj_name(key, entry=None):
    """building name in the current UI language: the user's own translation, else the template's, else the key"""
    if L == 'uk' or not key:
        return key
    own = (entry or {}).get('names', {}).get(L)
    if own:
        return own
    t = OBJ.get(key)
    return (t[0] if L == 'en' else t[1]) if t else key


def help_html():
    return HELP.get(L, HELP['uk'])


_CSS = ('<style>h3{color:#bc0000;margin:12px 0 3px 0;} p,li{font-size:13px;color:#2d231e;margin-bottom:3px;}'
        ' ul,ol{margin:0 0 0 18px;}</style>')
HELP = {
    'uk': _CSS + """
<h3>З чого почати</h3><ol>
<li>На вкладці «Міста» натисни <b>+ Додати місто</b> [[city]], впиши назву й населення.
Без створеного міста порахувати його ресурси не вийде.</li>
<li>Розгорни місто ▸ і додай споруди [[building]] кнопкою <b>+ Додати об'єкт</b> (над списком споруд).
Впиши працівників: [[edu_c]] С — середня освіта, [[edu_b]] В — вища, одразу на 3 зміни.</li>
<li>Для підприємств натисни піпетку [[pipette]] і обведи у грі вікно будівлі — виробництво й потреби запишуться самі.</li>
<li>У рядку кожного міста праворуч від населення видно, скільки йому треба ресурсів (норма на 1000 жителів), а внизу — для всіх міст разом.</li></ol>
<h3>Вікно</h3><ul>
<li><b>Ctrl+Shift+K</b> — сховати / показати калькулятор будь-коли, навіть під час гри.</li>
<li>Закріпити на панелі задач: запусти калькулятор, права кнопка по його значку на панелі задач → «Закріпити на панелі завдань».</li>
<li>Тягни вікно за бордовий заголовок, розмір змінюй за правий нижній кут.</li>
<li>[[minus]] — згорнути на панель задач, як звичайне вікно Windows; розгортаєш кліком по значку на панелі задач.</li>
<li>[[pin_on]] — калькулятор закріплений поверх усіх вікон і гри; [[pin_off]] — звичайне вікно. Клік перемикає.</li>
<li>[[help]] — ця інструкція; [[close]] — закрити (усе зберігається автоматично).</li>
<li>Гра має бути у віконному режимі або «вікно без рамки», інакше калькулятор поверх неї не видно.</li>
<li>Мова: УКР / ENG / DEU праворуч над таблицею. Назви споруд теж перекладаються.</li>
<li>Значок калькулятора в треї Windows (біля годинника): клік — сховати / показати, права кнопка — меню.</li>
<li>Видалив місто чи об'єкт помилково — <b>Скасувати</b> у смужці внизу або <b>Ctrl+Z</b>.
Щодня програма робить копію даних у папці <b>backups</b> (останні 14 днів).</li>
<li>[[save]] під перемикачем мови — зберегти все в таблицю Excel (.xlsx): міста, баланс ресурсів, норми на 1000 жителів,
мої об'єкти — за вибраний період і поточною мовою.</li>
<li>Коли мишка зупиняється над калькулятором, він забирає фокус у гри — кліки й колесо не йдуть у гру.
Мишка, що просто пролітає над ним, гру не чіпає. Якщо нічого не натиснув, фокус повертається грі.</li></ul>
<h3>Вкладка «Міста»</h3><ul>
<li>▸ біля назви розгортає місто; [[trash]] — видалити місто (під мишкою стає [[trash_red]]); ✕ — прибрати споруду.</li>
<li>Назву споруди вибирай зі списку або впиши нову й натисни Enter — програма запам'ятає її цифри.</li>
<li>Унизу міста — підсумки на 1 і на 3 зміни: [[edu_c]] С, [[edu_b]] В, [[total]] разом.
Перемикач <b>1 зміна / 3 зміни</b> показує людей на одну або на три зміни; перемикач <b>за трудодень / за місяць / за рік</b> показує виробництво й потреби за вибраний період. У самому низу — підсумки всіх міст і населення [[city]].</li>
<li><b>Додатково ▸</b> у місті: будинки для С і В; зупинки — 1–2 на кожну посадку (жителів на посадку) і 1–2 на кожне підприємство (впиши їх кількість).</li>
<li>Поля — це об'єкти «Поле мале / середнє / велике»: у колонці К-сть — кількість полів, урожай рахується за рік.
Кнопка [[fertiliser]] у рядку поля перемикає <b>з добривами / без</b>: з добривами — більший урожай і добрива в потребах, без — менший урожай і без потреб.</li><li>Іконка карти [[map]] поруч із кошиком [[trash]] у заголовку міста відкриває вкладку <b>Planner</b> саме з цим містом.</li></ul>
<h3>Вкладка «Planner»</h3><ul>
<li>[[map]] Планувальник міста на карті 20 000 × 20 000 м. Список міст — той самий, що на вкладці «Міста» [[city]]; у кожного міста своя карта.</li>
<li>[[plate_blue]] Праворуч <b>Бібліотека</b>: клік по блоку ставить його на карту (міські зони, транспорт, електро вузли, дороги, колії, річки, електромережа, текст). Ліворуч у <b>Блоках</b> — лише блоки вибраного міста: клік виділяє блок, ▸ відкриває налаштування (блоки з'являються згорнутими), [[eye]] ховає.</li>
<li>Кнопка [[plus]] біля «Бібліотека» додає свою іконку: назва, колір фону й картинка. Біля доданих іконок є кошик [[trash]] — видалити зі списку. Є [[plate_red]] «Станція метро» і [[plate_purple]] «Лінія метро».</li>
<li>Тягни блок мишкою; Ctrl/Shift+клік — кілька блоків, Shift+рамка або Ctrl+A — виділити всі. Поворот: кнопки ⟲ / ⟳ 90°, довільний кут, ручка повороту або клавіша <b>R</b>.</li>
<li>Перемикачі: сітка, прив'язка до сітки, магніт блоків, метри. Колесо — масштаб, середня/права кнопка або тло — переміщення.</li>
<li>Ctrl+Z скасовує дію на карті. [[save]] <b>Зберегти PNG</b> / <b>Зберегти PDF</b> — експорт карти. Мова карти змінюється разом з мовою програми, усе зберігається автоматично.</li></ul>
<h3>Піпетка [[pipette]]</h3><ul>
<li>Натисни піпетку в рядку споруди й обведи мишкою вікно будівлі в грі разом з рядками
«Maximum production per workday» і «Consumption at maximum production». Esc — скасувати.</li>
<li>Виробництво й потреби одразу записуються в рядок: значення за трудодень × 365.
Вода [[water]] й електроенергія [[eletric]] не рахуються.</li>
<li>Якщо обвести й рядки «Поточне число трудівників / інженерів», піпетка запише людей: трудівники → [[edu_c]] С, інженери → [[edu_b]] В, × 3 зміни.</li>
<li>Унизу з'являється смужка з тим, що записано; <b>Перевірити</b> — виправити вручну.</li>
<li>Продуктивність % і кількість будівель у рядку перераховують виробництво й потреби.
Кнопки «Виробництво» і «Потреби» — ручний ввід: число <b>за одну зміну (1 трудодень)</b>, як у вікні гри; місяць і рік програма рахує сама.</li></ul>
<h3>Вкладка «Мої об'єкти»</h3><ul>
<li>Список усіх споруд [[building]]: назва, виробництво, потреби, [[edu_c]] С і [[edu_b]] В — на 1 будівлю, люди на 3 зміни.</li>
<li>Зміни тут одразу оновлюють цю споруду в усіх містах; у містах кількість «×» множить людей і ресурси.</li>
<li>Піпетка [[pipette]] працює і тут; <b>+ Додати об'єкт</b> (зверху) — нова споруда внизу списку, ✕ — прибрати зі списку.
Дві однакові назви програма не дозволить.</li>
<li><b>Пошук…</b> — фільтр за назвою. Клік по <b>Назва</b> — за алфавітом ▼, ще клік — навпаки ▲, ще клік — твій порядок;
так само <b>Разом</b> — за кількістю людей. Заголовки таблиці лишаються на місці під час прокрутки.</li>
<li>Іконка зліва [[building]] — клік: будівля або ресурс з гри, або своя картинка PNG (стане 48×48, як іконки гри).
Іконка показується й у рядках міст.</li>
<li>Перемикач <b>1 зміна / 3 зміни</b> працює і тут. Англійську й німецьку назви можна виправити: перемкни мову й переіменуй.</li></ul>
<h3>Калькулятор населення і ресурси на 1000 жителів</h3><ul>
<li>Зліва від дискети — калькулятор: впиши будь-яку кількість жителів, і під ним з'явиться, скільки потрібно ресурсів:
[[eletronics]] електроніка, [[food]] хліб, [[meat]] м'ясо, [[clothes]] одяг, [[alcohol]] алкоголь,
а також [[eletric]] [[water]] [[usagewater]] [[waste_mixed]] [[heat]] комунальні (коли для них задана норма). Хрестик ✕ у вікні результату скидає число до нуля.</li>
<li><b>?</b> — формула розрахунку з поточними числами. <b>✎</b> — внести свої норми на 1000 жителів (за рік); нуль — ресурс не показується.</li>
<li>Перемикач <b>за трудодень / за місяць / за рік</b> міняє період і для калькулятора, і для рядків міст.</li></ul>
""",
    'en': _CSS + """
<h3>Getting started</h3><ol>
<li>On the «Cities» tab click <b>+ Add city</b> [[city]], type its name and population.
A city has to exist before its resources can be calculated.</li>
<li>Expand the city ▸ and add buildings [[building]] with <b>+ Add building</b>.
Enter workers: [[edu_c]] S — secondary education, [[edu_b]] H — higher, already for 3 shifts.</li>
<li>For factories click the pipette [[pipette]] and outline the building window in the game — production and needs are filled in.</li>
<li>In every city row, right of the population, you see what the city needs (rates per 1000 residents); at the bottom — for all cities together.</li></ol>
<h3>Window</h3><ul>
<li><b>Ctrl+Shift+K</b> — hide / show the calculator at any time, also while playing.</li>
<li>Pin to the taskbar: start the calculator, right-click its taskbar icon → «Pin to taskbar».</li>
<li>Drag the window by the maroon title bar, resize it from the bottom-right corner.</li>
<li>[[minus]] — minimize to the taskbar like any Windows window; click its taskbar icon to restore it.</li>
<li>[[pin_on]] — the calculator stays on top of all windows and the game; [[pin_off]] — a normal window. Click to switch.</li>
<li>[[help]] — these instructions; [[close]] — close (everything is saved automatically).</li>
<li>The game must run in windowed or borderless mode, otherwise the calculator is not visible over it.</li>
<li>Language: УКР / ENG / DEU above the table on the right. Building names are translated too.</li>
<li>The calculator icon in the Windows tray (by the clock): click — hide / show, right click — menu.</li>
<li>Deleted a city or a building by mistake — <b>Cancel</b> in the note at the bottom or <b>Ctrl+Z</b>.
Every day the program keeps a copy of the data in <b>backups</b> (the last 14 days).</li>
<li>[[save]] under the language switch — save everything as an Excel spreadsheet (.xlsx): cities, resource balance,
needs per 1000 residents, my buildings — for the chosen period, in the current language.</li>
<li>When the mouse stops over the calculator it takes the focus from the game — clicks and the wheel do not reach the game.
A mouse just passing over does not touch the game. If nothing was clicked, the game gets its focus back.</li></ul>
<h3>«Cities» tab</h3><ul>
<li>▸ next to the name expands the city; [[trash]] deletes the city (turns [[trash_red]] under the mouse); ✕ removes a building.</li>
<li>Pick a building name from the list or type a new one and press Enter — its numbers are remembered.</li>
<li>The city footer shows totals for 1 and 3 shifts: [[edu_c]] S, [[edu_b]] H, [[total]] total.
The <b>1 shift / 3 shifts</b> switch shows people for one or three shifts; the <b>per workday / per month / per year</b> switch shows production and needs for that period. At the very bottom: totals of all cities and the population [[city]].</li>
<li><b>Extra ▸</b> in a city: housing for S and H workers; bus stops — 1–2 per boarding place (residents per place) and 1–2 per enterprise (enter how many).</li>
<li>Fields are the buildings «Small / Medium / Big field»: Count = number of fields, the harvest is per year.
The [[fertiliser]] button in a field row switches <b>with / without fertilizer</b>: with — bigger harvest and fertilizer in the needs, without — smaller harvest, no needs.</li><li>The map icon [[map]] next to the trash can [[trash]] in a city header opens the <b>Planner</b> tab with that very city.</li></ul>
<h3>«Planner» tab</h3><ul>
<li>[[map]] City planner on a 20,000 × 20,000 m map. The city list is the same as on the «Cities» tab [[city]]; every city has its own map.</li>
<li>[[plate_blue]] <b>Library</b> on the right: click a block to place it on the map (city zones, transport, power nodes, roads, rails, rivers, power grid, text). <b>Blocks</b> on the left lists only the selected city's blocks: click selects, ▸ opens settings (blocks appear collapsed), [[eye]] hides.</li>
<li>The [[plus]] button next to «Library» adds your own icon: name, background color and an image. Added icons get a trash can [[trash]] to remove them. There is a [[plate_red]] «Metro station» and a [[plate_purple]] «Metro line».</li>
<li>Drag blocks with the mouse; Ctrl/Shift+click for several, Shift+box or Ctrl+A to select all. Rotate with the ⟲ / ⟳ 90° buttons, a free angle, the rotation handle or the <b>R</b> key.</li>
<li>Switches: grid, snap to grid, block magnet, meters. Wheel zooms; middle/right button or background pans.</li>
<li>Ctrl+Z undoes on the map. [[save]] <b>Save PNG</b> / <b>Save PDF</b> export the map. The map language follows the app language; everything is saved automatically.</li></ul>
<h3>Pipette [[pipette]]</h3><ul>
<li>Click the pipette in a building row and drag around the building window in the game, including the lines
«Maximum production per workday» and «Consumption at maximum production». Esc cancels.</li>
<li>Production and needs go straight into the row: value per workday × 365. Water [[water]] and electricity [[eletric]] are not counted.</li>
<li>Include the lines «Current number of workers / engineers» and the pipette fills in people: workers → [[edu_c]] S, engineers → [[edu_b]] H, × 3 shifts.</li>
<li>A note at the bottom shows what was written; <b>Check</b> lets you correct it.</li>
<li>Productivity % and the number of buildings in the row rescale production and needs.
The «Production» and «Needs» buttons — manual entry: the number <b>for one shift (1 workday)</b>, as in the game window; month and year are calculated.</li></ul>
<h3>«My buildings» tab</h3><ul>
<li>All your buildings [[building]]: name, production, needs, [[edu_c]] S and [[edu_b]] H — for 1 building, people for 3 shifts.</li>
<li>Changes here update this building in every city at once; in cities the «×» count multiplies people and resources.</li>
<li>The pipette [[pipette]] works here too; <b>+ Add building</b> — a new one, ✕ — remove it from the list.</li>
<li><b>Search…</b> filters by name. Click <b>Name</b> — A→Z ▼, again — reverse ▲, again — your own order;
<b>Total</b> sorts by the number of people. The table header stays while scrolling. New buildings appear at the bottom;
two equal names are not allowed.</li>
<li>The icon on the left [[building]] — click to pick a game building, a game resource or your own PNG (made 48×48 like the game icons).</li>
<li>The <b>1 shift / 3 shifts</b> switch works here too. English and German names can be corrected: switch the language and rename.</li></ul>
<h3>Population calculator and resources per 1000 residents</h3><ul>
<li>Left of the save button there is a calculator: type any number of residents and below it you get the resources needed:
[[eletronics]] electronics, [[food]] bread, [[meat]] meat, [[clothes]] clothes, [[alcohol]] alcohol,
and [[eletric]] [[water]] [[usagewater]] [[waste_mixed]] [[heat]] utilities (once a rate is set for them). The ✕ in the result window resets the number to zero.</li>
<li><b>?</b> — the calculation formula with the current numbers. <b>✎</b> — enter your own rates per 1000 residents (per year); zero — the resource is not shown.</li>
<li>The <b>per workday / per month / per year</b> switch changes the period for the calculator and for the city rows.</li></ul>
""",
    'de': _CSS + """
<h3>Erste Schritte</h3><ol>
<li>Im Reiter «Städte» auf <b>+ Stadt hinzufügen</b> [[city]] klicken, Namen und Einwohnerzahl eintragen.
Ohne angelegte Stadt lassen sich ihre Ressourcen nicht berechnen.</li>
<li>Stadt mit ▸ ausklappen und Gebäude [[building]] mit <b>+ Gebäude hinzufügen</b> anlegen.
Arbeiter eintragen: [[edu_c]] M — mittlere Bildung, [[edu_b]] H — Hochschulbildung, bereits für 3 Schichten.</li>
<li>Für Betriebe die Pipette [[pipette]] anklicken und im Spiel das Gebäudefenster umranden — Produktion und Bedarf werden eingetragen.</li>
<li>In jeder Stadtzeile rechts neben den Einwohnern steht, was die Stadt braucht (Raten pro 1000 Einwohner); unten — für alle Städte zusammen.</li></ol>
<h3>Fenster</h3><ul>
<li><b>Strg+Umschalt+K</b> — Rechner jederzeit aus- / einblenden, auch im Spiel.</li>
<li>An die Taskleiste anheften: Rechner starten, Rechtsklick auf sein Symbol in der Taskleiste → «An Taskleiste anheften».</li>
<li>Fenster an der dunkelroten Titelleiste ziehen, Größe unten rechts ändern.</li>
<li>[[minus]] — in die Taskleiste minimieren wie jedes Windows-Fenster; Klick auf das Taskleistensymbol stellt es wieder her.</li>
<li>[[pin_on]] — der Rechner bleibt über allen Fenstern und dem Spiel; [[pin_off]] — normales Fenster. Klick schaltet um.</li>
<li>[[help]] — diese Anleitung; [[close]] — schließen (alles wird automatisch gespeichert).</li>
<li>Das Spiel muss im Fenster- oder randlosen Modus laufen, sonst ist der Rechner darüber nicht sichtbar.</li>
<li>Sprache: УКР / ENG / DEU rechts über der Tabelle. Gebäudenamen werden mit übersetzt.</li>
<li>Rechner-Symbol im Windows-Infobereich (bei der Uhr): Klick — aus- / einblenden, Rechtsklick — Menü.</li>
<li>Stadt oder Gebäude versehentlich gelöscht — <b>Abbrechen</b> in der Leiste unten oder <b>Strg+Z</b>.
Jeden Tag legt das Programm eine Kopie der Daten in <b>backups</b> ab (die letzten 14 Tage).</li>
<li>[[save]] unter der Sprachwahl — alles als Excel-Tabelle (.xlsx) speichern: Städte, Ressourcenbilanz, Bedarf pro 1000 Einwohner,
meine Gebäude — für den gewählten Zeitraum, in der aktuellen Sprache.</li>
<li>Bleibt die Maus über dem Rechner stehen, holt er sich den Fokus vom Spiel — Klicks und Mausrad gehen nicht ins Spiel.
Nur darüber hinweg bewegt: das Spiel bleibt unberührt. Ohne Klick bekommt das Spiel den Fokus zurück.</li></ul>
<h3>Reiter «Städte»</h3><ul>
<li>▸ neben dem Namen klappt die Stadt aus; [[trash]] löscht die Stadt (unter der Maus [[trash_red]]); ✕ entfernt ein Gebäude.</li>
<li>Gebäudenamen aus der Liste wählen oder neu eintippen und Enter drücken — seine Zahlen werden gemerkt.</li>
<li>Unten in der Stadt stehen Summen für 1 und 3 Schichten: [[edu_c]] M, [[edu_b]] H, [[total]] gesamt.
Der Schalter <b>1 Schicht / 3 Schichten</b> zeigt das Personal für eine oder drei Schichten; der Schalter <b>pro Arbeitstag / pro Monat / pro Jahr</b> zeigt Produktion und Bedarf für diesen Zeitraum. Ganz unten: Summen aller Städte und die Einwohnerzahl [[city]].</li>
<li><b>Extras ▸</b> in einer Stadt: Wohngebäude; Haltestellen — 1–2 pro Einstiegsort (Einwohner pro Ort) und 1–2 pro Betrieb (Anzahl eintragen).</li>
<li>Felder sind die Gebäude «Kleines / Mittleres / Großes Feld»: Anzahl = Zahl der Felder, die Ernte gilt pro Jahr.
Die Taste [[fertiliser]] in der Feldzeile schaltet <b>mit / ohne Dünger</b>: mit — größere Ernte und Dünger im Bedarf, ohne — kleinere Ernte, kein Bedarf.</li><li>Das Kartensymbol [[map]] neben dem Papierkorb [[trash]] im Stadtkopf öffnet den Reiter <b>Planner</b> mit genau dieser Stadt.</li></ul>
<h3>Reiter «Planner»</h3><ul>
<li>[[map]] Stadtplaner auf einer Karte von 20 000 × 20 000 m. Die Städteliste ist dieselbe wie im Reiter «Städte» [[city]]; jede Stadt hat ihre eigene Karte.</li>
<li>[[plate_blue]] <b>Bibliothek</b> rechts: Klick auf einen Block setzt ihn auf die Karte (Stadtzonen, Verkehr, Stromknoten, Straßen, Gleise, Flüsse, Stromnetz, Text). <b>Blöcke</b> links zeigt nur die Blöcke der gewählten Stadt: Klick wählt aus, ▸ öffnet die Einstellungen (Blöcke erscheinen eingeklappt), [[eye]] blendet aus.</li>
<li>Die Taste [[plus]] neben «Bibliothek» fügt ein eigenes Symbol hinzu: Name, Hintergrundfarbe und Bild. Hinzugefügte Symbole haben einen Papierkorb [[trash]] zum Entfernen. Es gibt eine [[plate_red]] «U-Bahn-Station» und eine [[plate_purple]] «U-Bahn-Linie».</li>
<li>Blöcke mit der Maus ziehen; Strg/Shift+Klick für mehrere, Shift+Rahmen oder Strg+A wählt alle. Drehen: Tasten ⟲ / ⟳ 90°, freier Winkel, Drehgriff oder Taste <b>R</b>.</li>
<li>Schalter: Raster, Rasterfang, Blockmagnet, Meter. Mausrad zoomt; mittlere/rechte Taste oder Hintergrund verschiebt.</li>
<li>Strg+Z macht auf der Karte rückgängig. [[save]] <b>PNG speichern</b> / <b>PDF speichern</b> exportieren die Karte. Die Kartensprache folgt der Programmsprache; alles wird automatisch gespeichert.</li></ul>
<h3>Pipette [[pipette]]</h3><ul>
<li>Pipette in einer Gebäudezeile anklicken und im Spiel das Gebäudefenster samt den Zeilen
«Maximum production per workday» und «Consumption at maximum production» umranden. Esc bricht ab.</li>
<li>Produktion und Bedarf werden direkt in die Zeile geschrieben: Wert pro Arbeitstag × 365.
Wasser [[water]] und Strom [[eletric]] werden nicht gezählt.</li>
<li>Mit den Zeilen «Aktuelle Zahl der Arbeiter / Ingenieure» trägt die Pipette auch das Personal ein: Arbeiter → [[edu_c]] M, Ingenieure → [[edu_b]] H, × 3 Schichten.</li>
<li>Unten erscheint ein Hinweis mit dem Ergebnis; <b>Prüfen</b> erlaubt Korrekturen.</li>
<li>Produktivität % und Anzahl der Gebäude in der Zeile rechnen Produktion und Bedarf um.
Die Knöpfe «Produktion» und «Bedarf» — Eingabe von Hand: Zahl <b>für eine Schicht (1 Arbeitstag)</b>, wie im Spielfenster; Monat und Jahr werden berechnet.</li></ul>
<h3>Reiter «Meine Gebäude»</h3><ul>
<li>Alle Gebäude [[building]]: Name, Produktion, Bedarf, [[edu_c]] M und [[edu_b]] H — für 1 Gebäude, Personal für 3 Schichten.</li>
<li>Änderungen hier gelten sofort für dieses Gebäude in allen Städten; in den Städten multipliziert die Anzahl «×» Personal und Ressourcen.</li>
<li>Die Pipette [[pipette]] funktioniert auch hier; <b>+ Gebäude hinzufügen</b> — neues Gebäude, ✕ — aus der Liste entfernen.</li>
<li><b>Suchen…</b> filtert nach Name. Klick auf <b>Name</b> — A→Z ▼, nochmal — umgekehrt ▲, nochmal — eigene Reihenfolge;
<b>Gesamt</b> sortiert nach Personenzahl. Die Kopfzeile bleibt beim Scrollen stehen. Neue Gebäude erscheinen unten;
zwei gleiche Namen sind nicht erlaubt.</li>
<li>Symbol links [[building]] — Klick: Spielgebäude, Spielressource oder eigenes PNG (wird 48×48 wie die Spielsymbole).</li>
<li>Der Schalter <b>1 Schicht / 3 Schichten</b> gilt auch hier. Englische und deutsche Namen lassen sich korrigieren: Sprache wechseln und umbenennen.</li></ul>
<h3>Bevölkerungsrechner und Ressourcen pro 1000 Einwohner</h3><ul>
<li>Links neben dem Speichern-Knopf steht ein Rechner: beliebige Einwohnerzahl eintragen, darunter erscheint der Bedarf:
[[eletronics]] Elektronik, [[food]] Brot, [[meat]] Fleisch, [[clothes]] Kleidung, [[alcohol]] Alkohol,
und [[eletric]] [[water]] [[usagewater]] [[waste_mixed]] [[heat]] Versorgung (sobald eine Rate gesetzt ist). Das ✕ im Ergebnisfenster setzt die Zahl auf null zurück.</li>
<li><b>?</b> — die Berechnungsformel mit den aktuellen Zahlen. <b>✎</b> — eigene Raten pro 1000 Einwohner (pro Jahr) eintragen; Null — die Ressource wird nicht angezeigt.</li>
<li>Der Schalter <b>pro Arbeitstag / pro Monat / pro Jahr</b> ändert den Zeitraum für den Rechner und die Stadtzeilen.</li></ul>
""",
}

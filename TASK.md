Zadanie rekrutacyjne: Python Developer

Zaimplementuj proste API dla systemu informatycznego biblioteki. Wyobraź sobie, że API
będzie używane przez pracowników biblioteki do śledzenia i aktualizowania stanu
posiadanych przez bibliotekę książek. O każdej książce przechowujemy takie informacje jak:

- unikalny numer seryjny (wprowadzany przez pracownika, w formie sześciocyfrowej
  liczby)
- tytuł,
- autor,
- oraz czy jest obecnie wypożyczona, kiedy i kto ją wypożyczył (wypożyczający
  posiadają sześciocyfrowe numery karty bibliotecznej)
  API powinno umożliwiać:
- Dodanie nowej książki
- Usunięcie książki
- Pobranie listy wszystkich książek
- Aktualizację stanu książki: wypożyczona / dostępna
  Na potrzeby zadania, pomijamy uwierzytelnianie i autoryzację użytkowników.
  Rozwiązanie może zostać zaimplementowane za pomocą dowolnego frameworka / biblioteki
  sieciowej języka Python oraz powinno być dostarczone razem ze skryptem docker-compose.
  Wywołanie polecenia docker compose up powinno skutkować uruchomieniem działającej
  aplikacji. Jako bazy danych użyj PostgreSQL. Wybór reszty stosu technicznego jest
  dowolny.
  Rozwiązanie dostarcz w formie linku do publicznego repozytorium git (dowolny hosting).
  Powodzenia!

# ThunderTruth

Стратегическая игра булевыми операторами
против могучего Зевса.

## Установка консольной версии (v1.0)
### Вариант 1. Через Docker-образ.
1. Убедитесь, что у вас установлен [Docker](https://docs.docker.com/get-docker/).<br>
Для Windows также: установить [Windows Terminal](https://apps.microsoft.com/detail/9n0dx20hk701?hl=en-US&gl=US)
2. Создайте директорию с файлами-настройками: <br>
#### Mac OS
```
mkdir -p app/
touch app/.env
touch app/game.log
```
#### Windows
Через CMD:
```
mkdir app 2>nul
echo. > app\.env
echo. > app\game.log
```
3. Запустите Docker Dekstop и Docker-контейнер
#### Mac OS
```
docker run -it \
  -v ./app/.env:/app/.env \
  -v ./app/game.log:/app/game.log \
  ghcr.io/kaelteritter/thundertruth:latest
```
#### Windows
Через Windows Terminal (Win+R -> wt):
```
$newPath = Get-Location | Select-Object -ExpandProperty Path
docker run -it `
  -v "$newPath\app\.env:/app/.env" `
  -v "$newPath\app\game.log:/app/game.log" `
  ghcr.io/kaelteritter/thundertruth:latest
```
**Примечание**: не забудьте поменять [настройки](#настройки-игры) для
правильного вывода логов, размера доски и пр.

### Вариант 2. Через виртуальное окружение
> Внимание для пользователей Windows! Символы токенов отображаются в кодировке UTF-8. 
Интерфейс был протестирован на удаленном сервере с соверменной Windows в оболочке cmd.
В старых версиях cmd.exe utf-8 плохо интегрируется и не всегда передает кириллические символы и цвета.
В случае неправильного отображения попробуйте использовать powershell или [Windows Terminal](https://apps.microsoft.com/detail/9n0dx20hk701?hl=en-US&gl=US).
Или используйте вариант установки [Docker + Windows Terminal](#вариант-1-через-docker-образ) (протестировано вручную).

1. Клонировать репозиторий: <br>
```
git clone https://github.com/kaelteritter/ThunderTruth.git
```
2. Создать и активировать виртуальное окружение:
> **MacOS:**
```
python3 -m venv venv
source venv/bin/activate
```
> **Windows:**
```
python -m venv venv
.venv\Scripts\activate
```
3. Установить зависимости: 
```
pip install -r requirements.txt
```
4. Запустить скрипт из рабочей директории:
> **MacOS:**
```
python3 -m core.main
```
> **Windows:**
```
python -m core.main
```

## Настройки игры
Чтобы кастомизировать параметры игры нужно:
1) Открыть файл .env в рабочей директории
2) Заменить переменные вида VAR=VALUE на нужные в том же формате

###  Значение переменных
**DEBUG**: Режим разработки `True/False`- устанавливает уровень логгирования (DEBUG/WARNING) <br>
По умолчанию: `False` <br>
**PRODUCTION**: Режим продашкна `True/False` - выводит логи в отдельный файл/в консоль <br>
По умолчанию: `True` <br>
**BOARD_SIZE**: Размер игровой доски <br>
По умолчанию: `5` <br>
**INITIAL_TOKENS**: Начальное количество токенов 
По умолчанию: `4` <br>
**PLAYERS_AMOUNT**: Количество игроков (рекомендуется оставить значение по умолчнию до обновления) <br>
По умолчанию: `2` <br>
**AI_OPPONENT_DEFAULT**: Имя ИИ-соперника <br>
По умолчанию: `Зевс` <br>


## Разработка
- Tестирование: Unittest, GitHub Actions
- Контейниризация: Docker-образ на [ghcr.io](https://github.com/kaelteritter/ThunderTruth/pkgs/container/thundertruth)
- Стиль кода: PEP 8
- Зависимости: Указаны в `requirements.txt`

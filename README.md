
# Структура готового проекта

RBuilder - Основная директория приложения
    -- Папки:
    VM - рабочая директория виртуальной машины
    loader - исходники загрузчика
    preload - исходники критически важных компонентов API
    -- Файлы:
    rb.exe - главный исполняемый файл
    config.yml - файл конфигурации

При сборке VM происходит следующее:
- Создается `mpmissions\loader.vr.pbo` - это основной загрузчик, своего рода точка входа при запуске.
- Создается папка `preload` - в ней расположены инициализаторы сторонних компонентов, используемых в билде.
- В папке preload генерируется `rbuilder.h`, со списокм дефайнов из файла конфигурации `config.yml`

При сборке исходников:
- В корневой директории создается папка src.

# Принцип работы

1. Выполняется сборка виртуальной машины
2. Загружаются исходники в директорию виртуальной машины
3. Выполнение кода, валидация или иные действия

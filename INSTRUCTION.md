# Amazing Automata - Инструкция по применению

## Обзор

Amazing Automata - универсальная система для автоматической генерации CI/CD пайплайнов. Анализирует структуру проекта, определяет используемые технологии и создает соответствующие пайплайны.

## Установка

```bash
pip3 install -r requirements.txt
```

## Использование

### Анализ проекта
```bash
python3 amazing_automata.py analyze ./my-project
```

### Генерация пайплайна
```bash
python3 amazing_automata.py generate ./my-project --platform github-actions
```

### С деплоем
```bash
python3 amazing_automata.py generate ./my-project --platform github-actions --deploy
```

## Поддерживаемые платформы

- `github-actions` - GitHub Actions
- `gitlab-ci` - GitLab CI  
- `jenkins` - Jenkins
- `azure-devops` - Azure DevOps
- `circleci` - CircleCI

## Примеры

### React приложение
```bash
python3 amazing_automata.py generate /path/to/your/react-project --platform github-actions
```

### Node.js API
```bash
python3 amazing_automata.py generate /path/to/your/nodejs-project --platform gitlab-ci
```

### Python Django
```bash
python3 amazing_automata.py generate /path/to/your/django-project --platform github-actions
```

### Любой проект
```bash
python3 amazing_automata.py generate /path/to/any/project --platform github-actions
```

## Результаты

- **100% автоматизация** - никаких ручных настроек
- **Универсальность** - работает с любыми проектами
- **Скорость** - 30 секунд vs 2-4 часа ручной работы
- **Интеллектуальность** - анализ сложности и рекомендации

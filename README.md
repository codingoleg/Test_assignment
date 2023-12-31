# Test_assignment

## Installation

1. Клонируйте репозиторий:

```bash
git clone https://github.com/codingoleg/Test_assignment.git
```

2. Перейдите в папку проекта:

```bash
cd .\Test_assignment\
```

+ Если в Windows используется Hyper-V вместо WSL, для создания volumes нужно добавить путь проекта в Docker по
  инструкции: https://stackoverflow.com/questions/62215781/docker-compose-failed-to-build-filesharing-has-been-cancelled-eshoponcontain
+ Запустите docker-compose:

```bash
docker-compose up
```

## Usage
+ Все пути и параметры такие же, как в описании задания.

## About
+ Тестовый пользователь создается при подключении к БД. Параметры (ID, email) задаются через config.py и переменные
окружения.
+ Тестовой почтой outlook, указанной в переменных окружения, можно пользоваться из коробки, но при определенном 
количестве и/или частоте отправлений, ее могут заблокировать.
+ Для быстрого поиска по уведомлениям и для ограничения количества документов создаются две отдельные коллекции - для 
пользователя и для уведомлений. 
+ Количество документов в коллекции с уведомлениями ограничено переменной NOTIFICATION_LIMIT. Каждый последующий 
документ будет перезаписывать предыдущий, начиная с самого старого.
+ [GET] /list:
+ + если не задан 'skip', то 'skip' = 0
+ + если не задан 'limit' или значение 'limit' > NOTIFICATION_LIMIT, то 'limit' = NOTIFICATION_LIMIT
+ [POST] /create:
+ + 'notification_id' принимает значение 0 или 1 в тестовых целях и для удобного последующего запроса [POST]
/read с выбором 0 или 1.
+ + если не указан 'target_id', он добавляется в любом случае и имеет строковое значение id документа, 
который присвоил ему автоматически MongoDB.
+ Валидность входящих данных (типы, значения) обеспечивается pydantic. При возникновении ошибок, возвращается json c 
описанием.

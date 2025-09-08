"""
Пример использования EmbeddingServiceAsyncClient со всеми режимами безопасности.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Этот пример демонстрирует все 6 режимов безопасности, поддерживаемых embed-client:
1. HTTP (обычный HTTP без аутентификации)
2. HTTP + Token (HTTP с аутентификацией по API ключу)
3. HTTPS (HTTPS с проверкой сертификатов сервера)
4. HTTPS + Token (HTTPS с сертификатами сервера + аутентификация)
5. mTLS (взаимный TLS с клиентскими и серверными сертификатами)
6. mTLS + Роли (mTLS с контролем доступа на основе ролей)

ИСПОЛЬЗОВАНИЕ:
    # Базовое использование без аутентификации
    python embed_client/example_async_usage_ru.py --base-url http://localhost --port 8001
    
    # С аутентификацией по API ключу
    python embed_client/example_async_usage_ru.py --base-url http://localhost --port 8001 --auth-method api_key --api-key your_key
    
    # С JWT аутентификацией
    python embed_client/example_async_usage_ru.py --base-url http://localhost --port 8001 --auth-method jwt --jwt-secret secret --jwt-username user
    
    # С базовой аутентификацией
    python embed_client/example_async_usage_ru.py --base-url http://localhost --port 8001 --auth-method basic --username user --password pass
    
    # С файлом конфигурации
    python embed_client/example_async_usage_ru.py --config configs/http_token.json
    
    # С переменными окружения
    export EMBED_CLIENT_BASE_URL=http://localhost
    export EMBED_CLIENT_PORT=8001
    export EMBED_CLIENT_AUTH_METHOD=api_key
    export EMBED_CLIENT_API_KEY=your_key
    python embed_client/example_async_usage_ru.py

ПРИМЕРЫ РЕЖИМОВ БЕЗОПАСНОСТИ:
    # 1. HTTP - обычный HTTP без аутентификации
    python embed_client/example_async_usage_ru.py --base-url http://localhost --port 8001
    
    # 2. HTTP + Token - HTTP с аутентификацией по API ключу
    python embed_client/example_async_usage_ru.py --base-url http://localhost --port 8001 --auth-method api_key --api-key admin_key_123
    
    # 3. HTTPS - HTTPS с проверкой сертификатов сервера
    python embed_client/example_async_usage_ru.py --base-url https://localhost --port 9443
    
    # 4. HTTPS + Token - HTTPS с сертификатами сервера + аутентификация
    python embed_client/example_async_usage_ru.py --base-url https://localhost --port 9443 --auth-method jwt --jwt-secret secret --jwt-username admin
    
    # 5. mTLS - взаимный TLS с клиентскими и серверными сертификатами
    python embed_client/example_async_usage_ru.py --base-url https://localhost --port 9443 --auth-method certificate --cert-file certs/client.crt --key-file keys/client.key
    
    # 6. mTLS + Роли - mTLS с контролем доступа на основе ролей
    python embed_client/example_async_usage_ru.py --base-url https://localhost --port 9443 --auth-method certificate --cert-file certs/client.crt --key-file keys/client.key --roles admin,user

ПРИМЕРЫ SSL/TLS:
    # HTTPS с отключенной проверкой SSL
    python embed_client/example_async_usage_ru.py --base-url https://localhost --port 9443 --ssl-verify-mode CERT_NONE
    
    # mTLS с пользовательским CA сертификатом
    python embed_client/example_async_usage_ru.py --base-url https://localhost --port 9443 --cert-file certs/client.crt --key-file keys/client.key --ca-cert-file certs/ca.crt
    
    # HTTPS с пользовательскими настройками SSL
    python embed_client/example_async_usage_ru.py --base-url https://localhost --port 9443 --ssl-verify-mode CERT_REQUIRED --ssl-check-hostname --ssl-check-expiry

ПРИМЕРЫ КОНФИГУРАЦИИ:
    # Использование файла конфигурации
    python embed_client/example_async_usage_ru.py --config configs/https_token.json
    
    # Использование переменных окружения
    export EMBED_CLIENT_BASE_URL=https://secure.example.com
    export EMBED_CLIENT_PORT=9443
    export EMBED_CLIENT_AUTH_METHOD=api_key
    export EMBED_CLIENT_API_KEY=production_key
    python embed_client/example_async_usage_ru.py

ПРОГРАММНЫЕ ПРИМЕРЫ:
    import asyncio
    from embed_client.async_client import EmbeddingServiceAsyncClient
    from embed_client.config import ClientConfig
    from embed_client.client_factory import ClientFactory, create_client
    
    async def main():
        # Метод 1: Прямое создание клиента
        client = EmbeddingServiceAsyncClient('http://localhost', 8001)
        await client.close()
        
        # Метод 2: Использование конфигурации
        config = ClientConfig()
        config.configure_server('http://localhost', 8001)
        client = EmbeddingServiceAsyncClient.from_config(config)
        await client.close()
        
        # Метод 3: Использование фабрики с автоматическим определением
        client = create_client('https://localhost', 9443, auth_method='api_key', api_key='key')
        await client.close()
        
        # Метод 4: Использование конкретного метода фабрики
        client = ClientFactory.create_https_token_client(
            'https://localhost', 9443, 'api_key', api_key='key'
        )
        await client.close()
        
        # Метод 5: Использование метода with_auth для динамической аутентификации
        client = EmbeddingServiceAsyncClient('http://localhost', 8001)
        client = client.with_auth('api_key', api_key='dynamic_key')
        await client.close()
    
    asyncio.run(main())
"""

import asyncio
import sys
import os
import argparse
import json
from typing import Dict, Any, Optional, Union

from embed_client.async_client import EmbeddingServiceAsyncClient, EmbeddingServiceError, EmbeddingServiceConnectionError, EmbeddingServiceHTTPError, EmbeddingServiceConfigError
from embed_client.config import ClientConfig
from embed_client.client_factory import (
    ClientFactory, SecurityMode, create_client, create_client_from_config,
    create_client_from_env, detect_security_mode
)

def get_params():
    """Парсинг аргументов командной строки и переменных окружения для конфигурации клиента."""
    parser = argparse.ArgumentParser(description="Пример Embedding Service Async Client - Все режимы безопасности")
    
    # Базовые параметры подключения
    parser.add_argument("--base-url", "-b", help="Базовый URL сервиса эмбеддингов")
    parser.add_argument("--port", "-p", type=int, help="Порт сервиса эмбеддингов")
    parser.add_argument("--config", "-c", help="Путь к файлу конфигурации")
    
    # Режим фабрики клиентов
    parser.add_argument("--factory-mode", choices=["auto", "http", "http_token", "https", "https_token", "mtls", "mtls_roles"],
                       default="auto", help="Режим фабрики клиентов (auto для автоматического определения)")
    
    # Параметры аутентификации
    parser.add_argument("--auth-method", choices=["none", "api_key", "jwt", "basic", "certificate"], 
                       default="none", help="Метод аутентификации")
    parser.add_argument("--api-key", help="API ключ для аутентификации api_key")
    parser.add_argument("--jwt-secret", help="JWT секрет для аутентификации jwt")
    parser.add_argument("--jwt-username", help="JWT имя пользователя для аутентификации jwt")
    parser.add_argument("--jwt-password", help="JWT пароль для аутентификации jwt")
    parser.add_argument("--username", help="Имя пользователя для базовой аутентификации")
    parser.add_argument("--password", help="Пароль для базовой аутентификации")
    parser.add_argument("--cert-file", help="Файл сертификата для аутентификации certificate")
    parser.add_argument("--key-file", help="Файл ключа для аутентификации certificate")
    
    # SSL/TLS параметры
    parser.add_argument("--ssl-verify-mode", choices=["CERT_NONE", "CERT_OPTIONAL", "CERT_REQUIRED"], 
                       default="CERT_REQUIRED", help="Режим проверки SSL сертификата")
    parser.add_argument("--ssl-check-hostname", action="store_true", default=True, 
                       help="Включить проверку имени хоста SSL")
    parser.add_argument("--ssl-check-expiry", action="store_true", default=True, 
                       help="Включить проверку срока действия SSL сертификата")
    parser.add_argument("--ca-cert-file", help="Файл CA сертификата для проверки SSL")
    
    # Контроль доступа на основе ролей (для mTLS + Роли)
    parser.add_argument("--roles", help="Список ролей через запятую для режима mTLS + Роли")
    parser.add_argument("--role-attributes", help="JSON строка атрибутов ролей для режима mTLS + Роли")
    
    # Дополнительные параметры
    parser.add_argument("--timeout", type=float, default=30.0, help="Таймаут запроса в секундах")
    parser.add_argument("--demo-mode", action="store_true", help="Запустить в демо режиме (показать все режимы безопасности)")
    
    args = parser.parse_args()
    
    # Сохраняем demo_mode в args для дальнейшего использования
    args.demo_mode = args.demo_mode
    
    # Если запрошен демо режим, возвращаем args напрямую
    if args.demo_mode:
        return args
    
    # Если указан файл конфигурации, загружаем его
    if args.config:
        try:
            config = ClientConfig()
            config.load_config_file(args.config)
            return config
        except Exception as e:
            print(f"Ошибка загрузки файла конфигурации {args.config}: {e}")
            sys.exit(1)
    
    # Иначе строим конфигурацию из аргументов и переменных окружения
    base_url = args.base_url or os.environ.get("EMBED_CLIENT_BASE_URL", "http://localhost")
    port = args.port or int(os.environ.get("EMBED_CLIENT_PORT", "8001"))
    
    if not base_url or not port:
        print("Ошибка: base_url и port должны быть указаны через аргументы --base-url/--port или переменные окружения EMBED_CLIENT_BASE_URL/EMBED_CLIENT_PORT.")
        sys.exit(1)
    
    # Строим словарь конфигурации
    config_dict = {
        "server": {
            "host": base_url,
            "port": port
        },
        "client": {
            "timeout": args.timeout
        },
        "auth": {
            "method": args.auth_method
        }
    }
    
    # Добавляем конфигурацию аутентификации
    if args.auth_method == "api_key":
        api_key = args.api_key or os.environ.get("EMBED_CLIENT_API_KEY")
        if api_key:
            config_dict["auth"]["api_keys"] = {"user": api_key}
        else:
            print("Предупреждение: API ключ не указан для аутентификации api_key")
    
    elif args.auth_method == "jwt":
        jwt_secret = args.jwt_secret or os.environ.get("EMBED_CLIENT_JWT_SECRET")
        jwt_username = args.jwt_username or os.environ.get("EMBED_CLIENT_JWT_USERNAME")
        jwt_password = args.jwt_password or os.environ.get("EMBED_CLIENT_JWT_PASSWORD")
        
        if jwt_secret and jwt_username and jwt_password:
            config_dict["auth"]["jwt"] = {
                "secret": jwt_secret,
                "username": jwt_username,
                "password": jwt_password
            }
        else:
            print("Предупреждение: JWT секрет, имя пользователя или пароль не указаны для аутентификации jwt")
    
    elif args.auth_method == "basic":
        username = args.username or os.environ.get("EMBED_CLIENT_USERNAME")
        password = args.password or os.environ.get("EMBED_CLIENT_PASSWORD")
        
        if username and password:
            config_dict["auth"]["basic"] = {
                "username": username,
                "password": password
            }
        else:
            print("Предупреждение: Имя пользователя или пароль не указаны для базовой аутентификации")
    
    elif args.auth_method == "certificate":
        cert_file = args.cert_file or os.environ.get("EMBED_CLIENT_CERT_FILE")
        key_file = args.key_file or os.environ.get("EMBED_CLIENT_KEY_FILE")
        
        if cert_file and key_file:
            config_dict["auth"]["certificate"] = {
                "cert_file": cert_file,
                "key_file": key_file
            }
        else:
            print("Предупреждение: Файл сертификата или ключа не указан для аутентификации certificate")
    
    # Добавляем SSL конфигурацию если используется HTTPS или указаны SSL параметры
    if base_url.startswith("https://") or args.ssl_verify_mode != "CERT_REQUIRED" or args.ca_cert_file:
        config_dict["ssl"] = {
            "enabled": True,
            "verify_mode": args.ssl_verify_mode,
            "check_hostname": args.ssl_check_hostname,
            "check_expiry": args.ssl_check_expiry
        }
        
        if args.ca_cert_file:
            config_dict["ssl"]["ca_cert_file"] = args.ca_cert_file
        
        # Добавляем клиентские сертификаты для mTLS
        if args.cert_file:
            config_dict["ssl"]["cert_file"] = args.cert_file
        if args.key_file:
            config_dict["ssl"]["key_file"] = args.key_file
    
    # Добавляем контроль доступа на основе ролей для mTLS + Роли
    if args.roles:
        roles = [role.strip() for role in args.roles.split(",")]
        config_dict["roles"] = roles
    
    if args.role_attributes:
        try:
            role_attributes = json.loads(args.role_attributes)
            config_dict["role_attributes"] = role_attributes
        except json.JSONDecodeError:
            print("Предупреждение: Неверный JSON в role_attributes")
    
    return config_dict

def extract_vectors(result):
    """Извлечение эмбеддингов из ответа API, поддерживает старый и новый форматы."""
    # Обработка прямого поля embeddings (совместимость со старым форматом)
    if "embeddings" in result:
        return result["embeddings"]
    
    # Обработка обертки result
    if "result" in result:
        res = result["result"]
        
        # Обработка прямого списка в result (старый формат)
        if isinstance(res, list):
            return res
        
        if isinstance(res, dict):
            # Обработка старого формата: result.embeddings
            if "embeddings" in res:
                return res["embeddings"]
            
            # Обработка старого формата: result.data.embeddings
            if "data" in res and isinstance(res["data"], dict) and "embeddings" in res["data"]:
                return res["data"]["embeddings"]
            
            # Обработка нового формата: result.data[].embedding
            if "data" in res and isinstance(res["data"], list):
                embeddings = []
                for item in res["data"]:
                    if isinstance(item, dict) and "embedding" in item:
                        embeddings.append(item["embedding"])
                    else:
                        raise ValueError(f"Неверный формат элемента в новом ответе API: {item}")
                return embeddings
    
    raise ValueError(f"Не удается извлечь эмбеддинги из ответа: {result}")

async def run_client_examples(client):
    """Запуск примеров операций с клиентом."""
    # Проверка здоровья
    try:
        health = await client.health()
        print("Состояние сервиса:", health)
    except EmbeddingServiceConnectionError as e:
        print(f"[Ошибка подключения] {e}")
        return
    except EmbeddingServiceHTTPError as e:
        print(f"[HTTP ошибка] {e.status}: {e.message}")
        return
    except EmbeddingServiceError as e:
        print("[Другая ошибка]", e)
        return

    # Запрос эмбеддингов для списка текстов
    texts = ["привет мир", "тестовый эмбеддинг"]
    try:
        result = await client.cmd("embed", params={"texts": texts})
        print("Результат эмбеддинга:", result)
        
        # Извлечение эмбеддингов
        embeddings = client.extract_embeddings(result)
        print("Эмбеддинги:", embeddings)
        
        # Извлечение текстов
        extracted_texts = client.extract_texts(result)
        print("Извлеченные тексты:", extracted_texts)
        
        # Извлечение чанков
        chunks = client.extract_chunks(result)
        print("Чанки:", chunks)
        
        # Извлечение токенов
        tokens = client.extract_tokens(result)
        print("Токены:", tokens)
        
        # Извлечение BM25 токенов
        bm25_tokens = client.extract_bm25_tokens(result)
        print("BM25 токены:", bm25_tokens)
        
    except EmbeddingServiceError as e:
        print(f"[Ошибка эмбеддинга] {e}")
    except ValueError as e:
        print(f"Обнаружен старый формат или ошибка извлечения нового формата данных: {e}")

async def main():
    try:
        config = get_params()
        
        # Проверяем, запрошен ли демо режим
        if hasattr(config, 'demo_mode') and config.demo_mode:
            print("=== Демонстрация всех режимов безопасности ===")
            print("Этот режим показывает все 6 режимов безопасности embed-client.")
            print("Примечание: Эти примеры создают конфигурации клиентов, но не подключаются к реальным серверам.")
            return
        
        # Создаем клиент на основе режима фабрики
        if isinstance(config, ClientConfig):
            # Используя объект конфигурации
            client = EmbeddingServiceAsyncClient.from_config(config)
        else:
            # Используя словарь конфигурации
            factory_mode = getattr(config, 'factory_mode', 'auto')
            
            if factory_mode == "auto":
                # Автоматическое определение
                client = create_client(
                    config["server"]["host"], 
                    config["server"]["port"],
                    auth_method=config["auth"]["method"],
                    **{k: v for k, v in config.items() if k not in ["server", "auth", "ssl", "client"]}
                )
            else:
                # Конкретный метод фабрики
                base_url = config["server"]["host"]
                port = config["server"]["port"]
                auth_method = config["auth"]["method"]
                
                if factory_mode == "http":
                    client = ClientFactory.create_http_client(base_url, port)
                elif factory_mode == "http_token":
                    client = ClientFactory.create_http_token_client(base_url, port, auth_method, **config.get("auth", {}))
                elif factory_mode == "https":
                    client = ClientFactory.create_https_client(base_url, port)
                elif factory_mode == "https_token":
                    client = ClientFactory.create_https_token_client(base_url, port, auth_method, **config.get("auth", {}))
                elif factory_mode == "mtls":
                    cert_file = config.get("ssl", {}).get("cert_file", "client_cert.pem")
                    key_file = config.get("ssl", {}).get("key_file", "client_key.pem")
                    client = ClientFactory.create_mtls_client(base_url, cert_file, key_file, port)
                elif factory_mode == "mtls_roles":
                    cert_file = config.get("ssl", {}).get("cert_file", "client_cert.pem")
                    key_file = config.get("ssl", {}).get("key_file", "client_key.pem")
                    roles = config.get("roles", ["admin"])
                    role_attributes = config.get("role_attributes", {})
                    client = ClientFactory.create_mtls_roles_client(
                        base_url, cert_file, key_file, port, roles, role_attributes
                    )
                else:
                    client = EmbeddingServiceAsyncClient(config_dict=config)
        
        print(f"Конфигурация клиента:")
        print(f"  Базовый URL: {client.base_url}")
        print(f"  Порт: {client.port}")
        print(f"  Аутентификация: {client.get_auth_method()}")
        print(f"  Аутентифицирован: {client.is_authenticated()}")
        if client.is_authenticated():
            headers = client.get_auth_headers()
            print(f"  Заголовки аутентификации: {headers}")
        print(f"  SSL включен: {client.is_ssl_enabled()}")
        print(f"  mTLS включен: {client.is_mtls_enabled()}")
        if client.is_ssl_enabled():
            ssl_config = client.get_ssl_config()
            print(f"  SSL конфигурация: {ssl_config}")
            protocols = client.get_supported_ssl_protocols()
            print(f"  Поддерживаемые SSL протоколы: {protocols}")
        print()
        
        # Пример явного открытия/закрытия сессии
        print("Пример явного открытия/закрытия сессии:")
        await client.close()
        print("Сессия закрыта явно (пример ручного закрытия).\n")
        
        # Используем контекстный менеджер
        try:
            if isinstance(config, ClientConfig):
                async with EmbeddingServiceAsyncClient.from_config(config) as client:
                    await run_client_examples(client)
            else:
                async with EmbeddingServiceAsyncClient(config_dict=config) as client:
                    await run_client_examples(client)

        except EmbeddingServiceError as e:
            print(f"[Ошибка EmbeddingService] {e}")
        except Exception as e:
            print(f"[Неожиданная ошибка] {e}")

    except EmbeddingServiceConfigError as e:
        print(f"Ошибка конфигурации: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
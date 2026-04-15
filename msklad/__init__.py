# При запуске приложения обновляем структуру таблиц
try:
    from stock.models import force_update_table
    force_update_table()
except Exception as e:
    print(f"Table update error: {e}")

# Автоматическое обновление таблицы при запуске
try:
    from stock.models import migrate_accesskey_table
    migrate_accesskey_table()
except Exception as e:
    print(f"Table migration error: {e}")

try:
    from stock.models import ensure_admin_key
    ensure_admin_key()
except Exception as e:
    print(f"Admin key creation error: {e}")

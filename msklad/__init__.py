# При запуске приложения обновляем структуру таблиц
try:
    from stock.models import force_update_table
    force_update_table()
except Exception as e:
    print(f"Table update error: {e}")

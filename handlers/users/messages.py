
def product_message(title, price, is_sterile, description):
    price = int(price)
    text = f"""
🏷️ <b>Наименование товара:</b> {title}
💵 <b>Цена продукта:</b> {price}-so'm
🧼 <b>Стерильный/Нестерильный</b> {is_sterile}

📝 <b>Дополнительная информация</b>

{description}


"""
    return text

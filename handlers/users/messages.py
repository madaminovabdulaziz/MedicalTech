
def product_message(title, price, is_sterile, description):
    price = int(price)
    is_sterile_text = "Стерильный" if is_sterile == "steril" else "Нестерильный"
    text = f"""
🏷️ <b>Наименование товара:</b> {title}
💵 <b>Цена продукта:</b> {price}-сум
🧼 <b>Стерильный/Нестерильный</b> {is_sterile_text}

📝 <b>Дополнительная информация</b>

{description}


"""
    return text

from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase("restaurant_menu.db")


class BaseModel(Model):
    class Meta:
        database = db


# Модели данных
class Category(BaseModel):
    name = CharField(unique=True)


class Ingredient(BaseModel):
    name = CharField(unique=True)


class Dish(BaseModel):
    name = CharField()
    price = DecimalField(max_digits=10, decimal_places=2)
    description = TextField(null=True)
    category = ForeignKeyField(Category, backref="dishes")
    ingredients = ManyToManyField(Ingredient, backref="dishes")


# Для связи многие-ко-многим
DishIngredient = Dish.ingredients.get_through_model()


# Создание таблиц
def create_tables():
    with db:
        db.create_tables([Category, Ingredient, Dish, DishIngredient])


# Для работы с меню
def print_categories():
    categories = Category.select()
    if not categories:
        print("\nКатегории отсутствуют")
        return
    print("\nКатегории меню:")
    for cat in categories:
        print(f"{cat.id}. {cat.name}")


def print_ingredients():
    ingredients = Ingredient.select()
    if not ingredients:
        print("\nИнгредиенты отсутствуют")
        return
    print("\nИнгредиенты:")
    for ing in ingredients:
        print(f"{ing.id}. {ing.name}")


def print_dishes():
    dishes = Dish.select()
    if not dishes:
        print("\nБлюда отсутствуют")
        return
    print("\nМеню ресторана:")
    for dish in dishes:
        ingredients = ", ".join([i.name for i in dish.ingredients])
        print(
            f"""
        {dish.id}. {dish.name} 
        Цена: {dish.price} ₽
        Категория: {dish.category.name}
        Ингредиенты: {ingredients}
        Описание: {dish.description or 'нет описания'}
        """
        )


def add_category():
    name = input("\nВведите название категории: ").strip()
    try:
        Category.create(name=name)
        print("Категория добавлена!")
    except IntegrityError:
        print("Ошибка: Такая категория уже существует!")


def add_ingredient():
    name = input("\nВведите название ингредиента: ").strip()
    try:
        Ingredient.create(name=name)
        print("Ингредиент добавлен!")
    except IntegrityError:
        print("Ошибка: Такой ингредиент уже существует!")


def add_dish():
    name = input("\nВведите название блюда: ").strip()
    price = input("Введите цену: ").strip()
    description = input("Введите описание (необязательно): ").strip()

    print_categories()
    category_id = input("Введите ID категории: ").strip()

    print_ingredients()
    ingredient_ids = input("Введите ID ингредиентов через запятую: ").strip().split(",")

    try:
        category = Category.get_by_id(int(category_id))
        ingredients = [Ingredient.get_by_id(int(iid.strip())) for iid in ingredient_ids]

        dish = Dish.create(
            name=name, price=price, description=description or None, category=category
        )
        dish.ingredients.add(ingredients)
        print("Блюдо добавлено в меню!")
    except DoesNotExist:
        print("Ошибка: Неверный ID категории или ингредиента!")
    except ValueError:
        print("Ошибка: Некорректный ввод данных!")


def delete_category():
    print_categories()
    cat_id = input("\nВведите ID категории для удаления: ").strip()
    try:
        cat = Category.get_by_id(int(cat_id))
        if cat.dishes.count() > 0:
            print("Ошибка: Невозможно удалить категорию с блюдами!")
            return
        cat.delete_instance()
        print("Категория удалена!")
    except DoesNotExist:
        print("Ошибка: Категория не найдена!")


def delete_ingredient():
    print_ingredients()
    ing_id = input("\nВведите ID ингредиента: ").strip()
    try:
        ing = Ingredient.get_by_id(int(ing_id))
        if ing.dishes.count() > 0:
            print("Ошибка: Ингредиент используется в блюдах!")
            return
        ing.delete_instance()
        print("Ингредиент удален!")
    except DoesNotExist:
        print("Ошибка: Ингредиент не найден!")


def delete_dish():
    print_dishes()
    dish_id = input("\nВведите ID блюда: ").strip()
    try:
        dish = Dish.get_by_id(int(dish_id))
        dish.delete_instance()
        print("Блюдо удалено из меню!")
    except DoesNotExist:
        print("Ошибка: Блюдо не найдено!")


def print_menu():
    print("\nУправление меню ресторана:")
    print("1. Показать категории")
    print("2. Показать ингредиенты")
    print("3. Показать все блюда")
    print("4. Добавить категорию")
    print("5. Добавить ингредиент")
    print("6. Добавить блюдо")
    print("7. Удалить категорию")
    print("8. Удалить ингредиент")
    print("9. Удалить блюдо")
    print("0. Выход")


def main():
    create_tables()
    while True:
        print_menu()
        choice = input("\nВыберите действие: ").strip()

        actions = {
            "1": print_categories,
            "2": print_ingredients,
            "3": print_dishes,
            "4": add_category,
            "5": add_ingredient,
            "6": add_dish,
            "7": delete_category,
            "8": delete_ingredient,
            "9": delete_dish,
            "0": lambda: print("До свидания!") or exit(),
        }

        if action := actions.get(choice):
            action()
        else:
            print("Неверный ввод!")


if __name__ == "__main__":
    main()

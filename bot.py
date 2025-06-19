
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import os

API_TOKEN = '6702986171:AAHqocEsxrFB2MoNG_djIray2DQ7gtpmXOk'
ADMIN_USERNAME = '@Sergey_PIatonov'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class ReviewStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_photo = State()

@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer("Привет! 🐾 Оставьте, пожалуйста, отзыв о товаре. Сначала напишите текст отзыва.")
    await ReviewStates.waiting_for_text.set()

@dp.message_handler(state=ReviewStates.waiting_for_text, content_types=types.ContentTypes.TEXT)
async def process_text(message: types.Message, state: FSMContext):
    await state.update_data(review_text=message.text)
    await message.answer("Спасибо! Теперь, пожалуйста, прикрепите фото отзыва или фото с товаром 🐶")
    await ReviewStates.waiting_for_photo.set()

@dp.message_handler(state=ReviewStates.waiting_for_photo, content_types=types.ContentTypes.PHOTO)
async def process_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    review_text = data['review_text']

    # Пересылаем админу текст и фото
    sender = message.from_user.username or message.from_user.id
    await bot.send_message(ADMIN_USERNAME, f"📩 Новый отзыв от @{sender}:

{review_text}")
    await message.photo[-1].send_copy(ADMIN_USERNAME)

    # Выдаём промокод
    promo_code = get_next_promo_code()
    if promo_code:
        await message.answer(f"Спасибо за отзыв! 🎁 Ваш промокод: {promo_code}\nПримените его при следующем заказе.")
    else:
        await message.answer("Спасибо! Ваш отзыв получен. К сожалению, промокоды временно закончились, но мы свяжемся с вами позже.")

    await state.finish()

def get_next_promo_code():
    try:
        with open("promo_codes.txt", "r") as f:
            codes = f.read().splitlines()
        if not codes:
            return None
        promo = codes[0]
        with open("promo_codes.txt", "w") as f:
            f.write("\n".join(codes[1:]))
        return promo
    except:
        return None

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

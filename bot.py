import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext, MessageHandler, filters
import datetime
import telegram
import mysql.connector
import geopy.distance


# Buat koneksi ke database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="absenqu"
)

# Buat cursor untuk mengeksekusi query SQL
mycursor = mydb.cursor()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def daftar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.message.from_user.id
        user_name = update.message.from_user.first_name
        waktu_daftar = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # memeriksa apakah pengguna sudah terdaftar
        sql = "SELECT COUNT(*) FROM pengguna WHERE nama=%s"
        val = (user_name,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()

        if result[0] > 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Anda sudah terdaftar sebelumnya.")
            return

        # menambahkan pengguna baru ke database
        sql = "INSERT INTO pengguna (nama,chat_id, waktu_daftar) VALUES (%s,%s, %s)"
        val = (user_name, chat_id, waktu_daftar)
        mycursor.execute(sql, val)
        mydb.commit()

        await context.bot.send_message(chat_id=update.effective_chat.id, text="Anda telah berhasil terdaftar.")

    except telegram.error.Conflict:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Maaf, terjadi kesalahan saat melakukan pendaftaran. Silakan coba lagi nanti.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Selamat Datang di Apliaski AbsenQU")

async def absen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Meminta akses lokasi
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Silahkan share lokasi anda 📍 !")


async def location(update: Update, context: CallbackContext, alasan = None):
    user_id = update.message.from_user.first_name
    location = update.message.location
    latitude = location.latitude
    longitude = location.longitude
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Lokasi anda berada\n👨 Nama : {user_id}\n📌Latitude : {latitude}\n📌 Longitude : {longitude}")
    # await context.bot.send_location(chat_id=update.effective_chat.id, latitude=latitude, longitude=longitude)

    try:
        chat_id = update.message.from_user.id
        now = datetime.datetime.now().strftime('%H:%M:%S')
        user_name = update.message.from_user.first_name

        # memeriksa pendaftaran
        sql = "SELECT COUNT(*) FROM pengguna WHERE nama=%s"
        val = (user_name,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()

        if result[0] == 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Data anda belum terdaftar. Ketik /daftar untuk mendaftar !")
            return
        
        # Memeriksa apakah lokasi pengguna sesuai dengan yang tercatat di database
        sql = "SELECT latitude, longitude FROM pengguna WHERE nama=%s"
        val = (user_name,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()

        user_latitude = result[0]
        user_longitude = result[1]
        user_location = (user_latitude, user_longitude)
        current_location = (latitude, longitude)

        distance = geopy.distance.distance(user_location, current_location).km

        if distance > 1:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Anda tidak berada di dalam radius absen.\nSilahkan anda absen kembali !")
            return

        # # Memeriksa apakah pengguna telah melakukan absen pada hari yang sama sebelumnya
        # sql = "SELECT COUNT(*) FROM absen WHERE nama=%s AND DATE(jam_absen) = CURDATE()"
        # val = (user_name,)
        # mycursor.execute(sql, val)
        # result = mycursor.fetchone()

        # if result[0] > 0:
        #     await context.bot.send_message(chat_id=update.effective_chat.id, text="Anda sudah melakukan absen pada hari ini.")
        #     return

        if now >= '05:00:00' and now <= '08:00:00':
            jenis_absen = 'Absen Pagi'
            status = 'Tepat waktu'
        elif now >= '08:01:00' and now <= '15:29:59':
            jenis_absen = 'Absen Pagi'
            status = 'Terlambat'
        elif now >= '15:30:00' and now <= '23:00:00':
            jenis_absen = 'Absen Sore'
            status = 'Tepat waktu'
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Maaf, saat ini tidak bisa melakukan absen.")
            return

        waktu_absen = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Memasukkan data absen ke dalam tabel absen
        sql = "INSERT INTO absen (nama,jenis_absen, jam_absen, status, alasan) VALUES (%s, %s, %s, %s, %s)"
        val = (user_name, jenis_absen, waktu_absen, status, alasan)
        mycursor.execute(sql, val)
        mydb.commit()

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Terima Kasih.\n📖 Aksi: {jenis_absen}\n✅ Nama: {user_name}\n🕖 Jam Absen: {waktu_absen}\n✋ Status: {status}")
        # kirim pesan ke grup Telegram setelah pengguna berhasil absen
        group_chat_id = "-925633085"
        group_message = f"👨 Nama : {user_name}\n🕟 Jam absen: {waktu_absen}\n📖 Aksi : {jenis_absen}"
        await context.bot.send_message(chat_id=group_chat_id, text=group_message)
    except telegram.error.Conflict:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Maaf, terjadi kesalahan saat melakukan absen. Silakan coba lagi nanti.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(
        '6192400416:AAHgSAkjydqDMh5fkqf_Xfd9j2CfRpV0Uts').build()

    start_handler = CommandHandler('start', start)
    absen_handler = CommandHandler('absen', absen)
    daftar_handler = CommandHandler('daftar', daftar)
    location_handler = MessageHandler(filters.LOCATION, location)

    application.add_handler(start_handler)
    application.add_handler(absen_handler)
    application.add_handler(daftar_handler)
    application.add_handler(location_handler)

    application.run_polling()

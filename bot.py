import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext
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
        sql = "INSERT INTO pengguna (nama, waktu_daftar) VALUES (%s, %s)"
        val = (user_name, waktu_daftar)
        mycursor.execute(sql, val)
        mydb.commit()

        await context.bot.send_message(chat_id=update.effective_chat.id, text="Anda telah berhasil terdaftar.")
        
    except telegram.error.Conflict:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Maaf, terjadi kesalahan saat melakukan pendaftaran. Silakan coba lagi nanti.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Selamat Datang di Apliaski AbsenQU")


async def absen(update: Update, context: ContextTypes.DEFAULT_TYPE, alasan = None):
    try:
        now = datetime.datetime.now().strftime('%H:%M:%S')
        user_name = update.message.from_user.first_name
        
        # Memeriksa apakah pengguna sudah terdaftar
        sql = "SELECT COUNT(*) FROM pengguna WHERE nama=%s"
        val = (user_name,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()

        if result[0] == 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Anda belum terdaftar. Silakan daftar terlebih dahulu.")
            return
        
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

        # Get the saved location from the database
        sql = "SELECT latitude, longitude FROM pengguna WHERE nama=%s"
        val = (user_name,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()

        # Check if the saved location is not null
        if not all(result):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Maaf, lokasi anda belum terdaftar.")
            return
        
        # Check if the user is at the saved location
        user_location = update.message.location
        saved_location = (result[0], result[1])
        distance = geopy.distance.distance(user_location, saved_location).km

        if distance > 1:  # adjust the distance threshold as necessary
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Maaf, anda tidak berada pada lokasi yang benar.")
            return
        
        # Memasukkan data absen ke dalam tabel absen
        sql = "INSERT INTO absen (nama, jam_absen, status, alasan) VALUES (%s, %s, %s, %s)"
        val = (user_name, waktu_absen, status, alasan)
        mycursor.execute(sql, val)
        mydb.commit()

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Terima Kasih, {jenis_absen}\n✅Nama: {user_name}\n🕖Jam Absen: {waktu_absen}\n✋Status: {status}")
    except telegram.error.Conflict:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Maaf, terjadi kesalahan saat melakukan absen. Silakan coba lagi nanti.")

if __name__ == '__main__':
    application = ApplicationBuilder().token('6192400416:AAHgSAkjydqDMh5fkqf_Xfd9j2CfRpV0Uts').build()

    start_handler = CommandHandler('start', start)
    absen_handler = CommandHandler('absen', absen)
    daftar_handler = CommandHandler('daftar', daftar)

    application.add_handler(start_handler)
    application.add_handler(absen_handler)
    application.add_handler(daftar_handler)
    

    application.run_polling()

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext, MessageHandler, filters
import datetime
import telegram
import mysql.connector
import geopy.distance
import time
from functools import wraps

# Buat koneksi ke database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="absenqu"
)

# Memeriksa apakah koneksi terputus dan mencoba menghubungkan kembali
if mydb.is_connected() == False:
    print("KOneksi terputus. Mencoba menghubungi kembali...")
    mydb.reconnect(attempts=1, delay=0)
    if mydb.is_connected() == True:
        print("Koneksi berhasil tersambung kembali.")


# Buat cursor untuk mengeksekusi query SQL
mycursor = mydb.cursor()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Selamat Datang di Apliaski SiabsenQU")

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
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Selamat Datang di Apliaski SiabsenQU")

async def absen(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.from_user.id
        now = datetime.datetime.now().strftime('%H:%M:%S')
        user_name = update.message.from_user.first_name

        # memeriksa apakah pengguna sudah terdaftar
        sql = "SELECT COUNT(*) FROM pengguna WHERE nama=%s"
        val = (user_name,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()

        if result[0] == 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Data anda belum terdaftar. Ketik /daftar untuk mendaftar !")
            return

        # Meminta akses lokasi
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Silahkan share lokasi anda 📍 !")

async def location(update: Update, context: CallbackContext, alasan = None):
    user_id = update.message.from_user.first_name
    location = update.message.location
    latitude = location.latitude
    longitude = location.longitude
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Lokasi anda berada\n👨 Nama : {user_id}\n📌 Latitude : {latitude}\n📌 Longitude : {longitude}")
    # await context.bot.send_location(chat_id=update.effective_chat.id, latitude=latitude, longitude=longitude)

    try:
        chat_id = update.message.from_user.id
        now = datetime.datetime.now().strftime('%H:%M:%S')
        user_name = update.message.from_user.first_name

        # memeriksa apakah pengguna sudah terdaftar
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

        if user_latitude is None or user_longitude is None:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Lokasi Anda belum terdaftar, hubungi admin!")
            return

        distance = geopy.distance.distance(user_location, current_location).km

        if distance > 1:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Anda tidak berada di dalam radius absen.\nSilahkan anda absen kembali !")
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

        # Memeriksa apakah pengguna telah melakukan absen pada hari yang sama sebelumnya
        sql = "SELECT COUNT(*) FROM absen WHERE nama=%s AND DATE(jam_absen) = CURDATE() AND jenis_absen=%s"
        val = (user_name,jenis_absen)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()

        if result[0] > 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Anda sudah melakukan absen {jenis_absen} hari ini.")
            return

        waktu_absen = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Memasukkan data absen ke dalam tabel absen
        sql = "INSERT INTO absen (nama,jenis_absen, jam_absen, status, alasan) VALUES (%s, %s, %s, %s, %s)"
        val = (user_name, jenis_absen, waktu_absen, status, alasan)
        mycursor.execute(sql, val)
        mydb.commit()

        # kirim pesan status absen ke bot
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Terima Kasih.\n📖 Aksi: {jenis_absen}\n✅ Nama: {user_name}\n🕖 Jam Absen: {waktu_absen}\n✋ Status: {status}")

        # # kirim pesan ke grup Telegram setelah pengguna berhasil absen
        # group_chat_id = "-925633085"
        # group_message = f"✅ Nama : {user_name}\n🕟 Jam absen: {waktu_absen}\n📖 Aksi : {jenis_absen}"
        # await context.bot.send_message(chat_id=group_chat_id, text=group_message)

    except telegram.error.Conflict:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Maaf, terjadi kesalahan saat melakukan absen. Silakan coba lagi nanti.")


async def sakit (update : Update, context : ContextTypes.DEFAULT_TYPE, alasan=None):

    user_name = update.message.from_user.first_name
    waktu_absen = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    jenis_absen = 'Sakit'
    status = 'Tidak hadir'

    # memeriksa apakah pengguna sudah terdaftar
    sql = "SELECT COUNT(*) FROM pengguna WHERE nama=%s"
    val = (user_name,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()

    if result[0] == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Data anda belum terdaftar. Ketik /daftar untuk mendaftar !")
        return
    
    # Memeriksa apakah pengguna telah melakukan absen pada hari yang sama sebelumnya
    sql = "SELECT COUNT(*) FROM absen WHERE nama = %s AND DATE(jam_absen) = CURDATE() AND jenis_absen = %s"
    val = (user_name, jenis_absen)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()

    if result[0] > 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Anda sudah melakukan absen {jenis_absen} untuk hari ini.")
        return

    # Memasukkan data absen ke dalam tabel absen
    sql = "INSERT INTO absen (nama,jenis_absen, jam_absen, status, alasan) VALUES (%s, %s, %s, %s, %s)"
    val = (user_name, jenis_absen, waktu_absen, status, alasan)
    mycursor.execute(sql, val)
    mydb.commit()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Terima Kasih, Lekas sembuh.\n📖 Aksi : {jenis_absen}\n✅ Nama : {user_name}\n🕖 Waktu absen : {waktu_absen}\n✋ Status : {status}")

async def izin (update : Update, context : ContextTypes.DEFAULT_TYPE):

    # alasan = " ".join(context.args)
    user_name = update.message.from_user.first_name
    jenis_absen = 'Izin'
    
    # memeriksa apakah pengguna sudah terdaftar
    sql = "SELECT COUNT(*) FROM pengguna WHERE nama=%s"
    val = (user_name,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()

    if result[0] == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Data anda belum terdaftar. Ketik /daftar untuk mendaftar !")
        return
    
    # Memeriksa apakah pengguna telah melakukan absen pada hari yang sama sebelumnya
    sql = "SELECT COUNT(*) FROM absen WHERE nama = %s AND DATE(jam_absen) = CURDATE() AND jenis_absen = %s"
    val = (user_name, jenis_absen)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()

    if result[0] > 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Anda sudah melakukan absen {jenis_absen} untuk hari ini.")
        return
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Masukkan alasan anda ! ')
    
async def alasan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    input_alasan = update.message.text
    waktu_absen = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    jenis_absen = 'Izin'
    status = 'Tidak hadir'
    
    # Memeriksa apakah pengguna telah melakukan absen pada hari yang sama sebelumnya
    sql = "SELECT COUNT(*) FROM absen WHERE nama = %s AND DATE(jam_absen) = CURDATE() AND jenis_absen = %s"
    val = (user_name, jenis_absen)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()

    if result[0] > 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Anda sudah melakukan absen {jenis_absen} untuk hari ini.")
        return
    
    # Memasukkan data absen ke dalam tabel absen
    sql = "INSERT INTO absen (nama,jenis_absen, jam_absen, status, alasan) VALUES (%s, %s, %s, %s, %s)"
    val = (user_name, jenis_absen, waktu_absen, status, input_alasan)
    mycursor.execute(sql, val)
    mydb.commit()


    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Terima kasih, izin Anda sudah tercatat.\n📖 Aksi : {jenis_absen}\n✅ Nama : {user_name}\n🕖 Waktu absen : {waktu_absen}\n✋ Status : {status}\n📝 Alasan : {input_alasan}")
    

if __name__ == '__main__':
    application = ApplicationBuilder().token(
        '6160156503:AAF3D2SxB31ibEKsp67dIJZjcfp118qXHxo').build()

    # command bot telegram
    start_handler = CommandHandler('start', start)
    absen_handler = CommandHandler('absen', absen)
    daftar_handler = CommandHandler('daftar', daftar)
    location_handler = MessageHandler(filters.LOCATION, location)
    sakit_handler = CommandHandler('sakit', sakit)
    izin_handler = CommandHandler('izin', izin)
    alasan_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), alasan)

    # handler bot telegram
    application.add_handler(start_handler)
    application.add_handler(absen_handler)
    application.add_handler(daftar_handler)
    application.add_handler(location_handler)
    application.add_handler(sakit_handler)
    application.add_handler(izin_handler)
    application.add_handler(alasan_handler)

    application.run_polling()
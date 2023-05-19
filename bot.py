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

# ========= Funsi CRUD ========= #

# Fungsi decorator untuk mengatur waktu logout jika tidak ada aktivitas
def auto_logout(timeout):
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context):
            chat_id = update.effective_chat.id
            user_data = context.user_data.setdefault(chat_id, {})
            last_activity = user_data.get('last_activity', time.time())

            # Menghitung selisih waktu sejak aktivitas terakhir
            elapsed_time = time.time() - last_activity

            # Mengatur waktu aktivitas terakhir
            user_data['last_activity'] = time.time()

            result = await func(update, context)

            # Logout jika tidak ada aktivitas dalam waktu yang ditentukan
            if elapsed_time > timeout:
                del context.user_data[chat_id]  # Hapus data pengguna dari user_data

            return result
        return wrapper
    return decorator

@auto_logout(timeout=60)
async def login_data(update: Update, context: CallbackContext) -> None:
    # Cek apakah format perintah /login valid
    try:
        username, password = update.message.text.split()[1:]
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Format perintah salah. Contoh: /login username password")
        return

    # Verifikasi apakah username dan password valid
    is_admin = False
    sql = "SELECT * FROM admin WHERE username = %s AND password = %s"
    val = (username, password)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    if result:
        is_admin = True

    # Berikan tindakan sesuai dengan status admin
    if is_admin:
        context.user_data[update.effective_chat.id] = {'admin': True}
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Anda telah berhasil login sebagai admin.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Username atau password salah.")

@auto_logout(timeout=60)
async def read_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Periksa apakah pengguna memiliki akses admin
    if not context.user_data.get(update.effective_chat.id, {}).get('admin', False):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Maaf, hanya admin yang dapat mengakses fungsi ini.")
        return

    # Jika pengguna adalah admin, jalankan kode normal untuk membaca data
    sql = "SELECT * FROM pengguna"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    message = "Data yang tersimpan di database:\n\n"
    for row in result:
        message += f"ID: {row[0]},\nNama: {row[1]},\nWaktu Daftar: {row[2]},\nLatitude: {row[3]},\nLongitude: {row[4]},\nChat ID: {row[5]}\n\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

@auto_logout(timeout=60)
async def create_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Periksa apakah pengguna memiliki akses admin
    if not context.user_data.get(update.effective_chat.id, {}).get('admin', False):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Maaf, hanya admin yang dapat mengakses fungsi ini.")
        return

    # Jika pengguna adalah admin, jalankan kode normal untuk membuat data
    data = update.message.text.split()[1:]
    sql = "INSERT INTO pengguna (nama, waktu_daftar, latitude, longitude, chat_id) VALUES (%s, %s, %s, %s, %s)"
    val = tuple(data)
    mycursor.execute(sql, val)
    mydb.commit()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Data berhasil ditambahkan!")

@auto_logout(timeout=60)
async def edit_data(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    # Periksa apakah pengguna memiliki hak akses
    if not context.user_data.get(chat_id, {}).get('admin', False):
        await context.bot.send_message(chat_id=chat_id, text="Anda tidak memiliki hak akses.")
        return

    # Ambil data yang ingin diubah dari pesan pengguna
    try:
        id, kolom, nilai_baru = update.message.text.split()[1:]
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="Format pesan tidak valid.")
        return

    # Update data sesuai dengan id, kolom, dan nilai baru yang diberikan
    try:
        sql = f"UPDATE pengguna SET {kolom} = %s WHERE id = %s"
        val = (nilai_baru, id)
        mycursor.execute(sql, val)
        mydb.commit()
        await context.bot.send_message(chat_id=chat_id, text="Data berhasil diperbarui!")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Terjadi kesalahan: {e}")

@auto_logout(timeout=60)
async def delete_data(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    # Periksa apakah pengguna memiliki hak akses
    if not context.user_data.get(chat_id, {}).get('admin', False):
        await context.bot.send_message(chat_id=chat_id, text="Anda tidak memiliki hak akses.")
        return
    
    # Ambil id data yang ingin dihapus dari pesan pengguna
    try:
        id = update.message.text.split()[1]
    except IndexError:
        await context.bot.send_message(chat_id=chat_id, text="Format pesan tidak valid.")
        return

    # Hapus data dari database sesuai dengan id yang diberikan
    try:
        sql = "DELETE FROM pengguna WHERE id = %s"
        val = (id,)
        mycursor.execute(sql, val)
        mydb.commit()
        await context.bot.send_message(chat_id=chat_id, text="Data berhasil dihapus!")
    except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=f"Terjadi kesalahan: {e}")
            
# =============================== #

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

    start_handler = CommandHandler('start', start)
    absen_handler = CommandHandler('absen', absen)
    daftar_handler = CommandHandler('daftar', daftar)
    location_handler = MessageHandler(filters.LOCATION, location)
    sakit_handler = CommandHandler('sakit', sakit)
    izin_handler = CommandHandler('izin', izin)
    alasan_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), alasan)

    application.add_handler(start_handler)
    application.add_handler(absen_handler)
    application.add_handler(daftar_handler)
    application.add_handler(location_handler)
    application.add_handler(sakit_handler)
    application.add_handler(izin_handler)
    application.add_handler(alasan_handler)


    # Command CRUD
    login_handler = CommandHandler('login',login_data)
    read_handler = CommandHandler('read', read_data)
    create_handler = CommandHandler('create', create_data)
    edit_handler = CommandHandler('edit', edit_data)
    delete_handler = CommandHandler('delete', delete_data)

    # Handler CRUD
    application.add_handler(login_handler)
    application.add_handler(read_handler)
    application.add_handler(create_handler)
    application.add_handler(edit_handler)
    application.add_handler(delete_handler)

    application.run_polling()
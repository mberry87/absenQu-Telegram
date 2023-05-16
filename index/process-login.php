<?php
// Memulai sesi
session_start();

// Menghubungkan file config.php
require_once "config.php";

// Ambil data login dari formulir
$username = $_POST['username'];
$password = $_POST['password'];

// Query untuk mencari admin dengan username dan password yang sesuai
$sql = "SELECT * FROM admin WHERE username = '$username' AND password = '$password'";

// Jalankan query dan periksa hasilnya
$result = mysqli_query($conn, $sql);
if (!$result) {
    die("Query error: " . mysqli_error($conn));
}

// Periksa apakah data login benar
if (mysqli_num_rows($result) == 1) {
    // Data login benar, simpan informasi pengguna di sesi
    session_start();
    $_SESSION['username'] = $username;

    // Alihkan pengguna ke halaman utama
    header("Location: home.php");
    exit();
} else {
    // Data login salah, tampilkan pesan error dan kembali ke halaman login
    session_start();
    $_SESSION['error'] = "Username atau password salah.";
    header("Location: login.php");
    exit();
}

// Tutup koneksi
mysqli_close($conn);
?>

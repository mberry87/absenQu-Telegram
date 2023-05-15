<?php
require_once 'config.php';

// Ambil ID pengguna dari URL
$id = $_GET['id'];

// Query untuk menghapus data pengguna dengan ID tertentu
$sql = "DELETE FROM pengguna WHERE id = $id";

if (mysqli_query($conn, $sql)) {
    // Jika query berhasil, redirect ke halaman daftar pengguna dengan pesan sukses
    header('Location: user.php?status=sukses_hapus');
} else {
    // Jika query gagal, tampilkan pesan error
    echo "Error: " . mysqli_error($conn);
}

mysqli_close($conn);

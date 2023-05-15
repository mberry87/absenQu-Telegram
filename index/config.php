<?php

$host = "localhost"; // Nama host database
$username = "root"; // Username database
$password = ""; // Password database
$dbname = "absenqu"; // Nama database

// Buat koneksi ke database
$conn = mysqli_connect($host, $username, $password, $dbname);

// Cek koneksi
if (!$conn) {
    die("Koneksi gagal: " . mysqli_connect_error());
}

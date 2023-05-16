<?php
session_start();

// Cek apakah user sudah login
if (!isset($_SESSION['username'])) {
    // Jika belum, redirect ke halaman login
    header('Location: login.php');
    exit();
}

// Ambil username dari session
$username = $_SESSION['username'];

// Koneksi ke database
require_once('config.php');

// Batasi jumlah data yang ditampilkan pada setiap halaman
$limit = 10;

// Hitung jumlah total data pada tabel
$queryCount = "SELECT COUNT(*) as total FROM pengguna";
$resultCount = mysqli_query($conn, $queryCount);
$rowCount = mysqli_fetch_assoc($resultCount);
$totalData = $rowCount['total'];

// Hitung jumlah total halaman yang tersedia
$totalPages = ceil($totalData / $limit);

// Tentukan halaman aktif
$currentPage = (isset($_GET['page']) && is_numeric($_GET['page'])) ? $_GET['page'] : 1;

// Hitung offset untuk query LIMIT
$offset = ($currentPage - 1) * $limit;

// Query untuk mengambil data absen dengan batasan jumlah dan offset
$query = "SELECT * FROM pengguna LIMIT $offset, $limit";
$result = mysqli_query($conn, $query)

?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
</head>

<body>
    <div class="container">
        <?php
        include 'navbar.php'
        ?>
    </div>
    <div class="container mt-4">
        <h5>Tabel Usert</h5>
        <table class="table table-responsive table-striped">
            <thead>
                <tr>
                    <th>No</th>
                    <th>Nama</th>
                    <th>Waktu_Daftar</th>
                    <th>Latitude</th>
                    <th>Longitude</th>
                    <th>Chat_ID</th>
                    <th>Aksi</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $no = 1;
                // Looping untuk menampilkan data user ke dalam tabel
                while ($row = mysqli_fetch_assoc($result)) {
                    echo "<tr>";
                    echo "<td>" . $no . "</td>";
                    echo "<td>" . $row['nama'] . "</td>";
                    echo "<td>" . $row['waktu_daftar'] . "</td>";
                    echo "<td>" . $row['latitude'] . "</td>";
                    echo "<td>" . $row['longitude'] . "</td>";
                    echo "<td>" . $row['chat_id'] . "</td>";
                    echo '<td>
                    <a href="edit_user.php?id=' . $row['id'] . '" class="btn btn-warning btn-sm">Edit</a>
                    <a href="hapus_user.php?id=' . $row['id'] . '" onclick="return confirm(\'Anda yakin ingin menghapus pengguna ini?\')" class="btn btn-danger btn-sm">Hapus</a>
                    </td>';
                    echo "</tr>";
                    $no++;
                }

                // Tutup koneksi ke database
                mysqli_close($conn);

                // Pesan sukses jika data berhasil dihapus
                if (isset($_GET['status']) && $_GET['status'] == 'sukses_hapus') {
                    echo '<div class="alert alert-success" role="alert">Data pengguna berhasil dihapus!</div>';
                }

                // Pesan error jika ada masalah saat menghapus data pengguna
                if (isset($_GET['status']) && $_GET['status'] == 'error_hapus') {
                    echo '<div class="alert alert-danger" role="alert">Terjadi kesalahan saat menghapus data pengguna.</div>';
                }

                ?>
            </tbody>
        </table>

        <nav aria-label="Page navigation ">
            <ul class="pagination justify-content-end">
                <?php if ($currentPage > 1) : ?>
                    <li class="page-item"><a class="page-link" href="?page=<?php echo ($currentPage - 1); ?>">Kembali</a></li>
                <?php endif; ?>

                <?php for ($i = 1; $i <= $totalPages; $i++) : ?>
                    <li class="page-item <?php echo ($i == $currentPage) ? 'active' : ''; ?>"><a class="page-link" href="?page=<?php echo $i; ?>"><?php echo $i; ?></a></li>
                <?php endfor; ?>

                <?php if ($currentPage < $totalPages) : ?>
                    <li class="page-item"><a class="page-link" href="?page=<?php echo ($currentPage + 1); ?>">Lanjut</a></li>
                <?php endif; ?>
            </ul>
        </nav>

    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>

    <?php
    include 'footer.php'
    ?>

</body>

</html>
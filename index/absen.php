<?php

// Koneksi ke database
require_once('config.php');

// Batasi jumlah data yang ditampilkan pada setiap halaman
$limit = 10;

// Hitung jumlah total data pada tabel
$queryCount = "SELECT COUNT(*) as total FROM absen";
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
$query = "SELECT * FROM absen ORDER BY id DESC LIMIT $offset, $limit";
$result = mysqli_query($conn, $query)

?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Absen</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
</head>

<body>
    <div class="container">
        <?php
        include 'navbar.php'
        ?>
    </div>
    <div class="container mt-4">
        <h5>Tabel Absen</h5>
        <table class="table table-responsive table-striped">
            <thead>
                <tr>
                    <th>No</th>
                    <th>Nama</th>
                    <th>Jenis Absen</th>
                    <th>Jam Absen</th>
                    <th>Status</th>
                    <th>Alasan</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $no = 1;
                // Looping untuk menampilkan data absen ke dalam tabel
                while ($row = mysqli_fetch_assoc($result)) {
                    echo "<tr>";
                    echo "<td>" . $no . "</td>";
                    echo "<td>" . $row['nama'] . "</td>";
                    echo "<td>" . $row['jenis_absen'] . "</td>";
                    echo "<td>" . $row['jam_absen'] . "</td>";
                    echo "<td>" . $row['status'] . "</td>";
                    echo "<td>" . $row['alasan'] . "</td>";
                    echo "</tr>";
                    $no++;
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
</body>

</html>